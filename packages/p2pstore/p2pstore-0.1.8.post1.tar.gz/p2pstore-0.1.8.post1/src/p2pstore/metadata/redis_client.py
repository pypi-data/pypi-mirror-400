"""
Redis Metadata Client 实现模块.

该模块实现了基于 Redis 的元数据客户端，支持三种部署模式：
- Standalone: 单机 Redis
- Sentinel: Redis Sentinel 高可用
- Cluster: Redis Cluster 集群

特性:
- 使用 String 数据结构存储元数据 (JSON 序列化)
- 使用 TTL 管理 Provider 和文件的生命周期
- 使用 Pub/Sub 机制实现删除事件通知（可选）
- 使用 Set 维护文件索引，加速 list_keys 查询
"""

import json
import random
import threading
import time
from typing import Any, Callable, TypeVar, cast

from ..core import MetadataClient
from ..utils.logger import LoggerManager


T = TypeVar("T")


class RedisMetadataClient(MetadataClient):
    """
    Redis 元数据客户端.

    Key 设计:
    - p2p:providers:{host}   : Provider 信息 (String with TTL)
    - p2p:files:{file_key}   : 文件元数据 (String with JSON)
    - p2p:files:index        : 所有文件 key 的集合 (Set)
    - p2p:events             : 文件变更 Pub/Sub 频道
    """

    PREFIX_PROVIDER = "p2p:providers:"
    PREFIX_FILE = "p2p:files:"
    KEY_FILE_INDEX = "p2p:files:index"
    CHANNEL_EVENTS = "p2p:events"

    def __init__(
        self,
        config: Any,  # P2PConfig
        local_ip: str,
        client_id: str,
        registered_keys: dict[str, int] | None = None,
    ):
        self.logger = LoggerManager.get_logger("redis-metadata-client")
        self.local_ip = local_ip
        self.client_id = client_id
        self._registered_keys = registered_keys if registered_keys is not None else {}

        # 配置
        self.config = config
        self.ttl = config.redis_key_ttl
        # Provider TTL: 0 表示跟随 redis_key_ttl，否则使用独立值
        self.provider_ttl = getattr(config, "redis_provider_ttl", 0) or self.ttl
        self.enable_watch = config.enable_watch

        # 连接 Redis
        # redis-py 的同步/异步类型存根在不同版本差异较大，这里显式标注为 Any
        # 避免静态分析将其误推断为 asyncio client 导致 Awaitable 相关误报。
        self._client: Any = self._connect_redis()

        # 重试配置：用于降低高并发/短暂抖动导致的“本轮失败退出”概率
        # 允许在 P2PConfig 中新增这些字段；不存在时使用默认值，不破坏兼容性
        self._max_retries: int = int(getattr(config, "redis_max_retries", 5))
        self._base_backoff_s: float = float(
            getattr(config, "redis_retry_backoff_s", 0.05)
        )

        # Lua 原子脚本：尽量减少“写成功/删成功但事件或索引更新失败”的不一致
        # 对于不支持 script 的 client，会自动 fallback
        self._lua_register_file: Callable[..., Any] | None = None
        self._lua_delete_file: Callable[..., Any] | None = None
        self._lua_bulk_delete_files: Callable[..., Any] | None = None
        try:
            register_script = getattr(self._client, "register_script", None)
            if callable(register_script):
                self._lua_register_file = cast(
                    Callable[..., Any],
                    register_script(
                        """
                        -- KEYS[1] = p2p:files:{file_key}
                        -- KEYS[2] = p2p:files:index
                        -- ARGV[1] = value(json)
                        -- ARGV[2] = ttl (0 means no ttl)
                        -- ARGV[3] = file_key
                        local ttl = tonumber(ARGV[2])
                        if ttl ~= nil and ttl > 0 then
                          redis.call('SETEX', KEYS[1], ttl, ARGV[1])
                        else
                          redis.call('SET', KEYS[1], ARGV[1])
                        end
                        redis.call('SADD', KEYS[2], ARGV[3])
                        return 1
                        """
                    ),
                )
                self.logger.info("[REDIS] register_file 已启用 Lua 原子写")

                # delete_file: 原子 get+del+srem，返回被删除的 value(json)；不存在则返回 false
                self._lua_delete_file = cast(
                    Callable[..., Any],
                    register_script(
                        """
                        -- KEYS[1] = p2p:files:{file_key}
                        -- KEYS[2] = p2p:files:index
                        -- ARGV[1] = file_key
                        local v = redis.call('GET', KEYS[1])
                        if v then
                          redis.call('DEL', KEYS[1])
                          redis.call('SREM', KEYS[2], ARGV[1])
                          return v
                        end
                        return false
                        """
                    ),
                )

                # bulk_delete_files: 原子批量 get+del+srem，返回被删除的 value(json) 列表
                # KEYS[1] = index, KEYS[2..] = file redis keys
                # ARGV[1..] = file_key(plain) 对应 KEYS[2..]
                self._lua_bulk_delete_files = cast(
                    Callable[..., Any],
                    register_script(
                        """
                        -- KEYS[1] = p2p:files:index
                        -- KEYS[2..n] = p2p:files:{file_key}
                        -- ARGV[1..n-1] = file_key
                        local out = {}
                        for i=2,#KEYS do
                          local v = redis.call('GET', KEYS[i])
                          if v then
                            redis.call('DEL', KEYS[i])
                            redis.call('SREM', KEYS[1], ARGV[i-1])
                            out[#out+1] = v
                          end
                        end
                        return out
                        """
                    ),
                )
                self.logger.info(
                    "[REDIS] delete_file/clear/delete_prefix 已启用 Lua 原子删"
                )
            else:
                self.logger.info(
                    "[REDIS] 当前 redis client 不支持 register_script，register_file 将使用 pipeline"
                )
        except Exception as e:
            # 不要因为 Lua 初始化失败而阻止客户端启动
            self.logger.warning(
                "[REDIS] register_file Lua 初始化失败，将回退到 pipeline: %s",
                e,
            )

        # 本地状态
        self.running = True
        self._stop_event = threading.Event()
        self.local_host = None
        self._all_hosts: list[str] = []
        self._hosts_lock = threading.Lock()
        self._watch_thread: threading.Thread | None = None
        self._heartbeat_thread: threading.Thread | None = None
        self._release_callback = None
        self._delete_prefix_callback = None  # 前缀删除回调
        self._pubsub: Any | None = None

        # 如果启用 TTL（文件或 Provider），启动心跳线程
        if self.ttl > 0 or self.provider_ttl > 0:
            self._heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop, daemon=True
            )
            self._heartbeat_thread.start()

        # 根据配置决定是否启动 Watch (Pub/Sub)
        if self.enable_watch:
            self._start_watch()
        else:
            self.logger.info("[REDIS] Watch 线程已禁用 (适用于纯 Consumer get 节点)")

    def _publish_delete_events_from_values(self, values: list[str]) -> int:
        """根据被删除记录的 JSON 值发布 delete 事件（带 put_id/client_id，用于 RDMA 版本匹配）。"""

        if (not self.enable_watch) or (not values):
            return 0

        pipe = self._client.pipeline()
        published = 0
        for v in values:
            try:
                data = json.loads(v)
                file_key = data.get("file_key")
                metadata = data.get("metadata", {})
                if not file_key:
                    continue
                event = {
                    "type": "delete",
                    "file_key": file_key,
                    "client_id": metadata.get("client_id"),
                    "put_id": metadata.get("put_id"),
                }
                pipe.publish(self.CHANNEL_EVENTS, json.dumps(event))
                published += 1
            except Exception:
                # 单条坏数据不影响整体删除流程
                continue

        if published > 0:
            self._with_retry("publish_delete_events(pipeline)", lambda: pipe.execute())
        return published

    def _with_retry(self, op_name: str, fn: Callable[[], T]) -> T:
        """对短暂连接/超时抖动做有限重试，尽量避免‘本轮失败退出’。"""

        last_e: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                return fn()
            except Exception as e:
                last_e = e
                name = type(e).__name__
                msg = str(e).lower()

                # 只对可恢复错误做重试：连接/超时/加载中/集群切换等
                recoverable = (
                    "timeout" in name.lower()
                    or "connection" in name.lower()
                    or "busyloading" in name.lower()
                    or "loading" in msg
                    or "timed out" in msg
                    or "timeout" in msg
                    or "connection" in msg
                    or "unavailable" in msg
                    or "try again" in msg
                )
                if (not recoverable) or attempt >= self._max_retries:
                    raise

                # 指数退避 + 抖动，避免惊群
                sleep_s = self._base_backoff_s * (2 ** (attempt - 1))
                sleep_s = sleep_s * (0.8 + 0.4 * random.random())
                self.logger.warning(
                    "[REDIS] %s 失败，准备重试: attempt=%d/%d, sleep=%.3fs, err_type=%s, err=%s",
                    op_name,
                    attempt,
                    self._max_retries,
                    sleep_s,
                    name,
                    e,
                )
                time.sleep(sleep_s)

        # 理论上不会到这里
        assert last_e is not None
        raise last_e

    def _bulk_delete(self, keys: list[str]) -> int:
        """批量删除 key：优先 UNLINK，fallback 到 DEL。返回删除数量（以 Redis 返回为准）。"""

        if not keys:
            return 0

        def _op():
            # redis-py: unlink(*names) 返回删除数量；不存在时 AttributeError
            unlink = getattr(self._client, "unlink", None)
            if callable(unlink):
                return unlink(*keys)
            return self._client.delete(*keys)

        res = self._with_retry("bulk_delete", _op)
        try:
            return int(cast(Any, res))
        except Exception:
            # 极端情况下 redis 客户端返回值类型不符合预期；宁可返回 0 也不要让清理流程崩掉
            return 0

    def _register_file_pipeline(self, key: str, file_key: str, value: str) -> None:
        """register_file 的 pipeline fallback（非原子，但比逐条命令 RTT 更少）。"""

        pipe = self._client.pipeline()
        if self.ttl > 0:
            pipe.setex(key, self.ttl, value)
        else:
            pipe.set(key, value)
        pipe.sadd(self.KEY_FILE_INDEX, file_key)
        pipe.execute()

    def _connect_redis(self):
        """根据配置连接 Redis."""
        try:
            import redis
            from redis.sentinel import Sentinel
        except ImportError as e:
            raise ImportError("redis 库未安装，请运行: pip install redis") from e

        mode = self.config.redis_mode
        self.logger.info(
            "[REDIS] 连接模式: %s, file_ttl=%ds, provider_ttl=%ds",
            mode,
            self.ttl,
            self.provider_ttl,
        )

        common_kwargs = {
            "socket_timeout": self.config.redis_socket_timeout,
            "socket_connect_timeout": self.config.redis_socket_connect_timeout,
            "decode_responses": True,  # 自动解码为字符串
            "health_check_interval": 30,  # 每 30 秒健康检查
        }

        if self.config.redis_password:
            common_kwargs["password"] = self.config.redis_password
        if self.config.redis_username:
            common_kwargs["username"] = self.config.redis_username

        if mode == "standalone":
            client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                **common_kwargs,
            )
            self.logger.info(
                "[REDIS] 连接单机: %s:%d db=%d",
                self.config.redis_host,
                self.config.redis_port,
                self.config.redis_db,
            )

        elif mode == "sentinel":
            sentinel = Sentinel(
                self.config.redis_sentinel_nodes,
                socket_timeout=self.config.redis_socket_timeout,
            )
            client = sentinel.master_for(
                self.config.redis_sentinel_service,
                db=self.config.redis_db,
                **common_kwargs,
            )
            self.logger.info(
                "[REDIS] 连接 Sentinel: nodes=%s, service=%s, db=%d",
                self.config.redis_sentinel_nodes,
                self.config.redis_sentinel_service,
                self.config.redis_db,
            )

        elif mode == "cluster":
            from redis.cluster import RedisCluster

            # Cluster 模式不支持 db 参数
            cluster_kwargs = {k: v for k, v in common_kwargs.items() if k != "db"}
            startup_nodes = [
                {"host": host, "port": port}
                for host, port in self.config.redis_cluster_nodes
            ]
            client = RedisCluster(
                startup_nodes=cast(Any, startup_nodes),
                **cluster_kwargs,
            )
            self.logger.info(
                "[REDIS] 连接 Cluster: nodes=%s",
                self.config.redis_cluster_nodes,
            )
        else:
            raise ValueError(f"不支持的 Redis 模式: {mode}")

        # 测试连接
        try:
            client.ping()
            self.logger.info("[REDIS] 连接成功")
        except Exception as e:
            self.logger.error("[REDIS] 连接失败: %s", e)
            raise

        return client

    def _start_watch(self):
        """启动 Pub/Sub 监听线程."""
        self._watch_thread = threading.Thread(target=self._watch_pubsub, daemon=True)
        self._watch_thread.start()

    def _watch_pubsub(self):
        """监听 Pub/Sub 频道的文件变更事件."""
        self.logger.info("[REDIS] 开始监听 Pub/Sub 频道: %s", self.CHANNEL_EVENTS)

        try:
            # 注意：pubsub.listen() 可能阻塞，导致 close() 后线程无法及时退出。
            # 这里改为 get_message + timeout 轮询，以便响应 stop_event。
            pubsub = self._client.pubsub()
            self._pubsub = pubsub
            pubsub.subscribe(self.CHANNEL_EVENTS)

            while self.running and (not self._stop_event.is_set()):
                try:
                    message = pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=5.0
                    )
                except Exception as e:
                    # 连接抖动时允许重试；不要让 watch 线程直接退出
                    if self.running and (not self._stop_event.is_set()):
                        self.logger.warning("[REDIS-WATCH] get_message 异常: %s", e)
                        time.sleep(0.2)
                    continue

                if not message:
                    continue

                if message.get("type") != "message":
                    continue

                try:
                    data = json.loads(message.get("data"))
                    event_type = data.get("type")
                    file_key = data.get("file_key")
                    deleted_client_id = data.get("client_id")
                    deleted_put_id = data.get("put_id")

                    self.logger.debug(
                        "[REDIS-WATCH] 收到事件: type=%s, key=%s, client_id=%s",
                        event_type,
                        file_key,
                        deleted_client_id,
                    )

                    if event_type == "delete" and file_key:
                        self._handle_delete_event(
                            file_key, deleted_put_id, deleted_client_id
                        )
                    elif event_type == "delete_prefix":
                        prefix = data.get("prefix")
                        initiator_client_id = data.get("initiator_client_id")
                        if prefix:
                            self._handle_delete_prefix_event(prefix, initiator_client_id)

                except json.JSONDecodeError as e:
                    self.logger.warning("[REDIS-WATCH] 解析消息失败: %s", e)
                except Exception as e:
                    self.logger.error(
                        "[REDIS-WATCH] 处理事件异常: %s", e, exc_info=True
                    )

        except Exception as e:
            if self.running and (not self._stop_event.is_set()):
                self.logger.error("[REDIS-WATCH] Pub/Sub 线程异常退出: %s", e)
        finally:
            try:
                if self._pubsub is not None:
                    self._pubsub.close()
            except Exception:
                pass
            self._pubsub = None

    def _handle_delete_event(
        self,
        file_key: str,
        deleted_put_id: int | None,
        deleted_client_id: str | None,
    ):
        """处理删除事件."""
        # 检查是否是本 client 的数据
        if file_key not in self._registered_keys:
            self.logger.debug(
                "[REDIS-WATCH] key=%s 不在 _registered_keys，跳过",
                file_key,
            )
            return

        # 获取本地记录
        current_key_info = self._registered_keys[file_key]
        current_put_id = (
            current_key_info.get("put_id")
            if isinstance(current_key_info, dict)
            else current_key_info
        )

        # 验证 client_id
        if deleted_client_id is not None and deleted_client_id != self.client_id:
            self.logger.warning(
                "[REDIS-WATCH] client_id 不匹配: key=%s, deleted=%s, my=%s",
                file_key,
                deleted_client_id,
                self.client_id,
            )
            return

        # 验证 put_id
        if deleted_put_id is not None and current_put_id != deleted_put_id:
            self.logger.info(
                "[REDIS-WATCH] put_id 不匹配，跳过: key=%s, current=%s, deleted=%s",
                file_key,
                current_put_id,
                deleted_put_id,
            )
            return

        # 触发释放回调
        self.logger.info(
            "[REDIS-WATCH] 触发释放回调: key=%s, put_id=%s, client_id=%s",
            file_key,
            current_put_id,
            self.client_id,
        )

        if self._release_callback:
            self._release_callback(file_key, current_put_id, self.client_id)
        else:
            self.logger.debug(
                "[REDIS-WATCH] 释放回调未设置，跳过: key=%s",
                file_key,
            )

    def _handle_delete_prefix_event(
        self, prefix: str, initiator_client_id: str | None = None
    ):
        """处理前缀删除事件（用于删除本地磁盘缓存）.

        Args:
            prefix: 被删除的前缀
            initiator_client_id: 发起删除操作的 client_id，用于避免发起方重复删除
        """
        # 如果是自己发起的删除，跳过回调（发起方已在 delete_prefix 中主动删除了本地缓存）
        if initiator_client_id == self.client_id:
            self.logger.debug(
                "[REDIS-WATCH] 跳过自身发起的前缀删除事件: prefix=%s, client_id=%s",
                prefix,
                self.client_id,
            )
            return

        self.logger.info(
            "[REDIS-WATCH] 收到前缀删除事件: prefix=%s, initiator=%s",
            prefix,
            initiator_client_id,
        )

        # 触发前缀删除回调（用于删除本地磁盘缓存）
        if self._delete_prefix_callback:
            try:
                self._delete_prefix_callback(prefix)
            except Exception as e:
                self.logger.error(
                    "[REDIS-WATCH] 前缀删除回调异常: prefix=%s, error=%s",
                    prefix,
                    e,
                )
        else:
            self.logger.debug(
                "[REDIS-WATCH] 前缀删除回调未设置，跳过: prefix=%s",
                prefix,
            )

    def _heartbeat_loop(self):
        """心跳循环，定期刷新 Provider 和文件的 TTL.

        优化: 使用 pipeline 批量刷新，减少 RTT 开销。
        30 万 key 场景下，从逐个 EXPIRE (30 万次 RTT) 优化为分批 pipeline (300 次 RTT)。
        """
        self.logger.info(
            "[REDIS] 心跳线程启动, file_ttl=%ds, provider_ttl=%ds",
            self.ttl,
            self.provider_ttl,
        )

        # 批量刷新大小：每批 1000 个 key
        batch_size = 1000

        while self.running:
            try:
                # 刷新间隔：取非零 TTL 中的最小值 / 3，确保在过期前至少刷新 3 次
                active_ttls = [t for t in (self.ttl, self.provider_ttl) if t > 0]
                min_ttl = min(active_ttls) if active_ttls else 60
                interval = max(1, min_ttl / 3)
                # 添加 10% 随机抖动
                jitter = interval * 0.1 * (random.random() * 2 - 1)
                # 用 Event.wait 代替 sleep，close() 时可以更快退出
                self._stop_event.wait(interval + jitter)

                if not self.running:
                    break

                heartbeat_start = time.time()
                provider_success = 0
                provider_failed = 0
                file_success = 0
                file_failed = 0

                # 刷新所有 Provider (使用 pipeline)，仅当 provider_ttl > 0
                with self._hosts_lock:
                    hosts_snapshot = list(self._all_hosts)

                if hosts_snapshot and self.provider_ttl > 0:
                    try:
                        pipe = self._client.pipeline()
                        for host in hosts_snapshot:
                            key = f"{self.PREFIX_PROVIDER}{host}"
                            pipe.expire(key, self.provider_ttl)
                        results = pipe.execute()
                        provider_success = sum(1 for r in results if r)
                        provider_failed = len(hosts_snapshot) - provider_success
                    except Exception as e:
                        self.logger.warning(
                            "[REDIS-HEARTBEAT] Provider TTL 批量刷新失败: error=%s",
                            e,
                        )
                        provider_failed = len(hosts_snapshot)

                # 刷新所有本地注册的文件 (使用 pipeline + 分批)，仅当 ttl > 0
                file_keys = list(self._registered_keys.keys())

                if file_keys and self.ttl > 0:
                    for i in range(0, len(file_keys), batch_size):
                        batch = file_keys[i : i + batch_size]
                        try:
                            pipe = self._client.pipeline()
                            for file_key in batch:
                                key = f"{self.PREFIX_FILE}{file_key}"
                                pipe.expire(key, self.ttl)
                            results = pipe.execute()
                            batch_success = sum(1 for r in results if r)
                            file_success += batch_success
                            file_failed += len(batch) - batch_success
                        except Exception as e:
                            self.logger.warning(
                                "[REDIS-HEARTBEAT] 文件 TTL 批量刷新失败: batch=%d-%d, error=%s",
                                i,
                                i + len(batch),
                                e,
                            )
                            file_failed += len(batch)

                heartbeat_elapsed = time.time() - heartbeat_start

                # 根据 key 数量决定日志级别
                total_keys = len(hosts_snapshot) + len(file_keys)
                if total_keys > 1000 or min_ttl > 60:
                    self.logger.info(
                        "[REDIS-HEARTBEAT] 续期完成: providers=%d(fail=%d), files=%d(fail=%d), "
                        "file_ttl=%ds, provider_ttl=%ds, elapsed=%.3fs",
                        provider_success,
                        provider_failed,
                        file_success,
                        file_failed,
                        self.ttl,
                        self.provider_ttl,
                        heartbeat_elapsed,
                    )
                else:
                    self.logger.debug(
                        "[REDIS-HEARTBEAT] 续期完成: providers=%d, files=%d, elapsed=%.3fs",
                        len(hosts_snapshot),
                        len(file_keys),
                        heartbeat_elapsed,
                    )

            except Exception as e:
                self.logger.error("[REDIS] 心跳循环异常: %s", e, exc_info=True)
                time.sleep(1)

    # ----------------------------------------------------------------
    # 核心接口实现
    # ----------------------------------------------------------------

    def register_provider(self, host: str) -> None:
        """注册 Provider."""
        try:
            with self._hosts_lock:
                if host not in self._all_hosts:
                    self._all_hosts.append(host)
                self.local_host = host

            key = f"{self.PREFIX_PROVIDER}{host}"
            value = json.dumps(
                {
                    "timestamp": time.time(),
                    "state": "active",
                    "client_id": self.client_id,
                }
            )

            def _op():
                if self.provider_ttl > 0:
                    return self._client.setex(key, self.provider_ttl, value)
                return self._client.set(key, value)

            self._with_retry("register_provider", _op)

            self.logger.info(
                "[REDIS] Provider 注册成功: host=%s, ttl=%ds, total_hosts=%d",
                host,
                self.provider_ttl,
                len(self._all_hosts),
            )

        except Exception as e:
            self.logger.error("[REDIS] 注册 Provider 失败: %s", e)
            raise

    def unregister_provider(self, host: str) -> None:
        """注销 Provider."""
        try:
            key = f"{self.PREFIX_PROVIDER}{host}"

            self._with_retry("unregister_provider", lambda: self._client.delete(key))
            with self._hosts_lock:
                try:
                    self._all_hosts.remove(host)
                except ValueError:
                    pass
            self.logger.info("[REDIS] Provider 注销成功: host=%s", host)
        except Exception as e:
            self.logger.error("[REDIS] 注销 Provider 失败: host=%s, error=%s", host, e)

    def register_file(self, file_key: str, host: str, metadata: dict) -> bool:
        """注册文件元数据."""
        key = f"{self.PREFIX_FILE}{file_key}"

        data = {
            "host": host,
            "metadata": metadata,
            "file_key": file_key,
        }
        value = json.dumps(data)

        self.logger.debug(
            "[REDIS] 注册文件元数据: key=%s, host=%s, metadata=%s",
            file_key,
            host,
            metadata,
        )

        try:

            def _op():
                if self._lua_register_file is not None and callable(
                    self._lua_register_file
                ):
                    # Lua 原子写：避免 SET 与 SADD 不一致
                    return self._lua_register_file(
                        keys=[key, self.KEY_FILE_INDEX],
                        args=[value, int(self.ttl), file_key],
                    )
                # fallback
                self._register_file_pipeline(key=key, file_key=file_key, value=value)
                return 1

            self._with_retry("register_file", _op)

            self.logger.debug("[REDIS] 文件元数据已写入: key=%s", file_key)
            return True

        except Exception as e:
            self.logger.error(
                "[REDIS] 注册文件失败: key=%s, error=%s",
                file_key,
                e,
                exc_info=True,
            )

            # 异常路径读回校验
            try:
                read_value = self._client.get(key)
                if read_value:
                    read_data = json.loads(read_value)
                    read_put_id = read_data.get("metadata", {}).get("put_id")
                    expected_put_id = metadata.get("put_id")

                    if expected_put_id and read_put_id == expected_put_id:
                        self.logger.warning(
                            "[REDIS] 注册异常但读回验证成功: key=%s, put_id=%s",
                            file_key,
                            read_put_id,
                        )
                        return True
            except Exception as verify_e:
                self.logger.warning(
                    "[REDIS] 读回校验也失败: key=%s, error=%s",
                    file_key,
                    verify_e,
                )

            return False

    def unregister_file(self, file_key: str) -> None:
        """注销文件（本地清理）."""
        self.delete_file(file_key)

    def delete_file(self, file_key: str) -> bool:
        """删除文件（全局删除）."""
        key = f"{self.PREFIX_FILE}{file_key}"

        self.logger.debug(
            "[REDIS] 准备删除文件: client_id=%s, key=%s",
            self.client_id,
            file_key,
        )

        try:
            deleted_value: str | None = None

            def _op():
                if self._lua_delete_file is not None and callable(
                    self._lua_delete_file
                ):
                    return self._lua_delete_file(
                        keys=[key, self.KEY_FILE_INDEX], args=[file_key]
                    )

                # fallback：非原子（get + pipeline），但兼容不支持 script 的 client
                v = self._client.get(key)
                pipe = self._client.pipeline()
                pipe.delete(key)
                pipe.srem(self.KEY_FILE_INDEX, file_key)
                pipe.execute()
                return v

            res = self._with_retry("delete_file", _op)

            if isinstance(res, str) and res:
                deleted_value = res
            elif res is False:
                deleted_value = None
            else:
                # 兼容 redis-py 对 lua false 的返回（可能是 None/0/False）
                deleted_value = res if isinstance(res, str) else None

            deleted = deleted_value is not None

            if deleted:
                self.logger.info(
                    "[REDIS] 删除成功: client_id=%s, key=%s",
                    self.client_id,
                    file_key,
                )

                # 发布删除事件（使用“被删除版本”的 metadata，确保 RDMA put_id 匹配）
                if deleted_value is not None:
                    try:
                        self._publish_delete_events_from_values([deleted_value])
                    except Exception as e:
                        self.logger.warning(
                            "[REDIS] 发布删除事件失败: key=%s, error=%s",
                            file_key,
                            e,
                        )
            else:
                self.logger.warning(
                    "[REDIS] 删除返回 0: client_id=%s, key=%s (可能已不存在)",
                    self.client_id,
                    file_key,
                )

            return deleted

        except Exception as e:
            self.logger.error(
                "[REDIS] 删除文件异常: client_id=%s, key=%s, error=%s",
                self.client_id,
                file_key,
                e,
            )
            return False

    def delete_prefix(self, prefix: str) -> tuple[bool, int]:
        """根据前缀删除文件.

        使用索引查询替代 SCAN，避免高并发场景下的 O(N) 全局遍历阻塞。
        PUT 使用 Lua 原子写入（SET + SADD），索引和元数据一致性有保证。

        Returns:
            tuple[bool, int]: (是否成功, 删除的 key 数量)
        """
        start = time.perf_counter()

        self.logger.debug(
            "[REDIS] delete_prefix 开始: prefix=%s",
            prefix,
        )

        try:
            # 从索引获取所有 key，本地过滤匹配前缀的 key
            # SMEMBERS 是 O(N) 但只执行一次，比 SCAN 在高并发下快得多
            index_start = time.perf_counter()
            all_keys = self._with_retry(
                "delete_prefix(smembers)",
                lambda: self._client.smembers(self.KEY_FILE_INDEX),
            )
            index_elapsed = time.perf_counter() - index_start

            # 本地过滤匹配前缀的 key
            file_keys = [k for k in all_keys if k.startswith(prefix)]

            if not file_keys:
                elapsed = time.perf_counter() - start
                self.logger.info(
                    "[REDIS] delete_prefix: prefix=%s 无匹配的 key (index=%d, elapsed=%.3fs)",
                    prefix,
                    len(all_keys),
                    elapsed,
                )
                return (True, 0)

            self.logger.info(
                "[REDIS] delete_prefix: prefix=%s, index=%d keys (%.3fs), matched=%d",
                prefix,
                len(all_keys),
                index_elapsed,
                len(file_keys),
            )

            # 分批删除
            deleted_total = 0
            batch_size = 1000
            use_lua = (
                self.enable_watch
                and self._lua_bulk_delete_files is not None
                and callable(self._lua_bulk_delete_files)
            )

            for i in range(0, len(file_keys), batch_size):
                batch_keys = file_keys[i : i + batch_size]
                redis_keys = [f"{self.PREFIX_FILE}{k}" for k in batch_keys]

                if use_lua:
                    lua_bulk_delete = self._lua_bulk_delete_files
                    # 使用默认参数捕获当前循环的值，避免闭包陷阱
                    _batch_keys = batch_keys
                    _redis_keys = redis_keys

                    def _lua_op(_rk=_redis_keys, _bk=_batch_keys):
                        return lua_bulk_delete(
                            keys=[self.KEY_FILE_INDEX, *_rk],
                            args=_bk,
                        )

                    deleted_values = self._with_retry(
                        "delete_prefix(lua_bulk_delete)", _lua_op
                    )
                    if isinstance(deleted_values, list) and deleted_values:
                        deleted_total += len(deleted_values)
                        self._publish_delete_events_from_values(
                            [v for v in deleted_values if isinstance(v, str)]
                        )
                else:
                    # fallback：不发布逐 key delete 事件
                    deleted_total += self._bulk_delete(redis_keys)
                    if batch_keys:
                        _batch_keys = batch_keys  # 捕获当前值
                        try:
                            self._with_retry(
                                "delete_prefix(srem)",
                                lambda _bk=_batch_keys: self._client.srem(
                                    self.KEY_FILE_INDEX, *_bk
                                ),
                            )
                        except Exception:
                            pass

            elapsed = time.perf_counter() - start

            # 发布批量删除事件（摘要），用于通知其他节点删除本地缓存
            if self.enable_watch:
                event = {
                    "type": "delete_prefix",
                    "prefix": prefix,
                    "count": deleted_total,
                    "initiator_client_id": self.client_id,  # 标识发起方，避免重复删除
                }
                try:
                    self._client.publish(self.CHANNEL_EVENTS, json.dumps(event))
                    self.logger.debug(
                        "[REDIS] delete_prefix 广播已发送: prefix=%s", prefix
                    )
                except Exception as e:
                    self.logger.warning(
                        "[REDIS] delete_prefix 广播失败: prefix=%s, error=%s",
                        prefix,
                        e,
                    )

            self.logger.debug(
                "[REDIS] delete_prefix 完成: prefix=%s, deleted=%d, elapsed=%.3fs",
                prefix,
                deleted_total,
                elapsed,
            )
            return (True, deleted_total)

        except Exception as e:
            self.logger.error(
                "[REDIS] delete_prefix 异常: prefix=%s, error=%s",
                prefix,
                e,
            )
            return (False, 0)

    def delete_prefix_batch(self, prefixes: list[str]) -> dict[str, tuple[bool, int]]:
        """批量根据前缀删除文件.

        Returns:
            dict[str, tuple[bool, int]]: {prefix: (是否成功, 删除数量)}
        """
        results = {}
        for prefix in prefixes:
            results[prefix] = self.delete_prefix(prefix)
        return results

    def delete_keys_batch(self, file_keys: list[str]) -> int:
        """按 key 列表直接删除文件（避免 SCAN）.

        适用于已知 key 列表的场景，比 delete_prefix 更高效。

        Args:
            file_keys: 要删除的 key 列表.

        Returns:
            int: 成功删除的 key 数量.
        """
        if not file_keys:
            return 0

        start = time.perf_counter()
        deleted_total = 0
        batch_size = 1000

        try:
            for i in range(0, len(file_keys), batch_size):
                batch_keys = file_keys[i : i + batch_size]
                redis_keys = [f"{self.PREFIX_FILE}{k}" for k in batch_keys]

                if (
                    self.enable_watch
                    and self._lua_bulk_delete_files is not None
                    and callable(self._lua_bulk_delete_files)
                ):
                    lua_bulk_delete = self._lua_bulk_delete_files

                    def _lua_op():
                        return lua_bulk_delete(
                            keys=[self.KEY_FILE_INDEX, *redis_keys],
                            args=batch_keys,
                        )

                    deleted_values = self._with_retry(
                        "delete_keys_batch(lua_bulk_delete)", _lua_op
                    )
                    if isinstance(deleted_values, list) and deleted_values:
                        deleted_total += len(deleted_values)
                        self._publish_delete_events_from_values(
                            [v for v in deleted_values if isinstance(v, str)]
                        )
                else:
                    # fallback：不发布 delete 事件
                    deleted_total += self._bulk_delete(redis_keys)
                    if batch_keys:
                        try:
                            self._with_retry(
                                "delete_keys_batch(srem)",
                                lambda: self._client.srem(
                                    self.KEY_FILE_INDEX, *batch_keys
                                ),
                            )
                        except Exception:
                            pass

            elapsed = time.perf_counter() - start
            self.logger.info(
                f"[REDIS] delete_keys_batch: keys={len(file_keys)}, deleted={deleted_total}, elapsed={elapsed:.3f}s"
            )
            return deleted_total

        except Exception as e:
            self.logger.error(f"[REDIS] delete_keys_batch failed: {e}")
            return deleted_total

    def check_connection(self, timeout_ms: int = 3000) -> bool:
        """检查 Redis 连通性."""
        try:
            self._client.ping()
            return True
        except Exception:
            return False

    def query_file(self, file_key: str) -> dict | None:
        """查询文件元数据."""
        key = f"{self.PREFIX_FILE}{file_key}"
        try:
            value = self._with_retry("query_file(get)", lambda: self._client.get(key))
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            self.logger.error(
                "[REDIS] query_file 查询异常: key=%s, error=%s",
                file_key,
                e,
            )
            return None

    def query_files_batch(self, file_keys: list[str]) -> dict[str, dict | None]:
        """批量查询文件元数据."""
        if not file_keys:
            return {}

        start_time = time.perf_counter()
        results: dict[str, dict | None] = {key: None for key in file_keys}

        # 优化：分批 MGET，避免单次请求过大导致超时或阻塞
        # 10000 keys * 400 bytes = 4MB，分批 1000 (400KB) 比较安全
        batch_size = 1000

        for i in range(0, len(file_keys), batch_size):
            batch_keys = file_keys[i : i + batch_size]
            redis_keys = [f"{self.PREFIX_FILE}{k}" for k in batch_keys]

            try:
                # 使用 MGET 批量获取
                values = self._with_retry(
                    f"query_files_batch(mget, batch={len(batch_keys)})",
                    lambda: self._client.mget(redis_keys),
                )

                for file_key, value in zip(batch_keys, values):
                    if value:
                        try:
                            results[file_key] = json.loads(value)
                        except json.JSONDecodeError as e:
                            self.logger.warning(
                                "[REDIS] 解析元数据失败: key=%s, error=%s",
                                file_key,
                                e,
                            )
            except Exception as e:
                self.logger.error(
                    "[REDIS] query_files_batch 分批查询失败: batch_start=%d, error=%s",
                    i,
                    e,
                )

        elapsed = time.perf_counter() - start_time
        found_count = sum(1 for v in results.values() if v is not None)
        self.logger.info(
            "[REDIS] batch query 完成: total=%d, found=%d, elapsed=%.4fs",
            len(file_keys),
            found_count,
            elapsed,
        )

        return results

    def get_prefix(self, prefix: str) -> dict[str, dict]:
        """根据前缀查询文件."""
        pattern = f"{self.PREFIX_FILE}{prefix}*"
        result = {}

        try:
            # 流式 SCAN + 分批 MGET，避免一次性持有所有 keys
            cursor = 0
            while True:
                cursor, keys = self._with_retry(
                    "get_prefix(scan)",
                    lambda: self._client.scan(
                        cursor=cursor,
                        match=pattern,
                        count=1000,
                    ),
                )

                if keys:
                    values = self._with_retry(
                        "get_prefix(mget)", lambda: self._client.mget(list(keys))
                    )
                    for key, value in zip(keys, values):
                        if value:
                            try:
                                data = json.loads(value)
                                file_key = data.get("file_key")
                                if file_key:
                                    result[file_key] = data
                            except json.JSONDecodeError:
                                pass

                if cursor == 0:
                    break

            self.logger.debug(
                "[REDIS] get_prefix 查询结果: prefix=%s, count=%d",
                prefix,
                len(result),
            )

        except Exception as e:
            self.logger.error(
                "[REDIS] get_prefix 查询异常: prefix=%s, error=%s",
                prefix,
                e,
            )

        return result

    def list_keys(self, prefix: str | None = None) -> list[str]:
        """列出所有文件 key."""
        # 如果没有前缀，优先尝试从 Set 索引获取（速度最快）
        if prefix is None:
            try:
                keys = self._with_retry(
                    "list_keys(smembers)",
                    lambda: self._client.smembers(self.KEY_FILE_INDEX),
                )
                result = list(keys) if keys else []
                self.logger.info("[REDIS] list_keys 查询结果: count=%d", len(result))
                return result
            except Exception as e:
                self.logger.error(
                    "[REDIS] list_keys(smembers) 异常: %s, 尝试 fallback 到 SCAN", e
                )
                # Fallback to SCAN

        # 使用 SCAN 遍历 (支持前缀过滤 或 smembers 失败兜底)
        try:
            pattern = f"{self.PREFIX_FILE}{prefix if prefix else ''}*"
            result = []
            cursor = 0
            while True:
                cursor, keys = self._with_retry(
                    "list_keys(scan)",
                    lambda: self._client.scan(
                        cursor=cursor,
                        match=pattern,
                        count=1000,
                    ),
                )
                for key in keys:
                    # 排除索引 key
                    if key != self.KEY_FILE_INDEX:
                        file_key = key[len(self.PREFIX_FILE) :]
                        result.append(file_key)
                if cursor == 0:
                    break

            self.logger.info(
                "[REDIS] list_keys(scan) 查询结果: prefix=%s, count=%d",
                prefix,
                len(result),
            )
            return result
        except Exception as e:
            self.logger.error("[REDIS] list_keys(scan) 失败: %s", e)
            return []

    def list_files(self) -> dict[str, dict]:
        """列出所有文件."""
        try:
            # 先获取所有 key
            all_keys = self.list_keys()
            if not all_keys:
                return {}

            # 批量获取元数据
            redis_keys = [f"{self.PREFIX_FILE}{k}" for k in all_keys]
            values = self._with_retry(
                "list_files(mget)", lambda: self._client.mget(redis_keys)
            )

            result = {}
            for file_key, value in zip(all_keys, values):
                if value:
                    try:
                        result[file_key] = json.loads(value)
                    except json.JSONDecodeError:
                        pass

            self.logger.debug("[REDIS] list_files 查询结果: count=%d", len(result))
            return result

        except Exception as e:
            self.logger.error("[REDIS] list_files 查询异常: %s", e)
            return {}

    def clear_files(self, use_prefix_delete: bool = True) -> dict:
        """清空所有文件元数据."""
        try:
            # 注意：50w 规模下 smembers/list_keys 会在客户端产生较大内存峰值。
            # 这里改为 SSCAN 流式遍历索引集合，并分批删除。
            self.logger.info(
                "[REDIS] 开始清空文件: client_id=%s (sscan stream)",
                self.client_id,
            )

            start = time.time()
            deleted_count = 0
            scanned = 0

            cursor = 0
            batch_size = 1000
            while True:
                cursor, members = self._with_retry(
                    "clear_files(sscan)",
                    lambda: self._client.sscan(
                        self.KEY_FILE_INDEX, cursor=cursor, count=batch_size
                    ),
                )

                if members:
                    scanned += len(members)
                    file_keys = list(members)
                    redis_keys = [f"{self.PREFIX_FILE}{k}" for k in file_keys]

                    if (
                        self.enable_watch
                        and self._lua_bulk_delete_files is not None
                        and callable(self._lua_bulk_delete_files)
                    ):
                        lua_bulk_delete = self._lua_bulk_delete_files

                        def _lua_op():
                            return lua_bulk_delete(
                                keys=[self.KEY_FILE_INDEX, *redis_keys],
                                args=file_keys,
                            )

                        deleted_values = self._with_retry(
                            "clear_files(lua_bulk_delete)", _lua_op
                        )
                        if isinstance(deleted_values, list) and deleted_values:
                            deleted_count += len(deleted_values)
                            self._publish_delete_events_from_values(
                                [v for v in deleted_values if isinstance(v, str)]
                            )
                    else:
                        # 无 watch / 无 lua：仅删除 key，索引最后整体删掉
                        deleted_count += self._bulk_delete(redis_keys)

                if cursor == 0:
                    break

            # 清空索引本身
            self._bulk_delete([self.KEY_FILE_INDEX])

            elapsed = time.time() - start
            self.logger.info(
                "[REDIS] 清空完成: scanned=%d, deleted=%d, elapsed=%.3fs",
                scanned,
                deleted_count,
                elapsed,
            )

            return {"success": True, "cleared": deleted_count, "failed": []}

        except Exception as e:
            self.logger.error("[REDIS] clear_files 异常: %s", e, exc_info=True)
            return {"success": False, "cleared": 0, "failed": [], "msg": str(e)}

    def set_release_callback(self, callback) -> None:
        """设置 buffer 释放回调."""
        self._release_callback = callback

    def set_delete_prefix_callback(self, callback) -> None:
        """设置前缀删除回调（用于删除本地磁盘缓存）."""
        self._delete_prefix_callback = callback

    def close(self) -> None:
        """关闭客户端."""
        self.running = False
        self._stop_event.set()

        self.logger.info(
            "[REDIS] 准备关闭客户端: all_hosts=%s",
            self._all_hosts,
        )

        # 先关闭 pubsub，避免 watch 线程卡在 socket 读上
        try:
            if self._pubsub is not None:
                self._pubsub.close()
        except Exception:
            pass
        self._pubsub = None

        # 尝试等待后台线程退出（daemon 不阻塞进程，但这里尽量释放资源）
        try:
            if self._watch_thread is not None:
                self._watch_thread.join(timeout=2)
        except Exception:
            pass

        try:
            if self._heartbeat_thread is not None:
                self._heartbeat_thread.join(timeout=2)
        except Exception:
            pass

        # 删除所有 Provider 注册
        with self._hosts_lock:
            hosts_snapshot = list(dict.fromkeys(self._all_hosts))

        for host in hosts_snapshot:
            try:
                key = f"{self.PREFIX_PROVIDER}{host}"
                self._with_retry(
                    "close(delete_provider)", lambda: self._client.delete(key)
                )
                self.logger.debug("[REDIS] 已删除 Provider: %s", host)
            except Exception as e:
                self.logger.warning("[REDIS] 删除 Provider 失败: %s, error=%s", host, e)

        with self._hosts_lock:
            self._all_hosts.clear()

        # 关闭连接
        try:
            self._client.close()
        except Exception as e:
            self.logger.warning("[REDIS] 关闭连接失败: %s", e)

        self.logger.info("[REDIS] Redis Metadata Client 已关闭")

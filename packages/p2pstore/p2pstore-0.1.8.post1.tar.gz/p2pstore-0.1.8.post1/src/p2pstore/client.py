"""
P2P Store Client 模块.

该模块提供了 P2P Store 系统的主客户端入口 `P2PClient`。
它封装了底层的元数据管理 (MetadataClient) 和数据传输 (Transport) 逻辑，
为上层应用提供统一的 put/get/list/delete 等 API。
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import os
import secrets
import time
from typing import Any

import numpy as np

from .core import TransferRequest
from .metadata import create_metadata_client
from .utils import (
    LoggerManager,
    MetricsCollector,
    P2PConfig,
    deserialize_object,
    numpy_from_file,
    serialize_object,
    serialize_tensor,
    setup_topology_env,
    validate_data_type,
)


class P2PClient:
    """面向P2P 传输的统一客户端, 支持多 Metadata / Transport 插拔."""

    def __init__(
        self,
        config: P2PConfig,
        check_metaserver: bool = True,
        enable_metrics: bool = False,
    ):
        """
        初始化 P2PClient.

        Args:
            config: P2P 配置.
            check_metaserver: 是否检查 Metaserver 连通性，默认 True.
                              如果为 True 且 Metaserver 不可用，抛出 RuntimeError.
            enable_metrics: 是否启用指标收集，默认 False.
                            启用后可通过 client.metrics 访问指标收集器.
        """
        self.config = config
        self._enable_metrics = enable_metrics

        # 专用线程池，用于隔离元数据阻塞操作，防止阻塞主线程池
        self._metadata_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1000, thread_name_prefix="metadata_worker"
        )

        # 生成 8 位随机字符串作为 client_id，用于日志子目录和日志格式
        self.client_id = secrets.token_hex(4)
        LoggerManager.set_sub_dir(self.client_id)

        # 初始化指标收集器（如果启用）
        self._metrics: MetricsCollector | None = None
        if enable_metrics:
            self._metrics = MetricsCollector(
                client_id=self.client_id,
                enable_logging=True,
                log_interval=1000,
            )

        self.logger = LoggerManager.get_logger(config.log_name or "p2p-client")
        self.logger.info("P2PClient 初始化: client_id=%s", self.client_id)

        # 打印所有配置
        self._log_config(config)

        from .transport import create_load_balancer, create_transport

        # 存储 {key: put_id}，用于版本控制，防止 Watch 线程误删新数据
        self._registered_keys = {}

        # 对于 RDMA 协议，根据是否指定设备决定拓扑策略
        if config.protocol == "rdma":
            if config.device:
                # 指定了设备，清除拓扑环境变量，让 Transfer Engine 直接用指定设备
                os.environ.pop("MC_CUSTOM_TOPO_JSON", None)
            else:
                # 未指定设备，自动设置拓扑环境变量
                setup_topology_env(include_cuda=True)

        local_ip = config.local_host.split(":")[0]
        self.metadata_client = create_metadata_client(
            config, local_ip, self.client_id, self._registered_keys
        )
        # 创建多个 transport 实例以分散负载
        # 通过环境变量 P2P_RDMA_INSTANCES 控制实例数量，默认为 1
        num_instances = int(os.getenv("P2P_RDMA_INSTANCES", "1"))
        num_instances = max(1, min(num_instances, 64))  # 限制在 1-64 之间

        self.transports = []
        self._transport_addrs = []  # 记录每个 transport 的地址
        self._addr_to_transport = {}  # 地址到 transport 的映射，用于 release

        for i in range(num_instances):
            transport = create_transport(config)
            if not transport.initialize(config.local_host, config.device):
                raise RuntimeError(f"Transport {i} 初始化失败, 请检查配置")
            addr = transport.get_local_addr()
            self.transports.append(transport)
            self._transport_addrs.append(addr)
            self._addr_to_transport[addr] = transport
            self.logger.info(
                "Transport %d/%d 初始化成功: addr=%s", i + 1, num_instances, addr
            )

        # 兼容旧代码：self.transport 指向第一个实例
        self.transport = self.transports[0]

        # 创建负载均衡器
        self._load_balancer = create_load_balancer(self.transports)
        self.logger.info(
            "负载均衡器初始化: send_strategy=%s, recv_strategy=%s",
            self._load_balancer.send_strategy,
            self._load_balancer.recv_strategy,
        )

        # 注册所有 Provider 地址
        for addr in self._transport_addrs:
            self.metadata_client.register_provider(addr)

        # 设置 buffer 释放回调
        self.metadata_client.set_release_callback(self._on_file_unregister)

        # 设置前缀删除回调（用于删除本地磁盘缓存）
        if hasattr(self.metadata_client, "set_delete_prefix_callback"):
            self.metadata_client.set_delete_prefix_callback(
                self._on_delete_prefix_event
            )

        # 检查 Metaserver 连通性
        if check_metaserver:
            if not self.metadata_client.check_connection():
                raise RuntimeError(
                    f"Metaserver 不可用: {config.metadata_server}，请确保 Metaserver 已启动"
                )

    def _log_config(self, config: P2PConfig) -> None:
        """打印所有配置项."""
        from dataclasses import fields

        self.logger.info("=" * 60)
        self.logger.info("P2PClient 配置:")
        self.logger.info("-" * 60)

        for field in fields(config):
            name = field.name
            value = getattr(config, name)

            # 对敏感信息做脱敏处理
            if "password" in name.lower() and value:
                display_value = "***"
            # 对长列表做截断显示
            elif isinstance(value, list) and len(value) > 5:
                display_value = f"{value[:3]}... (共 {len(value)} 项)"
            else:
                display_value = value

            self.logger.info("  %-30s: %s", name, display_value)

        # 打印相关环境变量
        self.logger.info("-" * 60)
        self.logger.info("相关环境变量:")
        env_vars = [
            "POD_IP",
            "P2P_RDMA_DEVICE",
            "P2P_RDMA_INSTANCES",
            "P2P_REDIS_KEY_TTL",
            "P2P_LB_SEND_STRATEGY",
            "P2P_LB_RECV_STRATEGY",
            "P2P_RDMA_TIMEOUT_MULTIPLIER",
            "P2P_RDMA_MAX_RETRIES",
            "P2P_RDMA_BASE_RETRY_INTERVAL",
            "P2P_QUERY_TIMEOUT",
            "MC_GID_INDEX",
        ]
        for var in env_vars:
            val = os.getenv(var)
            if val:
                self.logger.info("  %-30s: %s", var, val)

        self.logger.info("=" * 60)

    @property
    def metrics(self) -> MetricsCollector | None:
        """
        获取指标收集器.

        Returns:
            MetricsCollector | None: 如果启用了指标收集，返回收集器实例；否则返回 None.
        """
        return self._metrics

    def enable_metrics(self) -> MetricsCollector:
        """
        启用指标收集（如果尚未启用）.

        Returns:
            MetricsCollector: 指标收集器实例.
        """
        if self._metrics is None:
            self._metrics = MetricsCollector(
                client_id=self.client_id,
                enable_logging=True,
                log_interval=1000,
            )
        return self._metrics

    # ------------------------------------------------------------------
    # Data APIs
    # ------------------------------------------------------------------
    async def cache_all(
        self,
        save_dir: str | None = None,
        concurrency: int = 32,
        batch_mode: str = "auto",
        batch_size: int = 10000,
        rank: int = -1,
        world_size: int = 8,
        prefix: str | None = None,
        prefixes: list[str] | None = None,
    ) -> None:
        """
        下载所有文件到指定目录.

        Args:
            save_dir: 保存目录. 如果不指定，优先使用 config.persistence_dir，
                      否则使用默认值 "/root/paddlejob/tmpspace/p2pstore".
            concurrency: 并发下载数量，默认 32.
            batch_mode: 分批模式控制，可选值:
                - "auto": 自动选择（推荐）。key 数量 > 10000 时使用分批模式
                - "always": 强制使用分批模式（大数据量场景）
                - "never": 禁用分批，一次性获取所有元数据（小数据量场景）
            batch_size: 分批大小，默认 10000。仅在分批模式下生效.
            rank: 当前节点排名 (0 ~ world_size-1). -1 表示不启用分布式过滤.
            world_size: 总节点数量.
            prefix: 单个前缀过滤，只缓存匹配该前缀的 key.
            prefixes: 前缀列表，任意一个前缀匹配就会被缓存。
                      当同时传入 prefix 和 prefixes 时，会取并集。

        最佳实践:
            - < 1万 key: batch_mode="never" 或 "auto"
            - 1万-10万 key: batch_mode="auto", batch_size=10000
            - > 10万 key: batch_mode="always", batch_size=5000~10000
            - 30万+ key: batch_mode="always", batch_size=5000, concurrency=64

        Example:
            # 自动模式（推荐）
            await client.cache_all(save_dir="/cache")

            # 只缓存 model/ 开头的文件
            await client.cache_all(save_dir="/cache", prefix="model/")

            # 同时缓存多个前缀
            await client.cache_all(save_dir="/cache", prefixes=["model/", "data/"])
        """
        start_time = time.perf_counter()

        # 确定保存目录：优先使用参数 > config.persistence_dir > 默认值
        if save_dir is None:
            save_dir = self.config.persistence_dir or "/root/paddlejob/tmpspace/p2pstore"

        os.makedirs(save_dir, exist_ok=True)

        # 同步更新 persistence_dir，确保 delete_prefix 能删除正确的本地缓存
        self.config.persistence_dir = save_dir

        loop = asyncio.get_running_loop()

        if prefixes is not None and len(prefixes) == 0:
            prefixes = None

        if prefixes is not None:
            prefix_list = list(prefixes)
            if prefix:
                prefix_list.append(prefix)
        elif prefix:
            prefix_list = [prefix]
        else:
            prefix_list = None

        # 1. 获取 key 列表
        keys_start = time.perf_counter()
        all_keys = await loop.run_in_executor(
            self._metadata_executor,
            self.list,
            None,
        )
        keys_elapsed = time.perf_counter() - keys_start
        total_keys_in_redis = len(all_keys)

        # 2. 本地前缀过滤（避免 Redis 前缀查询）
        filter_start = time.perf_counter()
        prefix_stats: dict[str, int] = {}  # 每个前缀匹配的 key 数量
        if prefix_list is not None:
            # 统计每个前缀匹配的数量
            for p in prefix_list:
                prefix_stats[p] = sum(1 for k in all_keys if k.startswith(p))

            # 过滤出匹配任一前缀的 key
            all_keys = [
                k for k in all_keys
                if any(k.startswith(p) for p in prefix_list)
            ]
        filter_elapsed = time.perf_counter() - filter_start

        total = len(all_keys)
        self.logger.info(
            f"[CACHE_ALL] list_keys={total_keys_in_redis} ({keys_elapsed:.2f}s), "
            f"filter={total} keys from {len(prefix_list) if prefix_list else 0} prefixes ({filter_elapsed:.3f}s)"
        )

        # 输出每个前缀的匹配情况
        if prefix_stats:
            for p, count in prefix_stats.items():
                status = "found" if count > 0 else "NOT FOUND"
                self.logger.info(f"[CACHE_ALL] prefix '{p}': {count} keys ({status})")
            # 检查是否有完全没匹配的前缀
            missing_prefixes = [p for p, c in prefix_stats.items() if c == 0]
            if missing_prefixes:
                self.logger.warning(
                    f"[CACHE_ALL] WARNING: {len(missing_prefixes)} prefixes found no keys: {missing_prefixes}"
                )

        if rank >= 0 and rank % 8 != 0:
            self.logger.info(f"[CACHE_ALL] rank={rank} (rank%8={rank % 8}) != 0, skip")
            return

        if total == 0:
            self.logger.info("[CACHE_ALL] no keys to download")
            return

        # 3. 决定是否使用分批模式
        use_batch = self._should_use_batch_mode(batch_mode, total, batch_size)

        self.logger.info(
            f"[CACHE_ALL] start: save_dir={save_dir}, concurrency={concurrency}, "
            f"batch={'yes' if use_batch else 'no'} (size={batch_size})"
        )

        # 4. 初始化计数器和信号量
        sem = asyncio.Semaphore(concurrency)
        completed = [0]
        failed = [0]
        download_start = time.perf_counter()

        async def _download_task(key: str, entry: dict):
            async with sem:
                try:
                    safe_filename = key.replace("/", "_")
                    output_path = os.path.join(save_dir, safe_filename)
                    await self._get_with_metadata(key, entry, output_path)
                    completed[0] += 1
                except Exception as e:
                    failed[0] += 1
                    self.logger.error(f"[CACHE_ALL] download failed: {key}, {e}")

                # 进度日志：每 10% 或每 5000 个打印一次
                done = completed[0] + failed[0]
                progress_interval = max(total // 10, 5000)
                if done % progress_interval == 0 or done == total:
                    elapsed_so_far = time.perf_counter() - download_start
                    speed = done / elapsed_so_far if elapsed_so_far > 0 else 0
                    eta = (total - done) / speed if speed > 0 else 0
                    self.logger.info(
                        f"[CACHE_ALL] progress: {done}/{total} ({done*100//total}%), "
                        f"ok={completed[0]}, fail={failed[0]}, speed={speed:.1f}/s, eta={eta:.0f}s"
                    )

        # 5. 执行下载
        if not use_batch:
            # 单批次模式：一次性获取所有元数据
            meta_start = time.perf_counter()
            all_files_raw = await loop.run_in_executor(
                self._metadata_executor,
                self.metadata_client.query_files_batch,
                all_keys,
            )
            all_files = {k: v for k, v in all_files_raw.items() if v is not None}
            meta_elapsed = time.perf_counter() - meta_start
            self.logger.info(f"[CACHE_ALL] metadata: {len(all_files)} keys ({meta_elapsed:.2f}s)")

            tasks = [_download_task(key, entry) for key, entry in all_files.items()]
            if tasks:
                await asyncio.gather(*tasks)
        else:
            # 分批模式：边获取元数据边下载
            total_batches = (total + batch_size - 1) // batch_size
            meta_total_elapsed = 0.0

            for i in range(0, total, batch_size):
                batch_keys = all_keys[i : i + batch_size]

                meta_start = time.perf_counter()
                batch_metadata = await loop.run_in_executor(
                    self._metadata_executor,
                    self.metadata_client.query_files_batch,
                    batch_keys,
                )
                meta_total_elapsed += time.perf_counter() - meta_start

                tasks = [
                    _download_task(key, entry)
                    for key in batch_keys
                    if (entry := batch_metadata.get(key)) is not None
                ]
                if tasks:
                    await asyncio.gather(*tasks)

            self.logger.info(f"[CACHE_ALL] metadata: {total_batches} batches ({meta_total_elapsed:.2f}s)")

        # 6. 汇总结果
        download_elapsed = time.perf_counter() - download_start
        total_elapsed = time.perf_counter() - start_time
        speed = completed[0] / download_elapsed if download_elapsed > 0 else 0
        self.logger.info(
            f"[CACHE_ALL] done: total={total}, ok={completed[0]}, fail={failed[0]}, "
            f"download={download_elapsed:.2f}s, total={total_elapsed:.2f}s, speed={speed:.1f}/s"
        )

        # 记录 cache_all 指标
        if self._metrics:
            self._metrics.record_cache_all(
                success=(failed[0] == 0),
                latency=total_elapsed,
                total_keys=total,
                success_count=completed[0],
                failed_count=failed[0],
            )

    def _should_use_batch_mode(
        self, batch_mode: str, total: int, batch_size: int
    ) -> bool:
        """根据 batch_mode 和数据量决定是否使用分批模式."""
        if batch_mode == "always":
            return True
        elif batch_mode == "never":
            return False
        elif batch_mode == "auto":
            # 自动模式：key 数量超过 batch_size 时启用分批
            # 或者超过 10000 时启用（防止单次拉取过多数据）
            threshold = min(batch_size, 10000)
            return total > threshold
        else:
            self.logger.warning(
                f"[CACHE_ALL] 未知的 batch_mode={batch_mode}，使用 auto 模式"
            )
            return total > min(batch_size, 10000)

    def _select_transport_for_recv(self, remote_addr: str | None = None):
        """为接收路径选择一个 transport 实例.

        使用负载均衡器选择 transport 实例。默认策略为 sticky_hash，
        在多实例场景下，对 remote_addr 做稳定哈希，粘性选择同一个 transport，
        避免同一个 remote_addr 命中多个本地 rpc 端口，
        减少 TransferEngine 侧的 endpoint_store eviction。

        可通过环境变量 P2P_LB_RECV_STRATEGY 配置策略：
        - sticky_hash: 粘性哈希（默认）
        - round_robin: 轮询
        - least_active: 最少活跃请求
        - random: 随机选择
        """
        return self._load_balancer.select_for_recv(remote_addr)

    async def _get_with_metadata(
        self,
        key: str,
        entry: dict,
        output_path: str,
    ) -> bool:
        """
        使用预取的 metadata 直接下载数据（跳过元数据查询）.

        Args:
            key: 数据标识符.
            entry: 预取的 metadata (包含 host 和 metadata).
            output_path: 保存路径.

        Returns:
            bool: 下载是否成功.

        Raises:
            RuntimeError: 当传输失败时抛出异常，确保调用方能正确统计失败.
        """
        provider_addr = entry.get("host", "")
        metadata = entry.get("metadata", {})
        data_size = metadata.get("data_size", 0)

        request = self._request_from_metadata(key, metadata)
        if request is None:
            self.logger.error(f"[GET] 构建传输请求失败: key={key}")
            raise RuntimeError(f"构建传输请求失败: key={key}")

        # RDMA 传输超时策略
        size_mb = data_size / (1024 * 1024)
        if size_mb < 10:
            recv_timeout = max(10.0, size_mb * 0.3)
        elif size_mb < 100:
            recv_timeout = 3.0 + (size_mb - 10) * 0.1
        else:
            recv_timeout = min(12.0 + (size_mb - 100) * 0.018, 30.0)

        # 重试配置（与 get() 方法保持一致）
        max_retries = int(os.getenv("P2P_RDMA_MAX_RETRIES", "3"))
        base_retry_interval = float(os.getenv("P2P_RDMA_BASE_RETRY_INTERVAL", "0.5"))

        loop = asyncio.get_running_loop()

        selected_transport = self._select_transport_for_recv(provider_addr)
        selected_addr = selected_transport.get_local_addr()
        self.logger.debug(
            "[GET] key=%s 选择接收 transport: addr=%s (provider=%s)",
            key,
            selected_addr,
            provider_addr,
        )

        payload = None
        last_error = None

        # 只有 least_active 策略需要跟踪活跃请求，其他策略跳过以避免锁竞争
        use_tracking = self._load_balancer.recv_strategy == "least_active"
        if use_tracking:
            self._load_balancer.mark_active(selected_transport)
        try:
            for attempt in range(max_retries + 1):
                try:
                    payload = await asyncio.wait_for(
                        loop.run_in_executor(
                            None,
                            lambda: selected_transport.recv(
                                request=request, remote_addr=provider_addr
                            ),
                        ),
                        timeout=recv_timeout,
                    )

                    if payload is not None:
                        # 传输成功
                        if attempt > 0:
                            self.logger.info(
                                "[GET] RDMA 传输成功 (重试后): key=%s, 尝试 %d/%d",
                                key,
                                attempt + 1,
                                max_retries + 1,
                            )
                        # 异步保存文件
                        await loop.run_in_executor(
                            None, self._save_to_file, payload, output_path
                        )
                        return True

                    # payload 为 None
                    last_error = "transport returned None"
                    self.logger.warning(
                        "[GET] RDMA 传输返回 None: key=%s, 尝试 %d/%d",
                        key,
                        attempt + 1,
                        max_retries + 1,
                    )

                except asyncio.TimeoutError:
                    last_error = f"timeout after {recv_timeout:.1f}s"
                    self.logger.warning(
                        "[GET] RDMA 传输超时: key=%s, 尝试 %d/%d, timeout=%.1fs",
                        key,
                        attempt + 1,
                        max_retries + 1,
                        recv_timeout,
                    )

                except Exception as e:
                    last_error = str(e)
                    self.logger.warning(
                        "[GET] RDMA 传输异常: key=%s, 尝试 %d/%d, error=%s",
                        key,
                        attempt + 1,
                        max_retries + 1,
                        e,
                    )

                # 如果不是最后一次尝试，指数退避后重试
                if attempt < max_retries:
                    retry_delay = base_retry_interval * (2**attempt)
                    self.logger.debug(
                        "[GET] 等待 %.1fs 后重试: key=%s (尝试 %d/%d)",
                        retry_delay,
                        key,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(retry_delay)
        finally:
            if use_tracking:
                self._load_balancer.mark_complete(selected_transport)

        # 所有重试都失败
        self.logger.error(
            "[GET] RDMA 传输最终失败: key=%s, transport=%s, 已尝试 %d 次, 最后错误: %s",
            key,
            selected_addr,
            max_retries + 1,
            last_error,
        )
        raise RuntimeError(
            f"RDMA 传输最终失败: key={key}, 已尝试 {max_retries + 1} 次, 最后错误: {last_error}"
        )

    async def put(self, key: str, data: Any) -> bool:
        """
        注册数据到 P2P Store 系统.

        如果 key 已存在，会先删除旧数据（包括通知原节点释放内存），再注册新数据。
        使用多 transport 实例时，会随机选择一个 transport 以分散负载。

        Args:
            key: 数据的唯一标识符.
            data: 要注册的数据对象 (Tensor, 文件路径, bytes 等).

        Returns:
            bool: 注册是否成功.
        """
        start_time = time.perf_counter()
        self.logger.debug(
            "[PUT] 开始注册 key=%s, data_type=%s", key, type(data).__name__
        )
        if hasattr(data, "place"):
            self.logger.debug("[PUT] Input Tensor device: %s", data.place)

        # 使用负载均衡器选择 transport 实例
        selected_transport = self._load_balancer.select_for_send()
        selected_addr = selected_transport.get_local_addr()

        # ========== 阶段1: 检查 key 是否已存在 ==========
        phase1_start = time.perf_counter()
        loop = asyncio.get_running_loop()
        existing = await loop.run_in_executor(
            self._metadata_executor, self.metadata_client.query_file, key
        )
        phase1_elapsed = time.perf_counter() - phase1_start

        # ========== 阶段2: 释放旧数据（如果存在） ==========
        phase2_start = time.perf_counter()
        if existing:
            existing_host = existing.get("host", "unknown")
            existing_client = existing.get("metadata", {}).get("client_id", "unknown")
            self.logger.info(
                "[PUT] 检测到 key=%s 已存在 (host=%s, client=%s)，准备覆盖",
                key,
                existing_host,
                existing_client,
            )
            # 先同步释放本地内存，避免与 Watch 线程竞态
            if key in self._registered_keys:
                key_info = self._registered_keys[key]
                old_put_id = (
                    key_info.get("put_id") if isinstance(key_info, dict) else key_info
                )
                old_addr = (
                    key_info.get("transport_addr")
                    if isinstance(key_info, dict)
                    else None
                )
                self.logger.debug(
                    "[PUT] key=%s 在本地 _registered_keys (put_id=%s, addr=%s)，主线程同步释放内存",
                    key,
                    old_put_id,
                    old_addr,
                )
                try:
                    # 使用记录的 transport 地址找到对应的 transport 来释放
                    old_transport = self._addr_to_transport.get(
                        old_addr, self.transport
                    )
                    old_transport.release(key)
                    self._registered_keys.pop(key, None)
                    self.logger.debug(
                        "[PUT] 主线程已同步释放旧内存: key=%s, put_id=%s",
                        key,
                        old_put_id,
                    )
                except Exception as e:
                    self.logger.error("[PUT] 释放旧内存失败: key=%s, error=%s", key, e)
                    # 继续执行，尝试覆盖写
            else:
                self.logger.debug(
                    "[PUT] key=%s 不在本地 _registered_keys (远程节点数据)，跳过本地释放",
                    key,
                )
            # 再删除元数据（Watch 线程收到事件时，内存已经释放完毕）
            self.logger.debug("[PUT] 删除元数据: key=%s", key)
            await loop.run_in_executor(
                self._metadata_executor, self.metadata_client.delete_file, key
            )
        else:
            self.logger.debug("[PUT] key=%s 不存在，直接注册", key)
        phase2_elapsed = time.perf_counter() - phase2_start

        # ========== 阶段3: 数据序列化/构建传输请求 ==========
        phase3_start = time.perf_counter()
        data_type = validate_data_type(data)
        self.logger.debug("[PUT] 构建传输请求: key=%s, data_type=%s", key, data_type)
        payload, request = self._build_transfer_request(key, data, data_type)
        phase3_elapsed = time.perf_counter() - phase3_start

        # ========== 阶段4: RDMA 内存注册 ==========
        phase4_start = time.perf_counter()
        self.logger.debug(
            "[PUT] RDMA 注册: key=%s, size=%d bytes, transport=%s",
            key,
            getattr(request, "data_size", 0),
            selected_addr,
        )
        # 只有 least_active 策略需要跟踪活跃请求，其他策略跳过以避免锁竞争
        if self._load_balancer.send_strategy == "least_active":
            with self._load_balancer.track_request(selected_transport):
                success = selected_transport.send(
                    remote_addr=selected_addr,
                    request=request,
                    data=payload,
                )
        else:
            success = selected_transport.send(
                remote_addr=selected_addr,
                request=request,
                data=payload,
            )
        phase4_elapsed = time.perf_counter() - phase4_start

        if not success:
            self.logger.error(
                "[PUT] RDMA 注册失败: key=%s，client_id=%s, transport=%s",
                key,
                self.client_id,
                selected_addr,
            )
            # 记录失败指标
            if self._metrics:
                elapsed = time.perf_counter() - start_time
                self._metrics.record_put(
                    success=False,
                    latency=elapsed,
                    data_size=getattr(request, "data_size", 0),
                    key=key,
                )
            return False

        # ========== 阶段5: 注册元数据到 Redis ==========
        phase5_start = time.perf_counter()
        metadata = self._metadata_from_request(key, request)
        # 生成唯一的 put_id（纳秒时间戳），用于精确标识这次 PUT 操作
        put_id = time.time_ns()
        metadata["client_id"] = self.client_id
        metadata["put_id"] = put_id

        self.logger.debug(
            "[PUT] 注册元数据: key=%s, host=%s, put_id=%d",
            key,
            selected_addr,
            put_id,
        )
        register_success = await loop.run_in_executor(
            self._metadata_executor,
            lambda: self.metadata_client.register_file(
                file_key=key,
                host=selected_addr,
                metadata=metadata,
            ),
        )
        phase5_elapsed = time.perf_counter() - phase5_start

        if not register_success:
            # 元数据注册失败，释放已分配的 buffer
            self.logger.error(
                "[PUT] 元数据注册失败，回滚释放 RDMA 内存: key=%s", key
            )
            selected_transport.release(key)
            # 记录失败指标
            if self._metrics:
                elapsed = time.perf_counter() - start_time
                self._metrics.record_put(
                    success=False,
                    latency=elapsed,
                    data_size=request.data_size,
                    key=key,
                )
            return False

        # 存储 key -> {put_id, transport_addr} 映射，用于 Watch 线程版本控制和正确释放
        self._registered_keys[key] = {
            "put_id": put_id,
            "transport_addr": selected_addr,
        }
        elapsed = time.perf_counter() - start_time

        # 记录成功指标
        if self._metrics:
            self._metrics.record_put(
                success=True,
                latency=elapsed,
                data_size=request.data_size,
                key=key,
            )

        # INFO 级别输出各环节耗时
        self.logger.info(
            "[PUT] key=%s size=%d 耗时明细: "
            "检查存在=%.4fs, 释放旧数据=%.4fs, 序列化=%.4fs, RDMA注册=%.4fs, Redis元数据=%.4fs, 总计=%.4fs",
            key,
            request.data_size,
            phase1_elapsed,
            phase2_elapsed,
            phase3_elapsed,
            phase4_elapsed,
            phase5_elapsed,
            elapsed,
        )
        return True

    async def delete(self, key: str) -> bool:
        """
        删除数据 (可删除任意节点注册的数据).

        Args:
            key: 要删除的数据标识符.

        Returns:
            bool: 删除是否成功
        """
        is_local = key in self._registered_keys
        self.logger.debug(
            "[DELETE] 开始删除: key=%s, is_local=%s",
            key,
            is_local,
        )

        loop = asyncio.get_running_loop()
        success = await loop.run_in_executor(
            self._metadata_executor, self.metadata_client.delete_file, key
        )

        if success:
            self.logger.debug(
                "[DELETE] 元数据删除成功: key=%s. "
                "注意: 本地/远程内存释放将由 Watch 线程异步触发 (is_local=%s)",
                key,
                is_local,
            )
        else:
            self.logger.error(
                "[DELETE] 元数据删除失败: key=%s (可能不存在或服务异常)", key
            )
        return success

    async def delete_batch(self, keys: list[str]) -> dict[str, bool]:
        """
        批量删除数据.

        Args:
            keys: 要删除的数据标识符列表.

        Returns:
            dict[str, bool]: 每个 key 的删除结果.
        """
        results = {}
        for key in keys:
            success = await self.delete(key)
            results[key] = success
        return results

    async def get_prefix(self, prefix: str) -> dict[str, dict]:
        """
        根据前缀查询数据.

        Args:
            prefix: 数据标识符前缀.

        Returns:
            dict[str, dict]: 匹配的文件字典 {file_key: metadata}
        """
        self.logger.debug("[GET_PREFIX] 开始前缀查询: prefix=%s", prefix)
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self._metadata_executor, self.metadata_client.get_prefix, prefix
        )
        self.logger.debug(
            "[GET_PREFIX] 前缀查询完成: prefix=%s, count=%d", prefix, len(result)
        )
        return result

    async def delete_prefix(self, prefix: str) -> bool:
        """
        根据前缀删除数据.

        删除流程：
        1. 先主动删除本机的本地磁盘缓存（无需等待广播）
        2. 删除 Redis 元数据并发布广播事件
        3. 远程节点通过 Watch 线程收到广播后删除各自的本地缓存

        Args:
            prefix: 数据标识符前缀.

        Returns:
            bool: 删除是否成功
        """
        start_time = time.perf_counter()

        # 1. 删除本机本地磁盘缓存
        local_start = time.perf_counter()
        local_deleted = self._delete_local_cache_prefix(prefix)
        local_elapsed = time.perf_counter() - local_start

        # 2. 删除 Redis 元数据并发布广播事件
        redis_start = time.perf_counter()
        loop = asyncio.get_running_loop()
        success, redis_deleted = await loop.run_in_executor(
            self._metadata_executor, self.metadata_client.delete_prefix, prefix
        )
        redis_elapsed = time.perf_counter() - redis_start

        total_elapsed = time.perf_counter() - start_time
        if success:
            self.logger.info(
                f"[DELETE_PREFIX] prefix={prefix}, local={local_deleted} ({local_elapsed:.3f}s), "
                f"redis={redis_deleted} ({redis_elapsed:.3f}s), total={total_elapsed:.3f}s"
            )
        else:
            self.logger.error(f"[DELETE_PREFIX] failed: prefix={prefix}, elapsed={total_elapsed:.3f}s")
        return success

    async def delete_prefix_batch(self, prefixes: list[str]) -> dict[str, bool]:
        """
        批量根据前缀删除数据.

        使用高效实现：先获取所有 key，本地过滤后直接按 key 删除，
        避免对每个前缀做 Redis SCAN。

        删除流程：
        1. 获取所有 key，本地过滤匹配的 key
        2. 删除本机本地磁盘缓存
        3. 批量删除 Redis 元数据并发布广播事件
        4. 远程节点通过 Watch 线程收到广播后删除各自的本地缓存

        Args:
            prefixes: 前缀列表.

        Returns:
            dict[str, bool]: 每个前缀的删除结果.
        """
        start_time = time.perf_counter()
        loop = asyncio.get_running_loop()

        # 1. 获取所有 key
        list_start = time.perf_counter()
        all_keys = await loop.run_in_executor(
            self._metadata_executor,
            self.list,
            None,
        )
        list_elapsed = time.perf_counter() - list_start

        # 2. 本地前缀过滤
        filter_start = time.perf_counter()
        prefix_set = set(prefixes)
        keys_to_delete = [
            k for k in all_keys
            if any(k.startswith(p) for p in prefix_set)
        ]
        filter_elapsed = time.perf_counter() - filter_start

        if not keys_to_delete:
            self.logger.info(
                f"[DELETE_PREFIX_BATCH] no keys match {len(prefixes)} prefixes"
            )
            return {p: True for p in prefixes}

        # 3. 删除本地缓存
        local_start = time.perf_counter()
        for key in keys_to_delete:
            self._delete_local_cache(key)
        local_elapsed = time.perf_counter() - local_start

        # 4. 批量删除 Redis 元数据
        redis_start = time.perf_counter()
        deleted_count = await loop.run_in_executor(
            self._metadata_executor,
            self.metadata_client.delete_keys_batch,
            keys_to_delete,
        )
        redis_elapsed = time.perf_counter() - redis_start

        total_elapsed = time.perf_counter() - start_time
        self.logger.info(
            f"[DELETE_PREFIX_BATCH] prefixes={len(prefixes)}, matched={len(keys_to_delete)}, "
            f"deleted={deleted_count}, list={list_elapsed:.2f}s, filter={filter_elapsed:.3f}s, "
            f"local={local_elapsed:.3f}s, redis={redis_elapsed:.3f}s, total={total_elapsed:.2f}s"
        )

        # 返回结果（所有前缀都算成功，因为是批量删除）
        return {p: True for p in prefixes}

    def _on_file_unregister(
        self,
        key: str,
        deleted_put_id: int | None = None,
        deleted_client_id: str | None = None,
    ) -> None:
        """
        收到 file_unregister 广播时的回调, 释放本地 buffer 和删除本地磁盘缓存.

        注意：metadata_client 已经完成了所有检查（client_id + key 存在 + put_id 匹配），
        所以这里直接执行释放操作即可。

        Args:
            key: 文件 key
            deleted_put_id: 被删除的数据的 put_id（已在 metadata_client 中验证）
            deleted_client_id: 被删除的数据的 client_id（已在 metadata_client 中验证）
        """
        # 1. 删除本地磁盘缓存（无论 key 是否在 _registered_keys 中）
        self._delete_local_cache(key)

        # 2. 释放 RDMA buffer（仅当 key 在本地注册时）
        # 二次检查：防止从 metadata_client 检查到 callback 执行之间的竞态
        key_info = self._registered_keys.get(key)
        if key_info is None:
            self.logger.debug(
                "[WATCH-CALLBACK] key=%s 已不在 _registered_keys，跳过 RDMA 释放 (可能已被主线程释放或为远程节点数据)",
                key,
            )
            return

        # 获取 transport 地址
        if isinstance(key_info, dict):
            transport_addr = key_info.get("transport_addr")
            local_put_id = key_info.get("put_id")
        else:
            transport_addr = None
            local_put_id = key_info

        self.logger.info(
            "[WATCH-CALLBACK] 释放本地 buffer: key=%s, put_id=%s, transport=%s",
            key,
            deleted_put_id,
            transport_addr,
        )

        # 使用记录的 transport 地址找到对应的 transport 来释放
        target_transport = self._addr_to_transport.get(transport_addr, self.transport)
        target_transport.release(key)
        self._registered_keys.pop(key, None)

        # 打印 remaining keys 便于调试
        remaining_count = len(self._registered_keys)
        self.logger.info(
            "[WATCH-CALLBACK] key=%s 已释放, remaining_keys=%d",
            key,
            remaining_count,
        )
        if remaining_count > 0 and remaining_count <= 10:
            # 当剩余 key 较少时，打印详细信息便于调试
            self.logger.debug(
                "[WATCH-CALLBACK] 剩余 keys: %s",
                list(self._registered_keys.keys()),
            )

    def _on_delete_prefix_event(self, prefix: str) -> None:
        """
        收到 delete_prefix 广播时的回调, 删除本地磁盘缓存.

        Args:
            prefix: 被删除的前缀
        """
        start_time = time.perf_counter()
        deleted_count = self._delete_local_cache_prefix(prefix)
        elapsed = time.perf_counter() - start_time
        self.logger.info(
            "[DELETE_PREFIX-WATCH] 收到广播删除本地缓存: prefix=%s, deleted=%d, elapsed=%.3fs",
            prefix,
            deleted_count,
            elapsed,
        )

    async def clear(self) -> dict:
        """
        清空所有文件.

        Returns:
            dict: {"success": bool, "cleared": int, "failed": list[str]}
        """
        clear_start_time = time.perf_counter()
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self._metadata_executor, self.metadata_client.clear_files
        )

        clear_elapsed = time.perf_counter() - clear_start_time
        cleared_count = result.get("cleared", 0)

        if result.get("success"):
            self.logger.info("所有数据已清除, 共 %d 个", cleared_count)
        else:
            failed = result.get("failed", [])
            self.logger.warning(
                "清空完成, 成功 %d 个, 失败 %d 个: %s",
                cleared_count,
                len(failed),
                failed,
            )

        # 记录清空指标
        if self._metrics:
            self._metrics.record_clear(
                success=result.get("success", False),
                latency=clear_elapsed,
                cleared_count=cleared_count,
            )

        return result

    async def get(
        self,
        key: str,
        output_path: str | None = None,
        inplace_tensor: Any | None = None,
    ) -> Any | None:
        """
        获取数据.

        Args:
            key: 数据标识符.
            output_path: 可选, 将数据保存到指定文件路径.
            inplace_tensor: 可选, 将数据直接写入该 Tensor (需支持 set_value).

        Returns:
            Optional[Any]: 获取到的数据对象, 失败则返回 None.
        """
        get_start_time = time.perf_counter()
        self.logger.debug("[GET] 开始查询: key=%s", key)

        # ========== 阶段1: 检查本地缓存 ==========
        phase1_start = time.perf_counter()
        local_dir = self.config.persistence_dir
        if local_dir:
            # 构建本地缓存路径（与 cache_all 保持一致：把 / 替换为 _）
            safe_filename = key.replace("/", "_")
            local_path = os.path.join(local_dir, safe_filename)

            # 检查文件是否存在
            loop = asyncio.get_running_loop()
            file_exists = await loop.run_in_executor(None, os.path.exists, local_path)

            if file_exists:
                self.logger.info(f"[GET] 命中本地持久化缓存: {local_path}")
                try:

                    def _load_local_file():
                        arr = np.fromfile(local_path, dtype=np.int32).reshape(-1, 8)
                        return arr

                    data = await loop.run_in_executor(None, _load_local_file)

                    if data is not None:
                        phase1_elapsed = time.perf_counter() - phase1_start
                        total_elapsed = time.perf_counter() - get_start_time
                        self.logger.info(
                            "[GET] key=%s 从本地缓存加载: shape=%s, dtype=%s, "
                            "缓存读取=%.4fs, 总计=%.4fs",
                            key,
                            data.shape,
                            data.dtype,
                            phase1_elapsed,
                            total_elapsed,
                        )
                        return data
                except Exception as e:
                    self.logger.warning(f"[GET] 读取本地缓存失败: {e}, 转为网络获取")
        phase1_elapsed = time.perf_counter() - phase1_start

        if inplace_tensor is not None and hasattr(inplace_tensor, "place"):
            self.logger.debug("[GET] inplace_tensor device: %s", inplace_tensor.place)

        # ========== 阶段2: 查询元数据 ==========
        phase2_start = time.perf_counter()
        entry = await self._query_metadata(key)
        phase2_elapsed = time.perf_counter() - phase2_start

        if not entry:
            self.logger.error("[GET] 数据不存在: key=%s", key)
            # 记录失败指标
            if self._metrics:
                get_elapsed = time.perf_counter() - get_start_time
                self._metrics.record_get(success=False, latency=get_elapsed, key=key)
            return None

        provider_addr = entry.get("host", "")
        metadata = entry.get("metadata", {})
        client_id = metadata.get("client_id", "unknown")
        data_size = metadata.get("data_size", 0)
        self.logger.debug(
            "[GET] 查询成功: key=%s, provider=%s, size=%d bytes",
            key,
            provider_addr,
            data_size,
        )

        # ========== 阶段3: 构建传输请求 ==========
        phase3_start = time.perf_counter()
        request = self._request_from_metadata(key, metadata)
        phase3_elapsed = time.perf_counter() - phase3_start

        if request is None:
            self.logger.error("[GET] 构建传输请求失败: key=%s", key)
            # 记录失败指标
            if self._metrics:
                get_elapsed = time.perf_counter() - get_start_time
                self._metrics.record_get(success=False, latency=get_elapsed, key=key)
            return None

        # RDMA 传输 (带重试机制)
        # 超时策略 (针对高性能 RDMA: 10GB/30s ≈ 333MB/s):
        #   - 小文件 (<10MB): 2-3 秒 (主要场景，高并发下留足余量)
        #   - 中文件 (10-100MB): 3-10 秒 (线性增长)
        #   - 大文件 (>100MB): 10-30 秒 (上限 30s，足够 10GB 传输)
        # 重试策略:
        #   - 最多重试 3 次 (共 4 次尝试)
        #   - 指数退避 + 抖动: 0.5s → 1s → 2s (避免高并发下重试风暴)
        size_mb = data_size / (1024 * 1024)  # 转换为 MB

        # 动态超时计算: 小文件快速失败，大文件留足时间
        if size_mb < 10:
            recv_timeout = max(10.0, size_mb * 0.3)  # 1MB->2s, 10MB->3s
        elif size_mb < 100:
            recv_timeout = 3.0 + (size_mb - 10) * 0.1  # 10MB->3s, 100MB->12s
        else:
            recv_timeout = min(
                12.0 + (size_mb - 100) * 0.018, 30.0
            )  # 100MB->12s, 1GB->30s

        max_retries = 3  # 最多重试 3 次
        base_retry_interval = 0.5  # 基础重试间隔（秒）

        self.logger.debug(
            "[GET] RDMA 传输准备: key=%s, remote=%s, client_id=%s, ptr=0x%x, "
            "size=%d bytes (%.2f MB), timeout=%.1fs",
            key,
            provider_addr,
            client_id,
            request.buffer_ptr or 0,
            data_size,
            size_mb,
            recv_timeout,
        )

        # ========== 阶段4: RDMA 传输 ==========
        phase4_start = time.perf_counter()
        payload = None
        last_error = None
        loop = asyncio.get_running_loop()
        selected_transport = self._select_transport_for_recv(provider_addr)
        selected_addr = selected_transport.get_local_addr()
        self.logger.debug(
            "[GET] 选择接收 transport: addr=%s (provider=%s)",
            selected_addr,
            provider_addr,
        )

        # 只有 least_active 策略需要跟踪活跃请求，其他策略跳过以避免锁竞争
        use_tracking = self._load_balancer.recv_strategy == "least_active"
        if use_tracking:
            self._load_balancer.mark_active(selected_transport)
        try:
            for attempt in range(max_retries + 1):
                try:
                    payload = await asyncio.wait_for(
                        loop.run_in_executor(
                            None,
                            lambda: selected_transport.recv(
                                request=request, remote_addr=provider_addr
                            ),
                        ),
                        timeout=recv_timeout,
                    )

                    if payload is not None:
                        # 传输成功，跳出重试循环
                        if attempt > 0:
                            self.logger.info(
                                "[GET] RDMA 传输成功 (重试后): key=%s, 尝试 %d/%d",
                                key,
                                attempt + 1,
                                max_retries + 1,
                            )
                        break

                    # payload 为 None，记录警告并重试
                    self.logger.warning(
                        "[GET] RDMA 传输返回 None: key=%s, 尝试 %d/%d",
                        key,
                        attempt + 1,
                        max_retries + 1,
                    )
                    last_error = "transport returned None"

                except asyncio.TimeoutError:
                    last_error = f"timeout after {recv_timeout:.1f}s"
                    self.logger.warning(
                        "[GET] RDMA 传输超时: key=%s, 尝试 %d/%d, timeout=%.1fs",
                        key,
                        attempt + 1,
                        max_retries + 1,
                        recv_timeout,
                    )

                except Exception as e:
                    last_error = str(e)
                    self.logger.warning(
                        "[GET] RDMA 传输异常: key=%s, 尝试 %d/%d, error=%s",
                        key,
                        attempt + 1,
                        max_retries + 1,
                        e,
                    )

                # 如果不是最后一次尝试，指数退避后重试
                if attempt < max_retries:
                    retry_delay = base_retry_interval * (2**attempt)  # 0.5s, 1s, 2s
                    self.logger.debug(
                        "[GET] 等待 %.1fs 后重试 (尝试 %d/%d)",
                        retry_delay,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(retry_delay)
        finally:
            if use_tracking:
                self._load_balancer.mark_complete(selected_transport)
        phase4_elapsed = time.perf_counter() - phase4_start

        # 所有重试都失败
        if payload is None:
            self.logger.error(
                "[GET] RDMA 传输最终失败: key=%s from %s (client_id=%s), "
                "已尝试 %d 次, 最后错误: %s",
                key,
                provider_addr,
                client_id,
                max_retries + 1,
                last_error,
            )
            # 记录失败指标
            if self._metrics:
                get_elapsed = time.perf_counter() - get_start_time
                self._metrics.record_get(
                    success=False, latency=get_elapsed, data_size=data_size, key=key
                )
            return None

        self.logger.debug(
            "[GET] RDMA 传输成功: key=%s, from %s (client_id=%s) received=%d bytes",
            key,
            provider_addr,
            client_id,
            len(payload),
        )

        # ========== 阶段5: 保存文件（可选） ==========
        phase5_start = time.perf_counter()
        if output_path:
            self.logger.debug("[GET] 保存到文件: %s", output_path)
            self._save_to_file(payload, output_path)
        phase5_elapsed = time.perf_counter() - phase5_start

        # ========== 阶段6: 数据解码 ==========
        phase6_start = time.perf_counter()
        result = self._decode_payload(request, payload, inplace_tensor)
        phase6_elapsed = time.perf_counter() - phase6_start

        elapsed = time.perf_counter() - get_start_time

        # 记录成功指标
        if self._metrics:
            self._metrics.record_get(
                success=True, latency=elapsed, data_size=data_size, key=key
            )

        # INFO 级别输出各环节耗时
        self.logger.info(
            "[GET] key=%s size=%d 耗时明细: "
            "本地缓存=%.4fs, 元数据查询=%.4fs, 构建请求=%.4fs, RDMA传输=%.4fs, 保存文件=%.4fs, 解码=%.4fs, 总计=%.4fs",
            key,
            data_size,
            phase1_elapsed,
            phase2_elapsed,
            phase3_elapsed,
            phase4_elapsed,
            phase5_elapsed,
            phase6_elapsed,
            elapsed,
        )
        return result

    async def exists(self, key: str) -> bool:  # pragma: no cover - 轻量辅助
        """
        检查数据是否存在.

        Args:
            key: 数据标识符.

        Returns:
            bool: 存在返回 True, 否则 False.
        """
        entry = await self._query_metadata(key)
        return entry is not None

    async def batch_get(
        self,
        keys: list[str],
        concurrency: int = 32,
    ) -> dict[str, Any | None]:
        """
        批量获取多个 key 的数据.

        使用批量查询 API 获取元数据，然后并发执行 RDMA 传输。
        相比循环调用 get()，batch_get 可显著减少元数据查询次数和总耗时。

        Args:
            keys: 要获取的数据 key 列表.
            concurrency: 并发 RDMA 传输数量，默认 32.
                         过高可能导致 RDMA 资源竞争，过低则传输效率下降.

        Returns:
            dict[str, Any | None]: 结果字典，key 为数据标识符，value 为数据或 None.
                                   如果某个 key 不存在或获取失败，对应 value 为 None.

        Example:
            >>> results = await client.batch_get(["key1", "key2", "key3"])
            >>> for key, data in results.items():
            ...     if data is not None:
            ...         print(f"{key}: shape={data.shape}")
            ...     else:
            ...         print(f"{key}: not found or failed")

        Performance Tips:
            - 对于大量小文件，增大 concurrency 可提升吞吐
            - 对于少量大文件，concurrency=8~16 即可
            - 建议单次 batch_get 不超过 1000 个 key
        """
        if not keys:
            return {}

        start_time = time.perf_counter()
        self.logger.info(
            "[BATCH_GET] 开始批量获取: count=%d, concurrency=%d",
            len(keys),
            concurrency,
        )

        # 1. 批量查询元数据
        loop = asyncio.get_running_loop()
        metadata_results = await loop.run_in_executor(
            self._metadata_executor,
            self.metadata_client.query_files_batch,
            keys,
        )

        # 统计查询结果
        found_keys = [k for k, v in metadata_results.items() if v is not None]
        missing_keys = [k for k, v in metadata_results.items() if v is None]

        self.logger.debug(
            "[BATCH_GET] 元数据查询完成: found=%d, missing=%d",
            len(found_keys),
            len(missing_keys),
        )

        if not found_keys:
            self.logger.warning("[BATCH_GET] 所有 key 均不存在")
            return {key: None for key in keys}

        # 2. 并发获取数据
        results = {key: None for key in keys}
        sem = asyncio.Semaphore(concurrency)

        # 重试配置
        max_retries = int(os.getenv("P2P_RDMA_MAX_RETRIES", "3"))
        base_retry_interval = float(os.getenv("P2P_RDMA_BASE_RETRY_INTERVAL", "0.5"))

        async def _fetch_single(key: str, entry: dict) -> tuple[str, Any | None]:
            """获取单个 key 的数据（带重试机制）."""
            async with sem:
                provider_addr = entry.get("host", "")
                metadata = entry.get("metadata", {})
                data_size = metadata.get("data_size", 0)

                request = self._request_from_metadata(key, metadata)
                if request is None:
                    self.logger.warning("[BATCH_GET] 构建传输请求失败: key=%s", key)
                    return key, None

                # 计算超时时间 (与 get() 方法保持一致)
                size_mb = data_size / (1024 * 1024)
                if size_mb < 10:
                    recv_timeout = max(10.0, size_mb * 0.3)
                elif size_mb < 100:
                    recv_timeout = 3.0 + (size_mb - 10) * 0.1
                else:
                    recv_timeout = min(12.0 + (size_mb - 100) * 0.018, 30.0)

                selected_transport = self._select_transport_for_recv(provider_addr)
                selected_addr = selected_transport.get_local_addr()
                self.logger.debug(
                    "[BATCH_GET] 选择接收 transport: addr=%s (provider=%s)",
                    selected_addr,
                    provider_addr,
                )

                # 带重试的 RDMA 传输
                # 只有 least_active 策略需要跟踪活跃请求，其他策略跳过以避免锁竞争
                last_error = None
                use_tracking = self._load_balancer.recv_strategy == "least_active"
                if use_tracking:
                    self._load_balancer.mark_active(selected_transport)
                try:
                    for attempt in range(max_retries + 1):
                        try:
                            payload = await asyncio.wait_for(
                                loop.run_in_executor(
                                    None,
                                    lambda: selected_transport.recv(
                                        request=request, remote_addr=provider_addr
                                    ),
                                ),
                                timeout=recv_timeout,
                            )

                            if payload is not None:
                                # 传输成功
                                if attempt > 0:
                                    self.logger.info(
                                        "[BATCH_GET] RDMA 传输成功 (重试后): key=%s, 尝试 %d/%d",
                                        key,
                                        attempt + 1,
                                        max_retries + 1,
                                    )
                                # 解码数据
                                data = self._decode_payload(request, payload, None)
                                return key, data

                            # payload 为 None
                            last_error = "transport returned None"
                            self.logger.warning(
                                "[BATCH_GET] RDMA 传输返回 None: key=%s, 尝试 %d/%d",
                                key,
                                attempt + 1,
                                max_retries + 1,
                            )

                        except asyncio.TimeoutError:
                            last_error = f"timeout after {recv_timeout:.1f}s"
                            self.logger.warning(
                                "[BATCH_GET] RDMA 传输超时: key=%s, 尝试 %d/%d",
                                key,
                                attempt + 1,
                                max_retries + 1,
                            )

                        except Exception as e:
                            last_error = str(e)
                            self.logger.warning(
                                "[BATCH_GET] RDMA 传输异常: key=%s, 尝试 %d/%d, error=%s",
                                key,
                                attempt + 1,
                                max_retries + 1,
                                e,
                            )

                        # 如果不是最后一次尝试，指数退避后重试
                        if attempt < max_retries:
                            retry_delay = base_retry_interval * (2**attempt)
                            await asyncio.sleep(retry_delay)

                    # 所有重试都失败
                    self.logger.error(
                        "[BATCH_GET] RDMA 传输最终失败: key=%s, 已尝试 %d 次, 最后错误: %s",
                        key,
                        max_retries + 1,
                        last_error,
                    )
                    return key, None
                finally:
                    if use_tracking:
                        self._load_balancer.mark_complete(selected_transport)

        # 创建所有获取任务
        tasks = []
        for key in found_keys:
            entry = metadata_results.get(key)
            if entry is not None:
                tasks.append(_fetch_single(key, entry))

        # 并发执行
        if tasks:
            fetch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in fetch_results:
                if isinstance(result, BaseException):
                    self.logger.warning("[BATCH_GET] 任务异常: %s", result)
                    continue
                if isinstance(result, tuple) and len(result) == 2:
                    key, data = result
                    results[key] = data

        # 统计结果
        success_count = sum(1 for v in results.values() if v is not None)
        elapsed = time.perf_counter() - start_time

        self.logger.info(
            "[BATCH_GET] 批量获取完成: total=%d, success=%d, failed=%d, elapsed=%.3fs",
            len(keys),
            success_count,
            len(keys) - success_count,
            elapsed,
        )

        return results

    async def batch_get_prefix(
        self,
        prefix: str,
        concurrency: int = 32,
    ) -> dict[str, Any | None]:
        """
        根据前缀批量获取数据.

        先查询指定前缀下的所有 key，然后并发获取所有数据。
        适用于按批次/分组存储的场景（如 RLHF rollout 数据）。

        Args:
            prefix: 数据 key 的前缀.
                    例如 "rollout_batch_0_" 会匹配所有以此开头的 key.
                    注意：建议在前缀末尾加分隔符（如 "_" 或 "/"）避免误匹配。
            concurrency: 并发 RDMA 传输数量，默认 32.

        Returns:
            dict[str, Any | None]: 结果字典，key 为完整的数据标识符，value 为数据或 None.

        Example:
            >>> # 假设有 key: rollout/0, rollout/1, rollout/2, ...
            >>> results = await client.batch_get_prefix("rollout/")
            >>> for key, data in results.items():
            ...     print(f"{key}: {data.shape if data is not None else 'None'}")

        Note:
            - 使用 get_prefix 一次性获取所有匹配的元数据
            - 建议前缀末尾带分隔符，避免 "12:7:0" 匹配到 "12:7:01"
        """
        start_time = time.perf_counter()
        self.logger.info(
            "[BATCH_GET_PREFIX] 开始前缀批量获取: prefix=%s, concurrency=%d",
            prefix,
            concurrency,
        )

        # 1. 查询前缀下的所有元数据
        loop = asyncio.get_running_loop()
        prefix_results = await loop.run_in_executor(
            self._metadata_executor,
            self.metadata_client.get_prefix,
            prefix,
        )

        if not prefix_results:
            self.logger.warning("[BATCH_GET_PREFIX] 前缀下无数据: prefix=%s", prefix)
            return {}

        keys = list(prefix_results.keys())
        self.logger.info(
            "[BATCH_GET_PREFIX] 前缀查询完成: prefix=%s, count=%d",
            prefix,
            len(keys),
        )

        # 2. 并发获取数据
        results: dict[str, Any | None] = {key: None for key in keys}
        sem = asyncio.Semaphore(concurrency)

        # 重试配置
        max_retries = int(os.getenv("P2P_RDMA_MAX_RETRIES", "3"))
        base_retry_interval = float(os.getenv("P2P_RDMA_BASE_RETRY_INTERVAL", "0.5"))

        async def _fetch_single(key: str, entry: dict) -> tuple[str, Any | None]:
            """获取单个 key 的数据（带重试机制）."""
            async with sem:
                provider_addr = entry.get("host", "")
                metadata = entry.get("metadata", {})
                data_size = metadata.get("data_size", 0)

                request = self._request_from_metadata(key, metadata)
                if request is None:
                    self.logger.warning(
                        "[BATCH_GET_PREFIX] 构建传输请求失败: key=%s", key
                    )
                    return key, None

                # 计算超时时间 (与 get() 方法保持一致)
                size_mb = data_size / (1024 * 1024)
                if size_mb < 10:
                    recv_timeout = max(10.0, size_mb * 0.3)
                elif size_mb < 100:
                    recv_timeout = 3.0 + (size_mb - 10) * 0.1
                else:
                    recv_timeout = min(12.0 + (size_mb - 100) * 0.018, 30.0)

                selected_transport = self._select_transport_for_recv(provider_addr)
                selected_addr = selected_transport.get_local_addr()
                self.logger.debug(
                    "[BATCH_GET_PREFIX] 选择接收 transport: addr=%s (provider=%s)",
                    selected_addr,
                    provider_addr,
                )

                # 带重试的 RDMA 传输
                # 只有 least_active 策略需要跟踪活跃请求，其他策略跳过以避免锁竞争
                last_error = None
                use_tracking = self._load_balancer.recv_strategy == "least_active"
                if use_tracking:
                    self._load_balancer.mark_active(selected_transport)
                try:
                    for attempt in range(max_retries + 1):
                        try:
                            payload = await asyncio.wait_for(
                                loop.run_in_executor(
                                    None,
                                    lambda: selected_transport.recv(
                                        request=request, remote_addr=provider_addr
                                    ),
                                ),
                                timeout=recv_timeout,
                            )

                            if payload is not None:
                                # 传输成功
                                if attempt > 0:
                                    self.logger.info(
                                        "[BATCH_GET_PREFIX] RDMA 传输成功 (重试后): key=%s, 尝试 %d/%d",
                                        key,
                                        attempt + 1,
                                        max_retries + 1,
                                    )
                                # 解码数据
                                data = self._decode_payload(request, payload, None)
                                return key, data

                            # payload 为 None
                            last_error = "transport returned None"
                            self.logger.warning(
                                "[BATCH_GET_PREFIX] RDMA 传输返回 None: key=%s, 尝试 %d/%d",
                                key,
                                attempt + 1,
                                max_retries + 1,
                            )

                        except asyncio.TimeoutError:
                            last_error = f"timeout after {recv_timeout:.1f}s"
                            self.logger.warning(
                                "[BATCH_GET_PREFIX] RDMA 传输超时: key=%s, 尝试 %d/%d",
                                key,
                                attempt + 1,
                                max_retries + 1,
                            )

                        except Exception as e:
                            last_error = str(e)
                            self.logger.warning(
                                "[BATCH_GET_PREFIX] RDMA 传输异常: key=%s, 尝试 %d/%d, error=%s",
                                key,
                                attempt + 1,
                                max_retries + 1,
                                e,
                            )

                        # 如果不是最后一次尝试，指数退避后重试
                        if attempt < max_retries:
                            retry_delay = base_retry_interval * (2**attempt)
                            await asyncio.sleep(retry_delay)

                    # 所有重试都失败
                    self.logger.error(
                        "[BATCH_GET_PREFIX] RDMA 传输最终失败: key=%s, 已尝试 %d 次, 最后错误: %s",
                        key,
                        max_retries + 1,
                        last_error,
                    )
                    return key, None
                finally:
                    if use_tracking:
                        self._load_balancer.mark_complete(selected_transport)

        # 创建所有获取任务
        tasks = []
        for key in keys:
            entry = prefix_results.get(key)
            if entry is not None:
                tasks.append(_fetch_single(key, entry))

        # 并发执行
        if tasks:
            fetch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in fetch_results:
                if isinstance(result, BaseException):
                    self.logger.warning("[BATCH_GET_PREFIX] 任务异常: %s", result)
                    continue
                if isinstance(result, tuple) and len(result) == 2:
                    key, data = result
                    results[key] = data

        # 统计结果
        success_count = sum(1 for v in results.values() if v is not None)
        elapsed = time.perf_counter() - start_time

        self.logger.info(
            "[BATCH_GET_PREFIX] 完成: prefix=%s, total=%d, success=%d, failed=%d, elapsed=%.3fs",
            prefix,
            len(keys),
            success_count,
            len(keys) - success_count,
            elapsed,
        )

        return results

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------
    async def _query_metadata(self, key: str) -> dict | None:
        """
        查询元数据 (带重试机制).

        从 Redis 查询指定 key 的元数据信息，包括数据所在节点、大小、类型等。
        查询失败时会进行重试，最多重试 5 次。

        Args:
            key: 数据的唯一标识符
                 示例: "model/layer1/weights"

        Returns:
            dict | None:
                - dict: 包含元数据的字典，结构如下:
                    {
                        "host": "10.0.0.1:5001,5002",  # 数据所在节点
                        "metadata": {
                            "object_type": "numpy",
                            "data_size": 40000,
                            "tensor_shape": [100, 100],
                            "tensor_dtype": "float32"
                        }
                    }
                - None: 数据不存在或查询失败

        超时与重试机制:
            - 单次查询超时: 5 秒
            - 最大重试次数: 5 次 (共 6 次尝试)
            - 重试间隔: 指数退避 0.5s → 1s → 2s → 4s → 8s

        示例:
            entry = await client._query_metadata("my_array")
            if entry:
                provider = entry["host"]  # "10.0.0.1:5001,5002"
                size = entry["metadata"]["data_size"]  # 40000
        """
        self.logger.debug("[QUERY] 查询元数据: key=%s", key)

        max_retries = 5
        base_retry_interval = 0.5
        query_timeout_env = os.getenv("P2P_QUERY_TIMEOUT")
        try:
            query_timeout = float(query_timeout_env) if query_timeout_env else 5.0
        except ValueError:
            query_timeout = 5.0
        # 安全边界: 防止异常配置导致过短或过长
        query_timeout = max(0.5, min(query_timeout, 10.0))
        last_error = None
        loop = asyncio.get_running_loop()

        for attempt in range(max_retries + 1):
            try:
                # 使用 run_in_executor 将同步的元数据调用放入专用线程池
                # 避免阻塞主事件循环
                result = await asyncio.wait_for(
                    loop.run_in_executor(
                        self._metadata_executor, self.metadata_client.query_file, key
                    ),
                    timeout=query_timeout,
                )

                if result:
                    if attempt > 0:
                        self.logger.info(
                            "[QUERY] 查询成功 (重试后): key=%s, 尝试 %d/%d",
                            key,
                            attempt + 1,
                            max_retries + 1,
                        )
                    else:
                        self.logger.debug("[QUERY] 查询成功: key=%s", key)
                    return result
                else:
                    # 数据不存在，不需要重试
                    self.logger.debug("[QUERY] 数据不存在: key=%s", key)
                    return None

            except asyncio.TimeoutError:
                last_error = f"timeout after {query_timeout}s"
                self.logger.warning(
                    "[QUERY] 查询超时: key=%s, 尝试 %d/%d, timeout=%.1fs",
                    key,
                    attempt + 1,
                    max_retries + 1,
                    query_timeout,
                )

            except Exception as e:
                last_error = str(e)
                self.logger.warning(
                    "[QUERY] 查询异常: key=%s, 尝试 %d/%d, error=%s",
                    key,
                    attempt + 1,
                    max_retries + 1,
                    e,
                )

            # 如果不是最后一次尝试，指数退避后重试
            if attempt < max_retries:
                retry_delay = base_retry_interval * (2**attempt)
                self.logger.debug(
                    "[QUERY] 等待 %.1fs 后重试 (尝试 %d/%d)",
                    retry_delay,
                    attempt + 1,
                    max_retries,
                )
                await asyncio.sleep(retry_delay)

        # 所有重试都失败
        self.logger.error(
            "[QUERY] 查询最终失败: key=%s, 已尝试 %d 次, 最后错误: %s",
            key,
            max_retries + 1,
            last_error,
        )
        return None

    def _build_transfer_request(self, key: str, data: Any, data_type: str):
        request = TransferRequest(
            object_type=data_type,
            data_size=0,
            tensor_shape=(),
            metadata={"file_key": key},
        )

        if data_type == "numpy":
            # Numpy 数组：直接传递，不序列化
            payload = data
            request.tensor_shape = tuple(payload.shape)
            request.tensor_dtype = str(payload.dtype)
            request.data_size = payload.nbytes

        elif data_type == "tensor":
            if not hasattr(data, "nbytes"):
                # Fallback: 如果无法直接获取大小，才不得不序列化（极少情况）
                payload = serialize_tensor(data)
                request.data_size = len(payload)
            else:
                # Paddle Tensor：直接传递，不序列化
                payload = data
            request.tensor_shape = tuple(payload.shape)
            request.tensor_dtype = str(payload.dtype)
            request.data_size = payload.nbytes

        elif data_type == "safetensors":
            payload = numpy_from_file(data)
            request.file_path = data
            request.data_size = int(payload.nbytes)
        elif data_type == "object":
            payload = serialize_object(data)
            request.data_size = int(payload.nbytes)
        else:
            raise TypeError(f"不支持的数据类型: {data_type}")

        return payload, request

    def _metadata_from_request(
        self, _key: str, request: TransferRequest
    ) -> dict[str, Any]:
        """从传输请求构建元数据字典 (_key 参数保留用于未来扩展)."""
        metadata = {
            "object_type": request.object_type,
            "data_size": request.data_size,
            "tensor_shape": request.tensor_shape,
            "tensor_dtype": request.tensor_dtype,
            "buffer_ptr": request.buffer_ptr,
        }
        metadata.update(request.metadata)
        return metadata

    def _request_from_metadata(
        self, _key: str, metadata: dict[str, Any]
    ) -> TransferRequest | None:
        """从元数据构建传输请求 (_key 参数保留用于未来扩展)."""
        object_type = metadata.get("object_type")
        data_size = int(metadata.get("data_size", 0))
        if not object_type or data_size <= 0:
            self.logger.error("元数据缺失 object_type 或 data_size, 无法传输")
            return None
        request = TransferRequest(
            object_type=object_type,
            data_size=data_size,
            tensor_shape=tuple(metadata.get("tensor_shape") or ()),
            tensor_dtype=metadata.get("tensor_dtype"),
            file_path=metadata.get("file_path", ""),
            buffer_ptr=metadata.get("buffer_ptr"),
            metadata=metadata.copy(),  # 传递完整的原始 metadata
        )
        return request

    def _decode_payload(
        self,
        request: TransferRequest,
        payload: Any,
        _inplace_tensor: Any | None,
    ) -> Any:
        """
        解码传输负载数据.

        Args:
            request: 传输请求对象
            payload: 原始负载数据
            _inplace_tensor: 保留参数，用于未来的原地写入优化

        Returns:
            解码后的数据对象
        """
        raw_bytes = self._to_bytes(payload)
        obj_type = request.object_type

        # Numpy: 直接从 raw bytes 恢复为 ndarray（零拷贝）
        if obj_type == "numpy":
            self.logger.debug(
                "[DECODE] key %s 恢复 Numpy 数组: shape=%s dtype=%s",
                request.metadata.get("file_key", ""),
                request.tensor_shape,
                request.tensor_dtype,
            )
            dtype = np.dtype(request.tensor_dtype)
            arr = np.frombuffer(raw_bytes, dtype=dtype)
            if request.tensor_shape:
                arr = arr.reshape(request.tensor_shape)
            return arr

        # Paddle Tensor / Safetensors: 返回 raw bytes 让用户自己加载
        if obj_type in ("tensor", "safetensors"):
            return raw_bytes

        if obj_type == "object":
            return deserialize_object(raw_bytes)

        return raw_bytes

    def _save_to_file(self, payload: Any, output_path: str) -> None:
        data = self._to_bytes(payload)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(data)
        self.logger.info("数据已保存到 %s", output_path)

    def _to_bytes(self, payload: Any) -> bytes:
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, np.ndarray):
            return payload.tobytes()
        if isinstance(payload, bytearray):
            return bytes(payload)
        return bytes(payload)

    def _delete_local_cache(self, key: str) -> bool:
        """
        删除指定 key 的本地磁盘缓存.

        Args:
            key: 文件 key

        Returns:
            bool: 是否成功删除（文件不存在也返回 True）
        """
        persistence_dir = self.config.persistence_dir
        if not persistence_dir:
            return True

        # 构建本地缓存路径（与 cache_all 保持一致：把 / 替换为 _）
        safe_filename = key.replace("/", "_")
        local_path = os.path.join(persistence_dir, safe_filename)

        try:
            if os.path.exists(local_path):
                os.remove(local_path)
                self.logger.info("[CACHE] 已删除本地缓存: %s", local_path)
                return True
            else:
                self.logger.debug("[CACHE] 本地缓存不存在，跳过: %s", local_path)
                return True
        except Exception as e:
            self.logger.warning("[CACHE] 删除本地缓存失败: %s, error=%s", local_path, e)
            return False

    def _delete_local_cache_prefix(self, prefix: str) -> int:
        """
        删除匹配前缀的所有本地磁盘缓存.

        注意：cache_all 保存文件时会把 key 中的 '/' 替换为 '_'，
        所以这里也需要匹配这种格式。
        例如 prefix="batch_0/" 会匹配文件名 "batch_0_*"

        Args:
            prefix: 文件 key 前缀

        Returns:
            int: 成功删除的文件数量
        """
        persistence_dir = self.config.persistence_dir
        if not persistence_dir:
            return 0

        if not os.path.exists(persistence_dir):
            return 0

        # 与 cache_all 一致：把 prefix 中的 / 替换为 _ 来匹配文件名
        safe_prefix = prefix.replace("/", "_")

        deleted_count = 0
        files_to_delete = []

        try:
            # 使用 os.scandir 替代 os.listdir，在大量文件场景下性能更好
            # 它可以避免加载所有文件名到内存，且部分文件属性(如 is_file)无需额外系统调用
            with os.scandir(persistence_dir) as it:
                for entry in it:
                    if entry.name.startswith(safe_prefix) and entry.is_file():
                        files_to_delete.append(entry.path)
        except Exception as e:
            self.logger.error(
                "[CACHE] 遍历本地缓存目录失败: %s, error=%s", persistence_dir, e
            )
            return 0

        if not files_to_delete:
            return 0

        # 定义删除单个文件的帮助函数
        def _delete_one(file_path: str) -> int:
            try:
                # 直接尝试删除，避免 TOCTOU 竞态条件
                os.remove(file_path)
                self.logger.debug("[CACHE] 已删除本地缓存: %s", file_path)
                return 1
            except FileNotFoundError:
                # 文件可能已被其他 client 删除，属于正常情况
                self.logger.debug(
                    "[CACHE] 文件已不存在（可能被其他进程删除）: %s", file_path
                )
                return 0
            except Exception as e:
                self.logger.warning(
                    "[CACHE] 删除本地缓存失败: %s, error=%s", file_path, e
                )
                return 0

        # 使用多线程并行删除，加速大量文件的清理过程
        # 根据文件数量动态调整线程数，最大 64 线程
        max_workers = min(64, len(files_to_delete))

        if max_workers <= 1:
            # 文件很少时，直接串行删除，避免线程池开销
            for f in files_to_delete:
                deleted_count += _delete_one(f)
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = executor.map(_delete_one, files_to_delete)
                deleted_count = sum(results)

        if deleted_count > 0:
            self.logger.debug(
                "[CACHE] _delete_local_cache_prefix: prefix=%s, deleted=%d",
                prefix,
                deleted_count,
            )

        return deleted_count

    # ------------------------------------------------------------------
    # Common APIs
    # ------------------------------------------------------------------
    def list(self, prefix: str | None = None) -> list[str]:
        """
        列出所有已注册的文件 key.

        使用 keys_only 模式，只获取 key 不获取 value，
        30万 key 速度比 list_files() 快 10-50 倍。

        Args:
            prefix: 可选的前缀过滤.

        Returns:
            list[str]: 文件 key 的列表.

        Example:
            >>> client.list()
            ['model/layer1', 'model/layer2', 'data/batch1']
            >>> client.list(prefix="model/")
            ['model/layer1', 'model/layer2']
        """
        return self.metadata_client.list_keys(prefix)

    def list_files(self) -> dict[str, dict]:
        """
        列出所有已注册的文件及其详细元数据.

        Returns:
            dict[str, dict]: 包含文件信息的字典, key 为文件名, value 为元数据.

        Example:
            >>> client.list_files()
            {
                'model/layer1': {
                    'host': '10.0.0.1:5001',
                    'metadata': {
                        'object_type': 'numpy',
                        'data_size': 40000,
                        'tensor_shape': [100, 100],
                        'tensor_dtype': 'float32'
                    }
                }
            }
        """
        return self.metadata_client.list_files()

    def close(self) -> None:
        """关闭客户端，注销所有已注册的 key 并释放资源."""
        # 先注销 Metaserver 上的元数据
        for key in list(self._registered_keys):
            try:
                self.metadata_client.unregister_file(key)
                self.logger.debug("已注销 key: %s", key)
            except Exception as e:
                self.logger.warning("注销 key '%s' 失败: %s", key, e)
            # 使用正确的 transport 释放本地 buffer
            key_info = self._registered_keys.get(key)
            if isinstance(key_info, dict):
                transport_addr = key_info.get("transport_addr")
                target_transport = self._addr_to_transport.get(
                    transport_addr, self.transport
                )
            else:
                target_transport = self.transport
            target_transport.release(key)
        self._registered_keys.clear()

        # 关闭 Metadata Client
        # 停止心跳续租线程，防止程序挂起
        if hasattr(self.metadata_client, "close"):
            self.metadata_client.close()

        # 关闭元数据专用线程池，避免线程泄漏/进程无法退出
        executor = getattr(self, "_metadata_executor", None)
        if executor is not None:
            try:
                executor.shutdown(wait=True, cancel_futures=True)
                self.logger.debug("Metadata executor 已关闭")
            except Exception as e:
                self.logger.warning("关闭 Metadata executor 失败: %s", e)
            finally:
                self._metadata_executor = None

        self.logger.info("P2PClient 已关闭")

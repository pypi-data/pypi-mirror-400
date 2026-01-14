"""
Configuration 模块.

该模块定义了 P2P 系统的统一配置类 `P2PConfig`。
Server 和 Client 共用同一配置类，用于集中管理所有可配置参数。

支持的元数据服务器:
- Redis: redis://[[username:]password@]host:port[/db][?param=value]
         redis+sentinel://[[username:]password@]host:port,...[/service_name][/db]
         redis+cluster://host:port,host:port,...

"""

import os
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlparse


@dataclass
class P2PConfig:
    """
    P2P Store 统一配置类（使用 Redis 作为元数据后端）.

    核心属性:
        metadata_server: 元数据服务器地址，支持以下格式:
            - Redis 单机: "redis://[[username:]password@]host:port[/db]"
            - Redis Sentinel: "redis+sentinel://host:port,.../service_name[/db]"
            - Redis Cluster: "redis+cluster://host:port,host:port,..."
        local_host: 本地地址，默认从环境变量 POD_IP 获取

    传输属性:
        protocol: 传输协议 (rdma/tcp)
        device: RDMA 设备名

    Usage:
        # Redis 单机模式
        config = P2PConfig(metadata_server="redis://localhost:6379/0")

        # Redis Sentinel 模式
        config = P2PConfig(
            metadata_server="redis+sentinel://10.0.0.1:26379,10.0.0.2:26379/mymaster/0"
        )

        # Redis Cluster 模式
        config = P2PConfig(
            metadata_server="redis+cluster://10.0.0.1:6379,10.0.0.2:6379"
        )

        client = P2PClient(config)
    """

    # 核心配置 (必填)
    metadata_server: str  # 格式: "redis://..."
    local_host: str = ""

    # 内部使用，自动从 metadata_server 解析
    metadata_type: str = "redis"  # 当前仅支持 "redis"

    # Redis 配置 (自动解析)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    redis_username: str | None = None
    redis_mode: str = "standalone"  # "standalone" | "sentinel" | "cluster"
    redis_sentinel_nodes: list[tuple[str, int]] = field(default_factory=list)
    redis_sentinel_service: str = "mymaster"
    redis_cluster_nodes: list[tuple[str, int]] = field(default_factory=list)
    redis_key_prefix: str = "p2p:"  # Redis key 前缀
    redis_socket_timeout: float = 10.0  # 连接超时 (秒)
    redis_socket_connect_timeout: float = 5.0  # 连接建立超时 (秒)

    # transport
    protocol: str = "rdma"
    device: str = "mlx5_3"
    meta_server: str = "P2PHANDSHAKE"

    # common
    max_retries: int = 3
    retry_interval: int = 5
    log_name: str | None = None
    enable_watch: bool = True  # 是否启用 Watch (Redis Pub/Sub)
    redis_key_ttl: int = 0  # Redis key TTL (秒)，0 表示永不过期（每轮手动 clear）
    redis_provider_ttl: int = 3600  # Provider TTL (秒)，用于进程异常退出时自动清理，0 表示跟随 redis_key_ttl
    persistence_dir: str | None = None  # 本地持久化缓存目录 (用于 Debug)

    def __post_init__(self) -> None:
        """初始化后处理."""
        # 优先使用环境变量中的 TTL 设置
        if os.getenv("P2P_REDIS_KEY_TTL"):
            try:
                self.redis_key_ttl = int(os.environ["P2P_REDIS_KEY_TTL"])
            except ValueError:
                pass

        # 自动填充 local_host
        if not self.local_host:
            self.local_host = os.getenv("POD_IP", "").strip() or "127.0.0.1"

        # 解析 metadata_server
        server = self.metadata_server.strip()
        if server.startswith("redis+sentinel://"):
            self.metadata_type = "redis"
            self.redis_mode = "sentinel"
            self._parse_redis_sentinel_addr(server[17:])  # 去掉 "redis+sentinel://"
        elif server.startswith("redis+cluster://"):
            self.metadata_type = "redis"
            self.redis_mode = "cluster"
            self._parse_redis_cluster_addr(server[16:])  # 去掉 "redis+cluster://"
        elif server.startswith("redis://"):
            self.metadata_type = "redis"
            self.redis_mode = "standalone"
            self._parse_redis_addr(server)  # 使用完整 URL 进行解析
        else:
            raise ValueError(
                f"配置错误: metadata_server 格式错误 '{server}'，"
                "支持的格式: 'redis://...', "
                "'redis+sentinel://...', 'redis+cluster://...'"
            )

    def _parse_redis_addr(self, url: str) -> None:
        """
        解析 Redis 单机模式的地址.

        格式: redis://[[username:]password@]host:port[/db][?param=value]
        示例:
            - redis://localhost:6379
            - redis://localhost:6379/0
            - redis://:password@localhost:6379/0
            - redis://user:password@localhost:6379/0
        """
        parsed = urlparse(url)

        self.redis_host = parsed.hostname or "localhost"
        self.redis_port = parsed.port or 6379
        self.redis_password = parsed.password
        self.redis_username = parsed.username

        # 解析数据库号 (路径中的第一个数字)
        if parsed.path and parsed.path != "/":
            path = parsed.path.strip("/")
            if path.isdigit():
                self.redis_db = int(path)

        # 解析查询参数
        if parsed.query:
            params = parse_qs(parsed.query)
            if "db" in params:
                self.redis_db = int(params["db"][0])
            if "socket_timeout" in params:
                self.redis_socket_timeout = float(params["socket_timeout"][0])
            if "key_prefix" in params:
                self.redis_key_prefix = params["key_prefix"][0]

    def _parse_redis_sentinel_addr(self, addr: str) -> None:
        """
        解析 Redis Sentinel 模式的地址.

        格式: [[username:]password@]host:port,host:port,.../service_name[/db]
        示例:
            - 10.0.0.1:26379,10.0.0.2:26379/mymaster
            - 10.0.0.1:26379,10.0.0.2:26379/mymaster/0
            - :password@10.0.0.1:26379,10.0.0.2:26379/mymaster/0
        """
        # 提取认证信息
        if "@" in addr:
            auth_part, addr = addr.rsplit("@", 1)
            if ":" in auth_part:
                username, password = auth_part.split(":", 1)
                self.redis_username = username if username else None
                self.redis_password = password if password else None
            else:
                self.redis_password = auth_part

        # 分离节点列表和服务名/db
        parts = addr.split("/")
        nodes_str = parts[0]
        service_name = parts[1] if len(parts) > 1 else "mymaster"
        db = int(parts[2]) if len(parts) > 2 else 0

        # 解析 Sentinel 节点
        sentinel_nodes = []
        for node in nodes_str.split(","):
            node = node.strip()
            if not node:
                continue
            if ":" in node:
                host, port = node.rsplit(":", 1)
                sentinel_nodes.append((host, int(port)))
            else:
                sentinel_nodes.append((node, 26379))  # 默认 Sentinel 端口

        if not sentinel_nodes:
            raise ValueError(
                f"配置错误: Redis Sentinel 节点列表为空 '{self.metadata_server}'"
            )

        self.redis_sentinel_nodes = sentinel_nodes
        self.redis_sentinel_service = service_name
        self.redis_db = db

    def _parse_redis_cluster_addr(self, addr: str) -> None:
        """
        解析 Redis Cluster 模式的地址.

        格式: [[username:]password@]host:port,host:port,...
        示例:
            - 10.0.0.1:6379,10.0.0.2:6379,10.0.0.3:6379
            - :password@10.0.0.1:6379,10.0.0.2:6379
        """
        # 提取认证信息
        if "@" in addr:
            auth_part, addr = addr.rsplit("@", 1)
            if ":" in auth_part:
                username, password = auth_part.split(":", 1)
                self.redis_username = username if username else None
                self.redis_password = password if password else None
            else:
                self.redis_password = auth_part

        # 解析集群节点
        cluster_nodes = []
        for node in addr.split(","):
            node = node.strip()
            if not node:
                continue
            if ":" in node:
                host, port = node.rsplit(":", 1)
                cluster_nodes.append((host, int(port)))
            else:
                cluster_nodes.append((node, 6379))  # 默认 Redis 端口

        if not cluster_nodes:
            raise ValueError(
                f"配置错误: Redis Cluster 节点列表为空 '{self.metadata_server}'"
            )

        self.redis_cluster_nodes = cluster_nodes

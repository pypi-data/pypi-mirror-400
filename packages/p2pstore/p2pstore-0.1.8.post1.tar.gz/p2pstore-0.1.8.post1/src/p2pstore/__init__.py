"""
P2P Store - 分布式 P2P 数据存储系统（使用 Redis 作为元数据后端）.

提供 Client API:
- P2PClient: 客户端，用于 put/get/list/delete 数据
- P2PConfig: 配置类

注意：当前版本使用 Redis 作为元数据后端，支持 Standalone/Sentinel/Cluster 模式。
"""

from .client import P2PClient
from .utils.config import P2PConfig

__all__ = [
    "P2PConfig",
    "P2PClient",
]

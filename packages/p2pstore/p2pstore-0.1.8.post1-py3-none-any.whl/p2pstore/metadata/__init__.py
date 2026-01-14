"""
Metadata 模块.

支持的元数据后端:
- Redis: redis://..., redis+sentinel://..., redis+cluster://...
"""

from ..core import MetadataClient
from ..utils.config import P2PConfig

try:
    from .redis_client import RedisMetadataClient
except ImportError:
    RedisMetadataClient = None


def create_metadata_client(
    config: P2PConfig,
    local_ip: str,
    client_id: str,
    registered_keys: dict[str, int] | None = None,
) -> MetadataClient:
    """
    创建元数据客户端.

    Args:
        config: P2PConfig 配置对象
        local_ip: 本地 IP 地址
        client_id: 客户端唯一标识符
        registered_keys: 已注册的 key 字典（用于 Watch 事件处理）

    Returns:
        MetadataClient 实例

    Raises:
        ImportError: 如果 redis 库未安装
    """
    if RedisMetadataClient is None:
        raise ImportError("请先安装 redis 库: pip install redis")

    return RedisMetadataClient(
        config=config,
        local_ip=local_ip,
        client_id=client_id,
        registered_keys=registered_keys,
    )


__all__ = [
    "MetadataClient",
    "RedisMetadataClient",
    "create_metadata_client",
]

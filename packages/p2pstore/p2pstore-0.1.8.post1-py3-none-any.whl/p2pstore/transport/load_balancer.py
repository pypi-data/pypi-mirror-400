"""RDMA Transport 负载均衡器.

支持的策略:
- random: 随机选择
- round_robin: 轮询，保证绝对均匀分布
- least_active: 最少活跃请求，动态负载感知
- sticky_hash: 粘性哈希，减少 endpoint eviction (用于 GET)
"""

from __future__ import annotations

import hashlib
import os
import random
import threading
from collections import defaultdict
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Transport


class TransportLoadBalancer:
    """RDMA Transport 负载均衡器.

    提供多种负载均衡策略，用于在多个 Transport 实例之间分配请求。

    Attributes:
        transports: Transport 实例列表
        send_strategy: PUT 操作使用的负载均衡策略
        recv_strategy: GET 操作使用的负载均衡策略
    """

    # 支持的策略
    STRATEGIES = ("random", "round_robin", "least_active", "sticky_hash")

    def __init__(
        self,
        transports: list[Transport],
        send_strategy: str = "round_robin",
        recv_strategy: str = "sticky_hash",
    ):
        """初始化负载均衡器.

        Args:
            transports: Transport 实例列表
            send_strategy: PUT 操作的策略，默认 round_robin
            recv_strategy: GET 操作的策略，默认 sticky_hash
        """
        if not transports:
            raise ValueError("transports 列表不能为空")

        self.transports = transports
        self._addr_to_transport: dict[str, Transport] = {}
        for t in transports:
            addr = t.get_local_addr()
            if addr:
                self._addr_to_transport[addr] = t

        self.send_strategy = self._validate_strategy(send_strategy)
        self.recv_strategy = self._validate_strategy(recv_strategy)

        # Round-robin 计数器
        self._rr_counter = 0

        # 活跃请求计数 (transport_addr -> active_count)
        self._active_requests: dict[str, int] = defaultdict(int)

        # 锁保护共享状态
        self._lock = threading.Lock()

    def _validate_strategy(self, strategy: str) -> str:
        """验证策略名称."""
        strategy = strategy.lower()
        if strategy not in self.STRATEGIES:
            raise ValueError(
                f"不支持的负载均衡策略: {strategy}，支持的策略: {self.STRATEGIES}"
            )
        return strategy

    def select_for_send(self, data_size: int = 0) -> Transport:
        """选择用于 PUT 操作的 Transport.

        Args:
            data_size: 数据大小（字节），用于 weighted 策略

        Returns:
            选中的 Transport 实例
        """
        if len(self.transports) == 1:
            return self.transports[0]

        if self.send_strategy == "round_robin":
            return self._round_robin()
        elif self.send_strategy == "least_active":
            return self._least_active()
        else:  # random
            return random.choice(self.transports)

    def select_for_recv(self, remote_addr: str | None = None) -> Transport:
        """选择用于 GET 操作的 Transport.

        对于 GET 操作，默认使用粘性哈希以减少 endpoint eviction。

        Args:
            remote_addr: 远程地址，用于粘性哈希

        Returns:
            选中的 Transport 实例
        """
        if len(self.transports) == 1:
            return self.transports[0]

        if self.recv_strategy == "sticky_hash" and remote_addr:
            return self._sticky_hash(remote_addr)
        elif self.recv_strategy == "round_robin":
            return self._round_robin()
        elif self.recv_strategy == "least_active":
            return self._least_active()
        else:  # random or no remote_addr
            return random.choice(self.transports)

    def _round_robin(self) -> Transport:
        """轮询选择，保证绝对均匀分布."""
        with self._lock:
            idx = self._rr_counter % len(self.transports)
            self._rr_counter += 1
            return self.transports[idx]

    def _least_active(self) -> Transport:
        """选择活跃请求最少的 Transport."""
        with self._lock:
            min_active = float("inf")
            candidates = []
            for t in self.transports:
                addr = t.get_local_addr()
                active = self._active_requests.get(addr, 0)
                if active < min_active:
                    min_active = active
                    candidates = [t]
                elif active == min_active:
                    candidates.append(t)
            # 如果有多个最小值，随机选一个
            return random.choice(candidates) if candidates else self.transports[0]

    def _sticky_hash(self, remote_addr: str) -> Transport:
        """粘性哈希，同一个 remote_addr 总是选择同一个 Transport."""
        # 使用 MD5 避免 Python 内置 hash 的随机种子问题
        digest = hashlib.md5(
            remote_addr.encode("utf-8"), usedforsecurity=False
        ).digest()
        idx = int.from_bytes(digest[:8], "big", signed=False) % len(self.transports)
        return self.transports[idx]

    def mark_active(self, transport: Transport) -> None:
        """标记 Transport 开始处理请求."""
        addr = transport.get_local_addr()
        with self._lock:
            self._active_requests[addr] += 1

    def mark_complete(self, transport: Transport) -> None:
        """标记 Transport 完成请求."""
        addr = transport.get_local_addr()
        with self._lock:
            self._active_requests[addr] = max(0, self._active_requests[addr] - 1)

    @contextmanager
    def track_request(self, transport: Transport):
        """上下文管理器，自动跟踪请求的开始和结束.

        Usage:
            with lb.track_request(transport):
                transport.send(...)
        """
        self.mark_active(transport)
        try:
            yield
        finally:
            self.mark_complete(transport)

    def get_transport_by_addr(self, addr: str) -> Transport | None:
        """根据地址获取 Transport."""
        return self._addr_to_transport.get(addr)

    def get_stats(self) -> dict:
        """获取负载均衡统计信息."""
        with self._lock:
            return {
                "num_transports": len(self.transports),
                "send_strategy": self.send_strategy,
                "recv_strategy": self.recv_strategy,
                "rr_counter": self._rr_counter,
                "active_requests": dict(self._active_requests),
            }


def create_load_balancer(
    transports: list[Transport],
    send_strategy: str | None = None,
    recv_strategy: str | None = None,
) -> TransportLoadBalancer:
    """创建负载均衡器，支持环境变量配置.

    环境变量:
        P2P_LB_SEND_STRATEGY: PUT 操作策略 (default: round_robin)
        P2P_LB_RECV_STRATEGY: GET 操作策略 (default: sticky_hash)

    Args:
        transports: Transport 实例列表
        send_strategy: PUT 策略，None 则从环境变量读取
        recv_strategy: GET 策略，None 则从环境变量读取

    Returns:
        配置好的 TransportLoadBalancer 实例
    """
    if send_strategy is None:
        send_strategy = os.getenv("P2P_LB_SEND_STRATEGY", "random")
    if recv_strategy is None:
        recv_strategy = os.getenv("P2P_LB_RECV_STRATEGY", "sticky_hash")

    return TransportLoadBalancer(
        transports=transports,
        send_strategy=send_strategy,
        recv_strategy=recv_strategy,
    )


__all__ = ["TransportLoadBalancer", "create_load_balancer"]

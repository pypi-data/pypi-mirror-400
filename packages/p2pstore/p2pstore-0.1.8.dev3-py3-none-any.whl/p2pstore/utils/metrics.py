"""
p2pstore 指标收集模块.

提供线程安全的指标收集功能，用于监控 PUT/GET/DELETE/CLEAR 操作，
包括延迟统计、成功率和吞吐量测量。

使用方法:
    from p2pstore.utils import MetricsCollector

    # 创建收集器
    metrics = MetricsCollector(client_id="my_client")

    # 记录操作
    metrics.record_put(success=True, latency=0.05, data_size=1024*1024)
    metrics.record_get(success=True, latency=0.03, data_size=1024*1024)

    # 获取报告
    report = metrics.get_report()
    print(report)

    # 重置（为下一个 step 准备）
    metrics.reset()
"""

from __future__ import annotations

import statistics
import threading
import time
from dataclasses import dataclass, field
from typing import Literal

from .logger import LoggerManager


@dataclass
class OperationStats:
    """单个操作类型的统计数据."""

    count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_bytes: int = 0
    latencies: list[float] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def record(self, success: bool, latency: float, data_size: int = 0) -> None:
        """
        记录单次操作.

        Args:
            success: 操作是否成功.
            latency: 操作延迟（秒）.
            data_size: 数据大小（字节）.
        """
        with self._lock:
            self.count += 1
            if success:
                self.success_count += 1
            else:
                self.failure_count += 1
            self.total_bytes += data_size
            self.latencies.append(latency)

    def reset(self) -> None:
        """重置所有统计数据."""
        with self._lock:
            self.count = 0
            self.success_count = 0
            self.failure_count = 0
            self.total_bytes = 0
            self.latencies.clear()

    def get_stats(self) -> dict:
        """
        获取计算后的统计数据.

        Returns:
            dict: 包含 count, success, failure, success_rate, throughput_mbps,
                  latency_avg/min/max/p50/p95/p99 的字典.
        """
        with self._lock:
            if not self.latencies:
                return {
                    "count": 0,
                    "success": 0,
                    "failure": 0,
                    "success_rate": 0.0,
                    "total_bytes": 0,
                    "throughput_mbps": 0.0,
                    "latency_avg": 0.0,
                    "latency_min": 0.0,
                    "latency_max": 0.0,
                    "latency_p50": 0.0,
                    "latency_p95": 0.0,
                    "latency_p99": 0.0,
                }

            sorted_latencies = sorted(self.latencies)
            n = len(sorted_latencies)
            total_time = sum(sorted_latencies)

            # 计算百分位数索引
            p50_idx = int(n * 0.50)
            p95_idx = int(n * 0.95)
            p99_idx = int(n * 0.99)

            # 吞吐量: total_bytes / total_time (MB/s)
            throughput_mbps = 0.0
            if total_time > 0:
                throughput_mbps = (self.total_bytes / (1024 * 1024)) / total_time

            return {
                "count": self.count,
                "success": self.success_count,
                "failure": self.failure_count,
                "success_rate": (
                    self.success_count / self.count * 100 if self.count > 0 else 0.0
                ),
                "total_bytes": self.total_bytes,
                "throughput_mbps": throughput_mbps,
                "latency_avg": statistics.mean(sorted_latencies),
                "latency_min": sorted_latencies[0],
                "latency_max": sorted_latencies[-1],
                "latency_p50": sorted_latencies[min(p50_idx, n - 1)],
                "latency_p95": sorted_latencies[min(p95_idx, n - 1)],
                "latency_p99": sorted_latencies[min(p99_idx, n - 1)],
            }


class MetricsCollector:
    """
    p2pstore 操作的线程安全指标收集器.

    收集并聚合 PUT、GET、DELETE 和 CLEAR 操作的指标，
    包括延迟百分位数、成功率和吞吐量。

    属性:
        client_id: 客户端标识符（用于日志）.
        start_time: 开始收集指标的时间.

    示例:
        >>> metrics = MetricsCollector(client_id="inference_0")
        >>> metrics.record_put(success=True, latency=0.05, data_size=1024*1024)
        >>> metrics.record_get(success=True, latency=0.03, data_size=1024*1024)
        >>> print(metrics.get_summary())
        >>> metrics.reset()  # 为下一个 step 重置
    """

    def __init__(
        self,
        client_id: str = "default",
        enable_logging: bool = True,
        log_interval: int = 1000,
    ):
        """
        初始化 MetricsCollector.

        Args:
            client_id: 客户端标识符（出现在日志中）.
            enable_logging: 是否定期记录日志.
            log_interval: 每 N 次操作记录一次日志.
        """
        self.client_id = client_id
        self.enable_logging = enable_logging
        self.log_interval = log_interval

        self._put_stats = OperationStats()
        self._get_stats = OperationStats()
        self._delete_stats = OperationStats()
        self._clear_stats = OperationStats()
        self._cache_all_stats = OperationStats()

        self._start_time = time.time()
        self._total_ops = 0
        self._lock = threading.Lock()

        self.logger = LoggerManager.get_logger("metrics")

    def record_put(
        self, success: bool, latency: float, data_size: int = 0, key: str = ""
    ) -> None:
        """
        记录 PUT 操作.

        Args:
            success: 操作是否成功.
            latency: 操作延迟（秒）.
            data_size: 数据大小（字节）.
            key: PUT 的 key（用于详细日志）.
        """
        self._put_stats.record(success, latency, data_size)
        self._increment_total_ops()

        if not success and self.enable_logging:
            self.logger.warning(
                "[METRICS] PUT 失败: client=%s, key=%s, latency=%.3fs",
                self.client_id,
                key,
                latency,
            )

    def record_get(
        self, success: bool, latency: float, data_size: int = 0, key: str = ""
    ) -> None:
        """
        记录 GET 操作.

        Args:
            success: 操作是否成功.
            latency: 操作延迟（秒）.
            data_size: 数据大小（字节）.
            key: GET 的 key（用于详细日志）.
        """
        self._get_stats.record(success, latency, data_size)
        self._increment_total_ops()

        if not success and self.enable_logging:
            self.logger.error(
                "[METRICS] GET 失败: client=%s, key=%s, latency=%.3fs",
                self.client_id,
                key,
                latency,
            )

    def record_delete(self, success: bool, latency: float, key: str = "") -> None:
        """
        记录 DELETE 操作.

        Args:
            success: 操作是否成功.
            latency: 操作延迟（秒）.
            key: 删除的 key.
        """
        self._delete_stats.record(success, latency, 0)
        self._increment_total_ops()

    def record_clear(
        self, success: bool, latency: float, cleared_count: int = 0
    ) -> None:
        """
        记录 CLEAR 操作.

        Args:
            success: 操作是否成功.
            latency: 操作延迟（秒）.
            cleared_count: 清除的 key 数量.
        """
        self._clear_stats.record(success, latency, cleared_count)
        self._increment_total_ops()

        if self.enable_logging:
            self.logger.info(
                "[METRICS] CLEAR: client=%s, success=%s, cleared=%d, latency=%.3fs",
                self.client_id,
                success,
                cleared_count,
                latency,
            )

    def record_cache_all(
        self,
        success: bool,
        latency: float,
        total_keys: int = 0,
        success_count: int = 0,
        failed_count: int = 0,
    ) -> None:
        """
        记录 cache_all 操作.

        Args:
            success: 整体操作是否成功.
            latency: 总操作延迟（秒）.
            total_keys: 处理的总 key 数量.
            success_count: 成功下载的数量.
            failed_count: 失败下载的数量.
        """
        self._cache_all_stats.record(success, latency, total_keys)

        if self.enable_logging:
            self.logger.info(
                "[METRICS] CACHE_ALL: client=%s, success=%s, total=%d, "
                "downloaded=%d, failed=%d, latency=%.3fs",
                self.client_id,
                success,
                total_keys,
                success_count,
                failed_count,
                latency,
            )

    def _increment_total_ops(self) -> None:
        """递增总操作数并定期记录日志."""
        with self._lock:
            self._total_ops += 1
            if self.enable_logging and self._total_ops % self.log_interval == 0:
                self._log_periodic_stats()

    def _log_periodic_stats(self) -> None:
        """记录周期性统计数据."""
        elapsed = time.time() - self._start_time
        ops_per_sec = self._total_ops / elapsed if elapsed > 0 else 0

        put_stats = self._put_stats.get_stats()
        get_stats = self._get_stats.get_stats()

        self.logger.info(
            "[METRICS] client=%s | ops=%d | elapsed=%.1fs | ops/s=%.1f | "
            "PUT(ok=%d,fail=%d,avg=%.3fs) | GET(ok=%d,fail=%d,avg=%.3fs)",
            self.client_id,
            self._total_ops,
            elapsed,
            ops_per_sec,
            put_stats["success"],
            put_stats["failure"],
            put_stats["latency_avg"],
            get_stats["success"],
            get_stats["failure"],
            get_stats["latency_avg"],
        )

    def get_report(self) -> dict:
        """
        获取完整的指标报告.

        Returns:
            dict: 包含所有操作统计数据的完整指标报告.
        """
        elapsed = time.time() - self._start_time

        return {
            "client_id": self.client_id,
            "elapsed_seconds": elapsed,
            "total_operations": self._total_ops,
            "operations_per_second": self._total_ops / elapsed if elapsed > 0 else 0,
            "put": self._put_stats.get_stats(),
            "get": self._get_stats.get_stats(),
            "delete": self._delete_stats.get_stats(),
            "clear": self._clear_stats.get_stats(),
            "cache_all": self._cache_all_stats.get_stats(),
        }

    def get_summary(self) -> str:
        """
        获取人类可读的指标摘要.

        Returns:
            str: 格式化的摘要字符串.
        """
        report = self.get_report()
        put = report["put"]
        get = report["get"]

        lines = [
            f"=== 指标摘要 (client={self.client_id}) ===",
            f"耗时: {report['elapsed_seconds']:.2f}s | 总操作数: {report['total_operations']}",
            "",
            "PUT 操作:",
            f"  数量: {put['count']} (成功={put['success']}, 失败={put['failure']})",
            f"  成功率: {put['success_rate']:.2f}%",
            f"  吞吐量: {put['throughput_mbps']:.2f} MB/s",
            f"  延迟: avg={put['latency_avg']*1000:.2f}ms, "
            f"p50={put['latency_p50']*1000:.2f}ms, "
            f"p95={put['latency_p95']*1000:.2f}ms, "
            f"p99={put['latency_p99']*1000:.2f}ms",
            "",
            "GET 操作:",
            f"  数量: {get['count']} (成功={get['success']}, 失败={get['failure']})",
            f"  成功率: {get['success_rate']:.2f}%",
            f"  吞吐量: {get['throughput_mbps']:.2f} MB/s",
            f"  延迟: avg={get['latency_avg']*1000:.2f}ms, "
            f"p50={get['latency_p50']*1000:.2f}ms, "
            f"p95={get['latency_p95']*1000:.2f}ms, "
            f"p99={get['latency_p99']*1000:.2f}ms",
        ]

        return "\n".join(lines)

    def reset(self) -> None:
        """重置所有指标，为新的收集周期做准备."""
        self._put_stats.reset()
        self._get_stats.reset()
        self._delete_stats.reset()
        self._clear_stats.reset()
        self._cache_all_stats.reset()

        with self._lock:
            self._start_time = time.time()
            self._total_ops = 0

        if self.enable_logging:
            self.logger.info("[METRICS] 重置: client=%s", self.client_id)

    def get_put_success_rate(self) -> float:
        """获取 PUT 操作成功率 (0-100)."""
        stats = self._put_stats.get_stats()
        return stats["success_rate"]

    def get_get_success_rate(self) -> float:
        """获取 GET 操作成功率 (0-100)."""
        stats = self._get_stats.get_stats()
        return stats["success_rate"]

    def has_failures(self) -> bool:
        """检查是否有任何操作失败."""
        put = self._put_stats.get_stats()
        get = self._get_stats.get_stats()
        delete = self._delete_stats.get_stats()
        clear = self._clear_stats.get_stats()

        return (
            put["failure"] > 0
            or get["failure"] > 0
            or delete["failure"] > 0
            or clear["failure"] > 0
        )

    def assert_no_failures(
        self, operation: Literal["put", "get", "all"] = "all"
    ) -> None:
        """
        断言没有失败发生.

        Args:
            operation: 要检查的操作类型 ("put", "get", 或 "all").

        Raises:
            AssertionError: 如果检测到任何失败.
        """
        if operation in ("put", "all"):
            put = self._put_stats.get_stats()
            if put["failure"] > 0:
                raise AssertionError(
                    f"检测到 PUT 失败: {put['failure']}/{put['count']}"
                )

        if operation in ("get", "all"):
            get = self._get_stats.get_stats()
            if get["failure"] > 0:
                raise AssertionError(
                    f"检测到 GET 失败: {get['failure']}/{get['count']}"
                )


# 全局指标实例（方便使用）
_global_metrics: MetricsCollector | None = None
_global_lock = threading.Lock()


def get_global_metrics(client_id: str = "global") -> MetricsCollector:
    """
    获取或创建全局 MetricsCollector 实例.

    Args:
        client_id: 创建新实例时使用的客户端 ID.

    Returns:
        MetricsCollector: 全局指标实例.
    """
    global _global_metrics
    with _global_lock:
        if _global_metrics is None:
            _global_metrics = MetricsCollector(client_id=client_id)
        return _global_metrics


def reset_global_metrics() -> None:
    """重置全局指标实例."""
    global _global_metrics
    with _global_lock:
        if _global_metrics is not None:
            _global_metrics.reset()

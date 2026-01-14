"""
监控 Metrics Hooks

这个模块提供了监控回调机制，让使用者可以集成到自己的监控系统
（Prometheus, Datadog, CloudWatch 等）

使用示例：
    from skill_scheduler.metrics import MetricsCallback, register_callback

    # 自定义监控回调
    class MyMetrics(MetricsCallback):
        def on_skill_start(self, skill_name, params):
            # 发送到你的监控系统
            prometheus_counter.inc()

        def on_skill_complete(self, skill_name, duration, success):
            if success:
                prometheus_histogram.observe(duration)

    # 注册回调
    register_callback(MyMetrics())
"""
import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionMetrics:
    """单次执行指标"""
    skill_name: str
    start_time: float
    end_time: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """执行时长（秒）"""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None


class MetricsCallback:
    """
    监控回调基类

    子类可以重写这些方法来集成到自己的监控系统
    """

    def on_skill_start(self, skill_name: str, params: Dict[str, Any]) -> None:
        """
        技能开始执行时调用

        Args:
            skill_name: 技能名称
            params: 输入参数
        """
        pass

    def on_skill_complete(
        self,
        skill_name: str,
        duration: float,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """
        技能执行完成时调用

        Args:
            skill_name: 技能名称
            duration: 执行时长（秒）
            success: 是否成功
            error_message: 错误消息（如果失败）
        """
        pass

    def on_skill_error(self, skill_name: str, error: Exception) -> None:
        """
        技能执行出错时调用

        Args:
            skill_name: 技能名称
            error: 异常对象
        """
        pass

    def on_llm_request(self, model: str, prompt_tokens: int) -> None:
        """
        LLM 请求开始时调用

        Args:
            model: 模型名称
            prompt_tokens: 提示词 token 数
        """
        pass

    def on_llm_response(
        self,
        model: str,
        duration: float,
        total_tokens: int,
        cost: Optional[float] = None
    ) -> None:
        """
        LLM 响应返回时调用

        Args:
            model: 模型名称
            duration: 请求时长（秒）
            total_tokens: 总 token 数
            cost: 成本（美元）
        """
        pass


class MetricsRegistry:
    """
    指标注册中心

    管理所有的监控回调，提供线程安全的调用机制
    """

    def __init__(self):
        self._callbacks: List[MetricsCallback] = []
        self._lock = threading.Lock()
        self._current_executions: Dict[int, ExecutionMetrics] = {}
        self._execution_counter = 0
        self._counter_lock = threading.Lock()

    def register(self, callback: MetricsCallback) -> None:
        """注册监控回调"""
        with self._lock:
            self._callbacks.append(callback)

    def unregister(self, callback: MetricsCallback) -> None:
        """取消注册监控回调"""
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

    def clear(self) -> None:
        """清除所有回调"""
        with self._lock:
            self._callbacks.clear()

    def notify_skill_start(
        self,
        skill_name: str,
        params: Dict[str, Any]
    ) -> int:
        """
        通知技能开始执行

        Returns:
            execution_id: 执行ID，用于后续匹配
        """
        # 生成执行ID
        with self._counter_lock:
            self._execution_counter += 1
            execution_id = self._execution_counter

        # 记录执行指标
        metrics = ExecutionMetrics(
            skill_name=skill_name,
            start_time=time.time(),
            params=params
        )
        self._current_executions[execution_id] = metrics

        # 通知所有回调
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback.on_skill_start(skill_name, params)
                except Exception as e:
                    # 回调出错不应影响主流程
                    print(f"Metrics callback error: {e}")

        return execution_id

    def notify_skill_complete(
        self,
        execution_id: int,
        success: bool,
        error_message: Optional[str] = None
    ) -> Optional[ExecutionMetrics]:
        """
        通知技能执行完成

        Returns:
            ExecutionMetrics: 完整的执行指标
        """
        if execution_id not in self._current_executions:
            return None

        metrics = self._current_executions.pop(execution_id)
        metrics.end_time = time.time()
        metrics.success = success
        metrics.error_message = error_message

        # 通知所有回调
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback.on_skill_complete(
                        skill_name=metrics.skill_name,
                        duration=metrics.duration,
                        success=success,
                        error_message=error_message
                    )
                except Exception as e:
                    print(f"Metrics callback error: {e}")

        return metrics

    def notify_skill_error(
        self,
        execution_id: int,
        error: Exception
    ) -> None:
        """通知技能执行出错"""
        if execution_id not in self._current_executions:
            return

        metrics = self._current_executions[execution_id]
        metrics.end_time = time.time()
        metrics.success = False
        metrics.error_message = str(error)

        # 通知所有回调
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback.on_skill_error(metrics.skill_name, error)
                except Exception as e:
                    print(f"Metrics callback error: {e}")

    def notify_llm_request(
        self,
        model: str,
        prompt_tokens: int
    ) -> None:
        """通知 LLM 请求"""
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback.on_llm_request(model, prompt_tokens)
                except Exception as e:
                    print(f"Metrics callback error: {e}")

    def notify_llm_response(
        self,
        model: str,
        duration: float,
        total_tokens: int,
        cost: Optional[float] = None
    ) -> None:
        """通知 LLM 响应"""
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback.on_llm_response(model, duration, total_tokens, cost)
                except Exception as e:
                    print(f"Metrics callback error: {e}")


# 全局指标注册中心
_global_registry = MetricsRegistry()


def register_callback(callback: MetricsCallback) -> None:
    """注册监控回调到全局注册中心"""
    _global_registry.register(callback)


def unregister_callback(callback: MetricsCallback) -> None:
    """从全局注册中心取消注册"""
    _global_registry.unregister(callback)


def get_registry() -> MetricsRegistry:
    """获取全局指标注册中心"""
    return _global_registry


# ========== 内置实现示例 ==========

class ConsoleMetricsCallback(MetricsCallback):
    """
    控制台输出监控回调（用于调试）

    输出示例：
        [METRICS] Skill text-process started
        [METRICS] Skill text-process completed in 0.52s
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def on_skill_start(self, skill_name: str, params: Dict[str, Any]) -> None:
        if self.enabled:
            print(f"[METRICS] Skill {skill_name} started")

    def on_skill_complete(
        self,
        skill_name: str,
        duration: float,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        if self.enabled:
            status = "✓" if success else "✗"
            print(f"[METRICS] Skill {skill_name} {status} completed in {duration:.2f}s")
            if error_message:
                print(f"[METRICS] Error: {error_message}")


class InMemoryMetricsCallback(MetricsCallback):
    """
    内存中的监控回调（用于测试和简单场景）

    属性:
        executions: 执行历史列表
        llm_requests: LLM 请求列表
    """

    def __init__(self):
        self.executions: List[ExecutionMetrics] = []
        self.llm_requests: List[Dict[str, Any]] = []

    def on_skill_complete(
        self,
        skill_name: str,
        duration: float,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        self.executions.append({
            "skill_name": skill_name,
            "duration": duration,
            "success": success,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })

    def on_llm_response(
        self,
        model: str,
        duration: float,
        total_tokens: int,
        cost: Optional[float] = None
    ) -> None:
        self.llm_requests.append({
            "model": model,
            "duration": duration,
            "total_tokens": total_tokens,
            "cost": cost,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_success_rate(self, skill_name: Optional[str] = None) -> float:
        """获取成功率"""
        if not self.executions:
            return 0.0

        executions = self.executions
        if skill_name:
            executions = [e for e in executions if e["skill_name"] == skill_name]

        successful = sum(1 for e in executions if e["success"])
        return successful / len(executions) if executions else 0.0

    def get_average_duration(self, skill_name: Optional[str] = None) -> float:
        """获取平均执行时长"""
        if not self.executions:
            return 0.0

        executions = self.executions
        if skill_name:
            executions = [e for e in executions if e["skill_name"] == skill_name]

        durations = [e["duration"] for e in executions]
        return sum(durations) / len(durations) if durations else 0.0

    def get_total_count(self) -> int:
        """获取总执行次数"""
        return len(self.executions)

    def get_success_count(self) -> int:
        """获取成功执行次数"""
        return sum(1 for e in self.executions if e["success"])

    def get_failure_count(self) -> int:
        """获取失败执行次数"""
        return sum(1 for e in self.executions if not e["success"])


# Prometheus 集成示例（需要 prometheus_client 库）
class PrometheusMetricsCallback(MetricsCallback):
    """
    Prometheus 监控回调

    使用示例：
        pip install prometheus_client

        callback = PrometheusMetricsCallback()
        register_callback(callback)

        # 启动 metrics HTTP 服务器
        from prometheus_client import start_http_server
        start_http_server(9090)
    """

    def __init__(self):
        try:
            from prometheus_client import Counter, Histogram, Summary

            # 定义指标
            self.skill_executions = Counter(
                'skill_executions_total',
                'Total number of skill executions',
                ['skill_name', 'status']
            )

            self.skill_duration = Histogram(
                'skill_duration_seconds',
                'Skill execution duration in seconds',
                ['skill_name']
            )

            self.llm_requests = Counter(
                'llm_requests_total',
                'Total number of LLM requests',
                ['model']
            )

            self.llm_tokens = Summary(
                'llm_tokens_total',
                'Total LLM tokens used',
                ['model']
            )

            self._enabled = True
        except ImportError:
            print("Warning: prometheus_client not installed. Install with: pip install prometheus_client")
            self._enabled = False

    def on_skill_complete(
        self,
        skill_name: str,
        duration: float,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        if not self._enabled:
            return

        status = "success" if success else "error"
        self.skill_executions.labels(skill_name=skill_name, status=status).inc()
        self.skill_duration.labels(skill_name=skill_name).observe(duration)

    def on_llm_response(
        self,
        model: str,
        duration: float,
        total_tokens: int,
        cost: Optional[float] = None
    ) -> None:
        if not self._enabled:
            return

        self.llm_requests.labels(model=model).inc()
        self.llm_tokens.labels(model=model).observe(total_tokens)

"""日志接口定义

使用 Protocol 定义日志接口，支持鸭子类型和类型检查。
任何实现了这些方法的对象都可以作为 Logger 使用。

v3.38.2: 新增，替代 loguru 实现 structlog
v3.38.4: 添加异步方法签名（ainfo, adebug 等）
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Logger(Protocol):
    """日志接口

    定义 structlog.BoundLogger 的核心方法签名，用于类型注解。

    使用 Protocol 而非 ABC 的好处：
    1. 支持鸭子类型 - structlog.BoundLogger 自动满足接口
    2. 不需要继承 - 解耦具体实现
    3. 类型检查 - mypy/pyright 可以验证类型

    Example:
        >>> def process_order(logger: Logger, order_id: int):
        ...     logger.info("处理订单", order_id=order_id)

    Note:
        日志级别由消息性质决定（debug/info/warning/error），
        全局 logging.level 配置控制显示过滤。
    """

    def debug(self, event: str, **kwargs: Any) -> None:
        """记录 DEBUG 级别日志

        Args:
            event: 事件描述（如 "用户登录", "订单创建"）
            **kwargs: 结构化字段（如 user_id=123, order_id=456）
        """
        ...

    def info(self, event: str, **kwargs: Any) -> None:
        """记录 INFO 级别日志"""
        ...

    def warning(self, event: str, **kwargs: Any) -> None:
        """记录 WARNING 级别日志"""
        ...

    def error(self, event: str, **kwargs: Any) -> None:
        """记录 ERROR 级别日志"""
        ...

    def critical(self, event: str, **kwargs: Any) -> None:
        """记录 CRITICAL 级别日志"""
        ...

    def exception(self, event: str, **kwargs: Any) -> None:
        """记录异常日志（自动包含堆栈）"""
        ...

    def bind(self, **kwargs: Any) -> "Logger":
        """绑定上下文字段

        Args:
            **kwargs: 要绑定的上下文字段

        Returns:
            绑定了上下文的新 Logger 实例

        Example:
            >>> logger = get_logger(__name__)
            >>> request_logger = logger.bind(request_id="abc123", user_id=456)
            >>> request_logger.info("订单创建", order_id=789)
            # 输出包含 request_id、user_id、order_id
        """
        ...

    def unbind(self, *keys: str) -> "Logger":
        """解除上下文字段绑定

        Args:
            *keys: 要解除绑定的字段名

        Returns:
            解除绑定后的新 Logger 实例
        """
        ...

    def try_unbind(self, *keys: str) -> "Logger":
        """尝试解除上下文字段绑定（如果不存在则忽略）

        Args:
            *keys: 要解除绑定的字段名

        Returns:
            解除绑定后的新 Logger 实例
        """
        ...


@runtime_checkable
class AsyncLogger(Protocol):
    """异步日志接口

    提供非阻塞的日志方法，在独立线程池中执行。
    适用于高并发异步应用，避免日志 I/O 阻塞主协程。

    structlog 的 BoundLogger 已经实现了这些方法（以 a 前缀开头）。

    Example:
        >>> async def handle_request(logger: AsyncLogger):
        ...     await logger.ainfo("处理请求", request_id="abc123")

    Note:
        异步方法会增加每条日志的计算开销，但不会阻塞应用。
        适用于 I/O 密集型或需要 JSON 序列化大量数据的场景。
    """

    async def adebug(self, event: str, **kwargs: Any) -> None:
        """异步记录 DEBUG 级别日志"""
        ...

    async def ainfo(self, event: str, **kwargs: Any) -> None:
        """异步记录 INFO 级别日志"""
        ...

    async def awarning(self, event: str, **kwargs: Any) -> None:
        """异步记录 WARNING 级别日志"""
        ...

    async def aerror(self, event: str, **kwargs: Any) -> None:
        """异步记录 ERROR 级别日志"""
        ...

    async def acritical(self, event: str, **kwargs: Any) -> None:
        """异步记录 CRITICAL 级别日志"""
        ...

    async def aexception(self, event: str, **kwargs: Any) -> None:
        """异步记录异常日志（自动包含堆栈）"""
        ...

    def bind(self, **kwargs: Any) -> "AsyncLogger":
        """绑定上下文字段"""
        ...

    def unbind(self, *keys: str) -> "AsyncLogger":
        """解除上下文字段绑定"""
        ...


__all__ = ["Logger", "AsyncLogger"]

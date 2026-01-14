"""Logger 适配器 - 将 Component.log 方法适配为标准 logger 接口."""

from typing import Any, Callable


class ComponentLoggerAdapter:
    """将 Component.log 方法适配为标准 logger 对象.

    这个适配器允许将 Component 的 log 方法（接受 level 和 message 参数）
    转换为标准的 logger 接口（info(), debug(), error() 等方法）。

    这样可以让需要标准 logger 接口的模块（如 LLMManager）使用 Component 的日志系统，
    从而实现日志推送到 RabbitMQ 的功能。

    Example:
        >>> component = MyComponent()
        >>> logger = ComponentLoggerAdapter(component.log)
        >>> logger.info("这是一条信息")
        >>> logger.error("这是一条错误", error_type="ValueError")
    """

    def __init__(self, log_method: Callable[[str, str], None]):
        """初始化适配器.

        Args:
            log_method: Component 的 log 方法，签名为 log(level: str, message: str, **extra)
        """
        self._log = log_method

    def debug(self, message: str, **kwargs: Any) -> None:
        """记录 DEBUG 级别日志.

        Args:
            message: 日志消息
            **kwargs: 额外的日志字段
        """
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """记录 INFO 级别日志.

        Args:
            message: 日志消息
            **kwargs: 额外的日志字段
        """
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """记录 WARNING 级别日志.

        Args:
            message: 日志消息
            **kwargs: 额外的日志字段
        """
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """记录 ERROR 级别日志.

        Args:
            message: 日志消息
            **kwargs: 额外的日志字段
        """
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """记录 CRITICAL 级别日志.

        Args:
            message: 日志消息
            **kwargs: 额外的日志字段
        """
        self._log("CRITICAL", message, **kwargs)

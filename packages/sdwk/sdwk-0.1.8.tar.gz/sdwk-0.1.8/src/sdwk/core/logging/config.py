"""日志配置加载模块

从平台 API 动态获取 RabbitMQ 日志配置。
"""

import os
from typing import Any

from loguru import logger


def load_logging_config() -> dict[str, Any]:
    """加载日志配置

    从平台 API 动态获取 RabbitMQ 配置（使用缓存）。

    Returns:
        日志配置字典，包含以下字段：
        - enabled: 是否启用 RabbitMQ 日志
        - rabbitmq_host: RabbitMQ 服务器地址
        - rabbitmq_port: RabbitMQ 端口
        - rabbitmq_user: RabbitMQ 用户名
        - rabbitmq_password: RabbitMQ 密码
        - enable_local_log: 是否启用本地日志

    """
    try:
        # 导入配置缓存和项目设置
        from ..config_cache import get_sdk_settings
        from ..project_settings import settings

        # 从配置中获取本地日志开关
        enable_local_log = settings.get("logging.enable_local_log", True)

        # 从缓存获取平台配置
        settings_config = get_sdk_settings()

        # 如果没有获取到配置，返回默认配置
        if not settings_config:
            logger.warning("未获取到平台配置，RabbitMQ 日志功能将被禁用")
            return _get_default_config(enable_local_log=enable_local_log)

        # 提取 RabbitMQ 配置
        rabbitmq_config = settings_config.get("rabbitmq", {})

        # 构建日志配置
        logging_config = {
            "enabled": rabbitmq_config.get("enabled", False),
            "rabbitmq_host": rabbitmq_config.get("host"),
            "rabbitmq_port": rabbitmq_config.get("port", 5672),
            "rabbitmq_user": rabbitmq_config.get("user", "guest"),
            "rabbitmq_password": rabbitmq_config.get("password", "guest"),
            "rabbitmq_exchange": rabbitmq_config.get("exchange", "logs_exchange"),
            "enable_local_log": enable_local_log,
        }

        if logging_config["enabled"]:
            logger.info(f"已从平台获取 RabbitMQ 配置: {rabbitmq_config.get('host')}:{rabbitmq_config.get('port')}")

        return logging_config

    except Exception as e:
        # 配置加载失败，返回默认配置
        logger.warning(f"加载日志配置失败: {e}，使用默认配置")
        return _get_default_config()


def _get_default_config(enable_local_log: bool = True) -> dict[str, Any]:
    """获取默认配置

    Args:
        enable_local_log: 是否启用本地日志

    Returns:
        默认日志配置
    """
    return {
        "enabled": False,
        "rabbitmq_host": None,
        "rabbitmq_port": 5672,
        "rabbitmq_user": "guest",
        "rabbitmq_password": "guest",
        "enable_local_log": enable_local_log,
    }
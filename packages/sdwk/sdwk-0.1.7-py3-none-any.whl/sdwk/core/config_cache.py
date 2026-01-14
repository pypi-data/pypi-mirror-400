"""全局配置缓存模块

统一管理平台配置的获取和缓存,避免重复调用平台接口。
"""

import os
import threading
from typing import Any

from loguru import logger


class ConfigCache:
    """配置缓存单例类

    提供线程安全的配置缓存机制,确保平台配置只获取一次。
    """

    _instance = None
    _lock = threading.Lock()
    _config_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化配置缓存"""
        if self._initialized:
            return

        self._sdk_settings: dict[str, Any] | None = None
        self._load_attempted = False
        self._initialized = True

    def get_sdk_settings(self, force_reload: bool = False) -> dict[str, Any]:
        """获取 SDK 配置

        从平台获取配置并缓存。如果已经加载过,直接返回缓存的配置。

        Args:
            force_reload: 是否强制重新加载配置

        Returns:
            SDK 配置字典,包含:
            - rabbitmq: RabbitMQ 配置
            - output_path: 成果物输出路径

        Raises:
            Exception: 当配置加载失败时
        """
        # 如果已经有缓存且不强制重新加载,直接返回
        if self._sdk_settings is not None and not force_reload:
            return self._sdk_settings

        # 如果已经尝试加载过但失败了,且不强制重新加载,返回空配置
        if self._load_attempted and self._sdk_settings is None and not force_reload:
            return {}

        # 使用锁确保只有一个线程执行加载
        with self._config_lock:
            # 双重检查,避免重复加载
            if self._sdk_settings is not None and not force_reload:
                return self._sdk_settings

            try:
                self._sdk_settings = self._load_from_platform()
                self._load_attempted = True
                logger.info("已从平台加载 SDK 配置并缓存")
                return self._sdk_settings
            except Exception as e:
                self._load_attempted = True
                logger.warning(f"从平台加载配置失败: {e}")
                # 返回空配置而不是抛出异常,让调用方使用默认值
                return {}

    def _load_from_platform(self) -> dict[str, Any]:
        """从平台加载配置

        Returns:
            配置字典

        Raises:
            Exception: 当加载失败时
        """
        from .platform_client import PlatformClient
        from .project_settings import settings

        # 获取平台地址
        platform_url = settings.get("platform.url") or os.getenv("SDWK_PLATFORM_URL")
        if not platform_url:
            raise ValueError("未配置平台地址")

        # 获取平台 token
        platform_token = os.getenv("SDWK_PLATFORM_TOKEN")

        # 调用平台 API
        with PlatformClient(platform_url, platform_token) as client:
            config = client.get_sdk_settings()

        return config

    def get_rabbitmq_config(self) -> dict[str, Any]:
        """获取 RabbitMQ 配置

        Returns:
            RabbitMQ 配置字典
        """
        settings = self.get_sdk_settings()
        return settings.get("rabbitmq", )

    def get_output_path(self) -> str | None:
        """获取成果物输出路径

        Returns:
            输出路径,如果未配置则返回 None
        """
        settings = self.get_sdk_settings()
        return settings.get("output_path")

    def clear_cache(self):
        """清除缓存

        用于测试或需要重新加载配置的场景。
        """
        with self._config_lock:
            self._sdk_settings = None
            self._load_attempted = False
            logger.debug("配置缓存已清除")


# 全局单例实例
_config_cache = ConfigCache()


def get_sdk_settings(force_reload: bool = False) -> dict[str, Any]:
    """获取 SDK 配置(便捷函数)

    Args:
        force_reload: 是否强制重新加载配置

    Returns:
        SDK 配置字典
    """
    return _config_cache.get_sdk_settings(force_reload)


def get_rabbitmq_config() -> dict[str, Any]:
    """获取 RabbitMQ 配置(便捷函数)

    Returns:
        RabbitMQ 配置字典
    """
    return _config_cache.get_rabbitmq_config()


def get_output_path() -> str | None:
    """获取成果物输出路径(便捷函数)

    Returns:
        输出路径
    """
    return _config_cache.get_output_path()


def clear_config_cache():
    """清除配置缓存(便捷函数)"""
    _config_cache.clear_cache()

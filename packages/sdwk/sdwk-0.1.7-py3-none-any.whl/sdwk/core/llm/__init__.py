"""LLM 大模型调用模块.

提供统一的大模型调用接口,从平台动态获取配置。
"""

from .llm_manager import LLMManager
from .llm_service import LLMService

__all__ = ["LLMManager", "LLMService"]

"""LLM管理器模块.

提供大语言模型的统一管理接口,从平台获取配置。
"""

import os
from typing import Any

from langchain_openai import ChatOpenAI
from loguru import logger as default_logger
from openai import AsyncOpenAI

from ..platform_client import PlatformClient
from ..project_settings import settings


class LLMManager:
    """大语言模型管理器.

    从平台动态获取 LLM 配置,支持多模型切换。
    """

    def __init__(self, logger=None):
        """初始化LLM管理器.

        Args:
            logger: 自定义日志记录器,如果为 None 则使用默认的 loguru logger
                   可以传入组件的 self.log 来推送日志到消息队列
        """
        self.logger = logger if logger is not None else default_logger
        self._config = None
        self._load_config()

    def _load_config(self):
        """从平台加载 LLM 配置."""
        try:
            # 获取平台地址
            platform_url = settings.get("platform.url") or os.getenv("SDWK_PLATFORM_URL")
            if not platform_url:
                raise ValueError("未配置平台地址,请设置 SDWK_PLATFORM_URL 环境变量")

            # 获取平台 token (从环境变量获取 sdw-api-key)
            platform_token = os.getenv("SDWK_PLATFORM_TOKEN")
            if not platform_token:
                raise ValueError("未配置平台 Token,请设置 SDWK_PLATFORM_TOKEN 环境变量")

            # 调用平台 API 获取 LLM 配置
            self.logger.info(f"正在从平台获取 LLM 配置: {platform_url}")
            with PlatformClient(platform_url, platform_token) as client:
                self._config = client.get_llm_api_keys()

            self.logger.info("成功从平台加载 LLM 配置")
            self.logger.debug(f"LLM 配置: {self._config}")

        except Exception as e:
            self.logger.error(f"从平台加载 LLM 配置失败: {e}")
            raise

    @property
    def config(self) -> dict[str, Any]:
        """获取配置."""
        if self._config is None:
            self._load_config()
        return self._config

    @property
    def api_key(self) -> str:
        """获取 API Key."""
        return self.config.get("api_key", "")

    @property
    def base_url(self) -> str:
        """获取 API Base URL."""
        return self.config.get("api_base", "")

    @property
    def current_model_name(self) -> str:
        """获取当前模型名称."""
        return self.config.get("model_name", "")

    @property
    def current_model_config(self) -> dict[str, Any] | None:
        """获取当前模型配置."""
        model_name = self.current_model_name
        if model_name:
            return self.config.get(model_name)
        return None

    @property
    def models(self) -> list[str]:
        """获取可用模型列表."""
        return self.get_available_models()

    def set_current_model(self, model_name: str):
        """设置当前使用的模型.

        Args:
            model_name: 模型名称

        Raises:
            ValueError: 当模型不存在时
        """
        self.logger.debug(f"尝试设置模型: {model_name}")
        available_models = self.get_available_models()
        if model_name not in available_models:
            raise ValueError(f"未找到模型: {model_name}, 可用模型: {available_models}")

        # 更新配置中的默认模型
        self._config["default_model"] = model_name
        self.logger.info(f"当前使用模型切换为: {model_name}")

    def get_available_models(self) -> list[str]:
        """获取可用的模型列表.

        Returns:
            list: 可用模型名称列表
        """
        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = httpx.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=30.0,
                follow_redirects=True,
            )

            if response.status_code == 200:
                data = response.json()
                models = [item.get("id") for item in data.get("data", [])]

                # 将默认模型放在第一个
                default_model = self.config.get("default_model")
                if default_model and default_model in models:
                    models.remove(default_model)
                    models.insert(0, default_model)

                self.logger.debug(f"可用模型: {models}")
                return models
            else:
                self.logger.warning(f"获取模型列表失败,状态码: {response.status_code}")
                return []

        except Exception as e:
            self.logger.warning(f"获取模型列表失败: {e}")
            return []

    def get_current_model_name(self) -> str:
        """获取当前模型名称."""
        return self.current_model_name

    def get_model(self, model_name: str = "") -> ChatOpenAI:
        """获取指定模型.

        Args:
            model_name: 模型名称,如果为空则使用默认模型

        Returns:
            ChatOpenAI: LangChain ChatOpenAI 实例

        Raises:
            Exception: 当无可用模型时
        """
        model_names = self.get_available_models()
        if not model_names:
            # 如果无法获取模型列表,使用配置中的默认模型
            model_name = model_name or self.current_model_name
            if not model_name:
                raise Exception("当前无可用模型")
        else:
            if not model_name:
                model_name = self.current_model_name
            if model_name not in model_names:
                self.logger.warning(f"选择的模型 {model_name} 不存在,使用第一个可用模型")
                model_name = model_names[0]

        self.logger.info(f"当前使用模型: {model_name}")
        return ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=model_name,
        )

    def get_model_extra_config(self) -> dict[str, Any]:
        """获取模型的额外配置参数 (温度、max_tokens 等).

        Returns:
            dict: 额外配置参数
        """
        config = self.current_model_config
        extra_params = {}
        if config:
            for param in [
                "max_tokens",
                "temperature",
                "presence_penalty",
                "top_p",
                "frequency_penalty",
            ]:
                if param in config:
                    extra_params[param] = config[param]
        return extra_params

    async def call_current_model(self, user_message: str, prompt: str) -> str:
        """调用当前模型.

        Args:
            user_message: 用户消息
            prompt: 系统提示词

        Returns:
            str: 模型响应内容

        Raises:
            ValueError: 当未选择模型时
        """
        if not self.current_model_name:
            raise ValueError("当前未选择任何模型")

        self.logger.debug(f"创建 AsyncOpenAI 客户端: base_url={self.base_url}")
        client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

        model_or_deployment = self.current_model_name
        if not model_or_deployment:
            raise ValueError("缺少 model 配置")

        self.logger.debug(f"使用模型: {model_or_deployment}")

        # 准备参数
        extra_params = self.get_model_extra_config()
        self.logger.debug(f"额外参数: {extra_params}")

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message},
        ]
        self.logger.debug(f"消息: {messages}")

        try:
            self.logger.debug("发送请求到模型...")
            response = await client.chat.completions.create(
                model=model_or_deployment,
                messages=messages,
                **extra_params
            )
            self.logger.debug(f"原始响应: {response}")
            content = response.choices[0].message.content
            self.logger.debug(f"提取的内容: {content}")
            return content
        except Exception as e:
            self.logger.error(f"调用模型失败: {e}")
            raise

"""通用大模型服务.

封装 LLMManager 提供统一的 LLM 调用接口。
"""

import asyncio
import base64
from collections.abc import Generator
import json
import mimetypes
from pathlib import Path
from typing import Any, Literal

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from loguru import logger as default_logger
from openai import OpenAI
from pydantic import BaseModel

from ..logging import ComponentLoggerAdapter
from .llm_manager import LLMManager


class LLMService:
    """通用大模型服务."""

    def __init__(self, language_prompt_template: str = "", logger=None):
        """初始化LLM服务.

        Args:
            language_prompt_template: 语言提示词模板,支持 {{lang}} 占位符
            logger: 自定义日志记录器,如果为 None 则使用默认的 loguru logger
                   可以传入组件的 self.log 方法,会自动适配为标准 logger 接口
        """
        # 如果 logger 是一个可调用对象（如 Component.log 方法），则使用适配器
        if logger is not None and callable(logger):
            self.logger = ComponentLoggerAdapter(logger)
        else:
            self.logger = logger if logger is not None else default_logger

        self.llm_manager = LLMManager(logger=self.logger)
        self._language_prompt_template = language_prompt_template

    def _build_system_message(self, custom_system_message: str | None = None, lang: str = "zh") -> str:
        """构建完整的系统消息（包含语言提示词）.

        Args:
            custom_system_message: 自定义的系统消息
            lang: 语言代码，默认为 "ja"（日语）

        Returns:
            str: 完整的系统消息

        """
        # 替换语言模板中的 {{lang}} 占位符
        language_prompt = self._language_prompt_template.replace("{{lang}}", lang)

        if custom_system_message:
            return language_prompt + "\n\n" + custom_system_message
        return language_prompt.strip()

    def create_chat_prompt_template(
        self,
        system_message: str | None = None,
        human_message: str = "",
        messages: list[tuple] | None = None,
        skip_system_prefix: bool = False,
        template_format: Literal["f-string", "mustache", "jinja2"] = "f-string",
        lang: str | None = None,
    ) -> ChatPromptTemplate:
        """构造ChatPromptTemplate.

        Args:
            system_message: 系统消息
            human_message: 人类消息
            messages: 自定义消息列表 [("system", "..."), ("human", "..."), ("ai", "...")]
            skip_system_prefix: 是否跳过统一的系统提示词前缀（默认False）
            template_format: 模板默认格式
            lang: 语言代码，如果为 None 则从上下文中获取，默认为 "ja"（日语）

        Returns:
            ChatPromptTemplate: 聊天提示模板

        """
        # 优先使用传入的 lang，否则使用默认值
        effective_lang = lang if lang is not None else "zh"

        if messages:
            # 使用自定义消息列表
            if not skip_system_prefix:
                # 需要添加统一前缀
                if messages and messages[0][0] == "system":
                    # 第一条是system消息，将前缀附加到它前面
                    enhanced_messages = [("system", self._build_system_message(messages[0][1], effective_lang))] + list(messages[1:])
                    return ChatPromptTemplate.from_messages(enhanced_messages)
                # 第一条不是system消息，在最前面插入一条system消息（仅包含前缀）
                language_prompt = self._language_prompt_template.replace("{{lang}}", effective_lang)
                enhanced_messages = [("system", language_prompt.strip())] + list(messages)
                return ChatPromptTemplate.from_messages(enhanced_messages)
            # 跳过前缀，直接返回原始消息列表
            return ChatPromptTemplate.from_messages(messages)

        # 使用简单的系统+人类消息模式
        template_messages = []

        if system_message or not skip_system_prefix:
            # 构建完整的系统消息（包含统一前缀）
            full_system_message = self._build_system_message(system_message, effective_lang) if not skip_system_prefix else system_message
            if full_system_message:
                template_messages.append(("system", full_system_message))

        if human_message:
            template_messages.append(("human", human_message))

        return ChatPromptTemplate.from_messages(template_messages, template_format=template_format)

    def create_prompt_template(self, template: str, input_variables: list[str]) -> PromptTemplate:
        """构造PromptTemplate.

        Args:
            template: 提示模板字符串
            input_variables: 输入变量列表

        Returns:
            PromptTemplate: 提示模板

        """
        return PromptTemplate(template=template, input_variables=input_variables)

    def chat_completion(
        self,
        prompt_template: ChatPromptTemplate,
        input_data: dict[str, Any],
        **kwargs,
    ) -> str:
        """非流式聊天完成.

        Args:
            prompt_template: 聊天提示模板
            input_data: 输入数据
            **kwargs: 其他参数

        Returns:
            str: 模型响应内容

        """
        try:
            llm = self.llm_manager.get_model()

            # 构建链
            chain = prompt_template | llm

            # 调用模型
            response = chain.invoke(input_data, **kwargs)

            # 提取内容
            if hasattr(response, "content"):
                return response.content
            if isinstance(response, str):
                return response
            return str(response)

        except Exception as e:
            self.logger.error(f"聊天完成失败: {e}")
            raise

    def chat_completion_stream(
        self,
        prompt_template: ChatPromptTemplate,
        input_data: dict[str, Any],
        buffer_size: int = 1,
        **kwargs,
    ) -> Generator[str, None]:
        """流式聊天完成.

        Args:
            prompt_template: 聊天提示模板
            input_data: 输入数据
            buffer_size: 缓冲区大小，默认为1（逐个字符），设置为更大值可以批量发送
            **kwargs: 其他参数

        Yields:
            str: 模型响应内容片段

        """
        try:
            llm = self.llm_manager.get_model()

            # 构建链
            chain = prompt_template | llm

            # 缓冲区
            buffer = ""

            # 流式调用模型
            for chunk in chain.stream(input_data, **kwargs):
                content = ""
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                elif isinstance(chunk, str):
                    content = chunk

                if content:
                    buffer += content

                    # 当缓冲区达到指定大小时，输出内容
                    if len(buffer) >= buffer_size:
                        yield buffer
                        buffer = ""

            # 输出剩余内容
            if buffer:
                yield buffer

        except Exception as e:
            self.logger.error(f"流式聊天完成失败: {e}")
            raise

    async def structured_output(
        self,
        prompt_template: ChatPromptTemplate | PromptTemplate,
        input_data: dict[str, Any],
        output_model: type[BaseModel],
        method: str = "with_structured_output",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs,
    ) -> Any:
        """结构化输出（带重试机制）.

        Args:
            prompt_template: 提示模板
            input_data: 输入数据
            output_model: 输出模型类
            method: 结构化输出方法 ("with_structured_output", "pydantic_parser", "json_mode")
            max_retries: 最大重试次数，默认3次
            retry_delay: 重试间隔（秒），默认1.0秒
            **kwargs: 其他参数

        Returns:
            Any: 结构化输出结果

        Raises:
            Exception: 重试max_retries次后仍然失败时抛出异常

        """
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                self.logger.info(f"尝试结构化输出 (第 {attempt}/{max_retries} 次)")

                llm = self.llm_manager.get_model()

                if method == "with_structured_output":
                    # 使用 with_structured_output 方法
                    structured_llm = llm.with_structured_output(output_model)
                    chain = prompt_template | structured_llm
                    result = await chain.ainvoke(input_data, **kwargs)
                    self.logger.info(f"结构化输出成功 (第 {attempt} 次尝试)")
                    return result

                if method == "pydantic_parser":
                    # 使用 PydanticOutputParser
                    parser = PydanticOutputParser(pydantic_object=output_model)

                    # 如果是ChatPromptTemplate，需要添加格式说明
                    if isinstance(prompt_template, ChatPromptTemplate):
                        # 在最后添加格式说明
                        messages = prompt_template.messages + [HumanMessage(content=f"\n\n{parser.get_format_instructions()}")]
                        enhanced_template = ChatPromptTemplate.from_messages(messages)
                    else:
                        # PromptTemplate直接添加格式说明
                        enhanced_template = PromptTemplate(
                            template=prompt_template.template + "\n\n{format_instructions}",
                            input_variables=prompt_template.input_variables + ["format_instructions"],
                        )
                        input_data["format_instructions"] = parser.get_format_instructions()

                    chain = enhanced_template | llm | parser
                    result = await chain.ainvoke(input_data, **kwargs)
                    self.logger.info(f"结构化输出成功 (第 {attempt} 次尝试)")
                    return result

                if method == "json_mode":
                    # JSON模式（需要模型支持）
                    json_llm = llm.bind(response_format={"type": "json_object"})
                    chain = prompt_template | json_llm
                    response = await chain.ainvoke(input_data, **kwargs)

                    # 解析JSON响应
                    json_data = json.loads(response.content) if hasattr(response, "content") else json.loads(str(response))

                    result = output_model(**json_data)
                    self.logger.info(f"结构化输出成功 (第 {attempt} 次尝试)")
                    return result

                raise ValueError(f"不支持的结构化输出方法: {method}")

            except Exception as e:
                last_error = e
                self.logger.warning(f"结构化输出失败 (第 {attempt}/{max_retries} 次): {str(e)}")

                if attempt < max_retries:
                    # 还有重试机会，等待后重试
                    self.logger.info(f"等待 {retry_delay} 秒后重试...")
                    await asyncio.sleep(retry_delay)
                else:
                    # 已达到最大重试次数
                    self.logger.error(f"结构化输出失败，已重试 {max_retries} 次，放弃重试")
                    raise Exception(f"结构化输出失败（重试{max_retries}次后）: {str(last_error)}") from last_error
        return None

    def simple_completion(self, prompt: str, skip_system_prefix: bool = False, lang: str | None = None, **kwargs) -> str:
        """简单文本完成.

        Args:
            prompt: 提示文本
            skip_system_prefix: 是否跳过系统提示词前缀（默认False）
            lang: 语言代码，如果为 None 则从上下文中获取，默认为 "ja"（日语）
            **kwargs: 其他参数

        Returns:
            str: 模型响应

        """
        try:
            # 优先使用传入的 lang，否则使用默认值
            effective_lang = lang if lang is not None else "zh"

            llm = self.llm_manager.get_model()

            # 如果不跳过系统前缀，则添加系统提示词
            if not skip_system_prefix:
                full_prompt = self._build_system_message(lang=effective_lang) + "\n\n" + prompt
            else:
                full_prompt = prompt

            response = llm.invoke(full_prompt, **kwargs)

            if hasattr(response, "content"):
                return response.content
            return str(response)

        except Exception as e:
            self.logger.error(f"简单完成失败: {e}")
            raise

    def simple_completion_stream(self, prompt: str, buffer_size: int = 1, skip_system_prefix: bool = False, lang: str | None = None, **kwargs) -> Generator[str, None]:
        """简单流式文本完成.

        Args:
            prompt: 提示文本
            buffer_size: 缓冲区大小，默认为1（逐个字符），设置为更大值可以批量发送
            skip_system_prefix: 是否跳过系统提示词前缀（默认False）
            lang: 语言代码，如果为 None 则从上下文中获取，默认为 "ja"（日语）
            **kwargs: 其他参数

        Yields:
            str: 模型响应片段

        """
        try:
            # 优先使用传入的 lang，否则使用默认值
            effective_lang = lang if lang is not None else "zh"

            llm = self.llm_manager.get_model()

            # 如果不跳过系统前缀，则添加系统提示词
            if not skip_system_prefix:
                full_prompt = self._build_system_message(lang=effective_lang) + "\n\n" + prompt
            else:
                full_prompt = prompt

            # 缓冲区
            buffer = ""

            for chunk in llm.stream(full_prompt, **kwargs):
                content = ""
                if hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                elif isinstance(chunk, str):
                    content = chunk

                if content:
                    buffer += content

                    # 当缓冲区达到指定大小时，输出内容
                    if len(buffer) >= buffer_size:
                        yield buffer
                        buffer = ""

            # 输出剩余内容
            if buffer:
                yield buffer

        except Exception as e:
            self.logger.error(f"简单流式完成失败: {e}")
            raise

    def vision_completion(
        self,
        image_input: str | Path,
        prompt: str = "请描述这张图片的内容",
        model: str = "gpt-4o",
        max_tokens: int = 1000,
        detail: str = "auto",
        **kwargs,
    ) -> str:
        """图片识别（使用GPT-4o多模态能力）.

        Args:
            image_input: 图片输入，可以是：
                - 本地文件路径（Path 或 str）
                - 图片URL（http:// 或 https:// 开头）
                - base64编码的图片数据（data:image/... 开头）
            prompt: 对图片的提问或描述要求
            model: 使用的模型，默认 gpt-4o（支持视觉）
            max_tokens: 最大返回token数
            detail: 图片细节级别，可选 "low", "high", "auto"
            **kwargs: 其他参数

        Returns:
            str: 模型对图片的描述或回答

        Raises:
            ValueError: 当图片输入格式不正确时
            FileNotFoundError: 当本地图片文件不存在时
            Exception: 其他错误

        """
        try:
            # 处理图片输入
            image_url = self._prepare_image_input(image_input)

            # 使用 OpenAI 客户端
            client = OpenAI(
                api_key=self.llm_manager.api_key,
                base_url=self.llm_manager.base_url,
            )

            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": detail,
                            },
                        },
                    ],
                }
            ]

            # 调用模型
            self.logger.info(f"调用 {model} 进行图片识别...")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                **kwargs,
            )

            # 提取结果
            content = response.choices[0].message.content
            self.logger.info("图片识别完成")
            return content

        except Exception as e:
            self.logger.error(f"图片识别失败: {e}")
            raise

    def _prepare_image_input(self, image_input: str | Path) -> str:
        """准备图片输入，转换为API可接受的格式.

        Args:
            image_input: 图片输入（路径、URL或base64）

        Returns:
            str: 处理后的图片URL或base64数据

        Raises:
            ValueError: 当输入格式不正确时
            FileNotFoundError: 当文件不存在时

        """
        # 转换为字符串
        image_str = str(image_input)

        # 1. 如果是HTTP(S) URL，直接返回
        if image_str.startswith(("http://", "https://")):
            self.logger.debug(f"使用图片URL: {image_str}")
            return image_str

        # 2. 如果已经是base64格式（data:image/...），直接返回
        if image_str.startswith("data:image/"):
            self.logger.debug("使用base64编码的图片")
            return image_str

        # 3. 否则当作本地文件路径处理
        file_path = Path(image_str)
        if not file_path.exists():
            raise FileNotFoundError(f"图片文件不存在: {file_path}")

        # 读取文件并转换为base64
        self.logger.debug(f"读取本地图片文件: {file_path}")
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()

        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type or not mime_type.startswith("image/"):
            # 默认使用常见图片格式
            suffix = file_path.suffix.lower()
            mime_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
                ".bmp": "image/bmp",
            }
            mime_type = mime_map.get(suffix, "image/jpeg")

        # 编码为base64
        base64_image = base64.b64encode(image_data).decode("utf-8")
        data_url = f"data:{mime_type};base64,{base64_image}"

        self.logger.debug(f"图片已转换为base64格式 (MIME: {mime_type})")
        return data_url


# ==================== 依赖注入函数 ====================


def get_llm_service() -> LLMService:
    """获取LLM服务实例.

    Returns:
        LLMService: LLM服务实例

    """
    return LLMService()

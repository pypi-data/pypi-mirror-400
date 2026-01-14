"""
阿里云百联LLM客户端
基于OpenAI客户端实现，用于对接阿里云百联模型
"""

import json
import logging
from typing import Any, ClassVar

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from graphiti_core.llm_client.client import LLMClient
from graphiti_core.llm_client.config import LLMConfig, ModelSize
from graphiti_core.llm_client.errors import RateLimitError, RefusalError
from graphiti_core.prompts.models import Message

logger = logging.getLogger(__name__)

DEFAULT_MODEL = 'qwen-plus'
DEFAULT_SMALL_MODEL = 'qwen-turbo'


class AliyunLLMClient(LLMClient):
    """
    阿里云百联LLM客户端
    基于OpenAI客户端实现，用于对接阿里云百联模型
    """

    # Class-level constants
    MAX_RETRIES: ClassVar[int] = 2

    def __init__(
            self,
            config: LLMConfig,
            cache: bool = False,
            client: Any = None,
    ):
        """
        初始化阿里云百联LLM客户端

        Args:
            config: LLM配置
            cache: 是否使用缓存
            client: 可选的客户端实例
        """
        if cache:
            raise NotImplementedError('Caching is not implemented for AliyunLLMClient')

        super().__init__(config, cache)

        # 创建OpenAI客户端，指向阿里云API
        if client is None:
            self.client = AsyncOpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
        else:
            self.client = client

    def _convert_messages_to_openai_format(
            self, messages: list[Message]
    ) -> list[ChatCompletionMessageParam]:
        """转换消息格式为OpenAI格式"""
        openai_messages: list[ChatCompletionMessageParam] = []
        for m in messages:
            m.content = self._clean_input(m.content)
            if m.role == 'user':
                openai_messages.append({'role': 'user', 'content': m.content})
            elif m.role == 'system':
                openai_messages.append({'role': 'system', 'content': m.content})
        return openai_messages

    def _get_model_for_size(self, model_size: ModelSize) -> str:
        """根据模型大小获取合适的模型名称"""
        if model_size == ModelSize.small:
            return self.small_model or DEFAULT_SMALL_MODEL
        else:
            return self.model or DEFAULT_MODEL

    async def _create_completion(
            self,
            model: str,
            messages: list[ChatCompletionMessageParam],
            temperature: float | None,
            max_tokens: int,
            response_model: type[BaseModel] | None = None,
    ) -> Any:
        """创建完成请求"""
        return await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={'type': 'json_object'},
        )

    async def _create_structured_completion(
            self,
            model: str,
            messages: list[ChatCompletionMessageParam],
            temperature: float | None,
            max_tokens: int,
            response_model: type[BaseModel],
    ) -> Any:
        """创建结构化完成请求"""
        # 阿里云API可能不支持beta.parse，使用标准JSON格式
        # 在消息中添加模型schema信息
        schema_info = f"\n\n请按照以下JSON格式返回：\n{response_model.model_json_schema()}"
        messages[-1]['content'] += schema_info

        logger.info(f"发送请求到阿里云API:")
        logger.info(f"  Model: {model}")
        logger.info(f"  Base URL: {self.client.base_url}")
        logger.info(f"  API Key: {self.config.api_key[:10]}..." if self.config.api_key else "No API Key")
        logger.info(f"  Temperature: {temperature}")
        logger.info(f"  Max Tokens: {max_tokens}")
        logger.info(f"  Messages count: {len(messages)}")
        print(f"model: {model}, message={messages}, temperature={temperature}, max_tokens={max_tokens}")
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={'type': 'json_object'},
            )
            logger.info("阿里云API请求成功")
            return response
        except Exception as e:
            logger.error(f"阿里云API请求失败: {e}")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误详情: {str(e)}")

            # 如果是404错误，可能是端点或模型名称问题
            if "404" in str(e):
                logger.error("404错误 - 可能的原因:")
                logger.error("1. API端点不正确")
                logger.error("2. 模型名称不存在")
                logger.error("3. API密钥无效")
                logger.error(f"当前端点: {self.client.base_url}")
                logger.error(f"当前模型: {model}")

            raise

    def _handle_structured_response(self, response: Any) -> dict[str, Any]:
        """处理结构化响应"""
        response_object = response.choices[0].message
        content = response_object.content or '{}'

        try:
            result = json.loads(content)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 内容: {content}")
            raise Exception(f"无效的JSON响应: {content}")

    def _handle_json_response(self, response: Any) -> dict[str, Any]:
        """处理JSON响应"""
        result = response.choices[0].message.content or '{}'
        try:
            return json.loads(result)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 内容: {result}")
            raise Exception(f"无效的JSON响应: {result}")

    async def _generate_response(
            self,
            messages: list[Message],
            response_model: type[BaseModel] | None = None,
            max_tokens: int | None = None,
            model_size: ModelSize = ModelSize.medium,
    ) -> dict[str, Any]:
        """生成响应"""
        openai_messages = self._convert_messages_to_openai_format(messages)
        model = self._get_model_for_size(model_size)

        try:
            if response_model:
                response = await self._create_structured_completion(
                    model=model,
                    messages=openai_messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                    response_model=response_model,
                )
                print("aliyun_response", response)
                return self._handle_structured_response(response)
            else:
                response = await self._create_completion(
                    model=model,
                    messages=openai_messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens or self.max_tokens,
                )
                return self._handle_json_response(response)

        except Exception as e:
            logger.error(f'生成LLM响应时出错: {e}')
            import traceback
            logger.error(traceback.format_exc())
            raise

    async def generate_response(
            self,
            messages: list[Message],
            response_model: type[BaseModel] | None = None,
            max_tokens: int | None = None,
            model_size: ModelSize = ModelSize.medium,
    ) -> dict[str, Any]:
        """生成响应，带重试逻辑"""
        if max_tokens is None:
            max_tokens = self.max_tokens

        retry_count = 0
        last_error = None

        while retry_count <= self.MAX_RETRIES:
            try:
                response = await self._generate_response(
                    messages, response_model, max_tokens, model_size
                )
                return response
            except (RateLimitError, RefusalError):
                # 这些错误不应该触发重试
                raise
            except Exception as e:
                last_error = e

                # 如果达到最大重试次数，不再重试
                if retry_count >= self.MAX_RETRIES:
                    logger.error(f'达到最大重试次数 ({self.MAX_RETRIES})。最后错误: {e}')
                    raise

                retry_count += 1

                # 构造详细的错误消息给LLM
                error_context = (
                    f'之前的响应尝试无效。'
                    f'错误类型: {e.__class__.__name__}。'
                    f'错误详情: {str(e)}。'
                    f'请重试并提供有效的响应，确保输出符合预期的格式和约束。'
                )

                error_message = Message(role='user', content=error_context)
                messages.append(error_message)
                logger.warning(
                    f'应用错误后重试 (尝试 {retry_count}/{self.MAX_RETRIES}): {e}'
                )

        # 如果到达这里，抛出最后一个错误
        raise last_error or Exception('达到最大重试次数但没有具体错误')

    async def close(self):
        """关闭客户端"""
        if hasattr(self, 'client') and hasattr(self.client, 'close'):
            await self.client.close()

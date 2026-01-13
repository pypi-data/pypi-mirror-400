# -*- coding: UTF-8 -*-
# @Time : 2025/12/30 16:40 
# @Author : 刘洪波

from typing import Any, AsyncIterator, List, Optional
from tenacity import AsyncRetrying
from openai import AsyncOpenAI, AsyncAzureOpenAI
from llmskit.clients.base import AsyncLLMClient
from llmskit._types import Message, ToolDefinition, LLMEvent, ToolCall


class AsyncOpenAIClient(AsyncLLMClient):
    """OpenAI-compatible asynchronous client implementation.
    
    Supports OpenAI API and compatible APIs (e.g., vLLM, LocalAI, Ollama, etc.).
    Supports streaming output, tool calling, and reasoning process.
    """
    capabilities = {
        "tool_calling": True,
        "reasoning": True,
        "streaming": True,
    }

    def __init__(
            self,
            *,
            model: str,
            api_key: str,
            base_url: Optional[str] = None,
            **kwargs: Any,
    ):
        """Initialize OpenAI-compatible client.
        
        Args:
            model: Model name, e.g., "gpt-4", "gpt-3.5-turbo", etc.
            api_key: API key.
            base_url: Optional API base URL for custom endpoints (e.g., locally deployed vLLM).
                     If not provided, uses OpenAI official endpoint.
            **kwargs: Additional parameters passed to AsyncLLMClient (e.g., logger, retry_config, etc.).
        """
        super().__init__(**kwargs)
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def events(
            self,
            messages: List[Message],
            *,
            tools: Optional[List[ToolDefinition]] = None,
            **kwargs: Any,
    ) -> AsyncIterator[LLMEvent]:
        """Asynchronously generate response event stream for OpenAI-compatible API.
        
        Args:
            messages: List of messages, each message is a dict typically containing "role" and "content" fields.
            tools: Optional list of tool definitions for function calling.
            **kwargs: Additional parameters passed to OpenAI API (e.g., temperature, max_tokens, etc.).
        
        Yields:
            LLMEvent: LLM event, which may contain the following types:
                - "content": Text content chunk
                - "reasoning": Reasoning process (if model supports it, compatible with vLLM + Qwen)
                - "tool_call": Tool call
                - "done": Completion event
        """

        async for attempt in AsyncRetrying(**self.retry_config):
            with attempt:
                stream = await self.client.chat.completions.create(model=self.model, messages=messages, tools=tools, stream=True, **kwargs)
                tool_id = None
                async for chunk in stream:
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        if delta.content:
                            yield LLMEvent(type="content", text=delta.content)
                        # 兼容 DeepSeek/OpenAI O1/Qwen 不同的思维链字段名
                        reasoning = getattr(delta, 'reasoning_content', None) or getattr(delta, 'reasoning', None)
                        if reasoning:
                            yield LLMEvent(type="reasoning", text=reasoning)
                        if delta.tool_calls:
                            for call in delta.tool_calls:
                                if call.id:
                                    tool_id = call.id
                                if tool_id:
                                    yield LLMEvent(type="tool_call", tool_call=ToolCall(id=tool_id, name=call.function.name, arguments=call.function.arguments))
                yield LLMEvent(type="done")
                return


class AsyncAzureOpenAIClient(AsyncOpenAIClient):
    """Azure OpenAI asynchronous client implementation.
    
    Inherits from AsyncOpenAIClient, specifically for Azure OpenAI service.
    Automatically constructs Azure-specific API endpoint URL.
    """
    
    def __init__(
            self,
            *,
            deployment: str,
            api_key: str,
            endpoint: str,
            api_version: str = "2024-02-01",
            **kwargs: Any,
    ):
        """Initialize Azure OpenAI client.
        
        Args:
            deployment: Azure deployment name.
            api_key: Azure API key.
            endpoint: Azure endpoint URL (e.g., https://your-resource.openai.azure.com).
            api_version: API version, default "2024-02-01".
            **kwargs: Additional parameters passed to AsyncOpenAIClient (e.g., logger, retry_config, etc.).
        """
        super().__init__(
            model=deployment,
            api_key=api_key,
            base_url=None,
            **kwargs,
        )
        # 覆盖为正确的 Azure 客户端
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            api_version=api_version,
            api_key=api_key,
        )

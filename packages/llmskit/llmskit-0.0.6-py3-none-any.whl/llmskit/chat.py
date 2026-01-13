# -*- coding: UTF-8 -*-
# @Time : 2025/12/30 16:38 
# @Author : 刘洪波

import uuid
import logging
import asyncio
from typing import Any, AsyncIterator, Callable, List, Optional, Iterator
from llmskit._types import Message, ToolDefinition, LLMEvent, LLMChatComplete, ToolCall
from llmskit.clients.base import AsyncLLMClient
from llmskit.clients.openai import AsyncOpenAIClient
from llmskit.clients.claude import AsyncClaudeClient
from llmskit._utils import chat_complete, async_chat_complete


__all__ = [
    "ChatLLM", "AsyncChatLLM",
]


class AsyncChatLLM:
    """Asynchronous chat LLM wrapper class providing unified streaming and complete response interfaces.
    
    Supports multiple LLM providers (OpenAI, Anthropic, etc.) with a unified API.
    Supports tool calling, reasoning process recording, and other features.
    """
    
    def __init__(
        self,
        *,
        client: AsyncLLMClient,
        recorder: Optional[Callable[[str, dict], None]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize an asynchronous chat LLM instance.
        
        Args:
            client: Async LLM client instance for actual LLM API calls.
            recorder: Optional recorder function for logging requests and responses.
                     Function signature: (trace_id: str, data: dict) -> None
            logger: Optional logger for recording runtime logs. If not provided, uses default logger.
        """
        self.client = client
        self.recorder = recorder
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    @classmethod
    def from_openai(cls, model: str, api_key: str = "EMPTY", base_url: Optional[str] = None, recorder=None, logger=None, **kwargs):
        """Create an AsyncChatLLM instance from OpenAI configuration.
        
        Args:
            model: Model name, e.g., "gpt-4", "gpt-3.5-turbo", etc.
            api_key: OpenAI API key.
            base_url: Optional API base URL for custom endpoints (e.g., locally deployed vLLM).
            recorder: Optional recorder function for logging requests and responses.
            logger: Optional logger.
            **kwargs: Additional parameters passed to AsyncOpenAIClient.
        
        Returns:
            AsyncChatLLM: Configured asynchronous chat LLM instance.
        """
        client = AsyncOpenAIClient(model=model, api_key=api_key, base_url=base_url, **kwargs)
        return cls(client=client, recorder=recorder, logger=logger)

    @classmethod
    def from_gpt(cls, **kwargs):
        """Create an AsyncChatLLM instance from GPT configuration (alias for from_openai).
        
        Args:
            **kwargs: Parameters passed to from_openai.
        
        Returns:
            AsyncChatLLM: Configured asynchronous chat LLM instance.
        """
        return cls.from_openai(**kwargs)

    @classmethod
    def from_local(cls, **kwargs):
        """Create an AsyncChatLLM instance from GPT configuration (alias for from_openai).

        Args:
            **kwargs: Parameters passed to from_openai.

        Returns:
            AsyncChatLLM: Configured asynchronous chat LLM instance.
        """
        return cls.from_openai(**kwargs)

    @classmethod
    def from_anthropic(cls, model: str, api_key: str, base_url: Optional[str] = None, recorder=None, logger=None, **kwargs):
        """Create an AsyncChatLLM instance from Anthropic configuration.
        
        Args:
            model: Model name, e.g., "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", etc.
            api_key: Anthropic API key.
            base_url: Optional API base URL for custom endpoints
            recorder: Optional recorder function for logging requests and responses.
            logger: Optional logger.
            **kwargs: Additional parameters passed to AsyncClaudeClient.
        
        Returns:
            AsyncChatLLM: Configured asynchronous chat LLM instance.
        """
        client = AsyncClaudeClient(model=model, api_key=api_key, base_url=base_url, **kwargs)
        return cls(client=client, recorder=recorder, logger=logger)

    @classmethod
    def from_claude(cls, **kwargs):
        """Create an AsyncChatLLM instance from Claude configuration (alias for from_anthropic).
        
        Args:
            **kwargs: Parameters passed to from_anthropic.
        
        Returns:
            AsyncChatLLM: Configured asynchronous chat LLM instance.
        """
        return cls.from_anthropic(**kwargs)

    @classmethod
    def create(cls, provider: str, recorder=None, logger=None, **kwargs):
        """Generic factory method to create an AsyncChatLLM instance by provider name.
        
        Supported providers: "openai", "gpt", "anthropic", "claude", "local"
        
        Args:
            provider: Provider name (case-insensitive).
            recorder: Optional recorder function for logging requests and responses.
            logger: Optional logger.
            **kwargs: Parameters passed to the corresponding provider factory method:
                     - OpenAI/GPT/local: model, api_key, base_url, etc.
                     - Anthropic/Claude: model, api_key, etc.
        
        Returns:
            AsyncChatLLM: Configured asynchronous chat LLM instance.
        
        Raises:
            ValueError: If the provider name is not supported.
        """
        mapping = {
            "openai": cls.from_openai,
            "gpt": cls.from_openai,
            "local": cls.from_openai,
            "anthropic": cls.from_anthropic,
            "claude": cls.from_anthropic,
        }
        method = mapping.get(provider.lower())
        if not method:
            supported = ", ".join(mapping.keys())
            raise ValueError(f"Unknown provider: {provider}. Supported: {supported}")

        # Ensure recorder and logger are correctly passed to factory method
        return method(recorder=recorder, logger=logger, **kwargs)

    async def stream(
        self,
        *,
        messages: List[Message],
        tools: Optional[List[ToolDefinition]] = None,
        trace_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[LLMEvent]:
        """Asynchronously stream response events.
        
        Args:
            messages: List of messages, each message is a dict typically containing "role" and "content" fields.
                     Example: [{"role": "user", "content": "Hello"}]
            tools: Optional list of tool definitions for function calling.
            trace_id: Optional trace ID for logging and recording. If not provided, a UUID will be auto-generated.
            **kwargs: Additional parameters passed to the underlying client (e.g., temperature, max_tokens, etc.).
        
        Yields:
            LLMEvent: LLM event, which may contain the following types:
                - "content": Text content chunk
                - "reasoning": Reasoning process (if model supports it)
                - "tool_call": Tool call
                - "done": Completion event
        
        Raises:
            Exception: If an error occurs during LLM invocation.
        """

        trace_id = trace_id or str(uuid.uuid4())
        self.logger.info(f"LLM run start: {trace_id}")
        try:
            if self.recorder:
                self.recorder(trace_id, {"messages": messages, "tools": tools})

            async for event in self.client.events(messages, tools=tools, **kwargs):
                if self.recorder:
                    self.recorder(trace_id, {"event": event})
                yield event
        except Exception as e:
            self.logger.error(f"LLM run error: {trace_id}, Error: {str(e)}")
            raise
        finally:
            self.logger.info(f"LLM run done: {trace_id}")

    async def complete(self, **kwargs: Any) -> LLMChatComplete:
        """Asynchronously get complete chat response (non-streaming).
        
        Internally calls the stream method and collects all events to return complete results.
        
        Args:
            **kwargs: Parameters passed to the stream method, including:
                - messages: List of messages
                - tools: Optional list of tool definitions
                - trace_id: Optional trace ID
                - Other parameters (e.g., temperature, max_tokens, etc.)
        
        Returns:
            LLMChatComplete: Object containing complete response content, reasoning process, and tool calls.
        """
        return await async_chat_complete(self.stream(**kwargs))


class ChatLLM:
    """Synchronous chat LLM wrapper class providing unified streaming and complete response interfaces.
    
    Internally uses async client but provides synchronous interface for use in synchronous code.
    Supports multiple LLM providers (OpenAI, Anthropic, etc.) with a unified API.
    Supports tool calling, reasoning process recording, and other features.
    """
    
    def __init__(
            self,
            *,
            client: AsyncLLMClient,
            recorder: Optional[Callable[[str, dict], None]] = None,
            logger: Optional[logging.Logger] = None,
    ):
        """Initialize a synchronous chat LLM instance.
        
        Args:
            client: Async LLM client instance for actual LLM API calls.
            recorder: Optional recorder function for logging requests and responses.
                     Function signature: (trace_id: str, data: dict) -> None
            logger: Optional logger for recording runtime logs. If not provided, uses default logger.
        """
        self.client = client
        self.recorder = recorder
        self.logger = logger or logging.getLogger(self.__class__.__name__)

        # Core: manage internal event loop
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

    @classmethod
    def from_openai(cls, model: str, api_key: str = "EMPTY", base_url: Optional[str] = None, recorder=None, logger=None,
                    **kwargs):
        """Create a ChatLLM instance from OpenAI configuration.
        
        Args:
            model: Model name, e.g., "gpt-4", "gpt-3.5-turbo", etc.
            api_key: OpenAI API key.
            base_url: Optional API base URL for custom endpoints (e.g., locally deployed vLLM).
            recorder: Optional recorder function for logging requests and responses.
            logger: Optional logger.
            **kwargs: Additional parameters passed to AsyncOpenAIClient.
        
        Returns:
            ChatLLM: Configured synchronous chat LLM instance.
        """
        # Internally still uses async Client
        client = AsyncOpenAIClient(model=model, api_key=api_key, base_url=base_url, **kwargs)
        return cls(client=client, recorder=recorder, logger=logger)

    @classmethod
    def from_gpt(cls, **kwargs):
        """Create a ChatLLM instance from GPT configuration (alias for from_openai).
        
        Args:
            **kwargs: Parameters passed to from_openai.
        
        Returns:
            ChatLLM: Configured synchronous chat LLM instance.
        """
        return cls.from_openai(**kwargs)

    @classmethod
    def from_local(cls, **kwargs):
        """Create a ChatLLM instance from GPT configuration (alias for from_openai).

        Args:
            **kwargs: Parameters passed to from_openai.

        Returns:
            ChatLLM: Configured synchronous chat LLM instance.
        """
        return cls.from_openai(**kwargs)

    @classmethod
    def from_anthropic(cls, model: str, api_key: str, base_url: Optional[str] = None, recorder=None, logger=None, **kwargs):
        """Create a ChatLLM instance from Anthropic configuration.
        
        Args:
            model: Model name, e.g., "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", etc.
            api_key: Anthropic API key.
            base_url: Optional API base URL for custom endpoints
            recorder: Optional recorder function for logging requests and responses.
            logger: Optional logger.
            **kwargs: Additional parameters passed to AsyncClaudeClient.
        
        Returns:
            ChatLLM: Configured synchronous chat LLM instance.
        """
        # Internally still uses async Client
        client = AsyncClaudeClient(model=model, api_key=api_key, base_url=base_url, **kwargs)
        return cls(client=client, recorder=recorder, logger=logger)

    @classmethod
    def from_claude(cls, **kwargs):
        """Create a ChatLLM instance from Claude configuration (alias for from_anthropic).
        
        Args:
            **kwargs: Parameters passed to from_anthropic.
        
        Returns:
            ChatLLM: Configured synchronous chat LLM instance.
        """
        return cls.from_anthropic(**kwargs)

    @classmethod
    def create(cls, provider: str, recorder=None, logger=None, **kwargs):
        """Generic factory method to create a ChatLLM instance by provider name.
        
        Supported providers: "openai", "gpt", "anthropic", "claude", "local"
        
        Args:
            provider: Provider name (case-insensitive).
            recorder: Optional recorder function for logging requests and responses.
            logger: Optional logger.
            **kwargs: Parameters passed to the corresponding provider factory method:
                     - OpenAI/GPT/local: model, api_key, base_url, etc.
                     - Anthropic/Claude: model, api_key, etc.
        
        Returns:
            ChatLLM: Configured synchronous chat LLM instance.
        
        Raises:
            ValueError: If the provider name is not supported.
        """
        mapping = {
            "openai": cls.from_openai,
            "gpt": cls.from_openai,
            "local": cls.from_openai,
            "anthropic": cls.from_anthropic,
            "claude": cls.from_anthropic,
        }
        method = mapping.get(provider.lower())
        if not method:
            supported = ", ".join(mapping.keys())
            raise ValueError(f"Unknown provider: {provider}. Supported: {supported}")
        return method(recorder=recorder, logger=logger, **kwargs)

    def stream(
            self,
            *,
            messages: List[Any],
            tools: Optional[List[Any]] = None,
            trace_id: Optional[str] = None,
            **kwargs: Any,
    ) -> Iterator[dict]:
        """Synchronously stream response events.
        
        Internally drives async generator but provides synchronous interface.
        
        Args:
            messages: List of messages, each message is a dict typically containing "role" and "content" fields.
                     Example: [{"role": "user", "content": "Hello"}]
            tools: Optional list of tool definitions for function calling.
            trace_id: Optional trace ID for logging and recording. If not provided, a UUID will be auto-generated.
            **kwargs: Additional parameters passed to the underlying client (e.g., temperature, max_tokens, etc.).
        
        Yields:
            dict: LLM event dictionary, which may contain the following types:
                - {"type": "content", "text": "..."}: Text content chunk
                - {"type": "reasoning", "text": "..."}: Reasoning process (if model supports it)
                - {"type": "tool_call", "tool_call": {...}}: Tool call
                - {"type": "done"}: Completion event
        
        Raises:
            Exception: If an error occurs during LLM invocation.
        """
        trace_id = trace_id or str(uuid.uuid4())
        self.logger.info(f"LLM run start (sync mode): {trace_id}")

        if self.recorder:
            self.recorder(trace_id, {"messages": messages, "tools": tools})

        # Get async generator object
        async_gen = self.client.events(messages, tools=tools, **kwargs)

        try:
            while True:
                try:
                    # Key point: use run_until_complete to drive the next frame of async iterator
                    event = self._loop.run_until_complete(async_gen.__anext__())
                    if self.recorder:
                        self.recorder(trace_id, {"event": event})
                    yield event
                except StopAsyncIteration:
                    break
        except Exception as e:
            self.logger.error(f"LLM run error: {trace_id}, Error: {str(e)}")
            raise
        finally:
            self.logger.info(f"LLM run done: {trace_id}")

    def complete(self, **kwargs: Any) -> Any:
        """Synchronously get complete chat response (non-streaming).
        
        Internally calls the stream method and collects all events to return complete results.
        
        Args:
            **kwargs: Parameters passed to the stream method, including:
                - messages: List of messages
                - tools: Optional list of tool definitions
                - trace_id: Optional trace ID
                - Other parameters (e.g., temperature, max_tokens, etc.)
        
        Returns:
            LLMChatComplete: Object containing complete response content, reasoning process, and tool calls.
        """
        return chat_complete(self.stream(**kwargs))

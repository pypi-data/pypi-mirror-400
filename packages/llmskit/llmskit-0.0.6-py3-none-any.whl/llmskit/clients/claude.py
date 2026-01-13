# -*- coding: UTF-8 -*-
# @Time : 2025/12/30 16:40 
# @Author : 刘洪波
"""
Reference Materials：
https://platform.claude.com/docs/zh-CN/build-with-claude/streaming
"""

from typing import Any, AsyncIterator, List, Optional
from tenacity import AsyncRetrying
from anthropic import AsyncAnthropic
from llmskit.clients.base import AsyncLLMClient
from llmskit._types import Message, ToolDefinition, LLMEvent, ToolCall


class AsyncClaudeClient(AsyncLLMClient):
    """Anthropic Claude asynchronous client implementation.
    
    Supports streaming output, tool calling, and reasoning process for Claude models.
    """
    capabilities = {
        "tool_calling": True,
        "reasoning": True,
        "streaming": True,
    }

    def __init__(self, *, model: str, api_key: str, base_url: Optional[str] = None, **kwargs: Any):
        """Initialize Anthropic Claude client.
        
        Args:
            model: Claude model name, e.g., "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", etc.
            api_key: Anthropic API key.
            base_url: Optional API base URL for custom endpoints
            **kwargs: Additional parameters passed to AsyncLLMClient (e.g., logger, retry_config, etc.).
        """
        super().__init__(**kwargs)
        self.model = model
        self.client = AsyncAnthropic(api_key=api_key, base_url=base_url)

    async def events(
        self,
        messages: List[Message],
        *,
        tools: Optional[List[ToolDefinition]] = None,
        **kwargs: Any,
    ) -> AsyncIterator[LLMEvent]:
        """Asynchronously generate Claude response event stream.
        
        Args:
            messages: List of messages, each message is a dict typically containing "role" and "content" fields.
            tools: Optional list of tool definitions for function calling.
            **kwargs: Additional parameters passed to Anthropic API (e.g., temperature, max_tokens, etc.).
        
        Yields:
            LLMEvent: LLM event, which may contain the following types:
                - "content": Text content chunk
                - "reasoning": Reasoning process (thinking)
                - "tool_call": Tool call
                - "done": Completion event
        """
        async for attempt in AsyncRetrying(**self.retry_config):
            with attempt:
                async with self.client.messages.stream(model=self.model, messages=messages, tools=tools, **kwargs) as stream:
                    tool_id: Optional[str] = None
                    tool_name: Optional[str] = None
                    async for event in stream:
                        if event.type == "content_block_delta":
                            delta = event.delta
                            if delta.type == "text_delta":
                                yield LLMEvent(type="content", text=delta.text)
                            elif delta.type == "thinking_delta":
                                yield LLMEvent(type="reasoning", text=delta.thinking)
                            elif delta.type == "input_json_delta":
                                yield LLMEvent(type="tool_call",
                                               tool_call=ToolCall(id=tool_id,
                                                                  name=tool_name,
                                                                  arguments=delta.partial_json))
                        elif event.type == "content_block_start":
                            content_block = event.content_block
                            if content_block.type == 'tool_use':
                                tool_id, tool_name = content_block.id, content_block.name
                                yield LLMEvent(type="tool_call",
                                               tool_call=ToolCall(id=tool_id,
                                                                  name=tool_name,
                                                                  arguments=""))
                    yield LLMEvent(type="done")
                    return

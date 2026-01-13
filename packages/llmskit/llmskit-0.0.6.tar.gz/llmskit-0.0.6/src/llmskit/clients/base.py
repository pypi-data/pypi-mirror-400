# -*- coding: UTF-8 -*-
# @Time : 2025/12/30 16:39 
# @Author : 刘洪波
import abc
import logging
from typing import Any, AsyncIterator, List, Optional
from llmskit._types import Message, ToolDefinition, LLMEvent, ModelCapabilities
from llmskit._retry import build_retry_config


class AsyncLLMClient(abc.ABC):
    """Abstract base class for asynchronous LLM clients.
    
    Defines the interface that all LLM clients must implement, including streaming event generation.
    Subclasses need to implement the events method to provide specific LLM API call logic.
    """
    capabilities: ModelCapabilities

    def __init__(
        self,
        *,
        logger: Optional[logging.Logger] = None,
        retry_config: Optional[dict] = None,
    ):
        """Initialize an asynchronous LLM client.
        
        Args:
            logger: Optional logger for recording runtime logs. If not provided, uses default logger.
            retry_config: Optional retry configuration dictionary. If not provided, uses default retry config.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.retry_config = retry_config or build_retry_config(self.logger)

    @abc.abstractmethod
    async def events(
        self,
        messages: List[Message],
        *,
        tools: Optional[List[ToolDefinition]] = None,
        **kwargs: Any,
    ) -> AsyncIterator[LLMEvent]:
        """Asynchronously generate LLM response event stream.
        
        This is an abstract method that subclasses must implement to provide specific LLM API call logic.
        
        Args:
            messages: List of messages, each message is a dict typically containing "role" and "content" fields.
            tools: Optional list of tool definitions for function calling.
            **kwargs: Additional parameters passed to the underlying LLM API (e.g., temperature, max_tokens, etc.).
        
        Yields:
            LLMEvent: LLM event, which may contain the following types:
                - "content": Text content chunk
                - "reasoning": Reasoning process (if model supports it)
                - "tool_call": Tool call
                - "done": Completion event
        
        Raises:
            NotImplementedError: If subclass does not implement this method.
        """
        raise NotImplementedError

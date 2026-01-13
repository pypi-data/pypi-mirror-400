# -*- coding: UTF-8 -*-
# @Time : 2025/12/30 16:36 
# @Author : 刘洪波
from dataclasses import dataclass, field
from typing import TypedDict, Literal, Any, Optional, List, Dict

# Message type definition
# Typically contains "role" (e.g., "user", "assistant", "system") and "content" fields
Message = Dict[str, Any]


class ToolDefinition(TypedDict):
    """Tool definition type for function calling functionality.
    
    Attributes:
        name: Tool name for identification.
        description: Tool description explaining its purpose.
        input_schema: Input parameter schema definition (JSON Schema), compatible with multiple vendors and models.
    """
    name: str
    description: str
    input_schema: dict   # Compatible with multiple vendors and models


class ModelCapabilities(TypedDict):
    """Model capabilities definition describing supported features.
    
    Attributes:
        tool_calling: Whether tool calling (function calling) is supported.
        reasoning: Whether reasoning process output is supported.
        streaming: Whether streaming output is supported.
    """
    tool_calling: bool
    reasoning: bool
    streaming: bool


class ToolCall(TypedDict):
    """Tool call type representing a model's call to a tool.
    
    Attributes:
        id: ID of the tool call.
        name: Name of the called tool.
        arguments: Tool call arguments, typically in dict format.
    """
    id : str
    name: str
    arguments: Any


class LLMEvent(TypedDict, total=False):
    """LLM event type representing a single event in streaming output.
    
    Attributes:
        type: Event type, possible values:
            - "content": Text content chunk
            - "tool_call": Tool call
            - "reasoning": Reasoning process (if model supports it)
            - "done": Completion event
        text: Text content (used when type is "content" or "reasoning").
        tool_call: Tool call object (used when type is "tool_call").
        usage: Usage statistics (e.g., token count, etc.).
    """
    type: Literal[
        "content",
        "tool_call",
        "reasoning",
        "done",
    ]
    text: str
    tool_call: ToolCall
    usage: dict

@dataclass
class LLMChatComplete:
    """Complete chat response result.
    
    Attributes:
        content: Complete response text content.
        reasoning_content: Complete reasoning process (if model supports it).
        tool_calls: List of tool calls.
    """
    content: str = ""
    reasoning_content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)

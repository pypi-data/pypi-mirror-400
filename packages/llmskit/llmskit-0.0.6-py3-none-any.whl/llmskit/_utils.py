# -*- coding: UTF-8 -*-
# @Time : 2026/1/2 00:08 
# @Author : 刘洪波
from typing import Iterable, AsyncIterator, Any
from llmskit._types import ToolCall, LLMChatComplete, LLMEvent

def get_llm_chunks(event: LLMEvent, text_chunks: list, reasoning_chunks: list, tools_chunks: dict):
    if event["type"] == "content":
        text_chunks.append(event["text"])
    elif event["type"] == "reasoning":
        reasoning_chunks.append(event["text"])
    elif event["type"] == "tool_call":
        _id, _name, _arguments = event["tool_call"]["id"], event["tool_call"]["name"], event["tool_call"][
            "arguments"]
        if _id in tools_chunks:
            if _name:
                tools_chunks[_id]['name'].append(_name)
            if _arguments:
                tools_chunks[_id]['arguments'].append(_arguments)
        else:
            tools_chunks[_id] = {'name': [_name] if _name else [], 'arguments': [_arguments] if _arguments else []}
    return text_chunks, reasoning_chunks, tools_chunks

def merge_llm_chunks(text_chunks: list, reasoning_chunks: list, tools_chunks: dict):
    tool_calls = []
    for _id, tool in tools_chunks.items():
        tool_calls.append(ToolCall(id=_id, name="".join(tool["name"]), arguments="".join(tool["arguments"])))
    content = "".join(text_chunks)
    reasoning_content = "".join(reasoning_chunks)
    if content and not reasoning_content:
        if content.startswith("<think>") and "</think>" in content:
            _content = content.split("</think>")
            content, reasoning_content = _content[1], _content[0].replace("<think>", "")
    return LLMChatComplete(
        content=content,
        reasoning_content=reasoning_content,
        tool_calls=tool_calls
    )


def chat_complete(llm_stream_generator: Iterable[Any]) -> Any:
    """Synchronously get complete chat response (non-streaming).

    Internally calls the stream method and collects all events to return complete results.

    Args:
        llm_stream_generator: LLM stream generator
    Returns:
        LLMChatComplete: Object containing complete response content, reasoning process, and tool calls.
    """
    text_chunks, reasoning_chunks, tools_chunks = [], [], {}
    # Iterate over synchronous stream
    for event in llm_stream_generator:
        text_chunks, reasoning_chunks, tools_chunks = get_llm_chunks(event, text_chunks, reasoning_chunks, tools_chunks)
    return merge_llm_chunks(text_chunks, reasoning_chunks, tools_chunks)


async def async_chat_complete(async_llm_stream_generator: AsyncIterator[Any]) -> Any:
    """Synchronously get complete chat response (non-streaming).

    Internally calls the stream method and collects all events to return complete results.

    Args:
        async_llm_stream_generator: LLM stream generator
    Returns:
        LLMChatComplete: Object containing complete response content, reasoning process, and tool calls.
    """
    text_chunks, reasoning_chunks, tools_chunks = [], [], {}
    # Iterate over synchronous stream
    async for event in async_llm_stream_generator:
        text_chunks, reasoning_chunks, tools_chunks = get_llm_chunks(event, text_chunks, reasoning_chunks, tools_chunks)
    return merge_llm_chunks(text_chunks, reasoning_chunks, tools_chunks)

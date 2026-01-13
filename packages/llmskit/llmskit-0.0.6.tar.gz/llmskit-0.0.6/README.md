# llmskit
统一的LLM客户端与工具

## Documentation

完整的 API 文档待补充

## Installation

```bash
pip install llmskit
```

## Api
```python
# 调用embedding
from llmskit import OpenAIEmbeddings, AsyncOpenAIEmbeddings
# 调用LLM
from llmskit import ChatLLM, AsyncChatLLM
```

## Usage
```python
from llmskit.chat import ChatLLM


chat = ChatLLM.from_openai(model="", base_url="")
messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "who are you?"}
        ]

response = chat.complete(messages=messages)

print(response)
# 输出
# LLMChatComplete(content='I am Qwen, a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. I can answer questions, create text such as stories, official documents, emails, scripts, perform logical reasoning, coding, and more. I can also express opinions and play games. I am trained on a vast amount of internet text and have extensive knowledge and strong language understanding capabilities. How can I assist you today?', reasoning_content='', tool_calls=[])

print(response.content)
```


## Todo
使用新版的返回格式
```python
import openai
openai.responses.create()
```

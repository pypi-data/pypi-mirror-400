from __future__ import annotations
from typing import TypedDict, List, Literal, Optional, Any

from .core.http import HttpClient


AllowedModel = Literal[
    "bedrock/amazon.nova-pro-v1",
    "openai/gpt-4o",
    "anthropic/claude-3-5-sonnet",
    "cohere/command-r-plus",
]


class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class LlmRequest(TypedDict, total=False):
    model: AllowedModel | str
    messages: List[ChatMessage]
    temperature: float
    maxTokens: int
    stream: bool


class Llm:
    def __init__(self, http: HttpClient):
        self.http = http

    def llm_call(self, body: LlmRequest) -> Any:
        """
        Execute an LLM call.

        POST /llm/execute/calls

        Example:
            {
              "model": "bedrock/amazon.nova-pro-v1",
              "messages": [{"role": "user", "content": "Hello, how are you?"}]
            }
        """
        return self.http.request("POST", "/llm/execute/calls", json=body)



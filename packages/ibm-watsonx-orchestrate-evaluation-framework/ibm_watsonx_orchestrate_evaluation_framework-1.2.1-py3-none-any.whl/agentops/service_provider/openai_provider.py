from typing import Dict, List, Optional

import openai
from openai import ChatCompletion

from agentops.service_provider.provider import Provider


class OpenAIProvider(Provider):
    """Simple OpenAI client wrapper for prompt optimization."""

    def __init__(
        self,
        model: str = "gpt-4.1",
        api_key: str = None,
    ):
        super().__init__()
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        params: dict = {},
    ) -> ChatCompletion:
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
        )

    def encode(self, sentences: List[str]) -> List[list]:
        raise NotImplementedError(
            "encode is not implemented for OpenAIProvider"
        )

import os
from typing import Generator

import openai

from .base import LLMClient

openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIClient(LLMClient):
    def __init__(self, model: str = "gpt-4.1"):
        self.model = model

    def complete(self, messages: list[dict]) -> str:
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def stream(self, messages: list[dict]) -> Generator[str, None, None]:
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            stream=True
        )
        for chunk in response:
            yield chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""


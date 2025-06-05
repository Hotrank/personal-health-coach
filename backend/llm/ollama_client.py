from typing import Generator

from ollama import chat

from .base import LLMClient


class OllamaClient(LLMClient):
    def __init__(self, model: str = "llama3"):
        self.model = model

    def complete(self, messages: list[dict]) -> str:
        response = chat(
            model=self.model,
            messages=messages,
            stream=False,
        )
        return response["message"]["content"]

    def stream(self, messages: list[dict]) -> Generator[str, None, None]:
        stream = chat(
            model=self.model,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            yield chunk["message"]["content"]

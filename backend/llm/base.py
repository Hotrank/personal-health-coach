from abc import ABC, abstractmethod
from typing import Generator


class LLMClient(ABC):
    @abstractmethod
    def complete(self, messages: list[dict]) -> str:
        pass

    @abstractmethod
    def stream(self, messages: list[dict]) -> Generator[str, None, None]:
        pass

from .base import LLMClient


def get_llm_client(provider: str) -> LLMClient:
    """
    Factory function to get the appropriate LLM client based on the provider.

    Args:
        provider (str): The name of the LLM provider (e.g., "openai", "ollama").

    Returns:
        LLMClient: An instance of the appropriate LLM client.
    """
    if provider == "openai":
        from .openai_client import OpenAIClient

        return OpenAIClient()
    elif provider == "ollama":
        from .ollama_client import OllamaClient

        return OllamaClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

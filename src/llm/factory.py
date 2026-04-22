from .base import BaseLLM


def get_llm(provider: str = "anthropic", **kwargs) -> BaseLLM:
    """Factory function to get an LLM client by provider name."""
    if provider == "anthropic":
        from .anthropic_client import AnthropicLLM
        return AnthropicLLM(**kwargs)
    elif provider == "openai":
        from .openai_client import OpenAILLM
        return OpenAILLM(**kwargs)
    elif provider == "ollama":
        from .ollama_client import OllamaLLM
        return OllamaLLM(**kwargs)
    else:
        raise ValueError(
            f"Unknown provider '{provider}'. Available: ['anthropic', 'openai', 'ollama']"
        )

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def __call__(self, messages: list[dict], stop_sequences: list[str] | None = None) -> str:
        """Send messages and return text response."""
        pass

    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name string."""
        pass

from abc import ABC, abstractmethod


class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name used in action parsing."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description included in the system prompt."""
        pass

    @abstractmethod
    def __call__(self, input: str) -> str:
        """Execute the tool and return a string result."""
        pass

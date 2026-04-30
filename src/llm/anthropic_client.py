import anthropic
from dotenv import load_dotenv
from .base import BaseLLM

load_dotenv()


class AnthropicLLM(BaseLLM):
    def __init__(self, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024):
        self.client = anthropic.Anthropic()  # Reads ANTHROPIC_API_KEY from env
        self.model = model
        self.max_tokens = max_tokens

    def __call__(self, messages: list[dict], stop_sequences: list[str] | None = None) -> str:
        kwargs = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            system=messages[0]["content"],
            messages=messages[1:],
        )
        if stop_sequences:
            kwargs["stop_sequences"] = stop_sequences
        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def provider_name(self) -> str:
        return "anthropic"

from openai import OpenAI
from .base import BaseLLM


class OpenAILLM(BaseLLM):
    def __init__(self, model: str = "gpt-4o", max_tokens: int = 1024):
        self.client = OpenAI()  # Reads OPENAI_API_KEY from env
        self.model = model
        self.max_tokens = max_tokens

    def __call__(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,  # OpenAI uses system role inline
        )
        return response.choices[0].message.content

    def provider_name(self) -> str:
        return "openai"

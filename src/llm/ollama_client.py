import httpx
from .base import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def __call__(self, messages: list[dict], stop_sequences: list[str] | None = None) -> str:
        payload = {"model": self.model, "messages": messages, "stream": False}
        if stop_sequences:
            payload["options"] = {"stop": stop_sequences}
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json=payload,
        )
        return response.json()["message"]["content"]

    def provider_name(self) -> str:
        return "ollama"

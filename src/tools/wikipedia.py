import httpx
from .base import Tool


class WikipediaTool(Tool):
    @property
    def name(self) -> str:
        return "wikipedia"

    @property
    def description(self) -> str:
        return "Search Wikipedia for a topic. Returns a summary extract."

    def __call__(self, input: str) -> str:
        try:
            response = httpx.get(
                "https://en.wikipedia.org/api/rest_v1/page/summary/" + input,
                headers={"User-Agent": "agentic-ai/0.1 (https://github.com/agentic-ai)"},
                follow_redirects=True,
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("extract", "No extract found.")
            return f"Wikipedia error: HTTP {response.status_code}"
        except Exception as e:
            return f"Wikipedia error: {e}"

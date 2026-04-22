from .base import Tool


class WeatherTool(Tool):
    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "Get the current weather for a location. (Mock implementation for demos.)"

    def __call__(self, input: str) -> str:
        return f"Weather in {input}: 72°F, partly cloudy, humidity 45%."

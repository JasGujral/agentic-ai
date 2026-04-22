from .base import Tool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __getitem__(self, name: str) -> Tool:
        return self._tools[name]

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def descriptions(self) -> str:
        """Generate tool descriptions for the system prompt."""
        lines = []
        for tool in self._tools.values():
            lines.append(f"{tool.name}: {tool.description}")
        return "\n\n".join(lines)

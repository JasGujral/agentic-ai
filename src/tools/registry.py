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


class Registry:
    """Article 2 typed registry: exposes tool contracts to the model and dispatches typed calls."""

    def __init__(self, tools: list[Tool]):
        self._tools = {t.name: t for t in tools}

    def describe(self) -> str:
        # exactly what the model is shown when it decides
        return "\n".join(
            f"- {t.name}({', '.join(t.Args.model_fields)}): {t.description}"
            for t in self._tools.values()
        )

    def dispatch(self, tool: str, args: dict) -> str:
        if tool not in self._tools:
            return f"error: unknown tool '{tool}'"
        t = self._tools[tool]
        try:
            validated = t.Args.model_validate(args)     # untyped dict -> checked Args
        except Exception as e:
            return f"error: invalid args for {tool}: {e.__class__.__name__}"
        return t(validated)

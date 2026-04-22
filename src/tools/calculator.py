import re
from .base import Tool


class CalculatorTool(Tool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Evaluate a mathematical expression. Supports +, -, *, /, **, (, )."

    def __call__(self, input: str) -> str:
        # Only allow safe characters
        if not re.match(r'^[\d\s\+\-\*/\.\(\)\*]+$', input):
            return f"Error: invalid expression '{input}'"
        try:
            result = eval(input, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"Error: {e}"

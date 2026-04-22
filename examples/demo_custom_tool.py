"""Demo: Adding a custom tool to the agent.

Shows how to create a new tool by subclassing Tool and registering it.
Uses the mock weather tool + calculator. No API key needed for the tool itself,
but you still need an LLM provider key.
"""

from src.llm.factory import get_llm
from src.tools.base import Tool
from src.tools.calculator import CalculatorTool
from src.tools.weather import WeatherTool
from src.tools.registry import ToolRegistry
from src.prompts.react import build_react_prompt
from src.loop.agent import agent


# Step 1: Define a custom tool by subclassing Tool
class UnitConverterTool(Tool):
    @property
    def name(self) -> str:
        return "unit_converter"

    @property
    def description(self) -> str:
        return "Convert between units. Input format: 'value from_unit to_unit' (e.g., '100 celsius fahrenheit')."

    def __call__(self, input: str) -> str:
        parts = input.strip().split()
        if len(parts) != 3:
            return "Error: expected format 'value from_unit to_unit'"

        try:
            value = float(parts[0])
        except ValueError:
            return f"Error: '{parts[0]}' is not a number"

        from_unit = parts[1].lower()
        to_unit = parts[2].lower()

        # Simple conversion table
        if from_unit == "celsius" and to_unit == "fahrenheit":
            return str(value * 9 / 5 + 32)
        elif from_unit == "fahrenheit" and to_unit == "celsius":
            return str((value - 32) * 5 / 9)
        elif from_unit == "km" and to_unit == "miles":
            return str(value * 0.621371)
        elif from_unit == "miles" and to_unit == "km":
            return str(value * 1.60934)
        else:
            return f"Error: unsupported conversion from {from_unit} to {to_unit}"


# Step 2: Register tools (including the custom one)
tools = ToolRegistry()
tools.register(CalculatorTool())
tools.register(WeatherTool())
tools.register(UnitConverterTool())

# Step 3: Build a dynamic prompt that includes all registered tools
system_prompt = build_react_prompt(tools)

# Step 4: Run the agent
llm = get_llm("anthropic")
answer = agent(
    llm=llm,
    tools=tools,
    query="What is 100 degrees Celsius in Fahrenheit?",
    system_prompt=system_prompt,
)
print(f"\nAnswer: {answer}")

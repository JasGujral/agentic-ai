"""Basic demo: Eiffel Tower vs Empire State Building age comparison.

Uses Anthropic Claude as the LLM provider.
Requires ANTHROPIC_API_KEY environment variable.
"""

from src.llm.factory import get_llm
from src.tools.wikipedia import WikipediaTool
from src.tools.calculator import CalculatorTool
from src.tools.registry import ToolRegistry
from src.loop.agent import agent

llm = get_llm("anthropic")
tools = ToolRegistry()
tools.register(WikipediaTool())
tools.register(CalculatorTool())

answer = agent(
    llm=llm,
    tools=tools,
    query="How many years older is the Eiffel Tower than the Empire State Building?",
)
print(f"\nAnswer: {answer}")

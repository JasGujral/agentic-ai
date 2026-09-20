"""The seven components assembled into one runnable agent."""
from src.tools.registry import Registry
from src.tools.builtins import Calculator, SalesDB
from src.guardrails.guard import Guarded
from src.orchestration.agent import Agent

tools = Guarded(Registry([Calculator(), SalesDB()]),
                approve=lambda tool, args: input(f"approve {tool}{args}? ") == "y")

agent = Agent(tools=tools, max_steps=8)

if __name__ == "__main__":
    answer = agent.run(
        goal="Summarize this week's EMEA sales for the team",
        criteria="one sentence, cites the EMEA figure",
    )
    print(answer)

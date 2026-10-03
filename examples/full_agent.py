"""The seven components assembled into one runnable agent."""
from src.tools.registry import Registry
from src.tools.builtins import Calculator, SalesDB
from src.guardrails.guard import Guarded
from src.evaluation.check import SourceFigureCited
from src.orchestration.agent import Agent

registry = Registry([Calculator(), SalesDB()])
tools = Guarded(registry, approve=lambda tool, args: input(f"approve {tool}{args}? ") == "y")

agent = Agent(tools=tools, max_steps=8)

if __name__ == "__main__":
    answer = agent.run(
        goal="Summarize this week's EMEA sales for the team",
        criteria="one sentence, cites the EMEA figure",
        # the evaluator re-queries the source and confirms the figure — ground truth, not an opinion
        checks=(SourceFigureCited(registry, "sales_db", {"region": "EMEA"}),),
    )
    print(answer)

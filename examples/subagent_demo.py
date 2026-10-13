"""Article 3 demo: the same question, answered three ways, with one token ledger.

  (a) alone     the Article 2 agent reads the repo itself
  (b) explorer  the agent delegates reading to a subagent and gets back a summary
  (c) fan-out   three independent questions, three subagents in parallel

The corpus is this repo's own src/ tree, so the run is reproducible from the clone.
Requires ANTHROPIC_API_KEY. Run:  uv run python examples/subagent_demo.py [a|b|c]
"""
import sys
import time
from pathlib import Path

from src.orchestration.agent import Agent
from src.subagents.fanout import FanOut
from src.subagents.ledger import LedgeredMemory, TokenLedger
from src.subagents.spawn import Subagent
from src.subagents.workspace import workspace_tools
from src.tools.registry import Registry

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "src"     # the code only: no docs, no demos that contain the answer
BUDGET = 16_000          # the parent's context budget, in tokens

QUESTION = ("How does this repo's agent keep its context under budget? Name the module and "
            "function, and say what happens to the oldest transcript items when the budget is full.")
CRITERIA = "names the file and function, explains eviction, cites file paths"

FANOUT_QUESTION = ("Answer three independent questions about this repo, citing file paths: "
                   "(1) how working memory stays under its token budget; "
                   "(2) which tools the guardrails deny outright; "
                   "(3) which model the evaluation judge uses by default.")


def explorer(ledger: TokenLedger) -> Subagent:
    return Subagent("explore",
                    "Delegate a read-only question about the repo. A fresh agent searches and "
                    "reads the code, then returns a short summary with file pointers.",
                    tools=workspace_tools(CORPUS), ledger=ledger, max_steps=8)


def run(mode: str) -> None:
    ledger = TokenLedger()
    memory = LedgeredMemory("parent", ledger, budget=BUDGET)
    question = QUESTION
    if mode == "a":                                    # the parent holds the read tools itself
        tools = workspace_tools(CORPUS)
    elif mode == "b":                                  # the parent holds one tool: the subagent
        tools = [explorer(ledger)]
    else:                                              # the parent may fan out
        ex = explorer(ledger)
        tools = [ex, FanOut(ex, max_parallel=3)]
        question = FANOUT_QUESTION

    agent = Agent(Registry(tools), max_steps=12, memory=memory)
    t0 = time.perf_counter()
    answer = agent.run(question, CRITERIA, ask_user=lambda q: "no preference; use your judgement")
    elapsed = time.perf_counter() - t0

    print(f"\n=== run ({mode}) ===\n{answer}\n")
    print(ledger.report())
    p = ledger.by_agent["parent"]
    print(f"\nparent peak context {p.peak_context:,} tokens · all agents {ledger.total():,} "
          f"tokens · {elapsed:.1f}s")


if __name__ == "__main__":
    for mode in (sys.argv[1:] or ["a", "b", "c"]):
        run(mode)

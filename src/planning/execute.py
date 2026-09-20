"""Adaptive execution: run a small step, check it, bank the win, or re-plan.

Illustrative on its own: `execute` (the tools call, Section 3) and `evaluate`
(the evaluation gate, Section 4) are the seams this pattern sits between. The
fully-wired production loop is src/orchestration/agent.py.
"""
from src.planning.planner import make_plan

MAX_REPLANS = 2


def run(goal: str, tools: list[str]) -> list[str]:
    wins: list[str] = []                           # confirmed results, in order
    for _ in range(MAX_REPLANS + 1):
        plan = make_plan(goal, tools, done=wins)   # (re)plan the remaining work
        done, failed = set(), False
        while len(done) < len(plan.steps):
            step = plan.ready(done)[0]
            result = execute(step)                 # do one small task      (tools)       # noqa: F821
            if not evaluate(goal, step, result):   # check it in isolation  (evaluation)  # noqa: F821
                failed = True
                break                              # re-plan from what's confirmed
            done.add(step.id)
            wins.append(result)                    # bank the win
        if not failed:
            return wins
    raise RuntimeError("re-plan budget exhausted")

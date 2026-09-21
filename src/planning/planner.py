"""Produce a plan in one constrained call: the model fills the Plan schema."""
import os

import instructor
from anthropic import Anthropic

from src.planning.plan import Plan

client = instructor.from_anthropic(Anthropic())
MODEL = os.getenv("AGENT_MODEL", "claude-sonnet-4-5")   # override via env; any capable model works


def make_plan(goal: str, tools: list[str], done: list[str] | None = None) -> Plan:
    context = f"\nAlready confirmed: {done}" if done else ""
    return client.messages.create(
        model=MODEL,
        max_tokens=1024,
        response_model=Plan,          # instructor validates + retries against the schema
        messages=[{"role": "user",
                   "content": f"Goal: {goal}\nAvailable tools: {tools}{context}\n"
                              f"Produce an ordered plan for the remaining work. For each "
                              f"step, set `success` to what a good result for that step looks "
                              f"like, and `depends_on` where a step needs an earlier result."}],
    )

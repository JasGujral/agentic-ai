"""A subagent is a tool whose implementation is another agent loop.

It runs Article 2's Agent in a FRESH context window, and hands back a typed
Summary. The transcript, with every file it read, stays inside.
Many agents can read; one agent writes.
"""
import itertools
import os

import instructor
from anthropic import Anthropic
from pydantic import BaseModel, Field

from src.memory.memory import Memory
from src.orchestration.agent import Agent
from src.subagents.ledger import LedgeredMemory, TokenLedger
from src.subagents.summary import Summary
from src.tools.base import Tool
from src.tools.registry import Registry

client = instructor.from_anthropic(Anthropic())
MODEL = os.getenv("SUBAGENT_MODEL", os.getenv("AGENT_MODEL", "claude-sonnet-4-5"))


def _no_user(question: str) -> str:
    # a subagent has no user to ask; only the parent does
    return "No user is reachable from a subagent. Make a reasonable assumption, state it, and continue."


def summarize(brief: str, answer: str, transcript: list[str]) -> Summary:
    """Compress the subagent's whole run into the contract. This is the only exit."""
    return client.messages.create(
        model=MODEL,
        max_tokens=1024,
        response_model=Summary,
        max_retries=2,
        messages=[{"role": "user",
                   "content": f"Brief: {brief}\nFinal answer: {answer}\n"
                              f"Transcript of the work:\n" + "\n".join(transcript) +
                              "\n\nSummarize for the agent that sent the brief. Point to files "
                              "and line ranges instead of quoting them."}],
    )


class Subagent(Tool):
    read_only = True                       # it only ever holds read-only tools (checked below)

    class Args(BaseModel):
        brief: str = Field(description="A self-contained task: what to find and why. "
                                       "The subagent sees ONLY this text, none of your context.")

    def __init__(self, name: str, description: str, tools: list[Tool],
                 ledger: TokenLedger | None = None, max_steps: int = 8, budget: int = 8000):
        writers = [t.name for t in tools if not t.read_only]
        if writers:                        # least privilege, enforced in code
            raise ValueError(f"subagents read, the parent writes; not read-only: {writers}")
        self.name, self.description = name, description
        self.tools, self.max_steps, self.budget = tools, max_steps, budget
        self.ledger = ledger or TokenLedger()
        self._ids = itertools.count(1)

    def __call__(self, args: Args) -> str:
        label = f"{self.name}#{next(self._ids)}"
        memory: Memory = LedgeredMemory(label, self.ledger, budget=self.budget)   # a fresh window
        child = Agent(tools=Registry(self.tools), max_steps=self.max_steps, memory=memory)
        answer = child.run(goal=args.brief,
                           criteria="answers the brief, citing file paths as evidence",
                           ask_user=_no_user)
        return summarize(args.brief, answer, memory.history).render()   # only the summary crosses

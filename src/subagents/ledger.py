"""One token ledger across every agent in the run.

Two numbers matter, and they move in opposite directions:
  - the PARENT's context: what the agent that makes the decisions has to read each step
  - the TOTAL: what every agent together sends to the model, i.e. what you pay for
Isolation shrinks the first. It never shrinks the second.
"""
import threading
from dataclasses import dataclass

from src.memory.memory import Memory, n_tokens


@dataclass
class Usage:
    steps: int = 0
    sent: int = 0              # context tokens sent, summed over steps (~ input tokens billed)
    peak_context: int = 0      # largest single context this agent was shown
    peak_transcript: int = 0   # what that context would be with no budget at all
    evicted: int = 0           # most transcript items ever pushed out of the window


class TokenLedger:
    def __init__(self):
        self.by_agent: dict[str, Usage] = {}
        self._lock = threading.Lock()                   # subagents may run in parallel threads

    def observe(self, agent: str, context: int, transcript: int, evicted: int) -> None:
        with self._lock:
            u = self.by_agent.setdefault(agent, Usage())
            u.steps += 1
            u.sent += context
            u.peak_context = max(u.peak_context, context)
            u.peak_transcript = max(u.peak_transcript, transcript)
            u.evicted = max(u.evicted, evicted)

    def total(self) -> int:
        return sum(u.sent for u in self.by_agent.values())

    def report(self) -> str:
        rows = [f"{'agent':<14}{'steps':>6}{'peak ctx':>10}{'transcript':>12}{'evicted':>9}{'sent':>10}"]
        for name, u in self.by_agent.items():
            rows.append(f"{name:<14}{u.steps:>6}{u.peak_context:>10,}{u.peak_transcript:>12,}"
                        f"{u.evicted:>9}{u.sent:>10,}")
        rows.append(f"{'TOTAL':<14}{'':>6}{'':>10}{'':>12}{'':>9}{self.total():>10,}")
        return "\n".join(rows)


class LedgeredMemory(Memory):
    """Article 2's Memory, reporting every context it builds to the ledger."""

    def __init__(self, agent: str, ledger: TokenLedger, **kw):
        super().__init__(**kw)
        self.agent, self.ledger = agent, ledger

    def context(self, query: str = "") -> list[str]:
        ctx = super().context(query)
        kept = sum(1 for x in ctx if x in self.history)             # transcript items still in the window
        self.ledger.observe(self.agent,
                            context=sum(n_tokens(x) for x in ctx),
                            transcript=sum(n_tokens(x) for x in self.history),
                            evicted=len(self.history) - kept)
        return ctx

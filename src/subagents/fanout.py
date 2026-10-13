"""Parallel fan-out: independent reads, each in its own subagent, at the same time.

The Article 2 Agent is synchronous, so each subagent runs on a worker thread.
(An asyncio version would wrap the same threads with asyncio.to_thread.)
Capped, because an uncapped fan-out is a bill with no ceiling.
"""
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel, Field

from src.subagents.spawn import Subagent
from src.tools.base import Tool


class FanOut(Tool):
    name = "fan_out"
    read_only = True

    class Args(BaseModel):
        briefs: str = Field(description="Independent, self-contained briefs, ONE PER LINE. "
                                        "Each runs in its own subagent, in parallel.")

    def __init__(self, subagent: Subagent, max_parallel: int = 3):
        self.subagent, self.max_parallel = subagent, max_parallel
        self.description = (f"Run up to {max_parallel} independent '{subagent.name}' subagents "
                            f"in parallel and get one summary back from each.")

    def __call__(self, args: Args) -> str:
        briefs = [b.strip() for b in args.briefs.splitlines() if b.strip()]
        dropped = briefs[self.max_parallel:]
        briefs = briefs[: self.max_parallel]                      # the fan-out cap
        with ThreadPoolExecutor(max_workers=self.max_parallel) as pool:
            results = list(pool.map(lambda b: self.subagent(Subagent.Args(brief=b)), briefs))
        out = [f"[{i}] {b}\n{r}" for i, (b, r) in enumerate(zip(briefs, results), 1)]
        if dropped:
            out.append(f"(not run, over the cap of {self.max_parallel}: {dropped})")
        return "\n\n".join(out)

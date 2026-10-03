"""Grounded checks: validate a result against the world, not against an opinion.

The judge in grader.py grades on plausibility — and a confident wrong answer is
plausible. A *check* confirms against ground truth instead: re-run the query, run
the code, hit the API. Checks are deterministic and authoritative — when one
fails, the result is wrong, and there is no point asking a model to disagree.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.tools.registry import Registry


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    reason: str


class Check(ABC):
    """A verifier that reaches into the world to confirm a result."""

    @abstractmethod
    def __call__(self, goal: str, result: str) -> CheckResult:
        """Confirm `result` against ground truth; a failed check is authoritative."""


class SourceFigureCited(Check):
    """Re-derive a figure from its source tool and confirm the result cites it.

    The actor can hallucinate a number; the source tool cannot. This is the
    evaluator using its *own* tool to check reality — not a second opinion.
    """

    def __init__(self, tools: Registry, tool: str, args: dict):
        self.tools, self.tool, self.args = tools, tool, args

    def __call__(self, goal: str, result: str) -> CheckResult:
        truth = self.tools.dispatch(self.tool, self.args)      # ground truth, straight from the world
        figure = truth.split(":")[-1].strip()                  # "EMEA: 128000" -> "128000"
        if figure and figure in result.replace(",", ""):       # normalise "128,000" -> "128000"
            return CheckResult(True, f"result cites the source figure ({figure})")
        return CheckResult(False, f"source says {figure!r}; result does not cite it")

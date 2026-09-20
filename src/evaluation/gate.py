"""Turn a soft verdict into a hard decision with a tunable pass mark."""
from src.evaluation.grader import grade

PASS_MARK = 0.7   # the dial: raise it for stricter acceptance


def evaluate(goal: str, result: str, criteria: str) -> tuple[bool, str]:
    verdict = grade(goal, result, criteria)
    ok = verdict.passed and verdict.score >= PASS_MARK
    return ok, verdict.reason      # reason becomes feedback on a fail

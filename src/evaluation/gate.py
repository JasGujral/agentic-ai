"""Turn grounded checks and a soft verdict into one decision.

Two kinds of grading, in order of trust: hard checks that confirm against the
world (authoritative), then a soft judge for whatever is left to taste.
"""
from src.evaluation.grader import grade
from src.evaluation.check import Check

PASS_MARK = 0.7   # the dial for the soft judge: raise it for stricter acceptance


def evaluate(goal: str, result: str, criteria: str,
             checks: tuple[Check, ...] = ()) -> tuple[bool, str]:
    for check in checks:                          # hard checks first — grounded, authoritative
        outcome = check(goal, result)
        if not outcome.passed:
            return False, f"check failed: {outcome.reason}"   # the world disagrees; don't ask the model
    verdict = grade(goal, result, criteria)       # soft check — subjective quality, scored
    ok = verdict.passed and verdict.score >= PASS_MARK
    return ok, verdict.reason      # reason becomes feedback on a fail

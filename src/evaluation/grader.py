"""LLM-as-judge on a SEPARATE model: never let the actor grade its own work."""
import instructor
from anthropic import Anthropic

from src.evaluation.verdict import Verdict

judge = instructor.from_anthropic(Anthropic())
JUDGE_MODEL = "claude-opus-4-1"   # a separate, stronger model — never the actor's own


def grade(goal: str, result: str, criteria: str) -> Verdict:
    return judge.messages.create(
        model=JUDGE_MODEL,
        max_tokens=512,
        response_model=Verdict,
        messages=[{"role": "user",
                   "content": f"Goal: {goal}\nCriteria: {criteria}\n"
                              f"Result to grade:\n{result}\n\n"
                              f"Grade the result against the criteria."}],
    )

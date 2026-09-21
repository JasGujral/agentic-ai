"""The reasoning engine: constrain the model to emit a typed, validated Decision."""
import os

import instructor
from anthropic import Anthropic, APIConnectionError, RateLimitError
from tenacity import (retry, retry_if_exception_type,
                      stop_after_attempt, wait_exponential)

from src.reasoning.decision import Decision

client = instructor.from_anthropic(Anthropic())
MODEL = os.getenv("AGENT_MODEL", "claude-sonnet-4-5")   # override via env; any capable model works


def decide(goal: str, tools, history: str = "") -> Decision:
    """Ask the model for the next step as a ToolCall or Final (instructor validates + re-asks)."""
    return client.messages.create(
        model=MODEL,
        max_tokens=1024,
        response_model=Decision,   # the model must return a ToolCall or a Final
        max_retries=2,             # re-ask on a ValidationError
        messages=[{"role": "user",
                   "content": f"Goal: {goal}\nTools: {tools}\n{history}"
                              f"Decide the next step: call a tool, or give the final answer."}],
    )


@retry(
    retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
    wait=wait_exponential(min=1, max=30),   # 1s, 2s, 4s, ... capped at 30s
    stop=stop_after_attempt(4),
)
def decide_resilient(goal: str, tools, history: str = "") -> Decision:
    """decide(), wrapped so a transient network failure is retried with backoff."""
    return decide(goal, tools, history)

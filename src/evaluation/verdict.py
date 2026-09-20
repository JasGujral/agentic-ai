"""A verdict is typed too: did it pass, how well, and why."""
from pydantic import BaseModel, Field


class Verdict(BaseModel):
    passed: bool = Field(description="Did the result meet the criteria?")
    score: float = Field(ge=0.0, le=1.0, description="How well, from 0 to 1")
    reason: str = Field(description="One sentence: what's missing, or why it passed")

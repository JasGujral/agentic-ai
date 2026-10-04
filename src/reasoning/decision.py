"""A decision the reasoning engine returns: a typed ToolCall, Clarify, or Final, not prose."""
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    kind: Literal["tool_call"] = "tool_call"
    tool: str = Field(description="Name of the tool to invoke")
    args: dict[str, str] = Field(default_factory=dict, description="Arguments for the tool")


class Clarify(BaseModel):
    kind: Literal["clarify"] = "clarify"
    question: str = Field(description="A question to ask the user when the goal is ambiguous")


class Final(BaseModel):
    kind: Literal["final"] = "final"
    answer: str = Field(description="The final answer to the goal")


# a decision is exactly one of the three, discriminated on `kind`
Decision = Annotated[Union[ToolCall, Clarify, Final], Field(discriminator="kind")]

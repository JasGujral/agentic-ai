"""The contract: what crosses back from a subagent is a typed Summary, never the transcript.

Pointers, not excerpts: the parent gets "where to look", and pulls the lines
itself only if it needs them.
"""
from pydantic import BaseModel, Field


class Pointer(BaseModel):
    path: str = Field(description="File path the finding rests on")
    lines: str = Field(default="", description="Line range, e.g. '41-58'")
    why: str = Field(description="What is there, in a few words")


class Summary(BaseModel):
    answer: str = Field(description="The direct answer to the brief, in 1-3 sentences")
    findings: list[str] = Field(default_factory=list, description="Key facts, one line each, at most 5")
    pointers: list[Pointer] = Field(default_factory=list, description="Where the evidence is, at most 5")
    confidence: float = Field(ge=0.0, le=1.0, description="How sure, from 0 to 1")
    open_questions: list[str] = Field(default_factory=list, description="What the subagent could not settle")

    def render(self) -> str:
        # the ONLY thing the parent sees: compact text, a few hundred tokens
        out = [f"answer: {self.answer}", f"confidence: {self.confidence:.2f}"]
        out += [f"- {f}" for f in self.findings]
        out += [f"@ {p.path}:{p.lines}  {p.why}" for p in self.pointers]
        out += [f"? {q}" for q in self.open_questions]
        return "\n".join(out)

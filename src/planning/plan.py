"""A plan is a validated DAG of steps: a partial order, not a flat list."""
from pydantic import BaseModel, Field, model_validator


class Step(BaseModel):
    id: int
    action: str = Field(description="What to do in this step")
    tool: str = Field(description="Tool this step will call")
    depends_on: list[int] = Field(default_factory=list)   # ids that must finish first


class Plan(BaseModel):
    goal: str
    steps: list[Step]

    @model_validator(mode="after")
    def _check_dag(self):
        ids = {s.id for s in self.steps}
        if len(ids) != len(self.steps):
            raise ValueError("step ids must be unique")
        done = set()
        while len(done) < len(self.steps):                    # topologically drain the graph
            frontier = [s.id for s in self.steps
                        if s.id not in done and set(s.depends_on) <= done]
            if not frontier:                                  # stalled before finishing
                raise ValueError("dependencies form a cycle or reference a missing step")
            done.update(frontier)
        return self

    def ready(self, done: set[int]) -> list[Step]:
        # every step whose dependencies are already satisfied — the runnable frontier
        return [s for s in self.steps if s.id not in done and set(s.depends_on) <= done]

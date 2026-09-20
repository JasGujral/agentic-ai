"""Two typed tools: one pure, one standing in for the outside world."""
from pydantic import BaseModel, Field

from src.tools.base import Tool


class Calculator(Tool):
    name = "calculator"
    description = "Evaluate an arithmetic expression like '19 * 23'."

    class Args(BaseModel):
        expression: str = Field(description="A Python arithmetic expression")

    def __call__(self, args: Args) -> str:
        return str(eval(args.expression, {"__builtins__": {}}))   # illustrative — see guardrails


class SalesDB(Tool):
    name = "sales_db"
    description = "Look up the weekly sales total for a region."

    class Args(BaseModel):
        region: str = Field(description="Region name, e.g. 'EMEA'")

    def __call__(self, args: Args) -> str:
        data = {"EMEA": 128_000, "AMER": 254_000}
        return f"{args.region}: {data.get(args.region, 0)}"

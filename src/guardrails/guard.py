"""Guardrails: pre-act and post-act checks wrapping tool dispatch."""
from src.tools.registry import Registry

DENY_TOOLS = {"delete_db", "wire_transfer"}       # never allowed, whatever the model decides
NEEDS_APPROVAL = {"send_email", "place_order"}    # allowed only if a human says yes


def _leaks_secrets(text: str) -> bool:
    return "BEGIN PRIVATE KEY" in text or "password=" in text


class Guarded:
    """Wraps a Registry, keeping the same describe()/dispatch() interface."""

    def __init__(self, registry: Registry, approve=None):
        self.registry = registry
        self.approve = approve or (lambda tool, args: False)   # default: no approval

    def describe(self) -> str:
        return self.registry.describe()

    def dispatch(self, tool: str, args: dict) -> str:
        if tool in DENY_TOOLS:                                 # pre-act: hard deny
            return f"blocked: '{tool}' is not permitted"
        if tool in NEEDS_APPROVAL and not self.approve(tool, args):   # pre-act: approval gate
            return f"blocked: '{tool}' needs human approval"
        result = self.registry.dispatch(tool, args)            # the real call
        if _leaks_secrets(result):                             # post-act: screen the output
            return "blocked: result withheld (sensitive data)"
        return result

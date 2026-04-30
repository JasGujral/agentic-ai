import re
from dataclasses import dataclass


@dataclass
class Action:
    tool: str
    input: str


def parse(response: str) -> Action | None:
    """Parse an LLM response for an Action or Answer line.

    Returns:
        An Action with tool="Answer" for final answers,
        an Action with tool name and input for tool calls,
        or None if no pattern matches.
    """
    # Check for Action first — if the LLM emits both Action and Answer
    # in one response, we must process the Action (tool call) before the Answer.
    action_match = re.search(r"^Action:\s*(\w+):\s*(.+)$", response, re.MULTILINE)
    if action_match:
        return Action(
            tool=action_match.group(1).strip(),
            input=action_match.group(2).strip(),
        )

    # Check for Answer only when no Action is present
    answer_match = re.search(r"^Answer:\s*(.+)$", response, re.MULTILINE)
    if answer_match:
        return Action(tool="Answer", input=answer_match.group(1).strip())

    return None

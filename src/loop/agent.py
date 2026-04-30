from ..llm.base import BaseLLM
from ..tools.registry import ToolRegistry
from ..prompts.react import SYSTEM_PROMPT
from .parser import parse


def agent(
    llm: BaseLLM,
    tools: ToolRegistry,
    query: str,
    system_prompt: str = SYSTEM_PROMPT,
    max_turns: int = 10,
    verbose: bool = True,
) -> str:
    """Run the ReAct agent loop.

    Args:
        llm: An LLM provider instance.
        tools: A ToolRegistry with available tools.
        query: The user's question.
        system_prompt: The system prompt (defaults to the ReAct prompt).
        max_turns: Maximum number of Thought-Action-Observation cycles.
        verbose: Whether to print the agent's reasoning.

    Returns:
        The final answer string, or a message if max_turns is exceeded.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ]

    for turn in range(max_turns):
        if verbose:
            print(f"\n--- Turn {turn + 1} ---")

        response = llm(messages, stop_sequences=["PAUSE"])

        if verbose:
            print(response)

        action = parse(response)

        if action is None:
            # No action or answer parsed — append and continue
            messages.append({"role": "assistant", "content": response})
            continue

        if action.tool == "Answer":
            if verbose:
                print(f"\nFinal Answer: {action.input}")
            return action.input

        # Execute tool
        if action.tool in tools:
            observation = tools[action.tool](action.input)
        else:
            observation = f"Error: Unknown tool '{action.tool}'"

        if verbose:
            print(f"Observation: {observation}")

        # Append the assistant response and the observation
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    return "Max turns reached without an answer."

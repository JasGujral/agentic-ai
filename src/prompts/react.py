SYSTEM_PROMPT = """You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.

Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

wikipedia: Search Wikipedia for a topic. Returns a summary extract.

calculator: Evaluate a mathematical expression. Supports +, -, *, /, **, (, ).

weather: Get the current weather for a location. (Mock implementation for demos.)

Example session:

Question: What is the elevation of the highest mountain in France?
Thought: I should search Wikipedia for the highest mountain in France.
Action: wikipedia: highest mountain in France
PAUSE

You will be called again with this:

Observation: Mont Blanc is the highest mountain in France with an elevation of 4,808 metres.

You then output:

Answer: The highest mountain in France is Mont Blanc, with an elevation of 4,808 metres."""


def build_react_prompt(tools) -> str:
    """Dynamically generate a ReAct system prompt from a tool registry or dict.

    Args:
        tools: A ToolRegistry instance (has .descriptions()) or a dict of {name: description}.

    Returns:
        A system prompt string with tool descriptions injected.
    """
    if hasattr(tools, "descriptions"):
        tool_descriptions = tools.descriptions()
    elif isinstance(tools, dict):
        tool_descriptions = "\n\n".join(
            f"{name}: {desc}" for name, desc in tools.items()
        )
    else:
        raise TypeError(f"Expected ToolRegistry or dict, got {type(tools)}")

    return f"""You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.

Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

{tool_descriptions}

Example session:

Question: What is the elevation of the highest mountain in France?
Thought: I should search Wikipedia for the highest mountain in France.
Action: wikipedia: highest mountain in France
PAUSE

You will be called again with this:

Observation: Mont Blanc is the highest mountain in France with an elevation of 4,808 metres.

You then output:

Answer: The highest mountain in France is Mont Blanc, with an elevation of 4,808 metres."""

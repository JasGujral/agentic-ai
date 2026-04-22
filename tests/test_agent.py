from unittest.mock import MagicMock
from src.loop.agent import agent
from src.tools.registry import ToolRegistry
from src.tools.calculator import CalculatorTool
from src.tools.wikipedia import WikipediaTool


def make_mock_llm(responses: list[str]):
    """Create a mock LLM that returns scripted responses in sequence."""
    mock = MagicMock()
    mock.side_effect = responses
    mock.provider_name.return_value = "mock"
    return mock


def test_agent_eiffel_tower():
    """Integration test: the Eiffel Tower demo from the article."""
    responses = [
        "Thought: I need to find when the Eiffel Tower was built.\n"
        "Action: wikipedia: Eiffel Tower\nPAUSE",
        "Thought: The Eiffel Tower was built in 1889. Now the Empire State Building.\n"
        "Action: wikipedia: Empire State Building\nPAUSE",
        "Thought: Empire State Building was built in 1931. Let me calculate.\n"
        "Action: calculator: 1931 - 1889\nPAUSE",
        "Answer: The Eiffel Tower is 42 years older than the Empire State Building.",
    ]

    llm = make_mock_llm(responses)
    tools = ToolRegistry()
    tools.register(WikipediaTool())
    tools.register(CalculatorTool())

    # Mock wikipedia to return controlled responses
    from unittest.mock import patch, MagicMock as MM

    wiki_responses = iter([
        "The Eiffel Tower is a wrought-iron lattice tower, constructed from 1887 to 1889.",
        "The Empire State Building is a 102-story Art Deco skyscraper built in 1931.",
    ])

    original_wiki_call = WikipediaTool.__call__

    def mock_wiki(self, input):
        return next(wiki_responses)

    with patch.object(WikipediaTool, "__call__", mock_wiki):
        result = agent(llm=llm, tools=tools, query="How many years older is the Eiffel Tower than the Empire State Building?", verbose=False)

    assert "42" in result
    assert llm.call_count == 4


def test_agent_max_turns():
    """Test that max_turns is respected when LLM never produces an Answer."""
    responses = [
        "Thought: Let me think.\nAction: wikipedia: something\nPAUSE"
    ] * 5

    llm = make_mock_llm(responses)
    tools = ToolRegistry()
    tools.register(WikipediaTool())

    from unittest.mock import patch

    def mock_wiki(self, input):
        return "Some result."

    with patch.object(WikipediaTool, "__call__", mock_wiki):
        result = agent(llm=llm, tools=tools, query="test", max_turns=3, verbose=False)

    assert result == "Max turns reached without an answer."
    assert llm.call_count == 3


def test_agent_unknown_tool():
    """Test that an unknown tool name returns an error observation, not a crash."""
    responses = [
        "Thought: Let me use a tool.\nAction: nonexistent: test\nPAUSE",
        "Answer: I couldn't use that tool.",
    ]

    llm = make_mock_llm(responses)
    tools = ToolRegistry()
    tools.register(CalculatorTool())

    result = agent(llm=llm, tools=tools, query="test", verbose=False)
    assert result == "I couldn't use that tool."
    assert llm.call_count == 2

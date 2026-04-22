from src.loop.parser import parse, Action


def test_parse_answer():
    response = "Answer: The Eiffel Tower is 42 years older."
    action = parse(response)
    assert action == Action(tool="Answer", input="The Eiffel Tower is 42 years older.")


def test_parse_action():
    response = "Thought: I need to search.\nAction: wikipedia: Eiffel Tower\nPAUSE"
    action = parse(response)
    assert action == Action(tool="wikipedia", input="Eiffel Tower")


def test_parse_no_match():
    response = "I'm not sure what to do."
    action = parse(response)
    assert action is None


def test_parse_answer_with_colons():
    response = "Answer: The time is 3:30 PM: confirmed."
    action = parse(response)
    assert action is not None
    assert action.tool == "Answer"
    assert "3:30 PM" in action.input


def test_parse_extra_whitespace():
    response = "Action:  wikipedia:   Eiffel Tower  \nPAUSE"
    action = parse(response)
    assert action is not None
    assert action.tool == "wikipedia"
    assert action.input == "Eiffel Tower"


def test_parse_empty_response():
    action = parse("")
    assert action is None


def test_parse_calculator_action():
    response = "Thought: Let me calculate.\nAction: calculator: 1931 - 1889\nPAUSE"
    action = parse(response)
    assert action == Action(tool="calculator", input="1931 - 1889")

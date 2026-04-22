from unittest.mock import patch, MagicMock


def test_calculator_valid(calculator):
    assert calculator("2 + 2") == "4"


def test_calculator_subtraction(calculator):
    assert calculator("1931 - 1889") == "42"


def test_calculator_complex(calculator):
    assert calculator("(2 + 3) * 4") == "20"


def test_calculator_rejects_invalid(calculator):
    result = calculator("import os")
    assert "Error" in result


def test_calculator_rejects_letters(calculator):
    result = calculator("abc")
    assert "Error" in result


def test_wikipedia_success(wikipedia):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "extract": "The Eiffel Tower is a wrought-iron lattice tower."
    }

    with patch("src.tools.wikipedia.httpx.get", return_value=mock_response):
        result = wikipedia("Eiffel Tower")
        assert "Eiffel Tower" in result
        assert "wrought-iron" in result


def test_wikipedia_http_error(wikipedia):
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("src.tools.wikipedia.httpx.get", return_value=mock_response):
        result = wikipedia("nonexistent_page_xyz")
        assert "error" in result.lower() or "404" in result


def test_weather_returns_string(weather):
    result = weather("New York")
    assert isinstance(result, str)
    assert "New York" in result

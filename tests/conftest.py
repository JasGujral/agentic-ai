import pytest
from src.tools.registry import ToolRegistry
from src.tools.wikipedia import WikipediaTool
from src.tools.calculator import CalculatorTool
from src.tools.weather import WeatherTool


@pytest.fixture
def calculator():
    return CalculatorTool()


@pytest.fixture
def wikipedia():
    return WikipediaTool()


@pytest.fixture
def weather():
    return WeatherTool()


@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(WikipediaTool())
    reg.register(CalculatorTool())
    reg.register(WeatherTool())
    return reg

import pytest
from src.tools.registry import ToolRegistry
from src.tools.calculator import CalculatorTool


def test_register_and_retrieve(registry):
    tool = registry.get("calculator")
    assert tool is not None
    assert tool.name == "calculator"


def test_contains_known(registry):
    assert "calculator" in registry
    assert "wikipedia" in registry
    assert "weather" in registry


def test_contains_unknown(registry):
    assert "nonexistent" not in registry


def test_getitem(registry):
    tool = registry["calculator"]
    assert tool.name == "calculator"


def test_getitem_unknown(registry):
    with pytest.raises(KeyError):
        registry["nonexistent"]


def test_names(registry):
    names = registry.names()
    assert "calculator" in names
    assert "wikipedia" in names
    assert "weather" in names


def test_descriptions(registry):
    desc = registry.descriptions()
    assert "calculator" in desc
    assert "wikipedia" in desc
    assert "weather" in desc


def test_empty_registry():
    reg = ToolRegistry()
    assert reg.names() == []
    assert reg.descriptions() == ""
    assert reg.get("anything") is None

"""Grounded evaluation: a check confirms against the world, and a failing
hard check is authoritative — it short-circuits before the soft judge runs."""
from src.tools.registry import Registry
from src.tools.builtins import SalesDB
from src.evaluation import gate
from src.evaluation.check import SourceFigureCited
from src.evaluation.verdict import Verdict


def _registry() -> Registry:
    return Registry([SalesDB()])


def test_check_passes_when_result_cites_the_source_figure():
    check = SourceFigureCited(_registry(), "sales_db", {"region": "EMEA"})
    assert check("goal", "EMEA sales this week were 128,000.").passed


def test_check_fails_when_result_omits_the_source_figure():
    check = SourceFigureCited(_registry(), "sales_db", {"region": "EMEA"})
    outcome = check("goal", "Sales were strong across the board.")
    assert not outcome.passed
    assert "128000" in outcome.reason


def test_failing_check_short_circuits_before_the_judge(monkeypatch):
    def _never(*args, **kwargs):
        raise AssertionError("the judge must not run once a hard check has failed")
    monkeypatch.setattr(gate, "grade", _never)

    check = SourceFigureCited(_registry(), "sales_db", {"region": "EMEA"})
    ok, reason = gate.evaluate("goal", "no numbers here", "one sentence", checks=(check,))
    assert ok is False
    assert reason.startswith("check failed")


def test_passing_check_then_judge_decides(monkeypatch):
    monkeypatch.setattr(gate, "grade",
                        lambda g, r, c: Verdict(passed=True, score=0.9, reason="clear and cites EMEA"))
    check = SourceFigureCited(_registry(), "sales_db", {"region": "EMEA"})
    ok, reason = gate.evaluate("goal", "EMEA sales this week were 128,000.", "one sentence", checks=(check,))
    assert ok is True

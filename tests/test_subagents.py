"""Subagents: least privilege, fresh windows, summary-only hand-off, the fan-out cap,
and a workspace that cannot be escaped. Runs offline: the model is scripted."""
import pytest
from pydantic import BaseModel

import src.orchestration.agent as orch
import src.subagents.spawn as spawn
from src.planning.plan import Plan, Step
from src.reasoning.decision import Final, ToolCall
from src.subagents.fanout import FanOut
from src.subagents.ledger import LedgeredMemory, TokenLedger
from src.subagents.spawn import Subagent
from src.subagents.summary import Pointer, Summary
from src.subagents.workspace import ReadFile, Workspace, workspace_tools
from src.tools.base import Tool
from src.tools.registry import Registry

BIG = "x" * 4000          # a file read: ~1,000 tokens of observation


@pytest.fixture
def scripted(monkeypatch, tmp_path):
    """A scripted model: read once then answer (subagent), or delegate once then answer (parent)."""
    (tmp_path / "big.py").write_text(BIG)

    def decide(goal, tools, history=""):
        if "explore" in tools or "fan_out" in tools:                 # the parent
            tool = "fan_out" if "fan_out" in tools else "explore"
            if f"{tool}(" in history:
                return Final(answer="done")
            key = "briefs" if tool == "fan_out" else "brief"
            return ToolCall(tool=tool, args={key: "q1\nq2\nq3\nq4\nq5"})
        if "read_file(" in history:                                  # a subagent, second step
            return Final(answer="found it in big.py")
        return ToolCall(tool="read_file", args={"path": "big.py"})

    plan = Plan(goal="g", steps=[Step(id=1, action="a", tool="t", success="s")])
    monkeypatch.setattr(orch, "decide", decide)
    monkeypatch.setattr(orch, "make_plan", lambda *a, **k: plan)
    monkeypatch.setattr(orch, "evaluate", lambda *a, **k: (True, "ok"))
    monkeypatch.setattr(spawn, "summarize", lambda brief, answer, transcript: Summary(
        answer=answer, confidence=0.9, pointers=[Pointer(path="big.py", lines="1", why="the thing")]))
    return tmp_path


class Writer(Tool):
    name, description = "write_file", "writes"

    class Args(BaseModel):
        text: str

    def __call__(self, args):
        return "wrote"


def test_subagent_refuses_write_tools(tmp_path):
    with pytest.raises(ValueError, match="not read-only"):
        Subagent("explore", "d", [ReadFile(Workspace(tmp_path)), Writer()])


def test_only_the_summary_crosses_back(scripted):
    ledger = TokenLedger()
    explorer = Subagent("explore", "explore the repo", workspace_tools(scripted), ledger)
    parent_mem = LedgeredMemory("parent", ledger)
    orch.Agent(Registry([explorer]), memory=parent_mem).run("question", "criteria")

    parent_text = "\n".join(parent_mem.history)
    assert BIG not in parent_text                      # the file read stayed inside the subagent
    assert "@ big.py:1" in parent_text                 # the pointer came back
    assert ledger.by_agent["explore#1"].peak_transcript > ledger.by_agent["parent"].peak_transcript


def test_each_spawn_gets_a_fresh_window(scripted):
    ledger = TokenLedger()
    explorer = Subagent("explore", "d", workspace_tools(scripted), ledger)
    explorer(Subagent.Args(brief="first"))
    explorer(Subagent.Args(brief="second"))
    assert set(ledger.by_agent) == {"explore#1", "explore#2"}
    first, second = ledger.by_agent["explore#1"], ledger.by_agent["explore#2"]
    assert first.peak_transcript == second.peak_transcript   # #2 did not inherit #1's reads


def test_fan_out_is_capped(scripted):
    ledger = TokenLedger()
    explorer = Subagent("explore", "d", workspace_tools(scripted), ledger)
    out = FanOut(explorer, max_parallel=3)(FanOut.Args(briefs="q1\nq2\nq3\nq4\nq5"))
    assert len([a for a in ledger.by_agent if a.startswith("explore#")]) == 3
    assert "over the cap of 3" in out


def test_workspace_cannot_be_escaped(tmp_path):
    out = ReadFile(Workspace(tmp_path))(ReadFile.Args(path="../../etc/passwd"))
    assert out.startswith("error:") and "outside the workspace" in out


def test_ledger_total_is_the_sum_of_all_agents():
    ledger = TokenLedger()
    ledger.observe("parent", context=100, transcript=100, evicted=0)
    ledger.observe("explore#1", context=900, transcript=900, evicted=0)
    assert ledger.total() == 1000
    assert "TOTAL" in ledger.report()

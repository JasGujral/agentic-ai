"""Long-term memory: keyed upsert (dedup + supersede), relevance retrieval,
the token budget, and persistence across sessions via an injected store."""
from src.memory.memory import Memory


def test_duplicate_facts_collapse():
    mem = Memory()
    mem.remember("report figures in EUR")
    mem.remember("report figures in EUR")          # same fact again
    assert list(mem.store.values()) == ["report figures in EUR"]


def test_same_key_supersedes_stale_fact():
    mem = Memory()
    mem.remember("budget is 100k", key="budget")
    mem.remember("budget is 250k", key="budget")   # newer fact, same key
    assert mem.store["budget"] == "budget is 250k"
    assert len(mem.store) == 1


def test_forget_retracts_a_fact():
    mem = Memory()
    mem.remember("temporary note", key="temp")
    mem.forget("temp")
    assert "temp" not in mem.store


def test_retrieval_pulls_the_relevant_fact():
    mem = Memory()
    mem.remember("report figures in EUR", key="currency")
    mem.remember("Acme's fiscal year ends in March", key="fiscal")
    ctx = mem.context(query="which currency for the EUR sales report?")
    assert "report figures in EUR" in ctx
    assert "Acme's fiscal year ends in March" not in ctx   # irrelevant to this query


def test_budget_truncates_working_memory_but_keeps_long_term():
    mem = Memory(budget=50)                        # tiny budget
    mem.remember("report figures in EUR", key="currency")
    for i in range(200):
        mem.add(f"observation number {i} with some filler text to burn tokens")
    ctx = mem.context(query="currency for the report")
    assert "report figures in EUR" in ctx          # long-term fact survives
    assert len(ctx) < 201                           # most of the transcript was dropped


def test_injected_store_persists_across_sessions():
    store: dict[str, str] = {}                     # in prod: a dict backed by a DB or file

    session1 = Memory(store=store)
    session1.remember("report figures in EUR", key="currency")

    session2 = Memory(store=store)                 # fresh run, same store reloaded
    ctx = session2.context(query="currency for the EMEA report")
    assert "report figures in EUR" in ctx          # the preference came back for free

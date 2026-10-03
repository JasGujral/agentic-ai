"""Memory: a token-budgeted window over a transient transcript, plus a durable,
retrievable long-term store.

Two stores, two lifetimes:
  - working memory (`history`) : the running transcript of THIS run. Everything
    lands here; the oldest items fall out of the window once the budget is full.
  - long-term memory (`store`) : durable facts that outlive the run and are
    pulled back only when relevant. This is the part you persist.

What BELONGS in long-term memory (the write policy):
  - stated preferences and constraints   ("report figures in EUR")
  - stable facts about the user or domain ("Acme's fiscal year ends in March")
  - confirmed outcomes worth reusing      ("Q3 EMEA total = 128,000")
  - answers to clarifications             (so the agent never asks the same thing twice)

What NEVER does:
  - the raw transcript (that is working memory's job)
  - one-off, run-local observations with no reuse value
  - secrets, credentials, or anything you would not want surfaced next session

Writes are KEYED: a newer fact supersedes a stale one under the same key, and
duplicates collapse. Pass a dict-like `store` (file- or DB-backed) to persist
across sessions; the default in-memory dict lasts only for the process.
"""
import tiktoken

ENC = tiktoken.get_encoding("cl100k_base")


def n_tokens(text: str) -> int:
    return len(ENC.encode(text))


class Memory:
    def __init__(self, budget: int = 4000, store: dict[str, str] | None = None):
        self.budget = budget
        self.history: list[str] = []                        # working memory: the running transcript
        self.store: dict[str, str] = store if store is not None else {}   # long-term: durable facts

    def add(self, item: str) -> None:
        self.history.append(item)                           # transient: lives only in this run's window

    def remember(self, fact: str, key: str | None = None) -> None:
        self.store[key or fact] = fact                      # keyed upsert: newer supersedes, dupes collapse

    def forget(self, key: str) -> None:
        self.store.pop(key, None)                           # retract a fact that has gone stale

    def context(self, query: str = "") -> list[str]:
        relevant = self._retrieve(query)                    # pull the relevant long-term facts first
        used = sum(n_tokens(x) for x in relevant)
        window: list[str] = []
        for item in reversed(self.history):                 # then recent history, newest first
            t = n_tokens(item)
            if used + t > self.budget:                      # stop before the budget overflows
                break
            window.append(item)
            used += t
        return relevant + list(reversed(window))

    def _retrieve(self, query: str, k: int = 3) -> list[str]:
        # stand-in for embedding search: rank stored facts by word overlap with the query
        q = set(query.lower().split())
        facts = list(self.store.values())
        ranked = sorted(facts, key=lambda f: len(q & set(f.lower().split())), reverse=True)
        return [f for f in ranked[:k] if q & set(f.lower().split())]

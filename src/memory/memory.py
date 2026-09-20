"""Memory manages a token budget: keep recent history in context, retrieve the rest."""
import tiktoken

ENC = tiktoken.get_encoding("cl100k_base")


def n_tokens(text: str) -> int:
    return len(ENC.encode(text))


class Memory:
    def __init__(self, budget: int = 4000):
        self.budget = budget
        self.history: list[str] = []       # working memory: the running transcript
        self.store: list[str] = []         # long-term memory: facts kept outside the window

    def add(self, item: str) -> None:
        self.history.append(item)

    def remember(self, fact: str) -> None:
        self.store.append(fact)

    def context(self, query: str = "") -> list[str]:
        relevant = self._retrieve(query)                    # pull long-term facts first
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
        # stand-in for embedding search: rank facts by word overlap with the query
        q = set(query.lower().split())
        ranked = sorted(self.store, key=lambda f: len(q & set(f.lower().split())), reverse=True)
        return [f for f in ranked[:k] if q & set(f.lower().split())]

# agentic-ai

[![Tests](https://github.com/JasGujral/agentic-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/JasGujral/agentic-ai/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/JasGujral/agentic-ai)](https://github.com/JasGujral/agentic-ai/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/JasGujral/agentic-ai)](https://github.com/JasGujral/agentic-ai/pulls)
[![GitHub stars](https://img.shields.io/github/stars/JasGujral/agentic-ai?style=social)](https://github.com/JasGujral/agentic-ai/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/JasGujral/agentic-ai?style=social)](https://github.com/JasGujral/agentic-ai/network/members)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-Contributor%20Covenant-purple.svg)](CODE_OF_CONDUCT.md)
[![Built from scratch](https://img.shields.io/badge/frameworks-none-orange.svg)](#)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

AI agents from first principles — companion code for the **Agentic AI Builder's Series** on Substack.

No frameworks. No magic. Just math, code, and clear explanations.

---

## Quick Start

> **📖 Reading the series? Clone the branch for the article you're on.**
> Each article has its own branch containing the code for that article **and everything before
> it — nothing after**. So you never meet an abstraction the article hasn't explained yet.
> See [Branches](#branches) below.
>
> ⚠️ **The default branch is `develop`, which is work in progress** — it contains the article
> currently being written. Don't read from it unless you want spoilers. Use the article branch,
> or `main` for the newest published state.

```bash
# 1. Clone the branch for the article you're reading
git clone -b article-01-what-are-agents https://github.com/JasGujral/agentic-ai.git
cd agentic-ai
# (`main` = the newest published article. `develop` runs ahead with unpublished work.)

# 2. Install with uv
uv sync
uv sync --extra anthropic  # or: --extra openai, --extra all

# 3. Set your API key
cp .env.example .env
# Edit .env with your key (loaded automatically via python-dotenv)

# 4. Run the demo
uv run python examples/demo_basic.py
```

---

## Architecture

```
Question
   │
   ▼
┌──────────────────────────────────┐
│          Agent Loop              │
│                                  │
│  ┌─────────┐    ┌────────────┐  │
│  │   LLM   │───▶│   Parser   │  │
│  └─────────┘    └────────────┘  │
│       ▲              │          │
│       │         Action/Answer   │
│       │              │          │
│       │              ▼          │
│  ┌─────────┐    ┌────────────┐  │
│  │ Messages│◀───│   Tools    │  │
│  └─────────┘    └────────────┘  │
│                                  │
└──────────────────────────────────┘
   │
   ▼
 Answer
```

---

## Branches

**One branch per article.** Each article branch is a snapshot of the codebase as it stood when
that article was published — the aggregated code for Articles 1..N, and nothing after. So reading
in order never spoils an abstraction you haven't met yet.

`main` is the newest published state. `develop` runs ahead of it with the article currently being
written.

| Article | Branch | Status |
|---------|--------|--------|
| 1. What Are AI Agents, Really? | `article-01-what-are-agents` | published 2026-04-22 · = `main` |
| 2. What Every Production Agent Is Made Of | *(branch cut at publication)* | in progress on `develop` |

```bash
git clone -b article-01-what-are-agents https://github.com/JasGujral/agentic-ai.git
```

A later article may change an earlier article's abstractions — Article 2 turns Article 1's
string-in/string-out `Tool` into a typed schema, for instance. That is deliberate, and it is
exactly why the snapshots exist: the code grows with the teaching, and readers of an earlier
article stay on a snapshot taken before the change existed.

---

## Article → Code Mapping

| Article | Notebook | Key Modules |
|---------|----------|-------------|
| 1. What Are AI Agents, Really? | `notebooks/01_what_are_agents.ipynb` | `src/llm/`, `src/tools/`, `src/loop/`, `src/prompts/` |

---

## Provider Setup

### Anthropic (default)
```bash
uv sync --extra anthropic
export ANTHROPIC_API_KEY=your-key-here
uv run python examples/demo_basic.py
```

### OpenAI
```bash
uv sync --extra openai
export OPENAI_API_KEY=your-key-here
uv run python examples/demo_openai.py
```

### Ollama (local)
```bash
# No extra install needed — just run Ollama locally
ollama serve
ollama pull llama3.1
# Then use get_llm("ollama") in your code
```

---

## Adding Custom Tools

1. **Subclass `Tool`:**
```python
from src.tools.base import Tool

class MyTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "What this tool does."

    def __call__(self, input: str) -> str:
        return f"Result for: {input}"
```

2. **Register it:**
```python
tools.register(MyTool())
```

3. **Use a dynamic prompt** (so the LLM knows about your tool):
```python
from src.prompts.react import build_react_prompt
system_prompt = build_react_prompt(tools)
```

See `examples/demo_custom_tool.py` for a complete example.

---

## Branching Model

The reader guarantee above drives the whole model: **Article N's branch contains Articles 1..N and
nothing after.**

| Branch | Purpose |
|--------|---------|
| `develop` | Ongoing progress — all work lands here, including the article being written |
| `article-NN-slug` | A snapshot cut from `develop` when article N is published. What readers clone |
| `main` | Consolidation — the newest published snapshot |
| `article-NN-published` *(tag)* | Immutable record of what an article shipped with. A snapshot branch may take later fixes; the tag never moves |
| `master` | Legacy, from the previous git-flow setup. Not used |

**Contributors:** work against `develop`. If you're fixing something in already-published code,
say which article it affects — the fix goes to `develop` and is cherry-picked back to that
article's snapshot. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Running Tests

```bash
uv run pytest tests/ -v
```

---

## License

MIT

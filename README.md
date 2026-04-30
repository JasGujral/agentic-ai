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

```bash
# 1. Clone the repo
git clone https://github.com/JasGujral/agentic-ai.git
cd agentic-ai
git checkout develop  # development happens here

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

This project follows a **git-flow** branching strategy:

| Branch | Purpose |
|--------|---------|
| `master` | Production-ready releases only |
| `develop` | Integration branch (default) — all PRs target here |
| `feature/*` | New features — branch from `develop` |
| `fix/*` | Bug fixes — branch from `develop` |
| `hotfix/*` | Urgent production fixes — branch from `master`, merge back to both |

> **Contributors:** always branch from and PR into `develop`. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Running Tests

```bash
uv run pytest tests/ -v
```

---

## License

MIT

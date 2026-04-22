# agentic-ai

AI agents from first principles — companion code for the **Agentic AI Builder's Series** on Substack.

No frameworks. No magic. Just math, code, and clear explanations.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/hmostack/agentic-ai.git
cd agentic-ai

# 2. Install with uv
uv sync
uv sync --extra anthropic  # or: --extra openai, --extra all

# 3. Set your API key
cp .env.example .env
# Edit .env with your key

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

## Running Tests

```bash
uv run pytest tests/ -v
```

---

## License

MIT

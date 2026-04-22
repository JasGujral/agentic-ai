# agentic-ai — Repository Build Specification

> **Purpose:** Hand this file to Claude Code with:
> `Read REPO_SPEC.md and build the repo step by step. Test everything. Then help me push to GitHub.`

---

## 1. Project Overview

**agentic-ai** is the companion code repository for a Substack series called "Agentic AI Builder's Series." The series builds understanding of AI agents from first principles with math, code, and visuals.

This repo starts with Article 1: "What Are AI Agents, Really?" and will grow with each subsequent article.

### Design Principles
- Every code block in the article is runnable from this repo
- Multi-provider LLM support (Anthropic, OpenAI, local/Ollama)
- No frameworks — everything built from scratch
- Each component is independently testable
- Clean, minimal dependencies

---

## 2. Directory Structure

```
agentic-ai/
│
├── src/
│   ├── __init__.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py                # Abstract base class for LLM providers
│   │   ├── anthropic_client.py    # Anthropic Claude wrapper
│   │   ├── openai_client.py       # OpenAI GPT wrapper
│   │   ├── ollama_client.py       # Local model via Ollama
│   │   └── factory.py             # Factory: get_llm("anthropic") → client
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── react.py               # SYSTEM_PROMPT constant + builder functions
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py                # Tool base class / protocol
│   │   ├── registry.py            # ToolRegistry class (dict wrapper with validation)
│   │   ├── wikipedia.py           # Wikipedia search tool
│   │   ├── calculator.py          # Math evaluator tool
│   │   └── weather.py             # Weather tool (mock for demos)
│   │
│   └── loop/
│       ├── __init__.py
│       ├── parser.py              # Action dataclass + parse() function
│       └── agent.py               # The agent loop
│
├── notebooks/
│   └── 01_what_are_agents.ipynb   # Article 1 as a runnable notebook
│
├── examples/
│   ├── demo_basic.py              # The Eiffel Tower demo from the article
│   ├── demo_openai.py             # Same demo with OpenAI
│   └── demo_custom_tool.py        # Example: adding a custom tool
│
├── tests/
│   ├── __init__.py
│   ├── test_parser.py             # Unit tests for parser
│   ├── test_tools.py              # Unit tests for each tool
│   ├── test_registry.py           # Unit tests for tool registry
│   ├── test_agent.py              # Integration test for the full loop (mocked LLM)
│   └── conftest.py                # Shared fixtures
│
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE                        # MIT
└── README.md
```

---

## 3. Module Specifications

### 3.1 src/llm/base.py

Abstract base class that all LLM providers implement.

```python
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def __call__(self, messages: list[dict]) -> str:
        """Send messages and return text response."""
        pass
    
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name string."""
        pass
```

### 3.2 src/llm/anthropic_client.py

```python
import anthropic
from .base import BaseLLM

class AnthropicLLM(BaseLLM):
    def __init__(self, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024):
        self.client = anthropic.Anthropic()  # Reads ANTHROPIC_API_KEY from env
        self.model = model
        self.max_tokens = max_tokens
    
    def __call__(self, messages: list[dict]) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=messages[0]["content"],
            messages=messages[1:]
        )
        return response.content[0].text
    
    def provider_name(self) -> str:
        return "anthropic"
```

### 3.3 src/llm/openai_client.py

```python
from openai import OpenAI
from .base import BaseLLM

class OpenAILLM(BaseLLM):
    def __init__(self, model: str = "gpt-4o", max_tokens: int = 1024):
        self.client = OpenAI()  # Reads OPENAI_API_KEY from env
        self.model = model
        self.max_tokens = max_tokens
    
    def __call__(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages  # OpenAI uses system role inline
        )
        return response.choices[0].message.content
    
    def provider_name(self) -> str:
        return "openai"
```

### 3.4 src/llm/ollama_client.py

```python
import httpx
from .base import BaseLLM

class OllamaLLM(BaseLLM):
    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def __call__(self, messages: list[dict]) -> str:
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False}
        )
        return response.json()["message"]["content"]
    
    def provider_name(self) -> str:
        return "ollama"
```

### 3.5 src/llm/factory.py

```python
from .anthropic_client import AnthropicLLM
from .openai_client import OpenAILLM
from .ollama_client import OllamaLLM

def get_llm(provider: str = "anthropic", **kwargs):
    """Factory function to get an LLM client by provider name."""
    providers = {
        "anthropic": AnthropicLLM,
        "openai": OpenAILLM,
        "ollama": OllamaLLM,
    }
    if provider not in providers:
        raise ValueError(f"Unknown provider '{provider}'. Available: {list(providers.keys())}")
    return providers[provider](**kwargs)
```

### 3.6 src/prompts/react.py

The SYSTEM_PROMPT constant exactly as it appears in the article. Also include a `build_react_prompt(tools: dict)` function that dynamically generates the tool descriptions section from a tool registry.

### 3.7 src/tools/base.py

```python
from abc import ABC, abstractmethod

class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name used in action parsing."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description included in the system prompt."""
        pass
    
    @abstractmethod
    def __call__(self, input: str) -> str:
        """Execute the tool and return a string result."""
        pass
```

### 3.8 src/tools/registry.py

```python
from .base import Tool

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)
    
    def __contains__(self, name: str) -> bool:
        return name in self._tools
    
    def __getitem__(self, name: str) -> Tool:
        return self._tools[name]
    
    def names(self) -> list[str]:
        return list(self._tools.keys())
    
    def descriptions(self) -> str:
        """Generate tool descriptions for the system prompt."""
        lines = []
        for tool in self._tools.values():
            lines.append(f"{tool.name}: {tool.description}")
        return "\n\n".join(lines)
```

### 3.9 src/tools/wikipedia.py, calculator.py, weather.py

Implement the Tool base class. Code exactly matches the article:
- **wikipedia**: Uses `httpx.get` to Wikipedia REST API. Returns extract or error string.
- **calculator**: Validates expression against allowed chars, then `eval()`. Returns result or error string.
- **weather**: Mock implementation returning a fixed response. Included to demonstrate adding a third tool.

### 3.10 src/loop/parser.py

The `Action` dataclass and `parse()` function exactly as in the article. No changes.

### 3.11 src/loop/agent.py

The `agent()` function from the article, modified to accept:
- `llm`: a BaseLLM instance (instead of hardcoded Anthropic)
- `tools`: a ToolRegistry instance (instead of a plain dict)
- `system_prompt`: optional override (defaults to SYSTEM_PROMPT from react.py)
- `query`: the question
- `max_turns`: default 10
- `verbose`: default True

```python
from ..llm.base import BaseLLM
from ..tools.registry import ToolRegistry
from ..prompts.react import SYSTEM_PROMPT
from .parser import parse

def agent(
    llm: BaseLLM,
    tools: ToolRegistry,
    query: str,
    system_prompt: str = SYSTEM_PROMPT,
    max_turns: int = 10,
    verbose: bool = True
) -> str:
    # ... same loop logic as article, using llm() and tools[] ...
```

---

## 4. Tests

### 4.1 test_parser.py
- Test `parse()` correctly extracts Answer actions
- Test `parse()` correctly extracts tool call actions
- Test `parse()` fallback when no pattern matches
- Test edge cases: extra whitespace, multiple colons, empty response

### 4.2 test_tools.py
- Test `calculator` with valid expressions: "2 + 2" → "4", "1931 - 1889" → "42"
- Test `calculator` rejects invalid expressions: "import os" → error
- Test `wikipedia` with mocked httpx response (don't hit real API in tests)
- Test `weather` returns a string

### 4.3 test_registry.py
- Test register and retrieve tools
- Test `__contains__` for known and unknown tool names
- Test `descriptions()` generates prompt-ready text
- Test error for unknown tool access

### 4.4 test_agent.py (integration)
- Mock the LLM to return a scripted sequence of responses matching the Eiffel Tower demo
- Verify the agent produces the correct final answer
- Verify the correct number of turns
- Verify max_turns is respected (mock LLM that never outputs Answer:)
- Verify unknown tool name returns error observation, not crash

### Test framework: pytest
### Mocking: unittest.mock or pytest-mock for LLM and httpx calls

---

## 5. Notebook: 01_what_are_agents.ipynb

Mirrors the article structure:
1. Introduction cell (markdown)
2. Setup: `pip install` dependencies, import modules
3. §1 code: four levels of LLM usage
4. §2 code: MDP mapping
5. §3 code: ReAct trace example
6. §4 code: build each component, then run the full agent
7. Experiment cell: try different queries, add a custom tool

Each code cell should be independently runnable after the setup cell.

---

## 6. Examples

### demo_basic.py
```python
from src.llm.factory import get_llm
from src.tools.wikipedia import WikipediaTool
from src.tools.calculator import CalculatorTool
from src.tools.registry import ToolRegistry
from src.loop.agent import agent

llm = get_llm("anthropic")
tools = ToolRegistry()
tools.register(WikipediaTool())
tools.register(CalculatorTool())

answer = agent(
    llm=llm,
    tools=tools,
    query="How many years older is the Eiffel Tower than the Empire State Building?"
)
print(f"Answer: {answer}")
```

### demo_openai.py
Same as above but with `get_llm("openai")`.

### demo_custom_tool.py
Shows how to create a new tool by subclassing `Tool` and registering it.

---

## 7. Configuration Files

### pyproject.toml
```toml
[project]
name = "agentic-ai"
version = "0.1.0"
description = "AI agents from first principles — companion code for the Agentic AI Builder's Series"
requires-python = ">=3.10"
license = {text = "MIT"}
dependencies = [
    "httpx>=0.27.0",
]

[project.optional-dependencies]
anthropic = ["anthropic>=0.40.0"]
openai = ["openai>=1.50.0"]
all = ["anthropic>=0.40.0", "openai>=1.50.0"]
dev = ["pytest>=8.0", "pytest-mock>=3.12"]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

### requirements.txt
```
httpx>=0.27.0
anthropic>=0.40.0
openai>=1.50.0
pytest>=8.0
pytest-mock>=3.12
```

### .env.example
```
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

### .gitignore
```
__pycache__/
*.pyc
.env
.venv/
dist/
*.egg-info/
.pytest_cache/
.mypy_cache/
```

---

## 8. README.md

Structure:
- Title: "agentic-ai"
- One-line description: "AI agents from first principles — companion code for the Agentic AI Builder's Series"
- Quick start (3 steps: clone, install, run demo)
- Article link
- Architecture diagram (text-based, showing the loop)
- Table: article → notebook → code modules mapping
- Provider setup (Anthropic, OpenAI, Ollama)
- Adding custom tools (3-step guide)
- Running tests
- License (MIT)

---

## 9. Build Order for Claude Code

1. Create directory structure and all `__init__.py` files
2. Build `src/llm/` — base class, three providers, factory
3. Build `src/tools/` — base class, registry, three tools
4. Build `src/prompts/react.py` — system prompt
5. Build `src/loop/` — parser, agent
6. Build `tests/` — all test files with fixtures
7. Run `pytest` — everything should pass
8. Build `examples/` — three demo scripts
9. Build `notebooks/01_what_are_agents.ipynb`
10. Build config files — pyproject.toml, requirements.txt, .env.example, .gitignore
11. Build README.md
12. Initialize git, commit, push to GitHub

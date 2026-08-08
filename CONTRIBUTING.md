# Contributing to agentic-ai

Thanks for your interest in contributing! This project is the companion code for the **Agentic AI Builder's Series** on Substack, and we welcome contributions of all kinds.

## How to Contribute

### Reporting Bugs

1. Check [existing issues](https://github.com/JasGujral/agentic-ai/issues) to avoid duplicates
2. Open a new issue using the **Bug Report** template
3. Include steps to reproduce, expected vs actual behavior, and your environment

### Suggesting Features

1. Open an issue using the **Feature Request** template
2. Describe the use case and why it would benefit the project

### Submitting Code

1. **Fork** the repo and branch from the article branch your change belongs to.

   This repo has **one branch per article** — `article-NN-slug` — each containing the code for
   that article and everything before it, nothing after. `main` tracks the newest published
   article. Branch from the **earliest** article your change affects:
   ```bash
   git checkout article-01-what-are-agents   # the earliest branch your change affects
   git checkout -b fix/your-fix-name
   ```
   A fix to shared code must reach every later branch, so it starts at the earliest one and is
   merged forward. If you're unsure which branch to target, open an issue and ask — getting this
   wrong is the one mistake that breaks the reading experience for everyone.

2. **Install** dev dependencies:
   ```bash
   uv sync --extra all
   uv sync --group dev
   ```

3. **Write code** following the project conventions:
   - No frameworks — everything built from scratch
   - Each component should be independently testable
   - Keep dependencies minimal

4. **Add tests** for any new functionality:
   ```bash
   uv run pytest tests/ -v
   ```

5. **All tests must pass** before submitting

6. **Commit** with a clear message:
   ```bash
   git commit -m "Add: brief description of what you added"
   ```

7. **Push** and open a Pull Request against the article branch you started from

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Target the **earliest article branch** your change affects — never only the tip
- Fixes are merged forward branch by branch, in order, up to `main`
- `main` is only ever fast-forwarded to a published article's branch; nothing is merged into it
  directly
- **Never** add code to an article branch that its article does not explain — that branch is a
  reader's whole view of the project
- Reference any related issues (e.g., "Fixes #12")
- Include a description of what changed and why
- Make sure all tests pass
- Update documentation if needed

## Development Setup

```bash
git clone https://github.com/JasGujral/agentic-ai.git
cd agentic-ai
uv sync --extra all --group dev
cp .env.example .env
# Add your API keys to .env
uv run pytest tests/ -v
```

## Code Style

- Python 3.10+ with type hints
- Clear, readable code over clever code
- Docstrings for public functions
- Tests for all new functionality

## Code of Conduct

By participating, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

Open a [discussion](https://github.com/JasGujral/agentic-ai/issues) or reach out on the Substack comments.

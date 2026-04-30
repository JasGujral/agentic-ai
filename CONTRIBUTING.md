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

1. **Fork** the repo and create a branch from `develop`:
   ```bash
   git checkout develop
   git checkout -b feature/your-feature-name
   ```

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

7. **Push** and open a Pull Request against `develop`

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Target `develop` for all feature and fix PRs
- Only `develop → master` PRs are used for production releases
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

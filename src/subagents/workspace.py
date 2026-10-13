"""Read-only workspace tools: the explorer's whole toolkit.

Search and read are the high-volume, low-value-per-token work of an agent:
dozens of observations, of which the parent needs only the conclusion. These
tools are scoped to one root and can only read. That scope is set in code,
not left to the model.
"""
from pathlib import Path

from pydantic import BaseModel, Field

from src.tools.base import Tool

SKIP = {".git", ".venv", "__pycache__", "node_modules", ".ipynb_checkpoints"}
TEXT = {".py", ".md", ".toml", ".txt"}


class Workspace:
    """A directory the tools may read, and nothing outside it."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def safe(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        if p != self.root and self.root not in p.parents:     # no ../ escapes
            raise PermissionError(f"{rel!r} is outside the workspace")
        return p

    def files(self, sub: str = ".") -> list[Path]:
        return sorted(p for p in self.safe(sub).rglob("*")
                      if p.is_file() and p.suffix in TEXT
                      and not SKIP & set(p.relative_to(self.root).parts))


class ListFiles(Tool):
    name = "list_files"
    description = "List the text files under a directory of the repo."
    read_only = True

    class Args(BaseModel):
        subdir: str = Field(default=".", description="Directory relative to the repo root")

    def __init__(self, ws: Workspace):
        self.ws = ws

    def __call__(self, args: Args) -> str:
        try:
            return "\n".join(str(p.relative_to(self.ws.root)) for p in self.ws.files(args.subdir))
        except PermissionError as e:
            return f"error: {e}"


class ReadFile(Tool):
    name = "read_file"
    description = "Read a file (or a line range of it), with line numbers."
    read_only = True

    class Args(BaseModel):
        path: str = Field(description="File path relative to the repo root")
        start: str = Field(default="1", description="First line, 1-based")
        end: str = Field(default="400", description="Last line, inclusive")

    def __init__(self, ws: Workspace):
        self.ws = ws

    def __call__(self, args: Args) -> str:
        try:
            lines = self.ws.safe(args.path).read_text().splitlines()
        except (PermissionError, OSError) as e:
            return f"error: {e}"
        a, b = max(int(args.start), 1), min(int(args.end), len(lines))
        return "\n".join(f"{i:4d}  {lines[i - 1]}" for i in range(a, b + 1))


class SearchCode(Tool):
    name = "search_code"
    description = "Find lines containing a literal string across the repo; returns path:line: text."
    read_only = True

    class Args(BaseModel):
        pattern: str = Field(description="Literal text to search for")

    def __init__(self, ws: Workspace, max_hits: int = 40):
        self.ws, self.max_hits = ws, max_hits

    def __call__(self, args: Args) -> str:
        hits = []
        for p in self.ws.files():
            for i, line in enumerate(p.read_text().splitlines(), 1):
                if args.pattern.lower() in line.lower():
                    hits.append(f"{p.relative_to(self.ws.root)}:{i}: {line.strip()}")
                    if len(hits) >= self.max_hits:
                        return "\n".join(hits)
        return "\n".join(hits) or "no matches"


def workspace_tools(root: str | Path) -> list[Tool]:
    ws = Workspace(root)
    return [ListFiles(ws), ReadFile(ws), SearchCode(ws)]

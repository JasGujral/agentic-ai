"""Typed tool base (Article 2 upgrade of the Article-1 string Tool).

A tool is a name, a description the model reads to choose it, and a typed Args
schema it must fill to call it. Execution is the private __call__.

Article 3 adds one flag, `read_only`: many agents may read, only one may write.
"""
from abc import ABC, abstractmethod

from pydantic import BaseModel


class Tool(ABC):
    name: str
    description: str
    Args: type[BaseModel]
    read_only: bool = False   # Article 3: True if the tool only reads. Subagents may hold only these.

    @abstractmethod
    def __call__(self, args: BaseModel) -> str:
        """Execute against validated args; return a result the loop can read."""

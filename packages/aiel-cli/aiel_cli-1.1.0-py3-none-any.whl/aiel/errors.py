from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class CliError(Exception):
    message: str
    hint: Optional[str] = None
    code: int = 2

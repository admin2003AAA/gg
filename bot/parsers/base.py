"""
Base parser interface — unified API for all file parsers.
All concrete parsers must subclass BaseParser and implement parse().
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class ParseResult:
    """Unified result returned by every parser."""

    # File identity
    file_path: str
    file_name: str
    file_type: str
    file_size: int

    # Human-readable output
    content_preview: str = ""   # First ~2 000 chars for display
    summary: str = ""           # One-paragraph summary

    # Search
    search_text: str = ""       # Flattened text for FTS

    # Structured
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Each item: {"name": str, "columns": list[str], "row_count": int, "preview": list[dict]}
    tables: List[Dict[str, Any]] = field(default_factory=list)

    # Counters
    record_count: int = 0
    char_count: int = 0

    # Status
    success: bool = True
    error: str = ""


class BaseParser(ABC):
    """Abstract base class for all file parsers."""

    SUPPORTED_EXTENSIONS: tuple = ()
    PARSER_NAME: str = "base"

    def can_parse(self, path: Path) -> bool:
        return path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    @abstractmethod
    async def parse(self, path: Path) -> ParseResult:
        """Parse *path* and return a ParseResult."""
        ...

    def _base_result(self, path: Path) -> ParseResult:
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        return ParseResult(
            file_path=str(path),
            file_name=path.name,
            file_type=path.suffix.lower().lstrip("."),
            file_size=size,
        )

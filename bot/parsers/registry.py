"""
Parser registry — maps file extensions to concrete parser instances.
Parsers are loaded once and reused.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from .base import BaseParser, ParseResult
from .text_parser import TextParser
from .data_parser import CsvParser, JsonParser, XmlParser, YamlParser
from .db_parser import SqliteParser
from .document_parser import DocxParser, PdfParser, XlsxParser


class ParserRegistry:
    """Maintains a mapping of extension → parser and dispatches parse calls."""

    def __init__(self) -> None:
        self._parsers: List[BaseParser] = []
        self._ext_map: Dict[str, BaseParser] = {}

    def register(self, parser: BaseParser) -> None:
        self._parsers.append(parser)
        for ext in parser.SUPPORTED_EXTENSIONS:
            self._ext_map[ext.lower()] = parser

    def get_parser(self, path: Path) -> Optional[BaseParser]:
        return self._ext_map.get(path.suffix.lower())

    def supported_extensions(self) -> List[str]:
        return sorted(self._ext_map.keys())

    async def parse(self, path: Path) -> ParseResult:
        """Dispatch to the appropriate parser, or return an error result."""
        parser = self.get_parser(path)
        if parser is None:
            return ParseResult(
                file_path=str(path),
                file_name=path.name,
                file_type=path.suffix.lower().lstrip("."),
                file_size=path.stat().st_size if path.exists() else 0,
                success=False,
                error=f"No parser registered for extension '{path.suffix}'",
            )
        return await parser.parse(path)


# ─── Default registry (singleton) ────────────────────────────────────────────

def _build_default_registry() -> ParserRegistry:
    reg = ParserRegistry()
    reg.register(TextParser())
    reg.register(JsonParser())
    reg.register(CsvParser())
    reg.register(XmlParser())
    reg.register(YamlParser())
    reg.register(SqliteParser())
    reg.register(PdfParser())
    reg.register(DocxParser())
    reg.register(XlsxParser())
    return reg


registry: ParserRegistry = _build_default_registry()

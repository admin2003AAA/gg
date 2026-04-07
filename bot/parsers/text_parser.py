"""
Text-family parsers: TXT, LOG, Markdown, RST.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import chardet

from .base import BaseParser, ParseResult

_PREVIEW = 2_000
_MAX_READ = 500_000  # bytes


def _read_text_sync(path: Path, max_bytes: int = _MAX_READ) -> tuple[str, str]:
    """Return (text, detected_encoding)."""
    raw = path.read_bytes()[:max_bytes]
    info = chardet.detect(raw)
    enc = info.get("encoding") or "utf-8"
    try:
        text = raw.decode(enc, errors="replace")
    except LookupError:
        text = raw.decode("utf-8", errors="replace")
    return text, enc


class TextParser(BaseParser):
    SUPPORTED_EXTENSIONS = (".txt", ".log", ".md", ".markdown", ".rst", ".text")
    PARSER_NAME = "text"

    async def parse(self, path: Path) -> ParseResult:
        result = self._base_result(path)
        loop = asyncio.get_event_loop()
        try:
            text, enc = await loop.run_in_executor(None, _read_text_sync, path)
            lines = text.count("\n") + 1
            result.content_preview = text[:_PREVIEW]
            result.search_text = text[:100_000]
            result.char_count = len(text)
            result.record_count = lines
            result.metadata = {
                "lines": lines,
                "chars": len(text),
                "encoding": enc,
                "type": path.suffix.lstrip(".").upper() or "TXT",
            }
            ext = path.suffix.lower()
            if ext in (".md", ".markdown"):
                kind = "Markdown"
            elif ext == ".log":
                kind = "Log"
            elif ext == ".rst":
                kind = "reStructuredText"
            else:
                kind = "Text"
            result.summary = (
                f"📄 {kind} file · {lines:,} lines · {len(text):,} chars · encoding: {enc}"
            )
        except Exception as exc:
            result.success = False
            result.error = str(exc)
        return result

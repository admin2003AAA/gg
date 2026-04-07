"""
Data-family parsers: JSON, CSV, XML, YAML/YML.
"""
from __future__ import annotations

import asyncio
import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List

import chardet

from .base import BaseParser, ParseResult

_PREVIEW_ROWS = 5
_MAX_READ = 10_000_000  # 10 MB


# ─── helpers ─────────────────────────────────────────────────────────────────

def _detect_enc(raw: bytes) -> str:
    return chardet.detect(raw[:65_536]).get("encoding") or "utf-8"


def _decode(raw: bytes) -> str:
    enc = _detect_enc(raw)
    try:
        return raw.decode(enc, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


def _truncate_value(v: Any, max_len: int = 120) -> Any:
    if isinstance(v, str) and len(v) > max_len:
        return v[:max_len] + "…"
    return v


# ─── JSON ─────────────────────────────────────────────────────────────────────

class JsonParser(BaseParser):
    SUPPORTED_EXTENSIONS = (".json", ".jsonl", ".ndjson")
    PARSER_NAME = "json"

    async def parse(self, path: Path) -> ParseResult:
        result = self._base_result(path)
        loop = asyncio.get_event_loop()
        try:
            raw = await loop.run_in_executor(None, lambda: path.read_bytes()[:_MAX_READ])
            text = _decode(raw)
            data = json.loads(text)
            record_count, tables, meta = _analyse_json(data, path.name)
            result.record_count = record_count
            result.tables = tables
            result.metadata = meta
            result.content_preview = text[:2_000]
            result.search_text = json.dumps(data, ensure_ascii=False)[:100_000]
            result.char_count = len(text)
            result.summary = (
                f"📋 JSON file · {record_count:,} items · "
                + (f"{len(tables)} table(s)" if tables else "nested object")
            )
        except Exception as exc:
            result.success = False
            result.error = str(exc)
        return result


def _analyse_json(data: Any, fname: str) -> tuple:
    """Return (record_count, tables, metadata)."""
    if isinstance(data, list):
        rc = len(data)
        if rc > 0 and isinstance(data[0], dict):
            cols = list(data[0].keys())
            preview = [{k: _truncate_value(r.get(k)) for k in cols[:10]} for r in data[:_PREVIEW_ROWS]]
            tables = [{"name": fname, "columns": cols[:50], "row_count": rc, "preview": preview}]
        else:
            tables = [{"name": fname, "columns": [], "row_count": rc, "preview": []}]
        meta: Dict = {"root_type": "array", "item_count": rc}
    elif isinstance(data, dict):
        rc = len(data)
        tables = []
        meta = {"root_type": "object", "keys": list(data.keys())[:50]}
    else:
        rc = 1
        tables = []
        meta = {"root_type": type(data).__name__}
    return rc, tables, meta


# ─── CSV ──────────────────────────────────────────────────────────────────────

class CsvParser(BaseParser):
    SUPPORTED_EXTENSIONS = (".csv", ".tsv", ".tab")
    PARSER_NAME = "csv"

    async def parse(self, path: Path) -> ParseResult:
        result = self._base_result(path)
        loop = asyncio.get_event_loop()
        try:
            raw = await loop.run_in_executor(None, lambda: path.read_bytes()[:_MAX_READ])
            text = _decode(raw)
            rows, cols, preview = await loop.run_in_executor(None, _parse_csv, text)
            result.record_count = rows
            result.char_count = len(text)
            result.content_preview = text[:2_000]
            result.search_text = text[:100_000]
            result.tables = [{
                "name": path.stem,
                "columns": cols,
                "row_count": rows,
                "preview": preview,
            }]
            result.metadata = {"rows": rows, "columns": len(cols), "column_names": cols[:50]}
            result.summary = (
                f"📊 CSV file · {rows:,} rows · {len(cols)} columns"
            )
        except Exception as exc:
            result.success = False
            result.error = str(exc)
        return result


def _parse_csv(text: str) -> tuple:
    dialect = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|")
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    rows = 0
    cols: List[str] = []
    preview: List[Dict] = []
    for row in reader:
        if rows == 0:
            cols = list(row.keys())
        if rows < _PREVIEW_ROWS:
            preview.append({k: _truncate_value(v) for k, v in list(row.items())[:20]})
        rows += 1
    return rows, cols[:100], preview


# ─── XML ──────────────────────────────────────────────────────────────────────

class XmlParser(BaseParser):
    SUPPORTED_EXTENSIONS = (".xml", ".xsl", ".xslt", ".rss", ".atom")
    PARSER_NAME = "xml"

    async def parse(self, path: Path) -> ParseResult:
        result = self._base_result(path)
        loop = asyncio.get_event_loop()
        try:
            raw = await loop.run_in_executor(None, lambda: path.read_bytes()[:_MAX_READ])
            text = _decode(raw)
            meta, search = await loop.run_in_executor(None, _parse_xml, text)
            result.record_count = meta.get("element_count", 0)
            result.char_count = len(text)
            result.content_preview = text[:2_000]
            result.search_text = search[:100_000]
            result.metadata = meta
            result.summary = (
                f"🗂️ XML file · root: <{meta.get('root_tag', '?')}> · "
                f"{meta.get('element_count', 0):,} elements"
            )
        except Exception as exc:
            result.success = False
            result.error = str(exc)
        return result


def _parse_xml(text: str) -> tuple:
    """Parse XML safely using ElementTree (no external DTD loading)."""
    import xml.etree.ElementTree as ET  # stdlib — safe, no XXE
    root = ET.fromstring(text)
    elements = list(root.iter())
    element_count = len(elements)
    # Collect all text content for search
    parts = [e.text or "" for e in elements] + [e.tail or "" for e in elements]
    search = " ".join(p for p in parts if p.strip())
    attrs = {e.tag for e in elements}
    meta: Dict = {
        "root_tag": root.tag,
        "element_count": element_count,
        "unique_tags": list(attrs)[:50],
        "attributes": dict(root.attrib) if root.attrib else {},
    }
    return meta, search


# ─── YAML ─────────────────────────────────────────────────────────────────────

class YamlParser(BaseParser):
    SUPPORTED_EXTENSIONS = (".yaml", ".yml")
    PARSER_NAME = "yaml"

    async def parse(self, path: Path) -> ParseResult:
        result = self._base_result(path)
        loop = asyncio.get_event_loop()
        try:
            raw = await loop.run_in_executor(None, lambda: path.read_bytes()[:_MAX_READ])
            text = _decode(raw)
            data, meta = await loop.run_in_executor(None, _parse_yaml, text)
            result.char_count = len(text)
            result.content_preview = text[:2_000]
            result.search_text = json.dumps(data, ensure_ascii=False, default=str)[:100_000]
            result.metadata = meta
            result.record_count = meta.get("item_count", 1)
            result.summary = (
                f"⚙️ YAML file · root type: {meta.get('root_type', '?')} · "
                f"{meta.get('item_count', '?')} items"
            )
        except Exception as exc:
            result.success = False
            result.error = str(exc)
        return result


def _parse_yaml(text: str) -> tuple:
    import yaml  # PyYAML — safe_load only, no arbitrary code execution
    data = yaml.safe_load(text)
    if isinstance(data, list):
        meta: Dict = {"root_type": "list", "item_count": len(data)}
    elif isinstance(data, dict):
        meta = {"root_type": "mapping", "item_count": len(data), "keys": list(data.keys())[:50]}
    else:
        meta = {"root_type": type(data).__name__, "item_count": 1}
    return data, meta

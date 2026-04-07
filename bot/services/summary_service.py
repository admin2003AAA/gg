"""
SummaryService — builds human-readable summaries for indexed files.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from bot.database.manager import DatabaseManager
from bot.config import DB_PATH

_db = DatabaseManager(DB_PATH)


class SummaryService:
    async def get_summary(self, file_id: int) -> str:
        await _db.init()
        file = await _db.get_file_by_id(file_id)
        if not file:
            return "❌ File not found in index."
        return _build_summary(file)

    async def get_stats(self) -> Dict[str, Any]:
        await _db.init()
        return await _db.get_stats()


def _build_summary(f: Dict) -> str:
    lines: List[str] = [
        f"📄 **{f['filename']}**",
        f"🗂️ Type: `{f['file_type'].upper()}`",
        f"💾 Size: {_human_size(f.get('file_size', 0))}",
        f"📊 Records: {f.get('record_count', 0):,}",
        f"📅 Indexed: {(f.get('indexed_at') or '')[:19]}",
    ]

    summary = f.get("summary") or ""
    if summary:
        lines += ["", f"📝 {summary}"]

    # Tables / sheets
    tables_raw = f.get("tables_json") or "[]"
    try:
        tables: List[Dict] = json.loads(tables_raw)
    except Exception:
        tables = []

    if tables:
        lines.append("")
        lines.append(f"📋 **Tables / Sheets ({len(tables)}):**")
        for t in tables[:10]:
            name = t.get("name", "?")
            rows = t.get("row_count", "?")
            cols = t.get("columns") or t.get("column_names") or []
            col_str = ", ".join(str(c) for c in cols[:6])
            if len(cols) > 6:
                col_str += f" … +{len(cols)-6}"
            lines.append(f"  • **{name}** — {rows} rows | {col_str}")

    # Metadata highlights
    meta_raw = f.get("metadata_json") or "{}"
    try:
        meta: Dict = json.loads(meta_raw)
    except Exception:
        meta = {}

    interesting = {k: v for k, v in meta.items()
                   if k not in ("raw_meta",) and v not in (None, "", [], {})}
    if interesting:
        lines.append("")
        lines.append("🔍 **Metadata:**")
        for k, v in list(interesting.items())[:8]:
            lines.append(f"  • {k}: `{str(v)[:80]}`")

    return "\n".join(lines)


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"

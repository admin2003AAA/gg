"""
📝 منسقات الرسائل - Message Formatters
"""

import json
from typing import Dict, List

from humanize import naturalsize


def fmt_record(r: Dict, show_source: bool = True) -> str:
    lines = ["━" * 32]
    if r.get("full_name"):
        lines.append(f"👤 **{r['full_name']}**")
    if r.get("national_id"):
        lines.append(f"🪪 الهوية: `{r['national_id']}`")
    if r.get("province"):
        lines.append(f"🏛️ المحافظة: {r['province']}")
    if r.get("birth_date"):
        lines.append(f"📅 الولادة: {r['birth_date']}")
    elif r.get("birth_year"):
        lines.append(f"📅 سنة الولادة: {r['birth_year']}")
    if r.get("phone"):
        lines.append(f"📞 الهاتف: `{r['phone']}`")
    if r.get("address"):
        lines.append(f"📍 العنوان: {r['address'][:100]}")
    if r.get("gender"):
        lines.append(f"👤 الجنس: {r['gender']}")
    if r.get("nationality"):
        lines.append(f"🌍 الجنسية: {r['nationality']}")
    if r.get("email"):
        lines.append(f"📧 البريد: {r['email']}")
    if r.get("extra_fields"):
        try:
            extra = json.loads(r["extra_fields"])
            if extra:
                lines.append("➕ بيانات إضافية:")
                for k, v in list(extra.items())[:5]:
                    if v and str(v) not in {"None", "nan"}:
                        lines.append(f"   • {k}: {v}")
        except Exception:
            pass
    if show_source and r.get("source_file"):
        lines.append(f"\n📂 المصدر: `{r['source_file']}`")
    if r.get("_match_score"):
        lines.append(f"🎯 التطابق: **{r['_match_score']:.0f}%**")
    lines.append("━" * 32)
    return "\n".join(lines)


def fmt_results(results: List[Dict], total: int, page: int,
                per_page: int, query: str, ms: int = 0) -> str:
    if not results:
        return f"🔍 لا توجد نتائج لـ **{query}**"
    pages = max(1, (total + per_page - 1) // per_page)
    lines = [
        f"🔍 **نتائج البحث:** `{query}`",
        f"📊 {total:,} نتيجة │ صفحة {page}/{pages}",
    ]
    if ms:
        lines.append(f"⚡ وقت البحث: {ms}ms")
    lines.append("")
    for i, r in enumerate(results, 1):
        num  = (page - 1) * per_page + i
        name = r.get("full_name") or "—"
        nid  = r.get("national_id") or ""
        prov = r.get("province") or ""
        src  = r.get("source_file") or ""
        line = f"**{num}.** {name}"
        if nid:  line += f"  🪪`{nid}`"
        if prov: line += f"  🏛️{prov}"
        if src:  line += f"\n   📂 _{src}_"
        lines.append(line)
    return "\n".join(lines)


def fmt_stats(s: Dict) -> str:
    lines = [
        "📊 **إحصائيات النظام**",
        "━" * 32,
        f"📁 الملفات النشطة : **{s.get('active_files',0):,}**",
        f"📋 إجمالي السجلات : **{s.get('total_records',0):,}**",
        f"👥 المستخدمون     : **{s.get('total_users',0):,}**",
        f"🔍 إجمالي البحوث  : **{s.get('total_searches',0):,}**",
        "",
    ]
    perf = s.get("search_perf") or {}
    if perf.get("avg_ms"):
        lines += [
            "⚡ **أداء البحث:**",
            f"   متوسط : {perf['avg_ms']:.0f}ms",
            f"   أسرع  : {perf['min_ms']}ms   أبطأ: {perf['max_ms']}ms",
            "",
        ]
    provinces = s.get("top_provinces") or []
    if provinces:
        lines.append("🏛️ **توزيع المحافظات:**")
        mx = provinces[0]["cnt"]
        for p in provinces[:10]:
            bar = "█" * int(p["cnt"] / mx * 14) + "░" * (14 - int(p["cnt"] / mx * 14))
            name = (p["province"] or "غير محدد")[:14]
            lines.append(f"   {name:<14} {bar} {p['cnt']:,}")
    return "\n".join(lines)


def fmt_files(files: List[Dict]) -> str:
    if not files:
        return "📂 لا توجد ملفات مفهرسة."
    icons = {"active": "✅", "error": "❌", "indexing": "⏳", "removed": "🗑️"}
    lines = ["📁 **الملفات المفهرسة:**", "━" * 32]
    for f in files:
        icon = icons.get(f["status"], "❓")
        size = naturalsize(f.get("file_size") or 0)
        dt   = (f.get("indexed_at") or "")[:10]
        cnt  = f.get("record_count") or 0
        lines.append(
            f"{icon} **{f['filename']}**\n"
            f"   📊 {cnt:,} سجل │ 💾 {size} │ 📅 {dt}"
        )
    return "\n".join(lines)


def fmt_user(u: Dict) -> str:
    roles = {"admin": "مسؤول 👑", "operator": "مشغل 🔧", "viewer": "مشاهد 👁️"}
    name  = f"{u.get('first_name','')}{' '+u.get('last_name','') if u.get('last_name') else ''}".strip()
    return (
        f"👤 **{name}**\n"
        f"🆔 `{u['telegram_id']}`\n"
        f"📛 @{u.get('username') or 'بدون'}\n"
        f"🎭 {roles.get(u.get('role','viewer'), u.get('role','viewer'))}\n"
        f"🔍 اليوم: {u.get('daily_searches',0)} │ الإجمالي: {u.get('total_searches',0)}\n"
        f"🚫 محظور: {'نعم ❌' if u.get('is_banned') else 'لا ✅'}"
    )

"""
👁️ مراقب الملفات التلقائي - File Watcher (Watchdog)
يفهرس الملفات الجديدة تلقائيًا عند إضافتها للمجلد
"""

import asyncio
from pathlib import Path
from typing import Optional

from loguru import logger
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer

from bot.config import DATA_DIR, SUPPORTED_EXTENSIONS


class _Handler(FileSystemEventHandler):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self._loop = loop

    def on_created(self, event: FileCreatedEvent):
        if getattr(event, "is_directory", False):
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return
        logger.info(f"📥 ملف جديد رُصد: {path.name}")
        asyncio.run_coroutine_threadsafe(self._index(path), self._loop)

    async def _index(self, path: Path):
        from bot.core.indexer import index_file
        try:
            count = await index_file(str(path))
            logger.success(f"✅ فُهرس تلقائياً: {path.name} ({count:,} سجل)")
        except Exception as e:
            logger.error(f"❌ فشل الفهرسة التلقائية لـ {path.name}: {e}")


class FileWatcher:
    def __init__(self):
        self._observer: Optional[Observer] = None

    def start(self, loop: asyncio.AbstractEventLoop):
        path = str(DATA_DIR)
        self._observer = Observer()
        self._observer.schedule(_Handler(loop), path, recursive=True)
        self._observer.start()
        logger.info(f"👁️  مراقبة المجلد: {path}")

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()
            logger.info("🛑 توقف مراقب الملفات")


watcher = FileWatcher()

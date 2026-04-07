"""
⚙️ Central configuration — reads from .env via python-dotenv.
"""
import os
from pathlib import Path
from typing import List, Set

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data/files")
DB_PATH  = BASE_DIR / os.getenv("DB_PATH",  "data/db/index.db")
LOG_DIR  = BASE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

_admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: List[int] = [
    int(x.strip()) for x in _admin_ids_str.split(",") if x.strip().isdigit()
]

MAX_RESULTS_PER_SEARCH: int = int(os.getenv("MAX_RESULTS", "10"))
MAX_RESULTS: int             = MAX_RESULTS_PER_SEARCH   # legacy alias
DAILY_SEARCH_LIMIT: int      = int(os.getenv("DAILY_LIMIT", "100"))
CACHE_SIZE: int               = int(os.getenv("CACHE_SIZE", "1000"))
CHUNK_SIZE: int               = int(os.getenv("CHUNK_SIZE", "1000"))
LOG_LEVEL: str                = os.getenv("LOG_LEVEL", "INFO")
MAINTENANCE_MODE: bool        = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
BOT_LANG: str                 = os.getenv("BOT_LANG", "en")

MAX_FILE_SIZE_MB: int    = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

# All extensions the bot can accept / index
SUPPORTED_EXTENSIONS: Set[str] = {
    # text
    ".txt", ".log", ".md", ".markdown", ".rst", ".text",
    # data
    ".json", ".jsonl", ".ndjson",
    ".csv", ".tsv", ".tab",
    ".xml", ".xsl", ".rss", ".atom",
    ".yaml", ".yml",
    # database
    ".sqlite", ".db", ".sqlite3", ".s3db", ".sl3",
    # documents
    ".pdf",
    ".docx",
    ".xlsx", ".xls", ".xlsm", ".ods",
}

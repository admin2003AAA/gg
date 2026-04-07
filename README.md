# 📁 File Indexer Bot

A production-grade Telegram bot that automatically indexes files in a designated data directory and lets users search and explore their content — all via Telegram commands.

Built with **Python 3.11**, `python-telegram-bot` v21 (async), and SQLite FTS5.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Auto-indexing** | Drop files into `data/files/` and they're indexed automatically |
| **Multi-format** | txt · log · md · json · csv · xml · yaml · sqlite · db · pdf · docx · xlsx |
| **Full-text search** | SQLite FTS5 with Unicode support |
| **File summaries** | Schema, row counts, metadata per file |
| **Admin upload** | Send a file directly in Telegram to index it |
| **File watcher** | Watchdog monitors the data directory in real-time |
| **Async** | Non-blocking I/O throughout |
| **Logging** | Loguru — console + rotating file logs |
| **Docker** | One-command deployment |

---

## 🤖 Commands

| Command | Description | Who |
|---|---|---|
| `/start` | Welcome message | Everyone |
| `/help` | Command reference | Everyone |
| `/scan` | Scan & index all files in `data/files/` | Admin |
| `/files` | List all indexed files | Everyone |
| `/search <query>` | Full-text search across all files | Everyone |
| `/summary <id>` | Detailed summary for a file | Everyone |
| `/stats` | Indexing & usage statistics | Everyone |

> Admins can also **upload a file directly** to Telegram to index it.

---

## 📂 Supported Formats

| Category | Extensions |
|---|---|
| Text | `.txt` `.log` `.md` `.markdown` `.rst` |
| Data | `.json` `.jsonl` `.csv` `.tsv` `.xml` `.yaml` `.yml` |
| Database | `.sqlite` `.db` `.sqlite3` |
| Documents | `.pdf` `.docx` `.xlsx` `.xls` |

---

## 🚀 Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/admin2003AAA/gg.git
cd gg
cp .env.example .env
# Edit .env — set BOT_TOKEN and ADMIN_IDS
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add files to index

```bash
cp your_data_file.csv data/files/
```

### 4. Run

```bash
python run.py
```

Then in Telegram:
```
/scan        ← index data/files/
/files       ← list indexed files
/search foo  ← search content
/summary 1   ← details for file #1
```

---

## 🐳 Docker

```bash
cp .env.example .env   # configure first
docker compose up -d
```

Place files in `./data/files/` — they are mounted into the container.

---

## 🗂️ Project Structure

```
.
├── run.py                   # Entrypoint
├── bot/
│   ├── main.py              # Application setup & startup
│   ├── config.py            # Centralised configuration
│   ├── handlers/            # Telegram command handlers
│   │   ├── start_handler.py
│   │   ├── upload_handler.py
│   │   ├── scan_handler.py
│   │   ├── files_handler.py
│   │   ├── search_handler.py
│   │   ├── summary_handler.py
│   │   └── stats_handler.py
│   ├── parsers/             # File format parsers
│   │   ├── base.py          # BaseParser + ParseResult
│   │   ├── text_parser.py   # txt / log / md
│   │   ├── data_parser.py   # json / csv / xml / yaml
│   │   ├── db_parser.py     # sqlite / db
│   │   ├── document_parser.py  # pdf / docx / xlsx
│   │   └── registry.py      # Extension → parser mapping
│   ├── services/            # Business logic layer
│   │   ├── index_service.py
│   │   ├── search_service.py
│   │   └── summary_service.py
│   ├── core/
│   │   ├── indexer.py       # Core indexing orchestrator
│   │   └── file_watcher.py  # Watchdog-based auto-indexer
│   ├── database/
│   │   ├── manager.py       # Async SQLite manager (aiosqlite)
│   │   └── models.py        # DDL reference
│   └── utils/
│       ├── helpers.py       # Keyboards & message splitting
│       ├── formatters.py    # Rich text formatters
│       └── validators.py    # Input sanitisation
├── data/
│   ├── files/               # ← Put your data files here
│   └── db/                  # SQLite index lives here
├── logs/                    # Rotating log files
├── .env.example
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | — | **Required.** From [@BotFather](https://t.me/BotFather) |
| `ADMIN_IDS` | — | Comma-separated Telegram user IDs with admin rights |
| `DATA_DIR` | `data/files` | Directory to watch for files |
| `DB_PATH` | `data/db/index.db` | SQLite index database path |
| `MAX_RESULTS` | `10` | Max search results per query |
| `DAILY_LIMIT` | `100` | Daily search limit per user |
| `CACHE_SIZE` | `1000` | Search cache capacity |
| `MAX_FILE_SIZE_MB` | `50` | Maximum uploadable file size |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `MAINTENANCE_MODE` | `false` | Disable bot responses temporarily |

---

## 🔒 Security Notes

- XML is parsed with Python's `xml.etree.ElementTree` — no external DTD loading.
- YAML uses `yaml.safe_load` — no arbitrary code execution.
- SQLite files are opened read-only during schema inspection.
- DOCX is parsed without executing macros.
- All user input is sanitised before FTS queries.

---

## 📦 Adding a New Parser

1. Create a class that inherits `BaseParser` in `bot/parsers/`.
2. Set `SUPPORTED_EXTENSIONS` and implement `async def parse(path) -> ParseResult`.
3. Register it in `bot/parsers/registry.py`.

That's it — the new format is automatically available in all commands.

---

## 📄 License

MIT

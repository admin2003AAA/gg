"""
🗄️ نماذج قاعدة البيانات - Database Models
"""

CREATE_TABLES_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS files (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    filename      TEXT    NOT NULL,
    filepath      TEXT    NOT NULL UNIQUE,
    file_type     TEXT    NOT NULL,
    file_size     INTEGER DEFAULT 0,
    record_count  INTEGER DEFAULT 0,
    indexed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP,
    status        TEXT    DEFAULT 'active',
    error_message TEXT,
    columns_info  TEXT,
    field_mapping TEXT
);

CREATE TABLE IF NOT EXISTS records (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id      INTEGER NOT NULL,
    row_number   INTEGER NOT NULL,
    full_name    TEXT,
    national_id  TEXT,
    province     TEXT,
    birth_date   TEXT,
    birth_year   INTEGER,
    phone        TEXT,
    address      TEXT,
    gender       TEXT,
    nationality  TEXT,
    email        TEXT,
    extra_fields TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);

CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(
    full_name,
    national_id,
    province,
    phone,
    address,
    content     = records,
    content_rowid = id,
    tokenize    = 'unicode61'
);

CREATE TABLE IF NOT EXISTS users (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id       INTEGER UNIQUE NOT NULL,
    username          TEXT,
    first_name        TEXT,
    last_name         TEXT,
    role              TEXT    DEFAULT 'viewer',
    is_banned         INTEGER DEFAULT 0,
    daily_searches    INTEGER DEFAULT 0,
    total_searches    INTEGER DEFAULT 0,
    last_search_date  TEXT,
    joined_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS search_logs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    query          TEXT    NOT NULL,
    search_type    TEXT    DEFAULT 'simple',
    results_count  INTEGER DEFAULT 0,
    search_time_ms INTEGER DEFAULT 0,
    searched_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id)
);

CREATE TABLE IF NOT EXISTS system_settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── Indexes ─────────────��──────────────────
CREATE INDEX IF NOT EXISTS idx_rec_name    ON records(full_name);
CREATE INDEX IF NOT EXISTS idx_rec_nid     ON records(national_id);
CREATE INDEX IF NOT EXISTS idx_rec_prov    ON records(province);
CREATE INDEX IF NOT EXISTS idx_rec_phone   ON records(phone);
CREATE INDEX IF NOT EXISTS idx_rec_year    ON records(birth_year);
CREATE INDEX IF NOT EXISTS idx_rec_file    ON records(file_id);
CREATE INDEX IF NOT EXISTS idx_usr_tg      ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_log_user    ON search_logs(user_id);

-- ─── FTS Triggers ───────────────────────────
CREATE TRIGGER IF NOT EXISTS fts_ai AFTER INSERT ON records BEGIN
    INSERT INTO records_fts(rowid, full_name, national_id, province, phone, address)
    VALUES (new.id, new.full_name, new.national_id, new.province, new.phone, new.address);
END;

CREATE TRIGGER IF NOT EXISTS fts_ad AFTER DELETE ON records BEGIN
    INSERT INTO records_fts(records_fts, rowid, full_name, national_id, province, phone, address)
    VALUES ('delete', old.id, old.full_name, old.national_id, old.province, old.phone, old.address);
END;

CREATE TRIGGER IF NOT EXISTS fts_au AFTER UPDATE ON records BEGIN
    INSERT INTO records_fts(records_fts, rowid, full_name, national_id, province, phone, address)
    VALUES ('delete', old.id, old.full_name, old.national_id, old.province, old.phone, old.address);
    INSERT INTO records_fts(rowid, full_name, national_id, province, phone, address)
    VALUES (new.id, new.full_name, new.national_id, new.province, new.phone, new.address);
END;
"""

DEFAULT_SETTINGS_SQL = """
INSERT OR IGNORE INTO system_settings (key, value) VALUES
    ('maintenance_mode',  'false'),
    ('daily_limit',       '100'),
    ('max_results',       '10'),
    ('bot_version',       '2.1.0'),
    ('total_indexed',     '0');
"""

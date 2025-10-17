import sqlite3
from datetime import datetime

DB_PATH = "voice_times.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # Table for cumulative totals (per guild, per user)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS totals (
        guild_id INTEGER,
        user_id INTEGER,
        mute_seconds REAL DEFAULT 0,
        deaf_seconds REAL DEFAULT 0,
        PRIMARY KEY (guild_id, user_id)
    )
    """)
    # Table for active sessions (persist across restarts)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS active_sessions (
        guild_id INTEGER,
        user_id INTEGER,
        typ TEXT,            -- 'mute' or 'deaf'
        start_ts TEXT,       -- ISO timestamp in UTC
        PRIMARY KEY (guild_id, user_id, typ)
    )
    """)
    conn.commit()
    conn.close()

def start_session(guild_id: int, user_id: int, typ: str, start_ts: datetime):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO active_sessions (guild_id, user_id, typ, start_ts)
    VALUES (?, ?, ?, ?)
    """, (guild_id, user_id, typ, start_ts.isoformat()))
    conn.commit()
    conn.close()

def end_session_and_accumulate(guild_id: int, user_id: int, typ: str, end_ts: datetime):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT start_ts FROM active_sessions
    WHERE guild_id=? AND user_id=? AND typ=?
    """, (guild_id, user_id, typ))
    row = cur.fetchone()
    if not row:
        conn.close()
        return 0.0
    start_ts = datetime.fromisoformat(row["start_ts"])
    duration = (end_ts - start_ts).total_seconds()
    if duration < 0:
        duration = 0.0
    if typ == "mute":
        cur.execute("""
        INSERT INTO totals (guild_id, user_id, mute_seconds, deaf_seconds)
        VALUES (?, ?, ?, 0)
        ON CONFLICT(guild_id, user_id) DO UPDATE SET
          mute_seconds = totals.mute_seconds + excluded.mute_seconds
        """, (guild_id, user_id, duration))
    else:
        cur.execute("""
        INSERT INTO totals (guild_id, user_id, mute_seconds, deaf_seconds)
        VALUES (?, ?, 0, ?)
        ON CONFLICT(guild_id, user_id) DO UPDATE SET
          deaf_seconds = totals.deaf_seconds + excluded.deaf_seconds
        """, (guild_id, user_id, duration))
    # remove active session
    cur.execute("""
    DELETE FROM active_sessions
    WHERE guild_id=? AND user_id=? AND typ=?
    """, (guild_id, user_id, typ))
    conn.commit()
    conn.close()
    return duration

def is_session_active(guild_id: int, user_id: int, typ: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT 1 FROM active_sessions
    WHERE guild_id=? AND user_id=? AND typ=?
    """, (guild_id, user_id, typ))
    r = cur.fetchone() is not None
    conn.close()
    return r

def get_totals(guild_id: int, user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT mute_seconds, deaf_seconds FROM totals
    WHERE guild_id=? AND user_id=?
    """, (guild_id, user_id))
    row = cur.fetchone()
    conn.close()
    if not row:
        return 0.0, 0.0
    return float(row["mute_seconds"]), float(row["deaf_seconds"])

def get_top(guild_id: int, typ: str, limit=10):
    conn = get_conn()
    cur = conn.cursor()
    if typ == "mute":
        cur.execute("""
        SELECT user_id, mute_seconds as s FROM totals
        WHERE guild_id=?
        ORDER BY s DESC LIMIT ?
        """, (guild_id, limit))
    else:
        cur.execute("""
        SELECT user_id, deaf_seconds as s FROM totals
        WHERE guild_id=?
        ORDER BY s DESC LIMIT ?
        """, (guild_id, limit))
    rows = cur.fetchall()
    conn.close()
    return [(r["user_id"], float(r["s"])) for r in rows]

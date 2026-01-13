import os
import sqlite3
from typing import Iterable, Optional, List, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "supersearch.db")


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS meta(
  key TEXT PRIMARY KEY,
  val TEXT
);

CREATE TABLE IF NOT EXISTS files(
  id INTEGER PRIMARY KEY,
  path TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  is_dir INTEGER NOT NULL DEFAULT 0,
  dir TEXT NOT NULL,
  ext TEXT,
  size INTEGER,
  mtime REAL
);

CREATE INDEX IF NOT EXISTS idx_files_ext ON files(ext);
CREATE INDEX IF NOT EXISTS idx_files_dir ON files(dir);
CREATE INDEX IF NOT EXISTS idx_files_is_dir ON files(is_dir);
"""


def connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    try:
        cur = conn.execute("PRAGMA table_info(files)")
        cols = [row[1] for row in cur.fetchall()]
        if "is_dir" not in cols:
            conn.execute("ALTER TABLE files ADD COLUMN is_dir INTEGER NOT NULL DEFAULT 0")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_is_dir ON files(is_dir)")
    except Exception:
        pass
    conn.commit()


def bulk_upsert(conn: sqlite3.Connection, rows: Iterable[tuple]) -> int:
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO files(path,name,dir,ext,size,mtime,is_dir)
        VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(path) DO UPDATE SET
          name=excluded.name,
          dir=excluded.dir,
          ext=excluded.ext,
          size=excluded.size,
          mtime=excluded.mtime,
          is_dir=excluded.is_dir
        """,
        rows,
    )
    conn.commit()
    return cur.rowcount


def clear_all(conn: sqlite3.Connection, vacuum: bool = False) -> None:
    conn.execute("DELETE FROM files")
    conn.commit()
    if vacuum:
        conn.execute("VACUUM")
        conn.commit()


def search(conn: sqlite3.Connection, query: str, limit: int = 500) -> List[tuple]:
    q = query.strip()
    if not q:
        return []
    like = f"%{q.lower()}%"
    cur = conn.cursor()
    cur.execute(
        """
        SELECT name, path, dir, ext, size, mtime, is_dir
        FROM files
        WHERE name LIKE ?
        ORDER BY name ASC
        LIMIT ?
        """,
        (like, limit),
    )
    return cur.fetchall()


def delete_file(conn: sqlite3.Connection, path: str) -> None:
    conn.execute("DELETE FROM files WHERE path = ?", (path,))
    conn.commit()


def get_stats(conn: sqlite3.Connection) -> List[tuple]:
    """Returns [(ext, total_size, count), ...] grouped by extension"""
    cur = conn.cursor()
    cur.execute("SELECT ext, SUM(size), COUNT(*) FROM files WHERE is_dir=0 GROUP BY ext")
    return cur.fetchall()


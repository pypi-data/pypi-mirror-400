import os
import sys
import time
import threading
from typing import Iterable, List, Optional

from .db import bulk_upsert, clear_all, connect, init_db


def _get_drives() -> List[str]:
    import ctypes

    buf = ctypes.create_unicode_buffer(256)
    length = ctypes.windll.kernel32.GetLogicalDriveStringsW(256, buf)
    drives = buf[:length].split("\x00")

    DRIVE_FIXED = 3
    res: List[str] = []
    for d in drives:
        if not d:
            continue
        t = ctypes.windll.kernel32.GetDriveTypeW(d)
        if t == DRIVE_FIXED:
            res.append(d.rstrip("\\"))
    return res


def _ext(name: str) -> str:
    base, ext = os.path.splitext(name)
    return ext[1:].lower() if ext else ""


def scan_paths(roots: Optional[Iterable[str]] = None, stop_event: Optional[threading.Event] = None) -> int:
    conn = connect()
    init_db(conn)
    try:
        if roots is None:
            return 0
        total = 0
        rows: List[tuple] = []
        BATCH = 5000
        for root in roots:
            try:
                for dirpath, dirnames, filenames in os.walk(root, topdown=True):
                    if stop_event and stop_event.is_set():
                        return total
                    for dname in dirnames:
                        dpath = os.path.join(dirpath, dname)
                        try:
                            st = os.stat(dpath)
                            dsize = st.st_size
                            dmtime = st.st_mtime
                        except Exception:
                            dsize = None
                            dmtime = None
                        rows.append(
                            (
                                dpath,
                                dname,
                                dirpath,
                                "",
                                dsize,
                                dmtime,
                                1,
                            )
                        )
                    for name in filenames:
                        path = os.path.join(dirpath, name)
                        try:
                            st = os.stat(path)
                            size = st.st_size
                            mtime = st.st_mtime
                        except Exception:
                            size = None
                            mtime = None
                        rows.append(
                            (
                                path,
                                name,
                                dirpath,
                                _ext(name),
                                size,
                                mtime,
                                0,
                            )
                        )
                        if len(rows) >= BATCH:
                            total += bulk_upsert(conn, rows)
                            rows.clear()
            except Exception:
                continue
        if rows:
            total += bulk_upsert(conn, rows)
        return total
    finally:
        try:
            conn.close()
        except Exception:
            pass


class IndexerThread(threading.Thread):
    def __init__(self, roots: Optional[Iterable[str]] = None, on_progress=None, on_done=None):
        super().__init__(daemon=True)
        self.roots = list(roots) if roots else None
        self.on_progress = on_progress
        self.on_done = on_done
        self.stop_event = threading.Event()

    def run(self):
        start = time.time()
        total = scan_paths(self.roots, self.stop_event)
        dur = time.time() - start
        if self.on_done:
            try:
                self.on_done(total, dur)
            except Exception:
                pass

    def stop(self):
        self.stop_event.set()

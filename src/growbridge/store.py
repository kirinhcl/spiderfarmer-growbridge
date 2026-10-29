import json
import sqlite3
import time
from pathlib import Path


class Store:
    def __init__(self, path: Path):
        self.path = path.resolve()
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS samples(at REAL NOT NULL, data TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS samples_at ON samples(at);
            CREATE TABLE IF NOT EXISTS operations(
                id TEXT PRIMARY KEY, kind TEXT NOT NULL, params TEXT NOT NULL,
                state TEXT NOT NULL, result TEXT, at REAL NOT NULL);
        """)
        self.db.commit()

    def sample(self, data: dict) -> None:
        self.db.execute("INSERT INTO samples VALUES(?,?)", (time.time(), json.dumps(data)))
        self.db.commit()

    def history(self, hours: float, limit: int = 500) -> list[dict]:
        rows = self.db.execute(
            "SELECT at,data FROM samples WHERE at>=? ORDER BY at DESC LIMIT ?",
            (time.time() - hours * 3600, limit),
        ).fetchall()
        return [{"timestamp": at, "data": json.loads(data)} for at, data in reversed(rows)]

    def prune(self, days: int) -> None:
        self.db.execute("DELETE FROM samples WHERE at<?", (time.time() - days * 86400,))
        self.db.commit()

    def series(self, hours: float, points: int = 600) -> dict:
        end = time.time()
        start = end - hours * 3600
        bucket = max(1, (end - start) / points)
        count = self.db.execute(
            "SELECT COUNT(*) FROM samples WHERE at BETWEEN ? AND ?", (start, end)
        ).fetchone()[0]
        rows = self.db.execute(
            "SELECT s.at,s.data FROM samples s JOIN ("
            "SELECT MAX(rowid) AS sample_id FROM samples WHERE at BETWEEN ? AND ? "
            "GROUP BY CAST((at-?)/? AS INTEGER)) b ON s.rowid=b.sample_id ORDER BY s.at",
            (start, end, start, bucket),
        ).fetchall()
        return {
            "samples": [{"timestamp": at, "data": json.loads(data)} for at, data in rows],
            "window": {"start": start, "end": end, "bucket_seconds": bucket},
            "total_samples": count,
            "downsampled": count > len(rows),
        }

    def iter_samples(self, start: float, end: float):
        # StreamingResponse may advance this iterator on different worker threads.
        # This dedicated connection is read-only and used sequentially by the iterator.
        db = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True, check_same_thread=False)
        try:
            for at, data in db.execute(
                "SELECT at,data FROM samples WHERE at BETWEEN ? AND ? ORDER BY at", (start, end)
            ):
                yield at, json.loads(data)
        finally:
            db.close()

    def activity(self, limit: int = 20) -> list[dict]:
        rows = self.db.execute(
            "SELECT id,kind,params,state,at FROM operations ORDER BY at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [
            {
                "request_id": key,
                "action": kind,
                "params": json.loads(params),
                "state": state,
                "requested_at": at,
            }
            for key, kind, params, state, at in rows
        ]

    def operation(self, key: str):
        row = self.db.execute(
            "SELECT kind,params,state,result,at FROM operations WHERE id=?", (key,)
        ).fetchone()
        if row is None:
            return None
        return dict(zip(("kind", "params", "state", "result", "at"), row, strict=True))

    def begin(self, key: str, kind: str, params: dict) -> None:
        self.db.execute(
            "INSERT INTO operations VALUES(?,?,?,'pending',NULL,?)",
            (key, kind, json.dumps(params, sort_keys=True), time.time()),
        )
        self.db.commit()

    def complete(self, key: str, result: dict, state: str = "complete") -> None:
        self.db.execute(
            "UPDATE operations SET state=?,result=? WHERE id=?", (state, json.dumps(result), key)
        )
        self.db.commit()

    def pending(self) -> list[tuple[str, str]]:
        return self.db.execute("SELECT id,kind FROM operations WHERE state='pending'").fetchall()

    def last_pump(self) -> float:
        return self.db.execute(
            "SELECT COALESCE(MAX(at),0) FROM operations WHERE kind='pump'"
        ).fetchone()[0]

    def close(self):
        self.db.close()

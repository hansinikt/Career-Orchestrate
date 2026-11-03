"""SQLite via the standard library. User data ONLY. The catalog (skills, roles, courses) lives in data/v2/*.json under git, never in the database."""
import json, os, sqlite3, pathlib, threading
SCHEMA = (pathlib.Path(__file__).resolve().parent / "schema.sql").read_text()
_lock = threading.Lock()
def connect():
    path = os.environ.get("DB_PATH", str(pathlib.Path(__file__).resolve().parents[2] / "app.db"))
    c = sqlite3.connect(path, check_same_thread=False); c.row_factory = sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); c.executescript(SCHEMA); return c
class DB:
    def __init__(self): self.c = connect()
    def one(self, sql, args=()):
        with _lock: return self.c.execute(sql, args).fetchone()
    def all(self, sql, args=()):
        with _lock: return self.c.execute(sql, args).fetchall()
    def run(self, sql, args=()):
        with _lock: cur = self.c.execute(sql, args); self.c.commit(); return cur
    def log(self, at, actor, action, profile_id=None, detail=None):
        self.run("INSERT INTO audit_log(at,actor,action,profile_id,detail) VALUES (?,?,?,?,?)", (at, actor, action, profile_id, json.dumps(detail) if detail else None))

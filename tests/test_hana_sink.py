"""The HANA mirror is optional and must never break the app. Tested with a fake hdbcli (no SAP system is contacted)."""
import sys, types
from backend.app import hana_sink as H, orchestrator as O

ROW = dict(profile_id="prof_x", agent="skills_discovery", mode="rules", input_summary="a", output_summary="b", stopped_at_gate=False, created_at="2026-11-04T10:00:00+00:00")
class Cur:
    def __init__(s, log): s.log = log
    def execute(s, sql, params=None): s.log.append((sql, params))
    def fetchone(s): return (0,)
    def close(s): pass
class Conn:
    def __init__(s): s.log = []; s.commits = 0
    def cursor(s): return Cur(s.log)
    def commit(s): s.commits += 1
    def close(s): pass
def fake_hdbcli(monkeypatch, conn, fail=False):
    def connect(**kw):
        assert kw["encrypt"] is True and kw["port"] == 443         # HANA Cloud needs an encrypted connection on 443
        if fail: raise RuntimeError("down")
        return conn
    mod = types.ModuleType("hdbcli"); mod.dbapi = types.SimpleNamespace(connect=connect)
    monkeypatch.setitem(sys.modules, "hdbcli", mod); monkeypatch.setitem(sys.modules, "hdbcli.dbapi", mod.dbapi)
def reset(monkeypatch, on=True):
    for k in ("HANA_HOST", "HANA_USER", "HANA_PASSWORD"):
        monkeypatch.setenv(k, "x") if on else monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(H, "_conn", None); monkeypatch.setattr(H, "_ready", False); monkeypatch.setattr(H, "_down_until", 0.0)

def test_off_without_settings(monkeypatch):
    reset(monkeypatch, on=False); assert not H.enabled() and H._write(ROW) is False
def test_writes_one_row_and_creates_the_table(monkeypatch):
    reset(monkeypatch); conn = Conn(); fake_hdbcli(monkeypatch, conn)
    assert H._write(ROW) is True
    sql = [x[0] for x in conn.log]
    assert any("CREATE TABLE CO_AGENT_TRACE" in q for q in sql) and any("INSERT INTO CO_AGENT_TRACE" in q for q in sql)
    assert conn.log[-1][1] == ("prof_x", "skills_discovery", "rules", "a", "b", 0, "2026-11-04T10:00:00+00:00")
def test_failure_never_raises_and_pauses(monkeypatch):
    reset(monkeypatch); fake_hdbcli(monkeypatch, Conn(), fail=True)
    assert H._write(ROW) is False and H.status()["paused"] is True
    assert H._write(ROW) is False                                   # skipped during the pause, no second connection attempt
def test_orchestrator_still_saves_to_sqlite_when_hana_breaks(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.app import main as M
    from tests.test_v4 import make
    pid, p = make()                                                  # a real profile, so the foreign key holds
    monkeypatch.setattr(H, "mirror", lambda row: (_ for _ in ()).throw(RuntimeError("boom")))
    n0 = len(O.trace(pid)); O.record(pid, "skills_discovery", "rules", "in", "out")
    assert len(O.trace(pid)) == n0 + 1

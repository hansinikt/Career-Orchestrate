"""Orchestrator record: which agent did what, in time order. Summaries are one short line built from numbers and ids only: never the worker's text or name."""
import datetime as dt
AGENTS = ("skills_discovery", "market_intelligence", "learning_pathway", "inclusive_matching", "bias_audit", "human_in_the_loop")
_db = None
def bind(db): global _db; _db = db
def record(profile_id, agent, mode, input_summary, output_summary, stopped_at_gate=False, dedupe=False):
    assert agent in AGENTS, agent
    if dedupe:
        last = _db.one("SELECT mode,input_summary,output_summary FROM agent_trace WHERE profile_id=? AND agent=? ORDER BY id DESC LIMIT 1", (profile_id, agent))
        if last and (last["mode"], last["input_summary"], last["output_summary"]) == (mode, input_summary, output_summary): return
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    _db.run("INSERT INTO agent_trace(profile_id,agent,mode,input_summary,output_summary,stopped_at_gate,created_at) VALUES (?,?,?,?,?,?,?)",
            (profile_id, agent, mode, input_summary[:160], output_summary[:160], 1 if stopped_at_gate else 0, now))
    try:   # optional copy to SAP HANA Cloud; does nothing unless the HANA settings are set, and never stops the app
        from . import hana_sink
        hana_sink.mirror(dict(profile_id=profile_id, agent=agent, mode=mode, input_summary=input_summary[:160], output_summary=output_summary[:160], stopped_at_gate=stopped_at_gate, created_at=now))
    except Exception: pass
def trace(profile_id):
    rows = _db.all("SELECT * FROM agent_trace WHERE profile_id=? ORDER BY id", (profile_id,))
    return [dict(step=i, agent=r["agent"], mode=r["mode"], input_summary=r["input_summary"], output_summary=r["output_summary"], stopped_at_gate=bool(r["stopped_at_gate"]), created_at=r["created_at"]) for i, r in enumerate(rows, 1)]

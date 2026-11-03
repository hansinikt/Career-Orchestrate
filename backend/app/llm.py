"""Language-model adapter. One job: ask for JSON and hand it back, or return None so the caller falls back to rules.
Modes (APP_MODE): replay (default) = reuse a saved answer from data/v2/replay/ if one exists, never calls the network;
                  live = call the provider (needs LLM_PROVIDER=gemini and LLM_API_KEY); set LLM_RECORD=true to save answers for replay (synthetic demo data only).
The key is read from the environment or a local .env file (never committed). Only the worker's own work text and the public skill catalogue are sent: never the name."""
import hashlib, json, os, pathlib, logging, time
import httpx
ROOT = pathlib.Path(__file__).resolve().parents[2]
REPLAY = ROOT / "data" / "v2" / "replay"
log = logging.getLogger("llm")
_calls, _down_until = [], 0.0   # live-call times (all routes share one cap); time before which live calls are skipped after a failure
def _load_env():
    f = ROOT / ".env"
    if not f.is_file(): return
    for line in f.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if "=" in line:
            k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
_load_env()
def app_mode(): return os.environ.get("APP_MODE", "replay").lower()
def live_ready(): return app_mode() == "live" and os.environ.get("LLM_PROVIDER", "").lower() == "gemini" and bool(os.environ.get("LLM_API_KEY"))
def _key(task, system, user): return hashlib.sha256(f"{task}\n{system}\n{user}".encode()).hexdigest()[:24]
def _gemini(system, user):
    model = os.environ.get("LLM_MODEL") or "gemini-2.5-flash"
    body = {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": user}]}], "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}}
    r = httpx.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", json=body, headers={"x-goog-api-key": os.environ["LLM_API_KEY"]}, timeout=10)
    r.raise_for_status()
    return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
def ask_json(task, system, user):
    """-> (data, source) where source is 'live' or 'replay'; (None, None) when unavailable. Never raises."""
    k = _key(task, system, user); f = REPLAY / f"{task}_{k}.json"
    global _down_until
    t = time.time(); _calls[:] = [x for x in _calls if t - x < 60]
    try:
        if live_ready() and t >= _down_until and len(_calls) < int(os.environ.get("RATE_LIMIT_PER_MIN", "40")):
            _calls.append(t); data = _gemini(system, user); log.warning("LLM task %s answered live in %.1f s", task, time.time() - t)
            if os.environ.get("LLM_RECORD", "").lower() == "true":
                REPLAY.mkdir(parents=True, exist_ok=True); f.write_text(json.dumps(data, ensure_ascii=False, indent=1))
            return data, "live"
        if app_mode() == "replay" and f.is_file(): return json.loads(f.read_text()), "replay"
    except Exception as e:  # network, quota, bad JSON: the caller falls back to rules
        _down_until = time.time() + 60; log.warning("LLM call failed (%s); using rules for 60 s", type(e).__name__)
    return None, None

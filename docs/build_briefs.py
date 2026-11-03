"""Builds the five AI-ready briefs from docs/briefs/*.md, inserting real fixtures, the endpoint table, schema and contract so nothing is hand-copied."""
import json, re, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent; B = ROOT / "docs" / "briefs"; sys.path.insert(0, str(ROOT))
def trunc(o, n):
    if isinstance(o, list):
        r = [trunc(x, n) for x in o[:n]]; 
        if len(o) > n: r.append(f"... {len(o)-n} more")
        return r
    if isinstance(o, dict): return {k: trunc(v, n) for k, v in o.items()}
    return o
def fix(m): return json.dumps(trunc(json.loads((ROOT / "data/v2/fixtures" / f"{m.group(1)}.json").read_text()), int(m.group(2))), indent=2, ensure_ascii=False)
def js(m):
    d = json.loads((ROOT / m.group(1)).read_text()); key, idx = m.group(2), m.group(3)
    obj = d[key] if key != "-" else d
    obj = obj[int(idx)] if isinstance(obj, list) else obj[idx]
    return json.dumps(obj, indent=2, ensure_ascii=False)
def fil(m): return (ROOT / m.group(1)).read_text().rstrip("\n")
def endpoints(_):
    spec = json.loads((ROOT / "contracts/v2/openapi.json").read_text()); rows = ["| Method | Path | Request body | Success response |", "|---|---|---|---|"]
    ref = lambda d: (d or {}).get("$ref", "").split("/")[-1] or "-"
    for path, ops in sorted(spec["paths"].items()):
        for meth, o in ops.items():
            body = ref(((o.get("requestBody") or {}).get("content") or {}).get("application/json", {}).get("schema"))
            ok = next(((c, v) for c, v in o["responses"].items() if c.startswith("2")), ("200", {})); rs = ref(((ok[1].get("content") or {}).get("application/json") or {}).get("schema"))
            rows.append(f"| {meth.upper()} | `{path}` | {body} | {ok[0]} {rs if rs != '-' else ''} |")
    return "\n".join(rows)
def msglib(_):
    from engine import motivation as M
    rows = ["| Style | " + " | ".join(M.EVENTS) + " |", "|---|" + "---|" * len(M.EVENTS)]
    for st in M.STYLES: rows.append(f"| **{st}** | " + " | ".join(M.LIB[st][e].replace("|", "/") for e in M.EVENTS) + " |")
    return "\n".join(rows)
def rules(_):
    from engine import readiness as R
    return "\n".join(["| Rule id | Why flagged | Suggestion |", "|---|---|---|"] + [f"| `{a}` | {c} | {d} |" for a, b, c, d in R.RULES])
PRE = """=== INSTRUCTIONS FOR THE AI ASSISTANT (read this first, follow it exactly) ===
You are helping ONE developer on the {role} part of "Career Orchestrator", a hackathon prototype built by four first-time collaborators.
This brief is your ONLY source of truth. Rules:
1. Use only what is written in this brief and in files the developer pastes into the chat. If something is not specified, reply "Not specified in the brief" and ask the developer. Never guess.
2. Never invent: API endpoints, field names, status codes, library or package names, file names, course names, web links, statistics, or job adverts.
3. Never add or use age, date of birth, gender, graduation year, or years of experience, anywhere (code, data, screens, prompts, tests).
4. Allowed technology: {allowed}
5. Files you may create or change: {owns} Never change any other file.
6. Work on ONE task at a time. The developer will name a task id. Your FIRST reply must be a PLAN only (files to change, with bullet points). Wait for the developer to say "go" before writing code.
7. After writing code, give the exact command(s) to test it and list every assumption you made. Do not say "done" unless the tests pass.
8. If this brief contradicts itself or the request would break a rule, STOP and say so.
=== END OF INSTRUCTIONS ==="""
ROLES = {"frontend": ("FRONTEND", "plain HTML, CSS and JavaScript (ES modules) only. No npm, no frameworks (React, Vue, Angular and similar), no build tools, no CSS frameworks, no scripts loaded from the internet.", "everything inside frontend/ (index.html, app.js, config.js, strings.js, styles.css, screens/*.js). api.js is finished: change it only if the contract changes."),
         "backend": ("BACKEND", "Python 3.11+, the standard library, and ONLY these packages: fastapi, uvicorn, pydantic, httpx, pytest, PyYAML. No ORM, no other database than SQLite, no new frameworks, no task queues.", "backend/app/*, backend/requirements.txt (only if the team agrees), tools/*.py (new), the Makefile (only the backup and restore targets), and NEW test files named tests/test_backend_*.py."),
         "data": ("DATA AND AI", "Python 3.11+ standard library ONLY inside engine/ (no numpy, pandas, scikit-learn, no network calls, no database). Data files are JSON.", "engine/*.py, data/v2/skills.json, data/v2/roles.json, data/v2/aliases.json, data/*.py, and NEW test files named tests/test_engine_*.py. You must NOT edit data/v2/resources.json (only Dev 4, a human, edits it)."),
         "integration": ("INTEGRATION", "Git and GitHub, shell commands, Python 3.11+, the Makefile. No new libraries without asking.", "tests/*, .github/*, docs/*, data/v2/resources.json (a human enters verified courses only; you must never invent one).")}
def build(src):
    key = src.stem.split("_", 1)[1].split("_")[0].lower(); text = src.read_text()
    if key in ROLES: r = ROLES[key]; text = text.replace("{{PREAMBLE}}", PRE.format(role=r[0], allowed=r[1], owns=r[2]))
    text = re.sub(r"\{\{FIX:([a-z0-9_]+):(\d+)\}\}", fix, text); text = re.sub(r"\{\{FILE:([^}]+)\}\}", fil, text); text = re.sub(r"\{\{JSON:([^:}]+):([^:}]+):([^}]+)\}\}", js, text)
    text = text.replace("{{ENDPOINTS}}", endpoints(0)).replace("{{MSGLIB}}", msglib(0)).replace("{{RULES}}", rules(0))
    assert "{{" not in text, f"unresolved placeholder in {src.name}"
    out = B / "out" / src.name; out.write_text(text); return out, len(text.split()), len(text) // 4
for f in sorted(B.glob("0*.md")):
    o, w, t = build(f); print(f"{o.name}: {w} words, about {t} tokens")

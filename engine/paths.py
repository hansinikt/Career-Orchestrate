"""Job-option course paths. Pure functions, no I/O, no network.
For one role: which employer requirements the worker still lacks, which catalogue courses cover them, and the order to take them in (simplest first).
Nothing here is decided by a language model. A model may only write the one-sentence reason shown with each course (see backend/app/agents.py)."""
from __future__ import annotations

LEVEL_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2}
HAVE_LEVEL = 2          # a requirement counts as "already have" when the worker confirmed the matching skill at working level or above
MAX_COURSES = 5

def _text(course: dict) -> str:
    return " ".join([course["title"], *course.get("units", []), *course.get("topics", [])]).lower()

def covered_ids(course: dict, requirements: list[dict]) -> list[str]:
    t = _text(course)
    return [r["id"] for r in requirements if any(k in t for k in r["keywords"])]

def build_path(role_id: str, data: dict, levels: dict[str, int], max_courses: int = MAX_COURSES) -> dict:
    """-> {requirements: [...], courses: [...]} ; courses are ordered simplest first. levels: confirmed skill_id -> level."""
    reqs = data["requirements"].get(role_id, [])
    have = {r["id"] for r in reqs if r.get("skill_id") and levels.get(r["skill_id"], 0) >= HAVE_LEVEL}
    gaps = [r for r in reqs if r["id"] not in have]
    pool = []
    for c in data["courses"]:
        if role_id not in c["roles"]: continue
        cov = covered_ids(c, reqs); useful = [i for i in cov if i not in have]
        if useful: pool.append((c, cov, useful))
    # who gets in: most missing requirements covered first. SAP is only a tie-break. Then the chosen ones are ordered simplest first.
    pool.sort(key=lambda x: (-len(x[2]), "SAP" not in x[0]["provider"], x[0]["hours"] or 0, x[0]["course_id"]))
    chosen = pool[:max_courses]
    chosen.sort(key=lambda x: (LEVEL_RANK.get(x[0]["level"], 1), -len(x[2]), "SAP" not in x[0]["provider"], x[0]["hours"] or 0, x[0]["course_id"]))
    name = {r["id"]: r["name"] for r in reqs}
    out = []
    for c, cov, useful in chosen:
        out.append(dict(c, covers=[name[i] for i in useful], covers_ids=useful, missing_total=len(gaps)))
    reqs_out = [dict(id=r["id"], name=r["name"], evidence=r["evidence"], have=r["id"] in have, courses_covering=sum(1 for c, _, u in chosen if r["id"] in u)) for r in reqs]
    return dict(requirements=reqs_out, courses=out)

def default_reason(c: dict) -> str:
    # Why a person should take this course: where it fits and how much of the gap it closes. The topics themselves are shown on the "Covers" line, so they are not repeated here.
    n, m = len(c["covers"]), c["missing_total"]
    start = {"beginner": "Pitched at beginners, so a good place to start", "intermediate": "A step up that builds on the basics"}.get(c.get("level"), "A solid next step")
    gap = f"all {m}" if n == m else f"{n} of the {m}"
    return f"{start}. It tackles {gap} skills employers ask for in this role that you do not have yet." + (" You finish with a certificate you can show." if c.get("certificate") else "")

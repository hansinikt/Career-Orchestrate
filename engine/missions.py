"""Missions: small tasks built from plan steps (or, when the course has a chapter list, from its chapters) with fixed templates. No model, no invented content."""
def build(steps: list, done_ids: set, started_ids: set = frozenset(), declined_ids: set = frozenset(), chapters_by_step: dict | None = None, limit: int = 6) -> list:
    chapters_by_step = chapters_by_step or {}; raw = []
    for s in steps:
        name = s["skill_name"]; chs = chapters_by_step.get(s["order"]) or []
        if chs:
            for i, ch in enumerate(chs, 1):
                raw.append(dict(mission_id=f"m{s['order']}c{i}", order=len(raw) + 1, chapter_title=ch["title"], title=f"Show what you learned: {ch['title']}",
                                brief=f"Write one short paragraph (3 to 5 sentences) about how you would use \"{ch['title']}\" in your own work. Upload it as your proof.", source=f"Step {s['order']} · {name}"))
        else:
            raw.append(dict(mission_id=f"m{s['order']}", order=len(raw) + 1, chapter_title=None, title=f"Show your {name} in practice",
                            brief=f"Write one short paragraph (3 to 5 sentences) about a real task where you used {name}. Upload it as your proof.", source=f"Step {s['order']}"))
    out, open_left = [], 2
    for m in raw[:limit]:
        mid = m["mission_id"]
        if mid in done_ids: status, pct = "done", 100
        elif mid in declined_ids: status, pct = "declined", 0
        elif open_left > 0: status, pct = "open", (50 if mid in started_ids else 0); open_left -= 1
        else: status, pct = "locked", 0
        out.append(dict(m, status=status, percent=pct))
    return out

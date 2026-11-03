"""Reference implementation of deterministic engine stages. Pure functions, no I/O, no network.
Matching weights are PROVISIONAL engineering choices (see PRD s27)."""
from __future__ import annotations
import json, math, pathlib, re, itertools
DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
WEIGHTS = {"skill_coverage": 0.60, "preference_fit": 0.15, "learnability": 0.25}
H_MAX = 120.0          # hours at which learnability reaches 0
BLOCK_COV = 0.5        # mandatory skill with coverage below this is a blocking gap
FORBIDDEN_FEATURES = {"age", "dob", "birth_year", "graduation_year", "gender", "name", "years_experience"}

def load(folder: str = ""):
    """folder="" -> original seed (data/); folder="v2" -> team-CSV seed (data/v2/)."""
    d = DATA / folder if folder else DATA
    sk = {s["skill_id"]: s for s in json.loads((d/"skills.json").read_text())["skills"]}
    roles = json.loads((d/"roles.json").read_text())["roles"]
    res = json.loads((d/"resources.json").read_text())["resources"]
    return sk, roles, res

def coverage(user_level: int, required: int) -> float:
    return min(1.0, user_level / required)

def pref_fit(prefs: list[str], tags: list[str]):
    if not prefs: return None
    n = len(prefs); w = {t: n - i for i, t in enumerate(prefs)}
    return sum(w.get(t, 0) for t in tags) / sum(w.values())

def score_role(user: dict[str, int], role: dict, prefs: list[str], sk: dict, evidence: dict[str, list[str]] | None = None) -> dict:
    """user: confirmed skill_id -> level 1..3 ONLY (unconfirmed skills never reach this function)."""
    evidence = evidence or {}
    reqs = role["requirements"]
    wsum = sum(r["importance"] for r in reqs)
    f1 = sum(r["importance"] * coverage(user.get(r["skill_id"], 0), r["required_level"]) for r in reqs) / wsum
    gaps, matched, blocking, hours = [], [], [], 0.0
    for r in reqs:
        u = user.get(r["skill_id"], 0); cov = coverage(u, r["required_level"]); meta = sk[r["skill_id"]]
        g = max(0, r["required_level"] - u)
        if u > 0:
            matched.append(dict(skill_id=r["skill_id"], name=meta["name"], user_level=u, required_level=r["required_level"],
                                coverage=round(cov, 3), evidence_ids=evidence.get(r["skill_id"], [])))
        if g > 0:
            h = g * meta["hours_per_level"]; hours += h
            if r["mandatory"] and cov < BLOCK_COV: blocking.append(r["skill_id"])
            gaps.append(dict(skill_id=r["skill_id"], name=meta["name"], required_level=r["required_level"], user_level=u, gap_levels=g,
                             mandatory=r["mandatory"], importance=r["importance"], est_hours=float(h),
                             priority=round(r["importance"] * g * (1.5 if r["mandatory"] else 1.0), 2)))
    f4 = 1 - min(1.0, hours / H_MAX)
    f3 = pref_fit(prefs, role["tags"])
    w = dict(WEIGHTS)
    if f3 is None:                       # missing information is NOT zero: drop the feature and renormalise
        w.pop("preference_fit"); t = sum(w.values()); w = {k: v / t for k, v in w.items()}
    score = w["skill_coverage"] * f1 + w["learnability"] * f4 + (w["preference_fit"] * f3 if f3 is not None else 0)
    band = "strong_fit" if (f1 >= 0.75 and not blocking) else ("bridgeable" if (f1 >= 0.50 and len(blocking) <= 2) else "stretch")
    flags = []
    if role.get("requires_degree"): flags.append("degree_required_check_if_skills_based_alternative_exists")
    if role.get("max_experience_years") is not None: flags.append(f"experience_cap_{role['max_experience_years']}_years")
    gaps.sort(key=lambda g: -g["priority"])
    return dict(role_id=role["role_id"], title=role["title"], score=round(score, 4), band=band,
                feature_scores=dict(skill_coverage=round(f1, 4), preference_fit=None if f3 is None else round(f3, 4), learnability=round(f4, 4)),
                weights_used={k: round(v, 4) for k, v in w.items()}, blocking_gaps=blocking, matched=matched, gaps=gaps,
                est_gap_hours=float(hours), openness_flags=flags, provisional_weights=True)

def explain(rec: dict) -> str:
    m = ", ".join(x["name"] for x in rec["matched"][:3]) or "none yet"
    g = ", ".join(x["name"] for x in rec["gaps"][:2]) or "none"
    return (f"{rec['title']}: skill coverage {rec['feature_scores']['skill_coverage']:.0%}. Strongest matches: {m}. "
            f"Biggest gaps: {g} (~{rec['est_gap_hours']:.0f} h estimated). Band: {rec['band'].replace('_',' ')}. Weights are provisional.")

def rank(user, roles, prefs, sk, evidence=None):
    recs = [score_role(user, r, prefs, sk, evidence) for r in roles]
    recs.sort(key=lambda r: (-r["score"], r["role_id"]))       # deterministic tie-break
    for i, r in enumerate(recs, 1): r["rank"] = i; r["explanation"] = explain(r)
    return recs

def build_plan(rec: dict, user: dict, sk: dict, resources: list, weekly_hours: int | None, allow_unverified=True, allow_sample=False) -> dict:
    steps, unresolved, done = [], [], set(u for u, l in user.items() if l >= 1)
    gaps = rec["gaps"]
    gap_ids = {g["skill_id"] for g in gaps}
    # order: prerequisites first (topological over gap skills), then priority
    ordered, seen = [], set()
    def visit(g):
        if g["skill_id"] in seen: return
        seen.add(g["skill_id"])
        for p in sk[g["skill_id"]]["prerequisites"]:
            pg = next((x for x in gaps if x["skill_id"] == p), None)
            if pg: visit(pg)
        ordered.append(g)
    for g in gaps: visit(g)
    total = 0.0; order = 0
    for g in ordered:
        meta = sk[g["skill_id"]]; cur = g["user_level"]; builds = [p for p in meta["prerequisites"] if p in done]
        while cur < g["required_level"]:
            ok = [r for r in resources if g["skill_id"] in r["skill_ids"] and r["level_from"] <= cur < r["level_to"]
                  and (r["verification_status"] == "verified" or (allow_unverified and r["verification_status"] == "seed_unverified")
                       or (allow_sample and r["verification_status"] == "sample_placeholder"))]
            ok.sort(key=lambda r: (r["verification_status"] != "verified", r["verification_status"] == "sample_placeholder", r["provider"] != "SAP Learning Hub (student edition)", -r["level_to"], r["resource_id"]))
            res = ok[0] if ok else None
            nxt = min(res["level_to"], g["required_level"]) if res else g["required_level"]
            h = float((nxt - cur) * meta["hours_per_level"]); total += h; order += 1
            if res is None: unresolved.append(g["skill_id"])
            steps.append(dict(order=order, skill_id=g["skill_id"], skill_name=g["name"], status="resource_found" if res else "no_verified_resource",
                              resource=res, est_hours=h, builds_on=builds,
                              rationale=f"Moves {meta['name']} from level {cur} to {nxt} (target {g['required_level']})" + (" - mandatory" if g["mandatory"] else "")
                                        + (f"; builds on your {', '.join(sk[b]['name'] for b in builds)}" if builds else "")))
            cur = nxt
    return dict(role_id=rec["role_id"], total_est_hours=total,
                weeks_at_pace=None if not weekly_hours else math.ceil(total / weekly_hours), steps=steps, unresolved_skill_ids=unresolved)

# ---------------- grounding validators (anti-hallucination) ----------------
def norm(s): return re.sub(r"\s+", " ", s).strip().lower()
def quote_is_grounded(quote: str, source_texts: list[str]) -> bool:
    q = norm(quote); return bool(q) and any(q in norm(t) for t in source_texts)
NUM = re.compile(r"\d+(?:[,.]\d+)*%?")
def ungrounded_numbers(generated: str, source_texts: list[str]) -> list[str]:
    src = " ".join(source_texts); have = set(NUM.findall(src))
    return [n for n in NUM.findall(generated) if n not in have]

# ---------------- bias audit ----------------
AGE_LEXICON = ["recent graduate","digital native","young","energetic","fresh","veteran","seasoned","overqualified","old-school","set in their ways","tech-savvy millennial","adapt to new technology","too senior","near retirement"]
def lexicon_hits(text: str) -> int:
    t = norm(text); return sum(t.count(w) for w in AGE_LEXICON)
def kendall_tau(a: list[str], b: list[str]) -> float:
    pos = {x: i for i, x in enumerate(b)}; n = len(a); c = d = 0
    for i, j in itertools.combinations(range(n), 2):
        c += pos[a[i]] < pos[a[j]]; d += pos[a[i]] > pos[a[j]]
    return (c - d) / (n * (n - 1) / 2)
def jaccard(a, b):
    a, b = set(a), set(b); return 1.0 if not a and not b else len(a & b) / len(a | b)
THRESH = dict(skills_jaccard_min=0.90, top3_overlap_min=3, kendall_tau_min=0.90, max_abs_score_delta_max=0.03, plan_hours_delta_max=10.0, lexicon_hits_max=0)
def compare(base: dict, var: dict) -> dict:
    """base/var: {'skills': {id:level}, 'recs': ranked list, 'plan_hours': float, 'text': str}"""
    bo = [r["role_id"] for r in base["recs"]]; vo = [r["role_id"] for r in var["recs"]]
    bs = {r["role_id"]: r["score"] for r in base["recs"]}; vs = {r["role_id"]: r["score"] for r in var["recs"]}
    return dict(skills_jaccard=round(jaccard(base["skills"].items(), var["skills"].items()), 4), top3_overlap=len(set(bo[:3]) & set(vo[:3])),
                kendall_tau=round(kendall_tau(bo, vo), 4), max_abs_score_delta=round(max(abs(bs[k] - vs[k]) for k in bs), 4),
                plan_hours_delta=round(abs(base["plan_hours"] - var["plan_hours"]), 2), lexicon_hits=lexicon_hits(var["text"]))
def flags_for(variant_id: str, m: dict) -> list[dict]:
    out = []
    chk = [("skills_jaccard", m["skills_jaccard"] < THRESH["skills_jaccard_min"], THRESH["skills_jaccard_min"]),
           ("top3_overlap", m["top3_overlap"] < THRESH["top3_overlap_min"], THRESH["top3_overlap_min"]),
           ("kendall_tau", m["kendall_tau"] < THRESH["kendall_tau_min"], THRESH["kendall_tau_min"]),
           ("max_abs_score_delta", m["max_abs_score_delta"] > THRESH["max_abs_score_delta_max"], THRESH["max_abs_score_delta_max"]),
           ("plan_hours_delta", m["plan_hours_delta"] > THRESH["plan_hours_delta_max"], THRESH["plan_hours_delta_max"]),
           ("lexicon_hits", m["lexicon_hits"] > THRESH["lexicon_hits_max"], THRESH["lexicon_hits_max"])]
    for name, bad, th in chk:
        if bad: out.append(dict(variant_id=variant_id, metric=name, observed=float(m[name]), threshold=float(th),
                                message=f"{name}={m[name]} breaches threshold {th} versus baseline; route to human reviewer"))
    return out

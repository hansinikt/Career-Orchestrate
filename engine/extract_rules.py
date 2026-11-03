"""Rules-based skill suggestion (no LLM). Evidence quotes are always verbatim substrings of the worker's own text.
Rules: declared skills keep the worker's level; skills found only in text are 'extracted' and capped at level 2 (inference never exceeds 'performed')."""
import json, re, pathlib
from . import core as E
ALIASES = json.loads((pathlib.Path(__file__).resolve().parent.parent / "data" / "v2" / "aliases.json").read_text())["aliases"]
PERFORMED = {"coordinated","maintained","prepared","managed","organized","organised","updated","resolved","documented","checked","supported","tracked",
             "handled","processed","scheduled","arranged","ran","wrote","produced","reviewed","led","owned","designed","built","delivered"}
def clauses(text: str):
    out = []
    for part in re.split(r"[;,\n]| and ", text):
        p = part.strip(" .")
        if p and p in text: out.append(p)
    return out
def extract_from_text(texts: list[str]) -> dict:
    """-> {skill_id: {level, signal, quotes[]}}"""
    found = {}
    for ti, text in enumerate(texts):
        for cl in clauses(text):
            low = cl.lower(); verb = low.split()[0] if low.split() else ""
            for sid, words in ALIASES.items():
                if any(re.search(rf"\b{re.escape(w)}\b", low) for w in sorted(words, key=len, reverse=True)):
                    lvl = 2 if verb in PERFORMED else 1
                    d = found.setdefault(sid, dict(level=0, signal="mentioned", quotes=[]))
                    if lvl > d["level"]: d["level"] = lvl; d["signal"] = "performed" if lvl == 2 else "mentioned"
                    if cl not in [q["quote"] for q in d["quotes"]]: d["quotes"].append(dict(quote=cl, work_example_index=ti))
    return found
def suggest(declared: list[dict], texts: list[str], sk: dict) -> list[dict]:
    """declared: [{name, level 1..3}]. Returns suggestions sorted by skill name; every quote re-validated as grounded."""
    by_name = {s["name"].lower(): s for s in sk.values()}; sug = {}; unscored = []
    ext = extract_from_text(texts)
    for d in declared:
        meta = by_name.get(d["name"].lower())
        if meta is None: unscored.append(d["name"]); continue
        if meta["scored"]: sid, src = meta["skill_id"], "declared"
        elif meta["alias_of"]: sid, src = meta["alias_of"], "declared_alias"
        else: unscored.append(d["name"]); continue
        cur = sug.get(sid)
        if cur is None or d["level"] > cur["suggested_level"]:
            sug[sid] = dict(skill_id=sid, suggested_level=d["level"], source=src, declared_as=d["name"])
    for sid, e in ext.items():
        if sid in sug: sug[sid]["_quotes"] = e["quotes"]; continue
        sug[sid] = dict(skill_id=sid, suggested_level=min(2, e["level"]), source="extracted", declared_as=None, _quotes=e["quotes"])
    out = []
    for sid, s in sug.items():
        quotes = [q for q in s.pop("_quotes", ext.get(sid, {}).get("quotes", [])) if E.quote_is_grounded(q["quote"], texts)]
        sig = "declared_only" if (s["source"] != "extracted" and not quotes) else ("performed" if s["suggested_level"] >= 2 else "mentioned")
        why = {"declared": "You listed this skill", "declared_alias": f"You listed '{s['declared_as']}'; we matched it to {sk[sid]['name']} (please confirm)",
               "extracted": "Found in your work examples"}[s["source"]]
        out.append(dict(skill_id=sid, name=sk[sid]["name"], suggested_level=s["suggested_level"], source=s["source"], signal=sig, evidence=quotes,
                        explanation=why + ("; supported by your examples" if quotes and s["source"] != "extracted" else ("; no supporting example yet" if not quotes else ""))))
    out.sort(key=lambda x: x["name"]); return out, unscored

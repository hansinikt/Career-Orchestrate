"""Deterministic job-ad openness check (no LLM). Flags wording that can exclude people for reasons other than skills. Flags go to a human; nothing is rejected."""
import re
from . import core as E
RULES = [
 ("experience_cap", r"\b(?:up to|maximum of|max\.?|not more than|no more than)\s+\d+\s*(?:\+\s*)?years?\b|\b0\s*-\s*\d+\s*years?\b", "Caps experience, which can screen out experienced workers", "Describe the skills needed instead of limiting years"),
 ("fresher_wording", r"\bfreshers?\b|\brecent graduates?\b|\bnew graduates?\b|\bgraduated (?:in|after) \d{4}\b", "Targets new graduates", "Say 'entry-level role' and list the skills required"),
 ("age_coded_wording", r"\b(?:young|energetic|digital native|dynamic young|tech-savvy millennial)\b", "Age-coded wording", "Describe the behaviour or skill you need"),
 ("degree_required", r"\b(?:degree|graduate)\b[^.]{0,40}\b(?:required|mandatory|must)\b|\b(?:must|required|mandatory)\b[^.]{0,40}\bdegree\b", "Requires a degree; check whether skills or experience could substitute", "Add 'or equivalent experience' if appropriate"),
 ("min_years", r"\b(?:minimum|at least|min\.?)\s+\d+\s*years?\b", "Years requirement; years are a weak proxy for skill", "State the tasks the person should be able to do")]
def check(text: str) -> dict:
    flags = []
    for rid, pat, why, sug in RULES:
        for m in re.finditer(pat, text, flags=re.I):
            flags.append(dict(rule_id=rid, matched_text=m.group(0), why=why, suggestion=sug))
    hits = E.lexicon_hits(text)
    if hits and not any(f["rule_id"] == "age_coded_wording" for f in flags):
        flags.append(dict(rule_id="age_coded_wording", matched_text="(lexicon)", why="Age-coded wording", suggestion="Describe the behaviour or skill you need"))
    return dict(status="flagged" if flags else "no_flags", flags=flags, skills_first=not flags,
                limitations=["Keyword rules only: a clean result does not prove a role is fair.", "A person decides what to change."])

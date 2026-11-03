"""CV reading and writing. Pure functions, no network. The CV text is first cleaned: contact details, the name line, years, and lines about age, gender and similar are removed and never used.
Everything returned is a piece of the cleaned text (verbatim) except the education level, which is one of a fixed set."""
import json, pathlib, re
ALIASES = json.loads((pathlib.Path(__file__).resolve().parent.parent / "data" / "v2" / "aliases.json").read_text())["aliases"]
SENSITIVE = re.compile(r"(date of birth|\bd\.?o\.?b\b|\bborn\b|\bage\s*[:\-]|\bgender\b|\bsex\b|\bmarital\b|\bnationality\b|\breligion\b|\bcaste\b|father'?s name|\bphotograph\b|\bphoto\b|\bmale\b|\bfemale\b|years? of (work |professional )?experience)", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"); URL = re.compile(r"(https?://|www\.)\S+", re.I); PHONE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
YEARS = re.compile(r"\b(?:for |over |more than |nearly |about )?\d{1,2}\+?\s*(?:years?|yrs?)\b(?: of)?(?: work| professional)?(?: experience)?", re.I)
YEAR4 = re.compile(r"\b(?:19|20)\d{2}\b(?:\s*(?:-|–|—|to)\s*(?:(?:19|20)\d{2}|present|current|now))?", re.I)
HEADS = {"summary": r"summary|profile|objective|about me|professional summary", "experience": r"(?:work |professional |relevant )?experience|employment(?: history)?|work history",
         "skills": r"(?:key |core |technical )?skills|competenc(?:y|ies)|strengths", "education": r"education|academics?|academic background|qualifications",
         "certs": r"certifications?|certificates?|training|courses|licen[sc]es", "languages": r"languages?"}
BULLET = re.compile(r"^[\s\-*•–·▪●]+")
def _scrub_line(raw: str):
    """-> (line, changed). Removes contact details, years and year ranges. Returns ('', True) for lines about age, gender and similar."""
    if SENSITIVE.search(raw): return "", True
    l = URL.sub("", EMAIL.sub("", raw)); l = PHONE.sub("", l) if re.search(r"\d[\d\s().-]{7,}\d", l) else l
    l2 = YEAR4.sub("", YEARS.sub("", l)); changed = l2 != l
    l2 = re.sub(r"\(\s*\)", "", l2); l2 = re.sub(r"[ \t]{2,}", " ", l2).strip(" ,;|-–—\t")
    return l2, changed
def scrub(text: str) -> str:
    """For short worker-written text (one work example): same cleaning, no name-line removal."""
    return _scrub_line(text)[0]
def clean(text: str):
    """-> (cleaned_text, ignored_lines)"""
    out, ignored = [], 0
    for raw in text.replace("\r", "").split("\n"):
        l, ch = _scrub_line(raw); ignored += 1 if ch else 0; out.append(l)
    # drop a leading name line (short, no digits, before any heading)
    for i, l in enumerate(out):
        if not l: continue
        if len(l) <= 40 and not re.search(r"\d", l) and not _head(l) and 1 <= len(l.split()) <= 4: out[i] = ""
        break
    return "\n".join(out).strip(), ignored
def _head(line: str):
    t = re.sub(r"[:\s]+$", "", line.strip()); 
    if not t or len(t) > 32: return None
    for k, pat in HEADS.items():
        if re.fullmatch(pat, t, re.I): return k
    return None
def sections(text: str) -> dict:
    cur, out = None, {k: [] for k in HEADS}; out["_top"] = []
    for l in text.split("\n"):
        k = _head(l)
        if k: cur = k; continue
        if l.strip(): out[cur or "_top"].append(l.strip())
    return out
def _tokens(lines, maxlen=40):
    toks = []
    for l in lines:
        for t in re.split(r"[,;|•·▪●\n]|\s-\s|\s–\s", BULLET.sub("", l)):
            t = t.strip(" .:")
            if 2 <= len(t) <= maxlen and t not in toks: toks.append(t)
    return toks
LEVELS = [("master", r"\b(ph\.?d|doctorate|master|m\.?sc|m\.?a\.?|mba|m\.?tech|m\.?com)\b"), ("bachelor", r"\b(bachelor|b\.?sc|b\.?a\.?|b\.?com|b\.?tech|b\.?e\.?|bba|bca)\b"),
          ("diploma", r"\b(diploma|polytechnic|certificate)\b"), ("school", r"\b(high school|secondary|higher secondary|12th|10th|hsc|ssc|school)\b")]
def parse_rules(text: str, sk: dict) -> dict:
    S = sections(text); by_name = {s["name"].lower(): s["name"] for s in sk.values() if s["scored"]}
    alias_to_name = {w: sk[sid]["name"] for sid, ws in ALIASES.items() if sid in sk for w in ws}
    role = None; exp = S["experience"]
    if exp:
        first = BULLET.sub("", exp[0]).strip()
        if len(first) <= 80 and not BULLET.match(exp[0]): role = re.split(r"\s+(?:at|@)\s+|\s*[,|]\s*|\s+-\s+|\s+–\s+", first)[0].strip() or None
    pool = [l for l in (exp[1:] if role else exp)] or S["summary"] or []
    examples = []
    for l in pool:
        c = BULLET.sub("", l).strip()
        if len(c) >= 10 and c not in examples: examples.append(c[:300])
    skills, tools = [], []
    for t in _tokens(S["skills"]):
        name = by_name.get(t.lower()) or alias_to_name.get(t.lower())
        (skills if name else tools).append(name or t)
    skills = list(dict.fromkeys(skills))
    edu = []
    for l in S["education"][:5]:
        c = BULLET.sub("", l).strip()
        if len(c) < 3: continue
        lvl = next((k for k, pat in LEVELS if re.search(pat, c, re.I)), "other"); m = re.search(r"\b(?:in|of)\s+([A-Za-z&][A-Za-z&, ]{2,50}?)(?=\s*(?:,|\(|\||-|–|$))", c)
        inst = next((t for t in _tokens([c], 80) if re.search(r"university|college|institute|school|academy", t, re.I)), None)
        edu.append(dict(line=c[:160], level=lvl, field=(m.group(1).strip()[:80] if m else None), institution=(inst[:80] if inst else None)))
    certs = []
    for l in S["certs"][:10]:
        c = BULLET.sub("", l).strip()
        if len(c) < 3: continue
        parts = re.split(r"\s+[-–|]\s+|,\s+", c, maxsplit=1); certs.append(dict(name=parts[0].strip()[:100], issuer=(parts[1].strip()[:80] if len(parts) > 1 else None)))
    langs = [re.sub(r"\s*\(.*?\)", "", t).strip() for t in _tokens(S["languages"], 30)]
    return dict(current_role=role, work_examples=examples[:5], skills=skills[:30], tools=tools[:20], certifications=certs, education=edu, languages=[x for x in langs if x][:8])
def grounded(parsed: dict, cleaned: str) -> dict:
    """Keep only strings that appear in the cleaned CV text (for model answers). Education level must be a known value."""
    ok = lambda s: isinstance(s, str) and 1 <= len(s) <= 300 and s in cleaned
    lv = {"school", "diploma", "bachelor", "master", "other"}
    def strs(v, n): return [x for x in (v if isinstance(v, list) else []) if ok(x)][:n]
    certs = [dict(name=c["name"][:100], issuer=(c.get("issuer") if ok(c.get("issuer")) else None)) for c in (parsed.get("certifications") or []) if isinstance(c, dict) and ok(c.get("name"))][:10]
    edu = [dict(line=e["line"][:160], level=(e.get("level") if e.get("level") in lv else None), field=(e.get("field") if ok(e.get("field")) else None), institution=(e.get("institution") if ok(e.get("institution")) else None))
           for e in (parsed.get("education") or []) if isinstance(e, dict) and ok(e.get("line"))][:5]
    return dict(current_role=parsed.get("current_role") if ok(parsed.get("current_role")) else None, work_examples=[x for x in strs(parsed.get("work_examples"), 5) if len(x) >= 10],
                skills=strs(parsed.get("skills"), 30), tools=strs(parsed.get("tools"), 20), certifications=certs, education=edu, languages=strs(parsed.get("languages"), 8))

LEVEL_WORD = {"school": "School", "diploma": "Diploma or certificate", "bachelor": "Bachelor's degree", "master": "Master's degree or higher", "other": "Other"}
def render(name, role, goal, skills, examples, education, certs, languages, tools, completed, tasks) -> tuple[str, list]:
    """Plain-text CV for applicant tracking systems. Built ONLY from what the person confirmed or did: no levels of experience, no years, no age, no gender."""
    L, secs = [name.upper(), ""], []
    def sec(title, lines):
        if lines: L.extend([title, *lines, ""]); secs.append(title)
    top = ", ".join(skills[:8])
    sec("SUMMARY", [f"{role or 'Professional'} working towards {goal}." + (f" Skills confirmed against my own work: {top}." if top else "")] if goal else ([f"{role}."] if role else []))
    sec("SKILLS", ([", ".join(skills)] if skills else []) + ([f"Tools: {', '.join(tools)}"] if tools else []))
    sec("EXPERIENCE", ([role] if role else []) + [f"- {e}" for e in examples])
    sec("TRAINING AND CERTIFICATIONS", [f"- {c['name']}" + (f", {c['issuer']}" if c.get("issuer") else "") for c in certs] + [f"- Completed: {c}" for c in completed] + [f"- Practical task completed: {t}" for t in tasks])
    sec("EDUCATION", ["- " + ", ".join(x for x in (LEVEL_WORD.get(e["level"]), e.get("field"), e.get("institution")) if x) for e in education])
    sec("LANGUAGES", [", ".join(languages)] if languages else [])
    return "\n".join(L).strip() + "\n", secs

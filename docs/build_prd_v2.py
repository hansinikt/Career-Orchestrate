import json, re, pathlib, html, subprocess, sys
import markdown
ROOT = pathlib.Path(__file__).resolve().parent.parent; PRD = ROOT/"docs"/"prd_v2"; OUT = ROOT/"docs"
parts = ["a","b","c","d","e"]
def trunc(o, n):
    if isinstance(o, list):
        r = [trunc(x, n) for x in o[:n]]
        if len(o) > n: r.append(f"... {len(o)-n} more")
        return r
    if isinstance(o, dict): return {k: trunc(v, n) for k, v in o.items()}
    return o
def fix(m):
    name, n = m.group(1), int(m.group(2)); d = json.loads((ROOT/"data"/"v2"/"fixtures"/f"{name}.json").read_text())
    return json.dumps(trunc(d, n), indent=2, ensure_ascii=False)
def inc(m):
    t = (ROOT/m.group(1)).read_text()
    if m.group(1).endswith(".md"): t = "\n".join(t.splitlines()[1:])
    return t.rstrip("\n")
md = "\n".join((PRD/f"{p}.md").read_text() for p in parts)
md = re.sub(r"\{\{FIX:([a-z0-9_]+):(\d+)\}\}", fix, md)
md = re.sub(r"\{\{FILE:([^}]+)\}\}", inc, md)
def endpoints(_):
    spec = json.loads((ROOT/"contracts"/"v2"/"openapi.json").read_text()); rows = ["| Method | Path | Request body | Success response | Purpose |", "|---|---|---|---|---|"]
    ref = lambda d: (d or {}).get("$ref", "").split("/")[-1] or "-"
    for path, ops in sorted(spec["paths"].items(), key=lambda kv: kv[0]):
        for meth, o in ops.items():
            body = ref(((o.get("requestBody") or {}).get("content") or {}).get("application/json", {}).get("schema"))
            ok = next(((c, v) for c, v in o["responses"].items() if c.startswith("2")), ("200", {}))
            rs = ref(((ok[1].get("content") or {}).get("application/json") or {}).get("schema"))
            rows.append(f"| {meth.upper()} | `{path}` | {body} | {ok[0]} {rs if rs != '-' else ''} | {o.get('summary','').replace('_',' ')} |")
    return "\n".join(rows)
md = re.sub(r"\{\{ENDPOINTS\}\}", endpoints, md)
def msglib(_):
    sys.path.insert(0, str(ROOT)); from engine import motivation as M
    rows = ["| Style | " + " | ".join(M.EVENTS) + " |", "|---|" + "---|" * len(M.EVENTS)]
    for st in M.STYLES: rows.append(f"| **{st}** | " + " | ".join(M.LIB[st][e].replace("|", "/") for e in M.EVENTS) + " |")
    return "\n".join(rows)
def rules(_):
    sys.path.insert(0, str(ROOT)); from engine import readiness as R
    rows = ["| Rule id | Pattern (regular expression) | Why it is flagged | Suggestion shown |", "|---|---|---|---|"]
    for rid, pat, why, sug in R.RULES: rows.append(f"| `{rid}` | `{pat.replace('|', chr(92) + '|')}` | {why} | {sug} |")
    return "\n".join(rows)
md = re.sub(r"\{\{MSGLIB\}\}", msglib, md); md = re.sub(r"\{\{RULES\}\}", rules, md)
# section 31 pointer sentence fix-up for learning pathway heading
md = md.replace("O*NET", "O\\*NET")
md_docx = md.replace("\\newpage", "").replace('<div class="land" markdown="1">', "").replace("</div>", "")
(OUT/"PRD_v2.md").write_text(md_docx)
nofence = re.sub(r"```.*?```", "", md, flags=re.S)
heads = re.findall(r"^(#{1,2}) (.+)$", nofence, flags=re.M)
toc_items = [(len(h), t.strip()) for h, t in heads if not t.startswith("Career Orchestrator: Build")]
def render(pages=None):
    body = markdown.markdown(md.replace("\\newpage", '<div class="pb"></div>'), extensions=["tables", "fenced_code", "sane_lists", "md_in_html"])
    # absolute image paths
    body = body.replace('src="diagrams/', f'src="file://{OUT}/diagrams/')
    # heading ids
    def idrep(m):
        return f'<h{m.group(1)} id="h{abs(hash(m.group(2)))%10**8}">{m.group(2)}</h{m.group(1)}>'
    body = re.sub(r"<h([12])>(.*?)</h\1>", idrep, body)
    rows = ""
    for lvl, t in toc_items:
        hid = f"h{abs(hash(html.escape(t, quote=False)))%10**8}"
        pg = (pages or {}).get(t, "")
        rows += f'<div class="toc l{lvl}"><a href="#{hid}">{html.escape(t)}</a><span class="dots"></span><span class="pn">{pg}</span></div>'
    toc = f'<div class="pb"></div><h1 class="toc-title">Table of contents</h1>{rows}<div class="pb"></div>'
    # put TOC after the front-matter block (first <div class="pb"></div>)
    first = body.index('<div class="pb"></div>') if '<div class="pb"></div>' in body else 0
    body = body[:first] + toc + body[first+len('<div class="pb"></div>'):] if first else toc + body
    css = (OUT/"prd.css").read_text()
    return f'<!doctype html><html><head><meta charset="utf-8"><title>Career Orchestrator PRD</title><style>{css}</style></head><body>{body}</body></html>'
def pdf(htmlstr, path):
    (OUT/"_prd_v2.html").write_text(htmlstr)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); pg.goto(f"file://{OUT}/_prd_v2.html"); pg.wait_for_timeout(500)
        hdr = '<div style="font-size:7.5px;color:#666;width:100%;padding:0 18mm;display:flex;justify-content:space-between"><span>Career Orchestrator PRD v2.0 - SAP Hackfest 2026 (Theme 2)</span><span>Illustrative data. Provisional weights. A prototype, not a validated product.</span></div>'
        ftr = '<div style="font-size:8px;color:#666;width:100%;text-align:center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
        pg.pdf(path=str(path), format="A4", print_background=True, display_header_footer=True, header_template=hdr, footer_template=ftr,
               margin=dict(top="20mm", bottom="18mm", left="16mm", right="16mm"), outline=True, tagged=True)
        b.close()
out = OUT/"PRD_v2.pdf"
pdf(render(), out)
from pypdf import PdfReader
def pagemap():
    r = PdfReader(str(out)); texts = [re.sub(r"\s+", " ", (p.extract_text() or "")) for p in r.pages]
    toc_end = next(i for i, t in enumerate(texts) if "Table of contents" in t) + 1
    while "Appendix E: File checklist" in texts[toc_end] and "Table of contents" not in texts[toc_end]: toc_end += 1
    pages = {}; cur = toc_end
    for lvl, t in toc_items:
        key = re.sub(r"\s+", " ", t)
        for i in range(cur, len(texts)):
            if key in texts[i]: pages[t] = i + 1; cur = i; break
    return pages, len(texts)
pages, n = pagemap(); pdf(render(pages), out)
pages2, n2 = pagemap()
print("pages", n, n2, "toc entries", len(toc_items), "resolved", len(pages2), "stable", pages == pages2)
subprocess.run(["pandoc", str(OUT/"PRD_v2.md"), "-o", str(OUT/"PRD_v2.docx"), "--from", "gfm", "--resource-path", str(OUT), "--toc", "--toc-depth=2"], check=True)
print("docx ok")

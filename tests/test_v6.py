import os, sys, io, json, base64, pathlib, uuid
os.environ["DB_PATH"] = f"/tmp/co_test6_{uuid.uuid4().hex}.db"; os.environ["APP_MODE"] = "replay"; os.environ["RATE_LIMIT_PER_MIN"] = "100000"
ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from engine import cvfile as CF
c = TestClient(app)
CV_LINES = ["Anitha Raman", "Experience", "Office Assistant", "Maintained the filing system and updated employee records every week", "Prepared monthly attendance reports in Excel", "Skills", "Excel, Scheduling, Communication"]

def make_pdf(lines):
    esc = lambda s: s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = "BT /F1 11 Tf 14 TL 50 780 Td " + " ".join(f"({esc(l)}) Tj T*" for l in lines) + " ET"
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
            f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream", "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out = b"%PDF-1.4\n"; offs = []
    for i, o in enumerate(objs, 1): offs.append(len(out)); out += f"{i} 0 obj\n{o}\nendobj\n".encode()
    x = len(out); out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode() + b"".join(f"{o:010d} 00000 n \n".encode() for o in offs)
    return out + f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF".encode()
def make_docx(lines, table=None):
    from docx import Document
    d = Document()
    for l in lines: d.add_paragraph(l)
    if table:
        t = d.add_table(rows=len(table), cols=2)
        for i, (a, b) in enumerate(table): t.cell(i, 0).text, t.cell(i, 1).text = a, b
    b = io.BytesIO(); d.save(b); return b.getvalue()
def post(raw, name="cv.pdf"): return c.post("/api/v1/cv/file", json=dict(file_name=name, content_base64=base64.b64encode(raw).decode()))

def test_pdf_text_is_read():
    r = post(make_pdf(CV_LINES)); assert r.status_code == 200, r.text; j = r.json()
    assert "filing system" in j["text"] and "Excel" in j["text"] and j["pages"] == 1 and j["truncated"] is False
def test_docx_paragraphs_and_tables_are_read():
    r = post(make_docx(CV_LINES, [("Skills", "Excel, Scheduling"), ("Languages", "English, Tamil")]), "cv.docx"); assert r.status_code == 200, r.text; t = r.json()["text"]
    assert "filing system" in t and "Excel, Scheduling" in t and "Tamil" in t
def test_type_is_decided_by_content_not_by_name():
    assert post(make_pdf(CV_LINES), "cv.docx").status_code == 200 and post(make_docx(CV_LINES), "cv.pdf").status_code == 200
def test_text_goes_on_through_the_cv_reader():
    t = post(make_pdf(CV_LINES)).json()["text"]; r = c.post("/api/v1/cv/parse", json=dict(text=t)); assert r.status_code == 200
    assert any("filing" in x.lower() for x in r.json()["work_examples"]) or r.json()["skills"]
def test_scanned_or_blank_pdf_is_refused_with_a_plain_message():
    from pypdf import PdfWriter
    w = PdfWriter(); w.add_blank_page(595, 842); b = io.BytesIO(); w.write(b)
    r = post(b.getvalue()); assert r.status_code == 422 and "scan" in r.json()["error"]["message"]
def test_password_protected_pdf_is_refused():
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter(); [w.add_page(p) for p in PdfReader(io.BytesIO(make_pdf(CV_LINES))).pages]; w.encrypt("secret"); b = io.BytesIO(); w.write(b)
    r = post(b.getvalue()); assert r.status_code == 422 and "password" in r.json()["error"]["message"]
def test_old_doc_files_and_other_types_are_refused():
    assert "Old Word" in post(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"x" * 100, "cv.doc").json()["error"]["message"]
    r = post(b"MZ" + b"x" * 200, "cv.pdf"); assert r.status_code == 422 and "cannot be read" in r.json()["error"]["message"]
def test_zip_that_is_not_word_is_refused():
    import zipfile
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z: z.writestr("hello.txt", "x" * 100)
    assert post(b.getvalue(), "cv.docx").status_code == 422
def test_oversize_bad_base64_and_empty_are_refused():
    assert post(b"%PDF-" + b"x" * 2_100_000).status_code == 422
    assert c.post("/api/v1/cv/file", json=dict(file_name="a.pdf", content_base64="not base64!!!!")).status_code == 422
    with pytest.raises(CF.CVFileError): CF.extract_text(b"")
def test_unknown_fields_are_refused_like_everywhere_else():
    assert c.post("/api/v1/cv/file", json=dict(file_name="a.pdf", content_base64="QUJDREVGR0g=", age=40)).status_code == 422
def test_long_text_is_cut_and_flagged():
    r = post(make_docx(["Experience " + "filing records " * 40] * 80), "cv.docx").json(); assert r["truncated"] is True and len(r["text"]) <= 20000

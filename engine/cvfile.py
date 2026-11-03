"""Turns an uploaded CV file (PDF or Word .docx) into plain text. Bytes in, text out: no disk, no network.
The text then goes through the same CV reader as pasted text, and the person checks every field before anything is used.
We decide the type from the file's first bytes, never from its name. Scanned CVs (pictures of text) are not read: there is no text in them."""
from __future__ import annotations
import io, re, zipfile

MAX_BYTES = 2_000_000
MAX_PAGES = 20
MAX_CHARS = 20000
MAX_UNZIPPED = 25_000_000
MIN_CHARS = 40

class CVFileError(ValueError):
    """The message is written for the person who uploaded the file."""

def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def _pdf(data: bytes) -> tuple[str, int]:
    from pypdf import PdfReader
    try:
        r = PdfReader(io.BytesIO(data))
        if r.is_encrypted and not r.decrypt(""):
            raise CVFileError("This PDF is password protected. Save a copy without a password, or paste the text instead.")
        pages = len(r.pages); parts = []
        for pg in r.pages[:MAX_PAGES]:
            parts.append(pg.extract_text() or "")
    except CVFileError: raise
    except Exception:
        raise CVFileError("We could not open this PDF. Save it again, or paste the text instead.")
    return "\n\n".join(parts), pages

def _docx(data: bytes) -> tuple[str, int]:
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        names = z.namelist()
        if "word/document.xml" not in names: raise CVFileError("This file is not a Word document (.docx).")
        if sum(i.file_size for i in z.infolist()) > MAX_UNZIPPED: raise CVFileError("This file is too large to read. Paste the text instead.")
        from docx import Document
        from docx.table import Table
        from docx.text.paragraph import Paragraph
        doc = Document(io.BytesIO(data)); lines = []
        for sec in doc.sections:                       # names and contact lines are often in the page header
            lines += [p.text for p in sec.header.paragraphs if p.text.strip()]
        for child in doc.element.body.iterchildren():
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "p": lines.append(Paragraph(child, doc).text)
            elif tag == "tbl":
                for row in Table(child, doc).rows:
                    cells, seen = [], set()
                    for cell in row.cells:             # merged cells repeat; keep each once
                        if id(cell._tc) in seen: continue
                        seen.add(id(cell._tc)); t = cell.text.strip()
                        if t: cells.append(t)
                    if cells: lines.append("  |  ".join(cells))
    except CVFileError: raise
    except Exception:
        raise CVFileError("We could not open this Word file. Save it again as .docx, or paste the text instead.")
    return "\n".join(lines), 1

def extract_text(data: bytes) -> dict:
    """-> {text, truncated, pages}. Raises CVFileError with a plain message."""
    if not data: raise CVFileError("The file is empty.")
    if len(data) > MAX_BYTES: raise CVFileError("The file is larger than 2 MB. Paste the text instead.")
    if data[:5] == b"%PDF-": raw, pages = _pdf(data)
    elif data[:4] == b"PK\x03\x04": raw, pages = _docx(data)
    elif data[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1": raise CVFileError("Old Word files (.doc) cannot be read. Save the CV as .docx or PDF, or paste the text.")
    else: raise CVFileError("This file type cannot be read. Use PDF, Word (.docx), .txt or .md, or paste the text.")
    text = _clean(raw)
    if len(text) < MIN_CHARS:
        raise CVFileError("We found almost no text in this file. It may be a scan or a picture. Paste the text instead.")
    return dict(text=text[:MAX_CHARS], truncated=len(text) > MAX_CHARS, pages=pages)

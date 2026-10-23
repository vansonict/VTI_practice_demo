"""Sinh PDF trong bộ nhớ cho test (font chuẩn của reportlab nên văn bản không dấu để chạy trên mọi máy CI)."""

import io

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def make_pdf(pages: list[str]) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    for text in pages:
        y = 800
        words = text.split()
        for i in range(0, len(words), 12):
            c.drawString(40, y, " ".join(words[i : i + 12]))
            y -= 14
            if y < 40:
                break
        c.showPage()
    c.save()
    return buf.getvalue()


def make_blank_pdf(pages: int) -> bytes:
    """Giống PDF scan: có trang nhưng không có lớp văn bản."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    for _ in range(pages):
        c.rect(50, 50, 200, 200, fill=1)
        c.showPage()
    c.save()
    return buf.getvalue()


def make_encrypted_pdf(pages: list[str]) -> bytes:
    writer = PdfWriter()
    for page in PdfReader(io.BytesIO(make_pdf(pages))).pages:
        writer.add_page(page)
    writer.encrypt(user_password="secret", owner_password="owner")
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def make_corrupt_pdf() -> bytes:
    data = make_pdf(["Page one text"] * 3)
    return data[: len(data) // 3]

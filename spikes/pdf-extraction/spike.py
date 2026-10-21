"""Spike T0.1: so sánh thư viện đọc PDF cho bước xử lý tài liệu (SDD §3.8 A1).

Với mỗi thư viện và mỗi file mẫu, ghi:
  - phân loại: ok / password / corrupt / scanned / not_pdf
  - văn bản có nằm đúng trang không (dấu "Trang N" ở trang N)
  - tiếng Việt có dấu giữ nguyên không
  - số liệu trong bảng (trang 3) có trích được không
  - thời gian trích toàn bộ large.pdf (300 trang)
Kết quả in ra dạng bảng Markdown và ghi vào results.md.
"""
import time
from pathlib import Path

SAMPLES = Path(__file__).parent / "samples"
PDF_MAGIC = b"%PDF-"
SCANNED_RATIO = 0.5  # [Initial] tỷ lệ trang có văn bản dưới ngưỡng thì coi là scan (SDD A1 bước 4)
VI_PHRASE = "Điều khoản thanh toán"
TABLE_VALUE = "12,4"


class NeedsPassword(Exception):
    pass


def pages_pymupdf(path: Path) -> list[str]:
    import pymupdf

    doc = pymupdf.open(path)
    if doc.needs_pass:
        raise NeedsPassword()
    return [page.get_text() for page in doc]


def pages_pypdf(path: Path) -> list[str]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    if reader.is_encrypted:
        raise NeedsPassword()
    return [page.extract_text() or "" for page in reader.pages]


def pages_pdfplumber(path: Path) -> list[str]:
    import pdfplumber
    from pdfminer.pdfdocument import PDFPasswordIncorrect

    try:
        with pdfplumber.open(path) as pdf:
            return [page.extract_text() or "" for page in pdf.pages]
    except PDFPasswordIncorrect as exc:
        raise NeedsPassword() from exc


LIBS = {"PyMuPDF": pages_pymupdf, "pypdf": pages_pypdf, "pdfplumber": pages_pdfplumber}


def classify(extract, path: Path):
    if not path.read_bytes()[:5] == PDF_MAGIC:
        return "not_pdf", None
    try:
        pages = extract(path)
    except NeedsPassword:
        return "password", None
    except Exception as exc:  # noqa: BLE001 — spike: mọi lỗi đọc đều coi là file hỏng
        return f"corrupt ({type(exc).__name__})", None
    if not pages:
        return "corrupt (0 trang)", None
    with_text = sum(1 for t in pages if t.strip())
    if with_text / len(pages) < SCANNED_RATIO:
        return "scanned", pages
    return "ok", pages


def check_text(pages: list[str]) -> dict:
    norm = [" ".join(p.split()) for p in pages]
    on_right_page = all(f"Trang {i + 1}" in norm[i] and all(f"Trang {j + 1}" not in norm[i] for j in range(len(norm)) if j != i) for i in range(len(norm)))
    return {
        "page_ok": on_right_page,
        "vi_ok": any(VI_PHRASE in p for p in norm),
        "table_ok": len(norm) >= 3 and TABLE_VALUE in norm[2],
    }


def main() -> None:
    expected = {"text_vi.pdf": "ok", "password.pdf": "password", "corrupt.pdf": "corrupt", "scanned.pdf": "scanned", "fake.pdf": "not_pdf"}
    rows = ["| Thư viện | File | Kỳ vọng | Kết quả | Đúng | Đúng trang | Tiếng Việt | Bảng |", "|---|---|---|---|---|---|---|---|"]
    speed = ["| Thư viện | large.pdf (300 trang) | Giây |", "|---|---|---|"]
    for lib, extract in LIBS.items():
        for name, exp in expected.items():
            got, pages = classify(extract, SAMPLES / name)
            checks = check_text(pages) if (pages and got == "ok") else {}
            mark = lambda k: ("✅" if checks.get(k) else "❌") if checks else "—"  # noqa: E731
            rows.append(f"| {lib} | {name} | {exp} | {got} | {'✅' if got.startswith(exp) else '❌'} | {mark('page_ok')} | {mark('vi_ok')} | {mark('table_ok')} |")
        start = time.perf_counter()
        n = len(extract(SAMPLES / "large.pdf"))
        speed.append(f"| {lib} | {n} trang | {time.perf_counter() - start:.2f} |")
    out = "\n".join(["## Phân loại và chất lượng trích xuất", "", *rows, "", "## Tốc độ", "", *speed, ""])
    (Path(__file__).parent / "results.md").write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()

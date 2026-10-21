# Spike: thư viện đọc PDF (T0.1 / ADR-003)

Mã thử nghiệm, **không phải mã production**. So sánh PyMuPDF, pypdf, pdfplumber trên bộ PDF mẫu tự sinh (không có dữ liệu thật).

## Chạy lại

```bash
cd spikes/pdf-extraction
python -m venv .venv
.venv/Scripts/python -m pip install pymupdf pypdf pdfplumber reportlab pillow   # Linux/macOS: .venv/bin/python
.venv/Scripts/python make_samples.py    # sinh ./samples (cần font C:/Windows/Fonts/arial.ttf; đổi FONT_PATH trên hệ khác)
.venv/Scripts/python spike.py           # in bảng kết quả và ghi results.md
```

Trên Windows nên đặt `PYTHONIOENCODING=utf-8` để in tiếng Việt ra terminal.

## File

| File | Nội dung |
|---|---|
| `make_samples.py` | Sinh 6 PDF mẫu: văn bản tiếng Việt 5 trang có bảng, có mật khẩu, hỏng, scan, giả PDF, 300 trang |
| `spike.py` | Phân loại từng file theo từng thư viện, kiểm đúng trang / tiếng Việt / bảng, đo tốc độ |
| `results.md` | Kết quả lần chạy gần nhất (2026-10-21) |

`samples/` và `.venv/` không đưa vào git (sinh lại được).

## Giới hạn

PDF mẫu do máy sinh, bố cục đơn giản. Phải chạy lại trên bộ tài liệu mẫu thật của đội BD (T0.8) trước khi chốt ADR-003: thêm các file đó vào `samples/` và mở rộng `expected` trong `spike.py`.

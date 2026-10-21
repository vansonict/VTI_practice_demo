## Phân loại và chất lượng trích xuất

| Thư viện | File | Kỳ vọng | Kết quả | Đúng | Đúng trang | Tiếng Việt | Bảng |
|---|---|---|---|---|---|---|---|
| PyMuPDF | text_vi.pdf | ok | ok | ✅ | ✅ | ✅ | ✅ |
| PyMuPDF | password.pdf | password | password | ✅ | — | — | — |
| PyMuPDF | corrupt.pdf | corrupt | corrupt (0 trang) | ✅ | — | — | — |
| PyMuPDF | scanned.pdf | scanned | scanned | ✅ | — | — | — |
| PyMuPDF | fake.pdf | not_pdf | not_pdf | ✅ | — | — | — |
| pypdf | text_vi.pdf | ok | ok | ✅ | ✅ | ✅ | ✅ |
| pypdf | password.pdf | password | password | ✅ | — | — | — |
| pypdf | corrupt.pdf | corrupt | corrupt (PdfStreamError) | ✅ | — | — | — |
| pypdf | scanned.pdf | scanned | scanned | ✅ | — | — | — |
| pypdf | fake.pdf | not_pdf | not_pdf | ✅ | — | — | — |
| pdfplumber | text_vi.pdf | ok | ok | ✅ | ✅ | ✅ | ✅ |
| pdfplumber | password.pdf | password | corrupt (PdfminerException) | ❌ | — | — | — |
| pdfplumber | corrupt.pdf | corrupt | corrupt (PdfminerException) | ✅ | — | — | — |
| pdfplumber | scanned.pdf | scanned | scanned | ✅ | — | — | — |
| pdfplumber | fake.pdf | not_pdf | not_pdf | ✅ | — | — | — |

## Tốc độ

| Thư viện | large.pdf (300 trang) | Giây |
|---|---|---|
| PyMuPDF | 300 trang | 0.10 |
| pypdf | 300 trang | 0.64 |
| pdfplumber | 300 trang | 4.06 |

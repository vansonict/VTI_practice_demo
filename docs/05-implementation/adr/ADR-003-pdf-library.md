# ADR-003: Thư viện đọc PDF — pypdf (mặc định), PyMuPDF là phương án dự phòng

**Trạng thái:** Proposed — chờ IT/Bảo mật review giấy phép và kiểm lại trên bộ tài liệu mẫu thật (T0.8)

## Bối cảnh

Bước xử lý tài liệu ([SDD §3.8 A1](../../04-design/blueprint/SDD_Blueprint.md)) cần:

1. Trích văn bản **theo từng trang** để trích dẫn đúng số trang (BR-008).
2. Phân biệt file có mật khẩu, file hỏng, PDF dạng scan để báo đúng lý do (BR-003, US-103).
3. Giữ nguyên tiếng Việt có dấu và số liệu trong bảng.
4. Đủ nhanh với tài liệu lớn; giấy phép dùng được trong tổ chức.

## Spike

Mã và cách chạy: [`spikes/pdf-extraction/`](../../../spikes/pdf-extraction/README.md). Bộ file mẫu tự sinh, không có dữ liệu thật: văn bản tiếng Việt 5 trang (trang 3 có bảng), file có mật khẩu, file hỏng (cắt 40%), file scan 3 trang chỉ có ảnh, ảnh PNG đổi đuôi `.pdf`, file 300 trang. Kết quả chạy ngày 2026-10-21 (Windows, Python 3.12.10):

| Tiêu chí | PyMuPDF 2.0 | pypdf 6.21.1 | pdfplumber 0.11.10 |
|---|---|---|---|
| Văn bản đúng trang (dấu "Trang N" chỉ ở trang N) | ✅ | ✅ | ✅ |
| Tiếng Việt có dấu giữ nguyên | ✅ | ✅ | ✅ |
| Số liệu trong bảng (trang 3) | ✅ | ✅ | ✅ |
| Phát hiện file có mật khẩu | ✅ (`needs_pass`) | ✅ (`is_encrypted`) | ❌ lỗi bị bọc chung thành `PdfminerException`, không phân biệt được với file hỏng |
| Phát hiện file hỏng | ✅ (tự sửa, trả 0 trang) | ✅ (`PdfStreamError`) | ✅ |
| Phát hiện file scan (tỷ lệ trang có văn bản < 0.5) | ✅ | ✅ | ✅ |
| Phát hiện file không phải PDF (kiểm chữ ký `%PDF-`) | ✅ | ✅ | ✅ |
| 300 trang | **0,10 giây** | 0,64 giây | 4,06 giây |
| Giấy phép | **AGPL-3.0** hoặc thương mại (Artifex) | BSD-3-Clause | MIT |

Kết quả gốc: [`spikes/pdf-extraction/results.md`](../../../spikes/pdf-extraction/results.md).

## Quyết định

- Dùng **pypdf** làm thư viện mặc định: đạt mọi tiêu chí chức năng, đủ nhanh (khoảng 2 ms/trang), giấy phép BSD không ràng buộc.
- Bọc thư viện sau một giao diện nội bộ `PdfExtractor` trong module `ingestion` (trả `pages[]`, ném `PdfPasswordProtected`, `PdfCorrupt`), để đổi sang PyMuPDF chỉ cần thay một lớp.
- Kiểm chữ ký `%PDF-` trước khi mở (T2.1); ngưỡng scan 0.5 là `[Initial]`, kiểm lại với tài liệu thật (OQ-005).

## Phương án đã cân nhắc

| Phương án | Lý do không chọn làm mặc định |
|---|---|
| PyMuPDF | Nhanh nhất (~6 lần pypdf) và thường trích bố cục phức tạp tốt hơn, nhưng **giấy phép AGPL-3.0**: dùng trong dịch vụ mạng có thể kéo theo nghĩa vụ công khai mã nguồn, hoặc phải mua giấy phép thương mại. Cần IT/pháp chế quyết định. Giữ làm dự phòng nếu pypdf trích kém trên tài liệu thật |
| pdfplumber | Chậm nhất (~40 lần PyMuPDF) và không phân biệt được file có mật khẩu với file hỏng; mạnh về trích bảng chi tiết nhưng MVP chưa cần |

## Hệ quả

- **Tích cực:** không có ràng buộc giấy phép; đổi thư viện không ảnh hưởng phần còn lại.
- **Tiêu cực / rủi ro:** spike dùng PDF do máy sinh, bố cục đơn giản. Tài liệu thật (nhiều cột, bảng phức tạp, header/footer) có thể khiến pypdf trích kém hơn PyMuPDF. **Phải chạy lại spike trên bộ tài liệu mẫu thật của T0.8** trước khi chuyển sang Accepted.
- PyMuPDF tự sửa file hỏng: với file chỉ hỏng một phần, nó có thể trả về một số trang thay vì báo lỗi. Nếu chuyển sang PyMuPDF, cần quy tắc rõ (ví dụ: số trang đọc được khác số trang khai báo → coi là hỏng).
- **Việc tiếp theo:** gửi IT/Bảo mật bảng giấy phép; T1.3 hiện thực `PdfExtractor` với pypdf; T2.2 dùng các ngoại lệ trên để phân loại `UNUSABLE`.

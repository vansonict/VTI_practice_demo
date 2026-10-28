# Test Report — <TC-ID> <tiêu đề ca>

> Mẫu báo cáo một lần thực thi (IEEE 829 Test Log + Incident). Lưu tại `docs/06-verification/test-runs/<YYYY-MM-DD>_<TC-ID>/report.md`.

| Mục | Giá trị |
|---|---|
| Ca kiểm thử | [<TC-ID>](../../test-cases/<TC-ID>.md) |
| Kết luận | **Pass / Fail / Một phần / Bị chặn** |
| Ngày giờ thực thi | YYYY-MM-DD HH:MM (múi giờ) |
| Người/agent thực thi | <tên agent hoặc người> |
| Commit | `<git rev-parse --short HEAD>` |
| Ứng dụng | http://localhost:5173 (API `http://localhost:8000`) |
| Cấu hình | `CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`, `CWD_LLM_FAKE_MODE=<…>`, worker: chạy/không |
| Trình duyệt | Chrome <phiên bản>, headless, 1280×860 |
| Dữ liệu | TD-…, Q-… |

## 1. Kết quả từng bước

| # | Bước | Kết quả mong đợi | Kết quả thực tế | Đạt | Bằng chứng |
|---|---|---|---|---|---|
| 1 | <bước trong bảng đặc tả> | <copy từ ca> | <quan sát thực tế, số liệu cụ thể> | ✅/❌ | [network/01_…json](network/01_….json) |
| U1 | <thao tác tại giao diện> | <copy từ ca> | <quan sát thực tế> | ✅/❌ | ![U1](screenshots/01_U1_….png) · video 0:03 |

## 2. Bằng chứng

- Video toàn phiên: [video/session.webm](video/session.webm) (hoặc link lưu trữ nếu > 10 MB) — *Không áp dụng: <lý do>* với ca không có giao diện
- Ảnh chụp: `screenshots/` (… ảnh)
- Network: `network/` (… request)
- Log: [logs/automated.log](logs/automated.log), [logs/browser-console.log](logs/browser-console.log), [logs/env.txt](logs/env.txt)

## 3. Sai lệch so với đặc tả

<Bước nào không thực hiện được như mô tả, vì sao, đã làm gì thay thế. "Không có" nếu không có.>

## 4. Lỗi phát hiện

| Mã | Mức độ | Mô tả | Tái hiện | Bằng chứng | Trạng thái |
|---|---|---|---|---|---|
| BUG-<…> | Critical/High/Medium/Low | | 1. … 2. … | | Mở / Đã sửa ở `<commit>` |

## 5. Ghi chú

<Quan sát thêm, rủi ro, đề xuất cập nhật ca kiểm thử.>

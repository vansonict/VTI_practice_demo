# TC-X-09 — Embedding giả lập tất định và chuẩn hóa

> Nhóm: Xuyên suốt · Bản chi tiết tách từ [Test_Case_Specification.md](../Test_Case_Specification.md) · Dữ liệu TD-*/Q-*: [§2 dữ liệu kiểm thử](../Test_Case_Specification.md#2-dữ-liệu-kiểm-thử)

## Đặc tả

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | ADR-004 · T1.1 |
| Mức / loại | Unit |
| Ưu tiên | Thấp |
| Điều kiện trước | Không cần môi trường |
| Dữ liệu | "Điều khoản thanh toán" (2 lần), "hoàn toàn khác biệt" |
| Tự động | `cd backend && uv run pytest tests/test_units.py::test_fake_embedding_is_deterministic_normalized_and_lexical` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | `FakeEmbedding(dim=64).embed_query` cùng một câu hai lần | Hai vector bằng nhau, độ dài 64 |
| 2 | Tính chuẩn của vector | Tổng bình phương = 1 (sai số < 1e-9) |
| 3 | So độ tương đồng với câu khác hẳn | Tương đồng với chính nó > với câu khác |

## Nhiệm vụ của agent khi thực thi ca này

**Ứng dụng kiểm thử:** http://localhost:5173 (frontend; `/api` được proxy tới backend `:8000`). Quy trình chung, cách khởi động, quy ước bằng chứng và mẫu báo cáo: [README.md](README.md).

1. **Chuẩn bị:** dựng môi trường theo [README §2](README.md#2-chuẩn-bị-môi-trường) với **thư mục dữ liệu mới**.
2. **Tạo thư mục kết quả** `docs/06-verification/test-runs/<YYYY-MM-DD>_TC-X-09/` gồm `screenshots/`, `video/`, `network/`, `logs/`.
3. **Ca này không có thao tác trên giao diện.** Unit test của adapter, không có giao diện. Chạy lệnh ở dòng "Tự động" (hoặc các bước ở bảng trên), lưu toàn bộ output vào `logs/automated.log`. Ảnh chụp/video: ghi "Không áp dụng" kèm lý do trong báo cáo; vẫn đính kèm log làm bằng chứng.
4. Ghi lại phiên bản môi trường (`git rev-parse --short HEAD`, phiên bản Python/Node) vào `logs/env.txt`.
5. **So sánh** kết quả thực tế với cột "Kết quả mong đợi" ở bảng bước. Bất kỳ sai khác nào → Fail, trích đoạn log lỗi vào báo cáo.
6. **Viết báo cáo** `docs/06-verification/test-runs/<YYYY-MM-DD>_TC-X-09/report.md` theo [mẫu](TEST_REPORT_TEMPLATE.md): kết luận Pass/Fail/Bị chặn, bảng từng bước có kết quả thực tế và link bằng chứng, sai lệch so với ca kiểm thử, lỗi phát hiện.
7. **Cập nhật** dòng "Kết quả gần nhất" ở đầu file này (ngày, commit, kết quả, link báo cáo) và [traceability](../../05-implementation/traceability.md) nếu trạng thái thay đổi.

> Không đánh dấu Pass khi thiếu bằng chứng. Không dùng dữ liệu thật của đội BD. Không sửa code để làm test qua — mở lỗi thay vào đó.

# TC-X-07 — Không có lỗ hổng phụ thuộc đã biết

> Nhóm: Xuyên suốt · Bản chi tiết tách từ [Test_Case_Specification.md](../Test_Case_Specification.md) · Dữ liệu TD-*/Q-*: [§2 dữ liệu kiểm thử](../Test_Case_Specification.md#2-dữ-liệu-kiểm-thử)

## Đặc tả

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | Phase 7 L0 |
| Mức / loại | Bảo mật (SCA) |
| Ưu tiên | Trung bình |
| Điều kiện trước | Có mạng để tải cơ sở dữ liệu lỗ hổng |
| Dữ liệu | — |
| Tự động | Lệnh ở cột bước (cũng chạy trong CI) |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | `uv export --no-dev --no-hashes --format requirements-txt -o req.txt && uv run pip-audit -r req.txt` | "No known vulnerabilities found" |
| 2 | `npm audit --omit=dev --audit-level=high` | "found 0 vulnerabilities" |

## Nhiệm vụ của agent khi thực thi ca này

**Ứng dụng kiểm thử:** http://localhost:5173 (frontend; `/api` được proxy tới backend `:8000`). Quy trình chung, cách khởi động, quy ước bằng chứng và mẫu báo cáo: [README.md](README.md).

1. **Chuẩn bị:** dựng môi trường theo [README §2](README.md#2-chuẩn-bị-môi-trường) với **thư mục dữ liệu mới**.
2. **Tạo thư mục kết quả** `docs/06-verification/test-runs/<YYYY-MM-DD>_TC-X-07/` gồm `screenshots/`, `video/`, `network/`, `logs/`.
3. **Ca này không có thao tác trên giao diện.** Quét phụ thuộc, không có giao diện. Chạy lệnh ở dòng "Tự động" (hoặc các bước ở bảng trên), lưu toàn bộ output vào `logs/automated.log`. Ảnh chụp/video: ghi "Không áp dụng" kèm lý do trong báo cáo; vẫn đính kèm log làm bằng chứng.
4. Ghi lại phiên bản môi trường (`git rev-parse --short HEAD`, phiên bản Python/Node) vào `logs/env.txt`.
5. **So sánh** kết quả thực tế với cột "Kết quả mong đợi" ở bảng bước. Bất kỳ sai khác nào → Fail, trích đoạn log lỗi vào báo cáo.
6. **Viết báo cáo** `docs/06-verification/test-runs/<YYYY-MM-DD>_TC-X-07/report.md` theo [mẫu](TEST_REPORT_TEMPLATE.md): kết luận Pass/Fail/Bị chặn, bảng từng bước có kết quả thực tế và link bằng chứng, sai lệch so với ca kiểm thử, lỗi phát hiện.
7. **Cập nhật** dòng "Kết quả gần nhất" ở đầu file này (ngày, commit, kết quả, link báo cáo) và [traceability](../../05-implementation/traceability.md) nếu trạng thái thay đổi.

> Không đánh dấu Pass khi thiếu bằng chứng. Không dùng dữ liệu thật của đội BD. Không sửa code để làm test qua — mở lỗi thay vào đó.

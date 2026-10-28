# TC-X-06 — Health và readiness

> Nhóm: Xuyên suốt · Bản chi tiết tách từ [Test_Case_Specification.md](../Test_Case_Specification.md) · Dữ liệu TD-*/Q-*: [§2 dữ liệu kiểm thử](../Test_Case_Specification.md#2-dữ-liệu-kiểm-thử)

## Đặc tả

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | SAD §4.3 |
| Mức / loại | Integration |
| Ưu tiên | Thấp |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`) |
| Dữ liệu | — |
| Tự động | `cd backend && uv run pytest tests/test_units.py::test_health_and_ready` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | `GET /healthz` | 200 `{"status": "ok"}` |
| 2 | `GET /readyz` | 200 (kiểm CSDL, không gọi dịch vụ AI) |

## Nhiệm vụ của agent khi thực thi ca này

**Ứng dụng kiểm thử:** http://localhost:5173 (frontend; `/api` được proxy tới backend `:8000`). Quy trình chung, cách khởi động, quy ước bằng chứng và mẫu báo cáo: [README.md](README.md).

1. **Chuẩn bị:** dựng môi trường theo [README §2](README.md#2-chuẩn-bị-môi-trường) với **thư mục dữ liệu mới**.
2. **Tạo thư mục kết quả** `docs/06-verification/test-runs/<YYYY-MM-DD>_TC-X-06/` gồm `screenshots/`, `video/`, `network/`, `logs/`.
3. **Thực thi trên API** bằng Playwright, chụp màn hình **sau mỗi bước** (`screenshots/NN_<mô-tả>.png`), ghi mọi request/response `/api` vào `network/`:
   *Lý do không có thao tác giao diện:* `/healthz`, `/readyz` không đi qua proxy của frontend; gọi thẳng backend `http://localhost:8000`. Với bước GET, mở URL trong tab trình duyệt để chụp và quay; với bước khác, chụp JSON phản hồi hiển thị trong trang báo cáo tạm hoặc lưu file `network/`.

   | # | Thao tác tại http://localhost:5173 | Kết quả mong đợi | Bằng chứng bắt buộc |
   |---|---|---|---|
   | U1 | Mở `http://localhost:8000/healthz` trong trình duyệt | 200 `{"status":"ok"}` | `screenshots/01_*.png` |
   | U2 | Mở `http://localhost:8000/readyz` | 200 `{"status":"ready"}` | `screenshots/02_*.png` |

4. **Chạy phần tự động** (nếu ca có dòng "Tự động" ở trên), lưu toàn bộ output vào `logs/automated.log`.
5. **So sánh** kết quả thực tế với cột "Kết quả mong đợi" ở **cả hai** bảng (bước gốc và bước tại http://localhost:5173). Bất kỳ sai khác nào → Fail, chụp màn hình lỗi, lưu `logs/browser-console.log`.
6. **Viết báo cáo** `docs/06-verification/test-runs/<YYYY-MM-DD>_TC-X-06/report.md` theo [mẫu](TEST_REPORT_TEMPLATE.md): kết luận Pass/Fail/Bị chặn, bảng từng bước có kết quả thực tế và link bằng chứng, sai lệch so với ca kiểm thử, lỗi phát hiện.
7. **Cập nhật** dòng "Kết quả gần nhất" ở đầu file này (ngày, commit, kết quả, link báo cáo) và [traceability](../../05-implementation/traceability.md) nếu trạng thái thay đổi.

> Không đánh dấu Pass khi thiếu bằng chứng. Không dùng dữ liệu thật của đội BD. Không sửa code để làm test qua — mở lỗi thay vào đó.

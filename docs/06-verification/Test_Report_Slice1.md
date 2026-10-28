# Test Summary Report — Lát cắt 1 (walking skeleton)

> **Chuẩn:** IEEE 829-2008, Test Summary Report · **Kế hoạch:** [Master_Test_Plan.md](Master_Test_Plan.md) (MTP-CWD-001 v0.1)
> **Dành cho:** Reviewer Phase 8, Tech lead, QA lead.

| Mục | Giá trị |
|---|---|
| Mã | **TSR-CWD-001** |
| Ngày chạy | 2026-10-23 |
| Phiên bản được kiểm | Nhánh `Phase2_Implementation`, commit `163a7dd` |
| Môi trường | Cục bộ: Windows 10, Python 3.12.10 + uv, Node 24; SQLite tạm (ADR-006); adapter AI **giả lập** |
| Người chạy | Agent (L0 + L1); chưa có review L2 |
| Kết luận | **L0 đạt. L1 không có phát hiện mức Blocker/Critical, có 3 phát hiện Medium.** Lát cắt 1 sẵn sàng sang Phase 8 (review của người). Chưa đủ điều kiện nghiệm thu chất lượng, xem §4 |

---

## 1. Tóm tắt

- Mọi kiểm tra L0 đều xanh ở cả backend và frontend: format, lint, type check, 3/3 quy tắc phụ thuộc, **33/33** test backend, **11/11** test frontend, build, không có lỗ hổng phụ thuộc, kiểu API không lệch so với `openapi.yaml`.
- Độ phủ code backend **95%** (830 câu lệnh, thiếu 39); các module nghiệp vụ `app/modules` đạt **97–100%**.
- Theo kế hoạch có 70 ca kiểm thử. Lát cắt này có **26 ca đạt**, 7 ca đạt một phần, 20 ca chờ task GĐ2–5 và 17 ca bị chặn bởi OQ/PQ (Master Test Plan, Phụ lục A). Các bước chi tiết của 33 ca đã chạy nằm ở [Test_Case_Specification.md](Test_Case_Specification.md) và [Test_Cases.xlsx](Test_Cases.xlsx).
- Kết quả hiện tại chứng minh **luồng và quy tắc**: trích dẫn dựng từ evidence; ba cổng "không tìm thấy"; lỗi AI không bị biến thành "không tìm thấy"; tài liệu lỗi không bị trích dẫn. Kết quả này **chưa chứng minh chất lượng trả lời**, vì LLM và embedding vẫn là bản giả lập.

## 2. Sai khác so với kế hoạch (Variances)

| # | Sai khác | Lý do | Ảnh hưởng |
|---|---|---|---|
| V-1 | Chạy trên máy cục bộ, chưa có log từ GitHub Actions | Máy không có `gh`; CI chưa được xác nhận đã chạy (T0.5) | Bước gitleaks (quét secret) **chưa có bằng chứng** |
| V-2 | Bước quét lỗ hổng chạy bằng lệnh cục bộ tương đương CI | Như V-1 | Kết quả tương đương, nhưng được chạy trên Windows chứ không phải ubuntu |
| V-3 | E2E chỉ có lần kiểm thủ công ngày 2026-10-23 (T1.6), chưa chạy lại | Chưa có Playwright trong repo | TC-101-02, TC-104-02, TC-104-03 chỉ đạt một phần |
| V-4 | Không đo độ phủ code frontend | Script `test` là `vitest run`, chưa bật coverage | Không có số liệu cho G-12 phía UI |

## 3. Kết quả L0 (kiểm tra bằng máy)

### 3.1 Backend (`backend/`)

| Bước | Lệnh | Kết quả | Thời gian |
|---|---|---|---|
| Format | `uv run ruff format --check .` | ✅ 48 file đã đúng định dạng | 1 s |
| Lint | `uv run ruff check .` | ✅ không có lỗi | 1 s |
| Type check | `uv run mypy` (strict) | ✅ 41 file, 0 lỗi | 6 s |
| Quy tắc phụ thuộc | `uv run lint-imports` | ✅ giữ được 3/3 contract (62 file, 118 phụ thuộc) | 3 s |
| Test + coverage | `uv run pytest --cov` | ✅ **33 passed**, 0 failed, 0 skipped; 1 cảnh báo deprecation | 23 s (riêng phần test 5,3 s) |
| Lỗ hổng phụ thuộc | `uv export … && uv run pip-audit -r …` | ✅ không phát hiện lỗ hổng đã biết | — |

### 3.2 Frontend (`frontend/`)

| Bước | Lệnh | Kết quả | Thời gian |
|---|---|---|---|
| Cài đặt | `npm ci` | ✅ 0 lỗ hổng | — |
| Kiểu API khớp OpenAPI | `npm run gen:api && git diff --exit-code src/api/schema.d.ts` | ✅ không lệch | — |
| Type check | `npm run typecheck` | ✅ | 6 s |
| Lint | `npm run lint` | ✅ | 19 s |
| Test | `npm test` | ✅ **11 passed** (1 file) | 19 s |
| Build | `npm run build` | ✅ JS 273,6 kB (gzip 85,6 kB), CSS 12,7 kB | 7 s |
| Lỗ hổng phụ thuộc | `npm audit --omit=dev --audit-level=high` | ✅ 0 lỗ hổng | — |

### 3.3 Chỉ chạy được trên CI

| Bước | Kết quả |
|---|---|
| Quét secret (gitleaks) | ⏳ **Chưa có bằng chứng.** Cần mở tab Actions của repo và lưu log vào báo cáo này |

L0 chạy hết dưới 2 phút, nhanh hơn nhiều so với mức 10 phút của quy trình.

### 3.4 Độ phủ code backend

| Phần | Câu lệnh | Thiếu | Độ phủ | Ghi chú |
|---|---|---|---|---|
| `app/modules/*` (nghiệp vụ) | 276 | 2 | **99%** | `qa/service.py`, `documents/service.py`, `chunker.py`, `retrieval` đạt 100%; `ingestion/service.py` 97% (thiếu dòng 69, 79) |
| `app/api/*` | 129 | 2 | 98% | Nhánh `/readyz` báo CSDL không sẵn sàng chưa được test (`app.py:78-79`) |
| `app/db/*` | 186 | 3 | 98% | |
| `app/adapters/*` | 95 | 11 | 88% | `local_filestore.py` 82%: nhánh lỗi I/O chưa được test |
| `app/worker.py`, `app/main.py` | 18 | 18 | **0%** | Điểm vào tiến trình; logic nằm ở `IngestionService` (đã được test) |
| **Tổng** | **830** | **39** | **95%** | Ngưỡng đề xuất ≥ 70% (MTP §7): **đạt**, nhưng CI chưa chặn khi độ phủ xuống dưới ngưỡng (L1-01) |

## 4. Kết quả theo yêu cầu

| Story | AC đã kiểm tự động | Đánh giá |
|---|---|---|
| US-101 Upload | AC-101.1, 101.3 ✅; 101.2 🟡 | Đạt cho lát cắt; AC-101.4 cần UAT (T5.5) |
| US-102 Dung lượng | — | Chưa làm (T2.1); ngưỡng chờ OQ-004 |
| US-103 Tài liệu lỗi | AC-103.2, 103.3 ✅; AC-103.1 🟡 | Backend đạt; chưa kiểm UI hiển thị tên file + lý do; endpoint retry chưa có (T2.3) |
| US-104 Danh sách | Badge icon + chữ ✅; AC-104.2, 104.3 🟡 | AC-104.1 cần test đúng kịch bản 5 tài liệu (T2.7) |
| US-105 Xóa | — | Chưa làm (T2.4) |
| US-201 Hỏi | AC-201.1, 201.2, I-5, I-6, E-2 ✅ | AC-201.3 bị chặn bởi OQ-002 và bộ câu hỏi chuẩn |
| US-202 Chỉ từ kho | AC-202.1 🟡 (LLM giả lập) | Chưa có bộ đối kháng (T3.3) |
| US-203 Trích dẫn | AC-203.1 ✅, D-06 ✅, chunk theo trang ✅ | AC-203.2 bị chặn bởi OQ-002 |
| US-204 Không tìm thấy | AC-204.1 ✅, cổng 2 ✅, lỗi AI ≠ NOT_FOUND ✅; AC-204.3 🟡 | AC-204.2 bị chặn bởi OQ-002 |
| US-205…209 | — | Chưa làm hoặc bị chặn bởi PQ-01, PQ-02, OQ-006, OQ-007 |
| US-301, 302 | — | Bị chặn bởi OQ-008, OQ-009; G-10 hiện chỉ được kiểm bằng review code |
| US-401, 402 | — | GĐ4 |

**Trạng thái Launch gate liên quan:** G-01 chưa đạt (còn nhiều AC P0). G-03, G-05, G-08, G-09 **chưa quyết định được** vì OQ còn mở. G-12 đạt một phần: mọi story P0 đã có ca kiểm thử truy vết được trong kế hoạch, nhưng phần lớn chưa có test.

## 5. Kết quả L1 (agent review)

Phạm vi: toàn bộ code của lát cắt 1 tại `163a7dd`, đối chiếu với AC trong PRD §3, điều cấm trong `AGENTS.md` và rủi ro trong MTP §0.2. Agent không có quyền approve hay merge.

| ID | Mức | Vị trí | Phát hiện | Đề xuất |
|---|---|---|---|---|
| L1-01 | Medium | [.github/workflows/ci.yml:27](../../.github/workflows/ci.yml#L27) | CI đo coverage nhưng không chặn khi độ phủ giảm. Hiện đạt 95%, nhưng có thể giảm dần mà không ai phát hiện | Thêm `--cov-fail-under=<ngưỡng>` khi ngưỡng ở MTP §7 được duyệt |
| L1-02 | Medium | [backend/app/api/routes.py:44](../../backend/app/api/routes.py#L44) | `await f.read()` đọc toàn bộ file vào bộ nhớ và chưa có giới hạn kích thước. Một file rất lớn hoặc nhiều file cùng lúc có thể làm cạn bộ nhớ (TR-09, STRIDE DoS) | Đã thuộc T2.1. Nên giới hạn ở tầng HTTP (đọc theo khối, dừng khi vượt giới hạn tạm của OQ-004) thay vì chỉ kiểm sau khi đã đọc hết |
| L1-03 | Medium | Quy trình | E2E chỉ thủ công và CI chưa được xác nhận đã chạy trên GitHub. Hồi quy UI và quét secret chưa có bằng chứng tự động | Thêm Playwright cho F1, F2 (T2.7); xem Actions và lưu log (V-1) |
| L1-04 | Low | [backend/app/modules/ingestion/service.py:58](../../backend/app/modules/ingestion/service.py#L58), [backend/app/api/app.py:65](../../backend/app/api/app.py#L65) | `logger.exception` ghi cả stack trace và thông điệp lỗi của thư viện bên thứ ba (pypdf, adapter embedding sau này). Các thông điệp này có thể chứa một phần nội dung tài liệu, mâu thuẫn với G-10. Hiện chưa thấy trường hợp cụ thể | Trong TC-302-03 (T4.3), quét cả stack trace bằng chuỗi đánh dấu. Có thể chỉ ghi `type(exc).__name__` như ở nhánh `fail()` |
| L1-05 | Low | `frontend/package.json` (`"test": "vitest run"`) | Không đo độ phủ code frontend (V-4) | Bật `vitest run --coverage` và báo cáo con số; chưa đặt ngưỡng |
| L1-06 | Low | `app/worker.py` (0%) | Vòng lặp worker chưa được test. Rủi ro thấp vì logic nằm trong `IngestionService` đã được test | Chấp nhận; xem lại khi thêm timeout và tắt êm (T2.2) |
| L1-07 | Info | Test backend | Cảnh báo `StarletteDeprecationWarning`: `TestClient` dùng `httpx` đã lỗi thời | Theo dõi khi nâng cấp FastAPI/Starlette |

**Các điểm đã kiểm và đạt:**
- Module nghiệp vụ không import adapter, DB hay framework (`lint-imports`).
- Trích dẫn chỉ dựng từ bản ghi evidence ([qa/service.py](../../backend/app/modules/qa/service.py)).
- Truy xuất chỉ lấy tài liệu `READY` (`repositories.py`, điều kiện `DocumentRow.status == READY`).
- Lỗi AI trả `AI_*` 5xx và không bao giờ trả `NOT_FOUND`.
- Log chỉ ghi ID, số lượng và thời gian, không ghi nội dung câu hỏi hay tài liệu.
- Frontend không dùng `dangerouslySetInnerHTML`, nên React tự escape câu trả lời (giảm rủi ro XSS).
- Lỗi framework (body hỏng, route không tồn tại) cũng trả về theo mô hình lỗi chuẩn.

## 6. Lỗi (defects)

Lần chạy này **không phát hiện lỗi** (0 Blocker, 0 Critical, 0 Major). Các phát hiện L1 là cải tiến hoặc rủi ro đã có task theo dõi, không phải hành vi sai so với AC đã cài đặt.

## 7. Đánh giá tổng thể

| Câu hỏi | Trả lời |
|---|---|
| Lát cắt 1 có làm đúng những gì nó cam kết không? | **Có.** Mọi AC trong phạm vi lát cắt (traceability.md) đều có test tự động và đạt |
| Có thể chuyển sang Phase 8 (review của người) không? | **Có.** L0 xanh, không có phát hiện Blocker/Critical |
| Có thể nghiệm thu chất lượng hay pilot không? | **Không.** Thiếu LLM/embedding thật (OQ-009), bộ câu hỏi chuẩn (T0.8), ngưỡng (OQ-002), xác thực (OQ-008) |
| Độ tin cậy của kết quả | Cao cho luồng và quy tắc. **Thấp cho chất lượng trả lời**, vì adapter giả lập dùng so khớp từ vựng nên các ca "không tìm thấy" đạt dễ hơn thực tế (RT-06) |

## 8. Việc cần làm tiếp

1. Xem kết quả CI trên GitHub (Actions), lưu log gitleaks, cập nhật §3.3.
2. Phase 8: mở PR `Phase2_Implementation` → `main` để người khác tác giả review, dùng báo cáo này làm bằng chứng.
3. Chốt ngưỡng coverage (MTP §7), rồi xử lý L1-01 và L1-05.
4. GĐ2: T2.1 (xử lý cùng L1-02), T2.7 kèm E2E Playwright (L1-03).
5. Theo dõi OQ-002, OQ-008, OQ-009 và T0.8; đây là các điểm chặn 17 ca kiểm thử.

## 9. Phê duyệt

| Vai trò | Tên | Quyết định | Ngày |
|---|---|---|---|
| QA lead | [TBD: OQ-014] | | |
| Tech lead | [TBD: OQ-014] | | |

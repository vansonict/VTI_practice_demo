# Master Test Plan — "Chat với tài liệu" (MVP)

> **Chuẩn áp dụng:** IEEE 829-2008 (Software Test Documentation) · **Phương pháp:** [testPlan_prompt.md](../../References/verification/testPlan_prompt.md) · **Checklist:** `References/verification/Test_Plan_IEEE_829_Checklist.xlsx` (kết quả: [Test_Plan_Review_IEEE_829.xlsx](Test_Plan_Review_IEEE_829.xlsx))
> **Dành cho:** QA, Tech lead, Dev, Reviewer; PO/Sponsor đọc §2, §7, §16.
> **Quy ước:** `[TBD: OQ-xxx]` = chờ quyết định theo BRD §12 · `[Proposed]` = đề xuất của tài liệu này, chưa được xác nhận. Không tự điền ngưỡng cho mục `[TBD]`.
> **Kết quả chạy:** [Test_Report_Slice1.md](Test_Report_Slice1.md) (lần chạy đầu, lát cắt 1).

---

## 0. Phân tích đầu vào

### 0.1 Tài liệu đầu vào

| Loại | Tài liệu | Version | Thông tin dùng cho test |
|---|---|---|---|
| SRS/PRD | [PRD.md](../01-requirements/PRD.md) (PRD-CWD-001) | 0.1 Draft | Story, AC Given-When-Then (§3), edge case (§4.2), Launch gate G-01…G-17 (§5.1), analytics (§5.2) |
| BRD | [BRD.md](../01-requirements/BRD.md) | 0.1 Draft | BR-001…017, AC-001…017, rủi ro RSK-*, OQ |
| User stories (PO) | [User_Stories.md](../01-requirements/User_Stories.md) | 0.1 | Ngôn ngữ nghiệp vụ cho kịch bản UAT |
| Use case | [UseCase_Specification.md](../02-analysis/UseCase_Specification.md) | 0.1 | Luồng chính/phụ/ngoại lệ UC-01…14 |
| SAD | [SAD.md](../03-architecture/SAD.md) | 0.1 | STRIDE (§4.1), độ tin cậy (§4.2), quan sát (§4.3) |
| SDD (IEEE 1016) | [SDD_Blueprint.md](../04-design/blueprint/SDD_Blueprint.md) | 0.1 | Module, port, trạng thái (§3.7), ba cổng not-found (§3.8), mã lỗi (§3.6) |
| API | [openapi.yaml](../04-design/api/openapi.yaml) | một phần (5/14 operation) | Hợp đồng request/response/lỗi |
| UI/UX | [UI_UX_Design.md](../04-design/UI_UX_design/UI_UX_Design.md) + 4 bản mẫu HTML | 0.1 | Flow F1–F7, trạng thái UI, component, WCAG (§9) |
| Kế hoạch | [Implementation_Plan.md](../05-implementation/Implementation_Plan.md), [tasks/](../05-implementation/tasks/README.md) | 0.1 | Mốc M0–M5, chiến lược kiểm thử (§6), task T5.x |
| Truy vết | [traceability.md](../05-implementation/traceability.md) | 2026-10-23 | Story ↔ code ↔ test hiện có |
| Quy ước code | [AGENTS.md](../../AGENTS.md), [ADR-001…006](../05-implementation/adr/README.md) | — | Stack, lệnh kiểm tra, điều cấm |

### 0.2 Đánh giá rủi ro (đầu vào cho ưu tiên test)

Điểm = Khả năng (1–5) × Ảnh hưởng (1–5). Khả năng đánh giá theo trạng thái hiện tại (adapter AI giả lập, chưa đăng nhập).

| ID | Rủi ro sản phẩm | Nguồn | KN | AH | Điểm | Cách test giảm thiểu |
|---|---|---|---|---|---|---|
| TR-01 | Câu trả lời bịa / không có căn cứ trong kho | RSK-001, BR-007 | 4 | 5 | **20** | Ba cổng not-found; eval bộ câu hỏi chuẩn (MET-002, MET-005); bộ đối kháng |
| TR-02 | Trích dẫn sai tài liệu/trang | BR-008 | 3 | 5 | **15** | Unit chunker theo trang; trích dẫn dựng từ evidence; eval % đúng trang |
| TR-03 | Lộ tài liệu cho bên thứ ba hoặc qua log | RSK-002, BR-015, G-10 | 3 | 5 | **15** | Test chuỗi đánh dấu trong log/analytics; review egress; không gọi AI ngoài khi chưa có OQ-009 |
| TR-04 | Truy cập trái phép | BR-014, G-09 | 4 | 5 | **20** | Test bảng quyền mọi route (10/10 từ chối, 10/10 cho phép) |
| TR-05 | Lỗi AI hiển thị như "không tìm thấy" | PRD N-3, SDD §3.7 | 2 | 4 | 8 | Test ánh xạ lỗi `AI_*` 5xx ≠ `NOT_FOUND` 200 |
| TR-06 | Prompt injection qua câu hỏi hoặc nội dung PDF | G-11, PRD I-7 | 3 | 5 | **15** | Bộ đối kháng ≥ 30 ca (T3.3, T5.2) |
| TR-07 | Tài liệu lỗi/đang xử lý lọt vào truy xuất | BR-003 | 2 | 4 | 8 | Test truy xuất chỉ trên `READY` |
| TR-08 | Tài liệu kẹt `PROCESSING` khi worker lỗi/chết | SAD §4.2 | 3 | 3 | 9 | Test khóa job hết hạn, lỗi embedding, retry |
| TR-09 | Upload file độc hại/quá lớn làm treo hệ thống | SAD §4.1 | 3 | 4 | 12 | Test giới hạn kích thước/trang (T2.1), file giả PDF, upload song song |
| TR-10 | Thời gian trả lời không đạt | BR-012 | 3 | 3 | 9 | Test hiệu năng kho ở dung lượng tối đa (T5.1) |
| TR-11 | Người dùng không hiểu trạng thái/lỗi, không dùng bàn phím được | BR-004, UI_UX §9 | 2 | 3 | 6 | Component test, E2E, kiểm accessibility |
| TR-12 | Code lệch hợp đồng OpenAPI | T0.2 | 2 | 3 | 6 | Test bao phủ operation; CI so `schema.d.ts` |

---

## 1. Test Plan Identifier (IEEE 829 §5.1)

| Thuộc tính | Giá trị |
|---|---|
| Mã tài liệu | **MTP-CWD-001** |
| Version | 0.1 |
| Ngày | 2026-10-23 |
| Trạng thái | **Draft** — chờ review của QA lead và Tech lead |
| Phân loại | Internal — Confidential |
| Người soạn | QA — [TBD: OQ-014] (bản nháp soạn với sự hỗ trợ của AI) |
| Người duyệt | QA lead, Tech lead — [TBD: OQ-014] |
| Lịch sử | 0.1 (2026-10-23): bản đầu, sau lát cắt 1 Phase 6 |

## 2. Introduction (§5.2)

### 2.1 Mục đích

Kế hoạch này xác định cách kiểm chứng MVP "Chat với tài liệu" đáp ứng PRD §3 và Launch gate PRD §5.1: các mức và loại kiểm thử, ca kiểm thử truy vết tới AC, tiêu chí đạt/không đạt, môi trường, vai trò, lịch theo mốc và rủi ro. Đây là kế hoạch tổng (master) cho toàn bộ MVP; mỗi lần chạy có một báo cáo riêng (test summary report).

### 2.2 Phạm vi

**Trong phạm vi:** chức năng nhóm E1–E4 (story P0, P1), API REST `/api/v1`, worker xử lý tài liệu, giao diện S01–S03, chất lượng trả lời (eval), đối kháng (prompt injection), bảo mật cơ bản, hiệu năng, accessibility, hồi quy, UAT.

**Ngoài phạm vi:** xem §5.

### 2.3 Mục tiêu kiểm thử

| ID | Mục tiêu | Tiêu chí thành công | Truy vết |
|---|---|---|---|
| OBJ-01 | Mọi AC của story P0 được kiểm | 100% AC P0 có ca kiểm thử và đạt | G-01, G-12 |
| OBJ-02 | Câu trả lời có căn cứ và trích dẫn đúng | MET-002, MET-005, % trích dẫn đúng trang ≥ `[TBD: OQ-002]`; 100% câu trả lời có nội dung kèm trích dẫn | G-03 |
| OBJ-03 | Không nhầm lỗi hệ thống với "không tìm thấy" | 100% ca lỗi AI trả `AI_*` 5xx | PRD N-3 |
| OBJ-04 | Hợp đồng API khớp thiết kế | 100% operation trong `openapi.yaml` có hiện thực và test | T0.2 |
| OBJ-05 | Kiểm soát truy cập và dữ liệu | 10/10 từ chối, 10/10 cho phép; 0 chuỗi đánh dấu trong log/analytics | G-09, G-10 |
| OBJ-06 | Không còn lỗ hổng High/Critical | 0 mở, kể cả bộ prompt injection | G-11 |
| OBJ-07 | Hiệu năng | ≥ `[TBD: OQ-006]`% câu hỏi trong `[TBD: OQ-006]` giây | G-05 |
| OBJ-08 | Accessibility | Đạt mức WCAG được chốt `[Proposed: 2.1 AA]` | UI_UX §9 |

### 2.4 Tài liệu tham chiếu

Xem §0.1, cùng với IEEE 829-2008 và quy trình [agentic-sdlc-process.html](../../References/agentic-sdlc-process.html) (Phase 7: tháp L0 máy → L1 agent → L2 người).

## 3. Test Items (§5.3)

| ID | Hạng mục | Version | Vị trí | Ghi chú |
|---|---|---|---|---|
| SI-01 | Backend API (FastAPI) | 0.1.0 | `backend/app/api`, `app/modules` | `/api/v1`, mô hình lỗi chuẩn |
| SI-02 | Worker xử lý tài liệu | 0.1.0 | `backend/app/worker.py`, `app/modules/ingestion` | Tiến trình riêng |
| SI-03 | Adapter | 0.1.0 | `backend/app/adapters` | **Giả lập**: `FakeLlm`, `FakeEmbedding`; thật: pypdf, kho tệp local |
| SI-04 | Lưu trữ | 0.1.0 | `backend/app/db` | **SQLite + numpy tạm** (ADR-006); đích PostgreSQL + pgvector |
| SI-05 | Frontend SPA (React + TS) | 0.1.0 | `frontend/src` | Màn S02 |
| SI-06 | Hợp đồng API | một phần | `docs/04-design/api/openapi.yaml` | 5/14 operation |
| SI-07 | Cấu hình | — | `backend/app/config.py` (`CWD_*`) | Tham số `[Initial]` |
| SI-08 | Pipeline CI | — | `.github/workflows/ci.yml` | Chưa chạy trên GitHub (T0.5) |

**Phiên bản được kiểm** ghi trong từng báo cáo bằng mã commit.

**Bộ kiểm thử đi kèm:** `backend/tests/` (pytest; PDF tổng hợp sinh bằng reportlab ở `tests/pdfs.py`), `frontend/src/**/*.test.tsx` (Vitest + Testing Library). Chưa có: E2E tự động, bộ eval, bộ đối kháng.

## 4. Features to be Tested (§5.4)

### 4.1 Ma trận ưu tiên

| Ưu tiên | Tính năng | Story | Rủi ro (§0.2) |
|---|---|---|---|
| **Cao** | Hỏi đáp có căn cứ, ba cổng not-found | US-201, 202, 204 | TR-01 (20), TR-06 (15) |
| **Cao** | Trích dẫn tên tài liệu + trang | US-203 | TR-02 (15) |
| **Cao** | Truy cập có quyền | US-301 | TR-04 (20) |
| **Cao** | Dữ liệu trong phạm vi duyệt | US-302 | TR-03 (15) |
| **Cao** | Upload, kiểm file, xử lý, báo lỗi | US-101, 102, 103 | TR-07, TR-08, TR-09 |
| Trung bình | Tổng hợp nhiều tài liệu | US-206 | TR-01 |
| Trung bình | Hiệu năng | US-208 | TR-10 |
| Trung bình | Danh sách + trạng thái, xóa | US-104, 105 | TR-07, TR-11 |
| Trung bình | Ngôn ngữ | US-209 | — |
| Thấp | Mở trang nguồn, hỏi tiếp nối | US-205, 207 | — |
| Thấp | Đánh giá, thống kê | US-401, 402 | — |

### 4.2 Ma trận tính năng × loại kiểm thử

| Tính năng | Unit | Integration (API) | E2E | Eval | Đối kháng | Hiệu năng | Bảo mật | A11y | UAT |
|---|---|---|---|---|---|---|---|---|---|
| E1 Kho tài liệu (US-101…105) | ✓ | ✓ | ✓ | – | – | ✓ | ✓ | ✓ | ✓ |
| E2 Hỏi đáp (US-201…209) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| E3 Truy cập & dữ liệu (US-301, 302) | ✓ | ✓ | ✓ | – | ✓ | – | ✓ | ✓ | – |
| E4 Đo lường (US-401, 402) | ✓ | ✓ | ✓ | – | – | – | ✓ | ✓ | ✓ |
| Xuyên suốt (lỗi chuẩn, hợp đồng API, quy tắc phụ thuộc) | ✓ | ✓ | – | – | – | – | – | – | – |

### 4.3 Ca kiểm thử truy vết tới AC

**Trạng thái** tại lát cắt 1 (2026-10-23): ✅ đạt, tự động · 🟡 một phần · ⏳ chưa có (chờ task) · ⛔ bị chặn bởi OQ/PQ. Loại: **U** unit · **I** integration API · **C** component UI · **E** E2E · **V** eval · **A** đối kháng · **P** hiệu năng · **M** thủ công/UAT.

#### E1 — Kho tài liệu

| Mã | AC / nguồn | Kịch bản | Kết quả mong đợi | Loại | Test / task | Trạng thái |
|---|---|---|---|---|---|---|
| TC-101-01 | AC-101.1 | Upload 1 PDF hợp lệ | 202; tài liệu xuất hiện ngay với `PROCESSING` | I | `test_ac_101_1_upload_one_pdf_shows_processing_immediately` | ✅ |
| TC-101-02 | AC-101.2 | Worker xử lý xong | `READY`, UI tự cập nhật không tải lại | I + E | `test_ac_101_2_status_becomes_ready_after_processing`; polling UI: E2E thủ công | 🟡 (thiếu E2E tự động) |
| TC-101-03 | AC-101.3 | Upload nhiều file, có 1 file lỗi | Mỗi file có kết quả riêng; file lỗi không chặn file khác | I | `test_ac_101_3_multiple_files_get_independent_results` | ✅ |
| TC-101-04 | AC-101.4 | 3 nhân viên BD, mỗi người 5 PDF mẫu | 15/15 `READY`, không cần kỹ thuật hỗ trợ | M | T5.5 (UAT) | ⏳ |
| TC-101-05 | PRD N-1 | Mất mạng khi đang upload | "Upload thất bại — Thử lại"; không kẹt "Đang xử lý" | E | T2.6 | ⏳ |
| TC-101-06 | PRD I-4 | Upload trùng nội dung | Theo quyết định PQ-03 | I | T2.5 | ⛔ PQ-03 |
| TC-102-01 | AC-102.1 | Kho ở dung lượng tối đa, hỏi câu có đáp án ở tài liệu X | Trích dẫn tài liệu X | V | T5.1 | ⛔ OQ-004 |
| TC-102-02 | AC-102.2 | File vượt kích thước/số trang | Từ chối **trước khi xử lý**, nêu giới hạn và giá trị thực (`FILE_TOO_LARGE`, `TOO_MANY_PAGES`) | I + C | T2.1 | ⏳ (giá trị tạm của OQ-004) |
| TC-102-03 | AC-102.3 | Kho đầy, upload thêm | `LIBRARY_FULL` + hướng dẫn xóa | I + C | T2.1 | ⏳ |
| TC-103-01 | AC-103.1 | PDF scan / có mật khẩu / hỏng | `UNUSABLE` với lý do `scanned` / `password` / `corrupt`; không `READY` | I + E | `test_ac_103_1_unusable_documents_get_specific_reason`; hiển thị tên + lý do trên UI: chưa kiểm (T2.6, T2.7) | 🟡 (backend đạt) |
| TC-103-02 | AC-103.2 | Ảnh PNG đổi đuôi `.pdf` | Từ chối theo nội dung: `NOT_A_PDF`, "Chỉ hỗ trợ PDF" | I | `test_ac_103_2_png_renamed_to_pdf_is_rejected_by_content` | ✅ |
| TC-103-03 | AC-103.3 | Có tài liệu lỗi, hỏi câu liên quan | Nội dung tài liệu lỗi không bao giờ được trích | I | `test_ac_103_3_unusable_document_is_never_cited` | ✅ |
| TC-103-04 | PRD N-4 | Embedding lỗi khi xử lý | `UNUSABLE(processing_failed)`, `retryable`, không còn chunk; nút Thử lại | I + E | `test_embedding_failure_leaves_no_chunks_and_is_retryable`; endpoint retry T2.3 | 🟡 |
| TC-103-05 | SAD §4.2 | Worker chết giữa job | Job hết hạn khóa được nhận lại; mỗi job xử lý đúng một lần | I | `test_job_with_expired_lock_is_reclaimed`, `test_each_job_is_processed_exactly_once` | ✅ |
| TC-104-01 | AC-104.1 | 5 tài liệu, 1 lỗi | Đủ 5 tên; đúng 4 "Sẵn sàng", 1 "Không dùng được" | I + E | T2.7 | ⏳ |
| TC-104-02 | AC-104.2 | Kho rỗng | Empty state, khung chat khóa kèm hướng dẫn (E-1) | C + E | `components.test.tsx` (Composer E-1/E-2, `blockedReason`) | 🟡 (thiếu E2E) |
| TC-104-03 | AC-104.3 | Có tài liệu, đang ở chat | Danh sách luôn hiển thị cạnh khung chat | E | E2E thủ công | 🟡 |
| TC-104-04 | UI_UX §9 | Badge trạng thái | Luôn có icon + chữ, không chỉ dựa vào màu | C | `components.test.tsx` (StatusBadge) | ✅ |
| TC-105-01 | AC-005 | Xóa tài liệu X, hỏi 3 câu chỉ có trong X | 3/3 "không tìm thấy", không trích X | I | T2.4, T2.7 | ⏳ |
| TC-105-02 | US-105 | Lỗi giữa chừng khi xóa | Xóa chunk + document trong **một giao dịch**; không còn chunk mồ côi | I | T2.4 | ⏳ |
| TC-105-03 | PRD §4.1 #8 | Bấm xóa | Hộp xác nhận nêu tên + hệ quả; focus mặc định vào Hủy; Esc hủy | C + E | T2.6 | ⏳ |

#### E2 — Hỏi đáp

| Mã | AC / nguồn | Kịch bản | Kết quả mong đợi | Loại | Test / task | Trạng thái |
|---|---|---|---|---|---|---|
| TC-201-01 | AC-201.1 | Có tài liệu `READY`, gửi câu hỏi | Câu trả lời dạng văn bản | I | `test_ac_201_1_and_203_1_answer_cites_document_name_and_page` | ✅ (LLM giả lập) |
| TC-201-02 | AC-201.2 | Đang chờ trả lời | Có chỉ báo; nút Gửi khóa, không gửi trùng | C | `Composer`: "nút Gửi bị khóa khi ô trống, khi đang chờ và khi quá dài" | ✅ |
| TC-201-03 | AC-201.3 | Bộ câu hỏi chuẩn nhóm "một tài liệu" | Tỷ lệ đúng ≥ `[TBD: OQ-002]` | V | T1.8, T0.8 | ⛔ OQ-002, DEP-002 |
| TC-201-04 | PRD I-5 | Câu hỏi rỗng/chỉ khoảng trắng | UI: nút Gửi khóa; API: 422 `QUESTION_EMPTY` | C + I | `test_invalid_question_returns_422`; Composer | ✅ |
| TC-201-05 | PRD I-6 | Câu hỏi > giới hạn ký tự (tạm 1000) | Bộ đếm báo lỗi, chặn gửi; API 422 `QUESTION_TOO_LONG` kèm `actual`, `limit` | C + I | như trên; "đánh dấu lỗi khi vượt giới hạn ký tự" | ✅ |
| TC-201-06 | PRD E-2, PQ-04 | Chưa có tài liệu `READY` | API 409 `NO_READY_DOCUMENTS`; UI khóa ô nhập kèm lý do | I + C | `test_no_ready_documents_returns_409`; Composer | ✅ (theo đề xuất PQ-04 "không"; chờ PO chốt) |
| TC-201-07 | PRD N-2 | Mất mạng khi chờ | Lỗi gắn với câu hỏi + "Gửi lại", giữ nội dung | E | T3.8 | ⏳ |
| TC-201-08 | SDD §3.6 | Hỏi trong cuộc trò chuyện không tồn tại/không thuộc người dùng | 404 theo mô hình lỗi chuẩn | I | `test_unknown_conversation_returns_404` | ✅ |
| TC-202-01 | AC-202.1 | Câu hỏi kiến thức chung ("Thủ đô của Pháp?") | "Không tìm thấy", không dùng kiến thức ngoài | I + V | `test_ac_204_1_out_of_scope_question_is_not_found_without_calling_llm` (giả lập); với LLM thật: T3.3 | 🟡 |
| TC-202-02 | AC-202.2 | SME rà mọi nhận định trong bộ câu hỏi chuẩn | Số nhận định không truy được ≤ `[TBD: OQ-002]` | V + M | T3.10 | ⛔ OQ-002 |
| TC-202-03 | PRD I-7, G-11 | Câu hỏi/PDF chứa chỉ dẫn "bỏ qua tài liệu…" | Vẫn grounded; không làm theo chỉ dẫn trong dữ liệu | A | T3.3 (bộ đầu), T5.2 (≥ 30 ca) | ⏳ |
| TC-203-01 | AC-203.1 | Câu trả lời có nội dung | 100% kèm ≥ 1 trích dẫn tên tài liệu + trang, dựng từ evidence | I + C | `test_ac_201_1_and_203_1_*`; `components.test.tsx` "luôn hiển thị tên tài liệu và số trang" | ✅ |
| TC-203-02 | SDD D-06 | LLM trích mã bằng chứng không có | Bỏ nhận định đó; không còn nhận định → `NOT_FOUND` | I | `test_citation_to_unknown_evidence_is_dropped_and_becomes_not_found` | ✅ |
| TC-203-03 | BR-008 | PDF nhiều trang | Mỗi chunk thuộc đúng một trang; overlap chỉ trong trang | U + I | `test_chunker_never_crosses_pages_and_overlaps_within_page`, `test_text_pdf_ready_and_every_chunk_belongs_to_exactly_one_page` | ✅ |
| TC-203-04 | AC-203.2 | Bộ câu hỏi chuẩn | % trích dẫn đúng trang ≥ `[TBD: OQ-002]` | V | T1.8 | ⛔ OQ-002 |
| TC-203-05 | AC-203.3 `[nên]` | Nhận định có trích dẫn riêng | Trích dẫn đứng cạnh nhận định | C | T3.8 | ⏳ |
| TC-203-06 | PRD C-2 | Không xác định được trang | Theo PQ-05 | I | — | ⛔ PQ-05 |
| TC-204-01 | AC-204.1 | Câu hỏi ngoài kho | HTTP 200, `kind=NOT_FOUND`, không gọi LLM (cổng 1); UI kiểu riêng | I + C | `test_ac_204_1_*`; "không tìm thấy và lỗi hệ thống có thông điệp khác nhau" | ✅ |
| TC-204-02 | SDD §3.8 cổng 2 | LLM trả `INSUFFICIENT_EVIDENCE` | `NOT_FOUND` | U | `test_gate_2_insufficient_evidence_is_not_found` | ✅ |
| TC-204-03 | AC-204.2 | ≥ 10 câu ngoài kho trong bộ chuẩn | MET-005 ≥ `[TBD: OQ-002]` | V | T1.8 | ⛔ OQ-002 |
| TC-204-04 | AC-204.3 | Hiển thị "không tìm thấy" | Kèm gợi ý diễn đạt lại / kiểm tra danh sách; mở được danh sách | C | Chuỗi `vi.notFoundBody` đã có; chưa có test riêng | 🟡 |
| TC-204-05 | PRD N-3, SDD §3.7 | LLM timeout / hết hạn mức / không khả dụng | 504 `AI_TIMEOUT` / 503 `AI_QUOTA` / 503 `AI_UNAVAILABLE`; **không bao giờ** `NOT_FOUND` | I | `test_ai_failure_is_an_error_never_not_found` (tham số hóa) | ✅ |
| TC-204-06 | SAD §4.2 | Lỗi AI tạm thời | Timeout cứng, retry có backoff, circuit breaker | U + I | T3.4 | ⏳ |
| TC-205-01 | US-205 | Bấm trích dẫn | Mở đúng trang; tài liệu đã xóa → chip "đã xóa" | E | T3.8, T3.9 | ⛔ PQ-01 |
| TC-206-01 | AC-206.1/.2 | Câu hỏi cần ≥ 2 tài liệu | Trích dẫn đủ mọi tài liệu cần thiết; tỷ lệ ≥ `[TBD: OQ-002]` | V | T3.1, T3.10 | ⛔ OQ-002 |
| TC-206-02 | AC-206.3 | Hai tài liệu mâu thuẫn | Nêu cả hai giá trị kèm nguồn | V | T3.3 | ⛔ PQ-02 |
| TC-207-01 | AC-011 | 5 chuỗi hội thoại kịch bản | ≥ 4/5 câu tiếp nối đúng ngữ cảnh; "Cuộc trò chuyện mới" xóa ngữ cảnh | V + E | T3.5 | ⏳ |
| TC-208-01 | AC-208.1 | Kho tối đa, chạy bộ câu hỏi chuẩn | ≥ `[TBD: OQ-006]`% trong `[TBD: OQ-006]` giây | P | T5.1 | ⛔ OQ-004, OQ-006 |
| TC-208-02 | AC-208.2, PRD N-3 | Chờ quá ngưỡng | "Đang mất nhiều thời gian hơn bình thường" + Hủy | C + E | T3.8 | ⏳ |
| TC-209-01 | AC-209.1/.2 | Hỏi theo từng ngôn ngữ được chốt | Trả lời đúng ngôn ngữ câu hỏi; tỷ lệ đúng đạt ngưỡng US-201 | V | T3.6 | ⛔ OQ-007 |

#### E3 — Truy cập và dữ liệu

| Mã | AC / nguồn | Kịch bản | Kết quả mong đợi | Loại | Test / task | Trạng thái |
|---|---|---|---|---|---|---|
| TC-301-01 | AC-301.1 | Chưa đăng nhập / không có quyền, gọi **mọi** route | 10/10 từ chối; không lộ nội dung | I + E | T4.1, T4.2 | ⛔ OQ-008 (hiện dùng user dev cố định) |
| TC-301-02 | AC-301.2 | Tài khoản có quyền | 10/10 thành công | I + E | T4.1 | ⛔ OQ-008 |
| TC-301-03 | AC-301.3 `[nên]` | Phiên hết hạn khi đang gõ | Về đăng nhập; câu hỏi đang nhập không mất | E | T4.1 | ⛔ OQ-008 |
| TC-301-04 | SAD STRIDE (EoP) | Vai trò BD gọi `/stats/*` | 403 | I | T4.2 | ⏳ |
| TC-302-01 | AC-302.1 | Rà cấu hình triển khai | Khớp văn bản phê duyệt STK-004 | M | T4.3, T5.8 | ⛔ OQ-009 |
| TC-302-02 | AC-302.2 | Ứng dụng gọi ra ngoài | Chỉ tới tên miền trong danh sách cho phép | I | T4.3 | ⛔ OQ-009 |
| TC-302-03 | G-10 | Upload/hỏi với **chuỗi đánh dấu** duy nhất, quét log + analytics + stack trace | 0 lần xuất hiện | I | T4.3 | ⏳ (hiện chỉ kiểm bằng review code) |

#### E4 — Đo lường pilot

| Mã | AC / nguồn | Kịch bản | Kết quả mong đợi | Loại | Test / task | Trạng thái |
|---|---|---|---|---|---|---|
| TC-401-01 | AC-016 | Đánh giá 10 câu trả lời | 10/10 ghi được, đổi được; xuất hiện trong thống kê | I + E | T4.5 | ⏳ |
| TC-402-01 | AC-017 | Tuần thử nghiệm có kịch bản | Số liệu khớp 100%; trống → empty state | I + E | T4.7 | ⏳ |
| TC-402-02 | PRD §5.2, G-14 | Sinh từng sự kiện analytics | Đủ thuộc tính; **không** có nội dung câu hỏi/tài liệu | I | T4.6 | ⏳ |

#### Xuyên suốt

| Mã | Nguồn | Kiểm tra | Test | Trạng thái |
|---|---|---|---|---|
| TC-X-01 | SDD §3.6 | Mọi lỗi dùng `{error:{code,message,details,correlationId}}`, kể cả lỗi framework; mọi response có `X-Correlation-Id` | `test_every_response_has_correlation_id_and_errors_use_standard_body`, `test_framework_errors_also_use_standard_error_body` | ✅ |
| TC-X-02 | T0.2 | Mọi operation trong `openapi.yaml` có hiện thực | `test_implementation_covers_every_operation_in_design_openapi` | ✅ (5/5 operation hiện có) |
| TC-X-03 | T0.2 | `schema.d.ts` sinh từ `openapi.yaml` không lệch | CI: `npm run gen:api && git diff --exit-code` | ✅ (chạy cục bộ) |
| TC-X-04 | SDD §3.3 | Quy tắc phụ thuộc giữa các lớp | `lint-imports` (3 contract) | ✅ |
| TC-X-05 | T1.2 | Ghi DB lỗi thì không để tệp mồ côi | `test_no_orphan_file_when_database_write_fails` | ✅ |
| TC-X-06 | SAD §4.3 | `/healthz`, `/readyz` (không gọi AI) | `test_health_and_ready` | ✅ |
| TC-X-07 | Phase 7 L0 | Quét lỗ hổng phụ thuộc | `pip-audit`, `npm audit --omit=dev --audit-level=high` | ✅ (chạy cục bộ) |
| TC-X-08 | Phase 7 L0 | Quét secret | gitleaks trong CI | ⏳ (chỉ chạy được trên GitHub) |
| TC-X-09 | ADR-004 | Embedding giả lập tất định, chuẩn hóa | `test_fake_embedding_is_deterministic_normalized_and_lexical` | ✅ |

## 5. Features Not to be Tested (§5.5)

| Tính năng | Lý do | Rủi ro | Kế hoạch |
|---|---|---|---|
| US-106 OCR, US-107 phân kho, US-210 lịch sử nhiều phiên, US-211 xuất câu trả lời, US-303 SSO | P2, ngoài phạm vi MVP (PRD §3.0) | Thấp; US-106 có thể tăng nếu OQ-005 cho thấy nhiều PDF scan | Xem lại khi OQ-005, OQ-010 chốt |
| Thời gian hoạt động/độ ổn định của nhà cung cấp AI bên ngoài | Trách nhiệm nhà cung cấp; chưa chọn (OQ-009) | Trung bình | Chỉ kiểm cách hệ thống phản ứng khi AI lỗi (TC-204-05, TC-204-06) |
| Mobile và màn hình < 1024 px | Không phải yêu cầu (CON-002, PRD P-4) | Thấp | Chỉ kiểm không cuộn ngang ở 1024 px |
| Tải vượt 2 lần dung lượng tối đa, HA đa vùng, chaos | MVP một nút (CON-001, SAD §4.2) | Thấp | — |
| Kiểm thử xâm nhập chuyên sâu | Ngoài năng lực đội dự án | Trung bình | IT/Bảo mật quyết định khi review G-08 |
| PostgreSQL + pgvector, chỉ mục HNSW | Chưa có môi trường container (ADR-006) | Trung bình: hành vi tìm kiếm có thể khác bản numpy | Chạy lại toàn bộ integration + eval khi chuyển (T0.3, T0.6) |

## 6. Approach (§5.6)

### 6.1 Tháp đảm bảo chất lượng

| Tầng | Ai/cái gì | Nội dung | Khi nào |
|---|---|---|---|
| **L0 — máy** | CI (GitHub Actions), chạy lại được cục bộ | Format, lint, type check, quy tắc phụ thuộc, unit + integration + component test, coverage, build, khớp `schema.d.ts`, quét lỗ hổng phụ thuộc, quét secret | Mỗi push và pull request |
| **L1 — agent** | Agent review trên diff, không có quyền merge | Đối chiếu AC, điều cấm trong `AGENTS.md`, rủi ro §0.2; trích dẫn file:dòng | Mỗi pull request; kết quả ghi trong test report |
| **L2 — người** | Reviewer ≠ tác giả (Phase 8) | Đọc diff, rubric 7 tiêu chí | Mỗi pull request |
| **L3–L4** | Inspection, demo với stakeholder | Diff chạm xác thực, dữ liệu, lời gọi AI ngoài; UAT | T4.x, T5.x |

### 6.2 Các mức và loại kiểm thử

| Mức / loại | Công cụ | Phạm vi | Vào | Ra | Tự động |
|---|---|---|---|---|---|
| **Unit** | pytest; Vitest + Testing Library | Chunker, embedding giả lập, cổng not-found, component UI | Code biên dịch được | 100% đạt | ✅ CI |
| **Integration (API)** | pytest + `TestClient`, SQLite tạm theo từng test, adapter giả lập, PDF tổng hợp | Vòng đời tài liệu, worker, hỏi đáp, lỗi chuẩn | Unit đạt | 100% đạt | ✅ CI |
| **Contract** | Test bao phủ OpenAPI; `openapi-typescript` + `git diff` | Code ↔ `openapi.yaml`; adapter thật ↔ port (bộ contract test dùng chung khi có adapter thật) | Có thay đổi API hoặc adapter | 100% đạt | ✅ CI |
| **Kiến trúc** | import-linter | 3 contract phụ thuộc SDD §3.3 | — | 0 vi phạm | ✅ CI |
| **E2E** | Playwright (Chrome) `[Proposed]` | Flow F1–F7 (UI_UX §4) | Từ GĐ2 | Luồng chính đạt | ⏳ (hiện thủ công) |
| **Eval chất lượng** | Harness T1.8 gọi API, bộ câu hỏi chuẩn 3 nhóm | MET-002, MET-005, % trích dẫn đúng trang | Có T0.8 và adapter thật | Đạt ngưỡng OQ-002; không giảm so với lần trước (DoD #8) | Hàng đêm + khi đổi mô hình/tham số |
| **Đối kháng** | Bộ ca prompt injection (câu hỏi và nội dung PDF) | US-202, G-11 | Từ GĐ3 | 0 ca vượt quy tắc grounded | Tự động |
| **Bảo mật** | Công cụ quét ứng dụng web (DAST), pip-audit, npm audit, gitleaks | T5.2 | Có xác thực (T4.x) | 0 High/Critical | Một phần |
| **Hiệu năng** | Script tải `[Proposed: k6 hoặc Locust]` | Độ trễ hỏi đáp, thời gian xử lý tài liệu | Kho ở dung lượng tối đa | Đạt OQ-006 | Bán tự động |
| **Accessibility** | axe-core qua Playwright + bàn phím + trình đọc màn hình | S01–S03, hộp thoại | UI ổn định | Mức WCAG được chốt | Một phần |
| **Hồi quy** | Toàn bộ L0 + eval | Mọi thay đổi | — | Như L0 | ✅ CI |
| **UAT** | Kịch bản thủ công | AC-101.4 và luồng chính với 3 nhân viên BD | M4 đạt | Sponsor/PO chấp nhận | Thủ công |

### 6.3 Tự động và thủ công

| Tự động (CI, chặn merge) | Thủ công |
|---|---|
| Mọi test U/I/C, kiến trúc, contract, quét phụ thuộc, secret; sau GĐ2 thêm E2E; sau T1.8 thêm eval (chạy hàng đêm, chưa chặn merge) | UAT (AC-101.4), chấm SME cho MET-002/AC-202.2, thử trình đọc màn hình, rà cấu hình theo văn bản phê duyệt (AC-302.1), E2E thăm dò |

### 6.4 Dữ liệu kiểm thử

- **Chỉ dùng dữ liệu không nhạy cảm** cho tới G-08 (BR-015, `AGENTS.md`). PDF test sinh bằng code (`backend/tests/pdfs.py`): văn bản nhiều trang, scan (không có lớp chữ), có mật khẩu, hỏng, file giả PDF.
- Bộ tài liệu mẫu + bộ câu hỏi chuẩn do đội BD soạn (T0.8, DEP-002): ≥ 5 câu nhiều tài liệu, ≥ 10 câu ngoài kho (G-02).
- Chuỗi đánh dấu duy nhất (canary) cho test log/analytics (TC-302-03).
- Mỗi test integration dùng CSDL và thư mục tệp riêng, tạo mới và xóa sau test.

### 6.5 Quản lý lỗi

| Mức | Định nghĩa | Ví dụ |
|---|---|---|
| Blocker | Chặn luồng chính hoặc vi phạm điều cấm | Trả lời không có trích dẫn; tài liệu không `READY` bị trích; nội dung tài liệu trong log |
| Critical | Sai kết quả ở story P0, lỗ hổng bảo mật | Lỗi AI hiển thị thành "không tìm thấy"; truy cập không cần đăng nhập |
| Major | Tính năng P1 hỏng hoặc P0 có cách tránh | Polling không cập nhật trạng thái |
| Minor | Hiển thị, văn bản | Sai chính tả thông báo |

Nơi theo dõi: `[Proposed: GitHub Issues, nhãn bug + severity]`. G-07 yêu cầu 0 Blocker/Critical mở.

## 7. Item Pass/Fail Criteria (§5.7)

| Hạng mục | Đạt khi |
|---|---|
| Một lần build (L0) | Mọi bước CI xanh: 0 lỗi format/lint/type; 3/3 contract phụ thuộc; 100% test đạt; `schema.d.ts` không lệch; 0 lỗ hổng phụ thuộc mức High trở lên; 0 secret |
| Độ phủ code backend | ≥ **70%** dòng `[Proposed — theo quy trình Phase 7; PRD G-12 để [TBD]]`; logic nghiệp vụ `app/modules` ≥ 90% `[Proposed]` |
| Một story | Mọi AC Given-When-Then đạt (P1: tiêu chí kiểm chứng đạt); có test tự động trong CI (DoD #1–2) |
| Chất lượng trả lời | MET-002, MET-005, % trích dẫn đúng trang ≥ `[TBD: OQ-002]`; **100%** câu trả lời có nội dung kèm trích dẫn hợp lệ |
| Hiệu năng | ≥ `[TBD: OQ-006]`% câu hỏi trong `[TBD: OQ-006]` giây (G-05) |
| Bảo mật | 0 lỗ hổng High/Critical mở; 0 ca đối kháng vượt; 10/10 từ chối và 10/10 cho phép |
| Ra khỏi Phase 7 cho một PR | L0 xanh + L1 không còn phát hiện mức Blocker/Critical + test report cập nhật |
| Launch gate | G-01…G-17 theo PRD §5.1; **No-go bắt buộc** nếu G-03, G-08 hoặc G-09 không đạt |

Mục có ngưỡng `[TBD]` được ghi **"chưa quyết định được"**, không được coi là đạt.

## 8. Suspension Criteria and Resumption Requirements (§5.8)

| Tạm dừng khi | Tiếp tục khi |
|---|---|
| Phát hiện **dữ liệu thật** của BD hoặc lời gọi tới dịch vụ AI ngoài chưa được duyệt trong môi trường test | Xóa dữ liệu, rà log, báo IT/Bảo mật, có xác nhận bằng văn bản |
| L0 trên nhánh chính đỏ quá 1 ngày làm việc | Có commit sửa và CI xanh lại |
| Môi trường test hỏng (CSDL, kho tệp, worker không chạy) làm > 20% ca lỗi vì môi trường `[Proposed]` | Môi trường dựng lại sạch, chạy smoke (`/readyz`, upload 1 PDF, 1 câu hỏi) đạt |
| Có lỗi Blocker ở luồng upload hoặc hỏi đáp làm các ca sau không chạy được | Đã sửa, đã chạy lại ca gây lỗi và các ca phụ thuộc |
| Đổi mô hình/tham số mà eval giảm so với lần trước (khi đã có T1.8) | Hoàn tác hoặc chấp nhận có ghi nhận của Tech lead |
| Hợp đồng OpenAPI đổi mà chưa sinh lại kiểu | `npm run gen:api` và test contract đạt |

## 9. Test Deliverables (§5.9)

| Sản phẩm | Vị trí | Khi nào |
|---|---|---|
| Master Test Plan (tài liệu này) | `docs/06-verification/Master_Test_Plan.md` | Cập nhật mỗi mốc |
| Test Case Specification (bản chuẩn) + bản thực thi Excel | `docs/06-verification/Test_Case_Specification.md`, `Test_Cases.xlsx` | Viết bước chi tiết khi task bắt đầu |
| Kết quả review kế hoạch theo checklist IEEE 829 | `docs/06-verification/Test_Plan_Review_IEEE_829.xlsx` | Mỗi version |
| Test summary report (gồm L0, coverage, L1, lỗi, đánh giá) | `docs/06-verification/Test_Report_<lát cắt>.md` | Mỗi lát cắt / mốc |
| Log CI, báo cáo coverage (`coverage.xml`) | Artifact GitHub Actions | Mỗi lần chạy |
| Script test | `backend/tests/`, `frontend/src/**/*.test.tsx`, sau này `e2e/`, `eval/` | Theo task |
| Báo cáo eval chất lượng | `[Proposed: docs/06-verification/eval/]` | Mỗi lần chạy T1.8 |
| Báo cáo bảo mật, hiệu năng, accessibility, UAT | `docs/06-verification/` | T5.1–T5.5 |
| Ma trận truy vết cập nhật | `docs/05-implementation/traceability.md` | Mỗi story |
| Hồ sơ Launch gate | T5.8 | M5 |

## 10. Testing Tasks (§5.10)

| # | Việc | Người làm | Phụ thuộc | Task |
|---|---|---|---|---|
| 1 | Duy trì L0, chạy lại khi có PR | Dev + CI | — | T0.5 |
| 2 | Xác nhận CI chạy được trên GitHub, lưu log và coverage | Tech lead | Quyền xem Actions | T0.5 |
| 3 | Thêm ngưỡng coverage vào CI (`--cov-fail-under`) | Dev | Chốt ngưỡng ở §7 | — |
| 4 | Dựng E2E Playwright cho F1, F2 (vào CI) | QA/Dev | T2.6 | T2.7 |
| 5 | Soạn bộ tài liệu mẫu + bộ câu hỏi chuẩn | BD lead | — | T0.8 |
| 6 | Harness eval, báo cáo đầu tiên | Dev/QA | T0.8, T1.7 | T1.8 |
| 7 | Bộ đối kháng ban đầu → mở rộng ≥ 30 ca | QA | T3.3 | T3.3, T5.2 |
| 8 | Test bảng quyền mọi route; test chuỗi đánh dấu | Dev/QA | OQ-008, OQ-009 | T4.2, T4.3 |
| 9 | Test hiệu năng | QA | OQ-004, OQ-006, T4.9 | T5.1 |
| 10 | Test bảo mật | QA + IT/Bảo mật | T4.x | T5.2 |
| 11 | Kiểm accessibility | QA | UI ổn định | T5.3 |
| 12 | UAT | BD lead + 3 nhân viên BD | M4 | T5.5 |
| 13 | Viết test report mỗi lát cắt; hồ sơ Launch gate | QA | — | T5.8 |

## 11. Environmental Needs (§5.11)

| Môi trường | Thành phần | Dữ liệu | Adapter AI | Trạng thái |
|---|---|---|---|---|
| **Cục bộ (dev)** | Windows 10; Python 3.12.10 + uv; Node 24; SQLite tạm; Chrome cho E2E thủ công | PDF tổng hợp | Giả lập | Có |
| **CI** | GitHub Actions `ubuntu-latest`; uv; Node 24 | PDF tổng hợp | Giả lập | Đã cấu hình, **chưa xác nhận chạy** |
| **test** | Container: PostgreSQL + pgvector, kho tệp, API, worker; Playwright | Bộ mẫu + bộ câu hỏi chuẩn (không nhạy cảm) | Thật — nhà cung cấp được duyệt | ⛔ Chờ Docker/hạ tầng (T0.6, T4.9), OQ-009, DEP-003 |
| **pilot** | Như test | Dữ liệu thật **chỉ sau G-08** | Thật | ⛔ OQ-009 |

Công cụ cần thêm: Playwright (E2E, axe-core), công cụ tải, công cụ quét DAST, trình đọc màn hình (NVDA). Không cần GPU cho adapter giả lập; với embedding thật chạy nội bộ (ADR-004), cần đo CPU/RAM ở T1.7.

## 12. Responsibilities (§5.12)

| Vai trò | Trách nhiệm |
|---|---|
| QA | Kế hoạch này, ca kiểm thử, E2E, đối kháng, hiệu năng, accessibility, test report, hồ sơ Launch gate |
| Dev backend / frontend | Unit, integration, component test cho mỗi AC (TDD); giữ CI xanh |
| Tech lead | Duyệt kế hoạch; duy trì CI; chốt tham số `[Initial]` bằng số liệu eval |
| Agent (L1) | Review trên diff, chạy L0, soạn báo cáo; **không** approve, merge, deploy |
| Reviewer (L2) | Review PR, khác tác giả (Phase 8) |
| BD lead / SME | Bộ câu hỏi chuẩn, chấm MET-002, UAT |
| IT/Bảo mật | Review T4.3, T5.2; phê duyệt G-08 |
| PO / Sponsor | Chốt PQ/OQ chặn test; nghiệm thu; ký Go |

Tên người cụ thể: `[TBD: OQ-014]`.

## 13. Staffing and Training Needs (§5.13)

- QA cần hiểu **grounding và RAG**: ba cổng not-found, vì sao trích dẫn do hệ thống dựng (SDD D-06), khác biệt `NOT_FOUND` (200) với lỗi `AI_*` (5xx).
- Kỹ năng viết ca **prompt injection** và chấm kết quả đối kháng.
- Playwright + axe-core; pytest, Vitest.
- SME đội BD cần hướng dẫn chấm theo rubric thống nhất (đúng / đúng một phần / sai; trích dẫn đúng trang hay không) để kết quả MET-002 nhất quán giữa người chấm.
- Quy mô nhân sự: `[TBD: OQ-014]`.

## 14. Schedule (§5.14)

Chưa có ngày (OQ-012); gắn theo mốc của Implementation Plan §4.

| Mốc | Hoạt động kiểm thử | Điều kiện ra |
|---|---|---|
| M0 | Kế hoạch này được duyệt; CI chạy trên GitHub | CI xanh trên GitHub |
| M1 (lát cắt 1 đã xong) | L0 + test report lát cắt 1; báo cáo eval đầu tiên (chưa cần đạt ngưỡng) | Test report; eval chờ T0.8 |
| M2 | TC-101…105 đạt; E2E F1 trong CI | Mọi AC US-101…104 đạt |
| M3 | Eval đạt ngưỡng; bộ đối kháng ban đầu; TC-201…209 | Báo cáo eval đạt OQ-002 |
| M4 | TC-301, 302, 401, 402; test chuỗi đánh dấu; thử khôi phục | AC-014, AC-016, AC-017 đạt |
| M5 | Hiệu năng, bảo mật, accessibility, UAT; hồ sơ Launch gate | Sponsor ký Go |

## 15. Risks and Contingencies (§5.15)

| ID | Rủi ro kiểm thử | Ảnh hưởng | Dự phòng |
|---|---|---|---|
| RT-01 | Bộ câu hỏi chuẩn đến muộn (T0.8) | Không đo được G-03; không nghiệm thu US-201…206 | Harness eval làm trước với bộ câu hỏi tổng hợp từ PDF mẫu; nhắc owner theo T0.7 |
| RT-02 | OQ-009 chưa chốt: không có LLM/embedding thật | Kết quả hiện tại chỉ chứng minh **luồng và quy tắc**, không chứng minh chất lượng | Ghi rõ trong mọi report; chạy lại eval + integration khi có adapter thật; contract test cho adapter |
| RT-03 | Không có Docker → chưa có PostgreSQL + pgvector | Hành vi tìm kiếm và giao dịch khác bản SQLite | Chạy lại toàn bộ integration khi chuyển (ADR-006); không nghiệm thu hiệu năng trên SQLite |
| RT-04 | CI chưa từng chạy trên GitHub (máy không có `gh`) | Bước chỉ có trên CI (gitleaks) chưa có bằng chứng | Xem tab Actions trên web và lưu log vào report |
| RT-05 | E2E chỉ thủ công | Hồi quy UI có thể lọt | Ưu tiên Playwright cho F1, F2 ở GĐ2 |
| RT-06 | Adapter giả lập quá "dễ" (lexical) | Ca not-found đạt giả tạo | Eval và đối kháng với adapter thật là điều kiện của M3 |
| RT-07 | Hạn mức/chi phí AI khi chạy eval nhiều lần | Hết ngân sách (RSK-006) | Giới hạn số lần chạy; cache embedding; ngân sách theo OQ-013 |
| RT-08 | Ngưỡng `[TBD]` chưa chốt | Không kết luận được đạt/không đạt | Báo "chưa quyết định được"; theo dõi OQ-002, 004, 006 |

## 16. Approvals (§5.16)

| Vai trò | Tên | Quyết định | Chữ ký / ngày |
|---|---|---|---|
| QA lead | [TBD: OQ-014] | [Approve / Approve with conditions / Reject] | |
| Tech lead | [TBD: OQ-014] | [Approve / Reject] | |
| Product owner | [TBD: OQ-014] | [Approve / Reject] | |
| IT / Bảo mật (phần §6 bảo mật, TC-302) | [TBD: OQ-015] | [Approve / Reject] | |

---

## Phụ lục A — Thống kê độ phủ AC (lát cắt 1)

| Nhóm | Ca kiểm thử | ✅ | 🟡 | ⏳ | ⛔ |
|---|---|---|---|---|---|
| E1 Kho tài liệu | 21 | 6 | 5 | 8 | 2 |
| E2 Hỏi đáp | 30 | 12 | 2 | 6 | 10 |
| E3 Truy cập & dữ liệu | 7 | 0 | 0 | 2 | 5 |
| E4 Đo lường | 3 | 0 | 0 | 3 | 0 |
| Xuyên suốt | 9 | 8 | 0 | 1 | 0 |
| **Tổng** | **70** | **26** | **7** | **20** | **17** |

Bước chi tiết (điều kiện trước, dữ liệu, các bước, kết quả mong đợi) của 33 ca đã chạy: [Test_Case_Specification.md](Test_Case_Specification.md) · bản thực thi [Test_Cases.xlsx](Test_Cases.xlsx).

Nghĩa: lát cắt 1 đã kiểm tự động phần **luồng và quy tắc** (trích dẫn từ evidence, ba cổng, lỗi AI ≠ not-found, tài liệu lỗi không bị trích). Phần **chất lượng, quyền truy cập, hiệu năng** chưa kiểm được: chờ task GĐ2–5 hoặc bị chặn bởi OQ-002, 004, 006, 007, 008, 009.

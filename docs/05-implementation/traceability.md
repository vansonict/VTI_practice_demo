# Traceability — Yêu cầu ↔ Code ↔ Test

> Cập nhật sau mỗi lát cắt (Phase 6, bước REFINE). Mã AC theo PRD §3. Đường dẫn code tính từ gốc repo.
> **Cập nhật lần cuối:** 2026-10-23 — Lát cắt 1 (upload → xử lý → hỏi → trả lời có trích dẫn).

## Trạng thái theo user story

| Story | BR | UC | Trạng thái | Code chính | Test |
|---|---|---|---|---|---|
| US-101 Upload PDF | BR-001 | UC-02 | **Một phần**: upload nhiều file, trạng thái PROCESSING → READY, kiểm chữ ký PDF. Chưa: giới hạn kích thước/kho đầy (T2.1), trùng file (T2.5) | `backend/app/modules/documents/service.py`, `backend/app/api/routes.py`, `frontend/src/components/DocumentPanel.tsx` | `test_documents_api.py::test_ac_101_1_*`, `test_ac_101_2_*`, `test_ac_101_3_*`; E2E thủ công 2026-10-23 |
| US-102 Dung lượng kho | BR-002 | UC-02 | Chưa (T2.1) | — | — |
| US-103 Báo tài liệu lỗi | BR-003 | UC-03, 04 | **Một phần**: phân loại password/corrupt/scanned/processing_failed, không trích dẫn tài liệu không READY. Chưa: retry endpoint (T2.3), timeout/retry trong worker (T2.2) | `backend/app/modules/ingestion/service.py`, `backend/app/adapters/pypdf_extractor.py`, `frontend/src/components/DocumentPanel.tsx` | `test_ingestion.py::test_ac_103_1_*`, `test_documents_api.py::test_ac_103_2_*`, `test_qa_api.py::test_ac_103_3_*` |
| US-104 Danh sách + trạng thái | BR-004 | UC-05 | **Một phần**: danh sách, 3 trạng thái icon + chữ, lý do lỗi, kho rỗng, polling. Chưa: E2E tự động | `backend/app/api/routes.py`, `frontend/src/App.tsx`, `frontend/src/components/StatusBadge.tsx` | `components.test.tsx` (StatusBadge, blockedReason) |
| US-105 Xóa tài liệu | BR-005 | UC-06 | Chưa (T2.4) | — | — |
| US-201 Hỏi bằng ngôn ngữ tự nhiên | BR-006 | UC-07 | **Một phần**: hỏi → trả lời; kiểm câu hỏi rỗng/quá dài; chặn khi chưa có tài liệu sẵn sàng. Chưa: chất lượng thật (cần LLM + embedding thật, T1.7, T3.7, T3.10) | `backend/app/modules/qa/service.py`, `frontend/src/components/ChatPanel.tsx`, `Composer.tsx` | `test_qa_api.py::test_ac_201_1_*`, `test_invalid_question_*`, `test_no_ready_documents_*`; `components.test.tsx` (Composer) |
| US-202 Chỉ trả lời từ kho | BR-007 | UC-09 | **Một phần**: cổng 1 (ngưỡng liên quan, không gọi LLM), cổng 2, cổng 3 cơ bản. Chưa: chỉ thị hệ thống, chống prompt injection (T3.3), thử lại ở cổng 3 (T3.2) | `backend/app/modules/qa/service.py` | `test_qa_api.py::test_ac_204_1_*`, `test_citation_to_unknown_evidence_*`; `test_units.py::test_gate_2_*` |
| US-203 Trích dẫn nguồn | BR-008 | UC-09 | **Xong cho lát cắt**: trích dẫn dựng từ bản ghi đoạn (tên tài liệu + trang), không lấy từ văn bản mô hình. Chưa: đo % đúng trang trên bộ câu hỏi chuẩn (T1.8) | `backend/app/modules/qa/service.py`, `backend/app/modules/ingestion/chunker.py`, `frontend/src/components/Messages.tsx` | `test_qa_api.py::test_ac_201_1_and_203_1_*`, `test_ingestion.py::test_text_pdf_ready_and_every_chunk_belongs_to_exactly_one_page`, `test_units.py::test_chunker_*`; `components.test.tsx` |
| US-204 Báo "không tìm thấy" | BR-009 | UC-10 | **Một phần**: NOT_FOUND là HTTP 200, hiển thị khác lỗi hệ thống; lỗi AI là `AI_*` 5xx. Chưa: đo MET-005 (T1.8) | `backend/app/modules/qa/service.py`, `frontend/src/components/Messages.tsx` | `test_qa_api.py::test_ac_204_1_*`, `test_ai_failure_is_an_error_never_not_found`; `components.test.tsx` |
| US-205 Mở trang nguồn | (BR-018 đề xuất) | UC-12 | Chưa (T3.8, T3.9) | — | — |
| US-206 Tổng hợp nhiều tài liệu | BR-010 | UC-08 | Chưa kiểm (LLM giả lập chỉ trích một bằng chứng; T3.1, T3.10) | — | — |
| US-207 Hỏi tiếp nối | BR-011 | UC-11 | Chưa (T3.5) | — | — |
| US-208 Thời gian phản hồi | BR-012 | UC-07 | Chưa (đo ở T5.1; chờ lâu + Hủy ở T3.8) | — | — |
| US-209 Ngôn ngữ | BR-013 | UC-07 | Chưa (chờ OQ-007) | — | — |
| US-301 Truy cập có quyền | BR-014 | UC-01 | Chưa (T4.1): API đang dùng người dùng dev cố định | — | — |
| US-302 Dữ liệu trong phạm vi duyệt | BR-015 | — | Một phần: không có lời gọi ra ngoài (chỉ adapter giả lập); log không chứa nội dung | `backend/app/container.py` | — |
| US-401, US-402 | BR-016, 017 | UC-13, 14 | Chưa (GĐ4) | — | — |

## Yêu cầu xuyên suốt đã có kiểm tra tự động

| Yêu cầu | Nguồn | Kiểm tra |
|---|---|---|
| Module nghiệp vụ không phụ thuộc adapter/DB/framework | SDD §3.3 | `lint-imports` (3 contract) trong CI |
| Mọi lỗi API theo mô hình chuẩn kèm `correlationId` | SDD §3.6 | `test_units.py::test_every_response_has_correlation_id_*`, `test_framework_errors_also_use_standard_error_body` |
| Code khớp hợp đồng OpenAPI thiết kế | T0.2 | `test_units.py::test_implementation_covers_every_operation_in_design_openapi`; CI kiểm `schema.d.ts` sinh từ `openapi.yaml` |
| Không để tệp mồ côi khi giao dịch lỗi | T1.2 | `test_documents_api.py::test_no_orphan_file_when_database_write_fails` |
| Mỗi job xử lý đúng một lần; job quá hạn được nhận lại | T1.3 | `test_ingestion.py::test_each_job_*`, `test_job_with_expired_lock_is_reclaimed` |

## Lịch sử

| Ngày | Lát cắt | Ghi chú |
|---|---|---|
| 2026-10-23 | 1 — Walking skeleton | SQLite tạm (ADR-006), adapter AI giả lập; backend 33 test, độ phủ 95%; frontend 11 test; E2E thủ công qua trình duyệt |

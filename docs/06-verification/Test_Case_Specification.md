# Test Case Specification — "Chat với tài liệu" (MVP)

> **Chuẩn:** IEEE 829-2008, Test Case Specification · **Kế hoạch:** [Master_Test_Plan.md](Master_Test_Plan.md) §4.3 (mã TC-* giữ nguyên) · **Bản thực thi:** [Test_Cases.xlsx](Test_Cases.xlsx) (cùng nội dung, có cột ghi kết quả từng lần chạy)
> **Dành cho:** QA, Dev, Reviewer. **Bản chuẩn** là file này; khi sửa ca kiểm thử, sửa ở đây rồi cập nhật bản Excel.

| Mục | Giá trị |
|---|---|
| Mã / Version | TCS-CWD-001 / 0.1 — Draft |
| Ngày | 2026-10-23 |
| Phạm vi | 33 ca **chi tiết** (đã chạy ở lát cắt 1: 26 đạt, 7 một phần) + 37 ca **khung** (chờ task hoặc OQ/PQ) = 70 ca |
| Lần chạy gần nhất | 2026-10-23, commit `163a7dd`, Agent (L0) — xem [Test_Report_Slice1.md](Test_Report_Slice1.md) |

## 1. Cách đọc và cách chạy

- Mỗi ca có: truy vết, mức kiểm thử, ưu tiên, **điều kiện trước**, **dữ liệu** (mã ở §2), **các bước** kèm kết quả mong đợi, cách chạy tự động, kết quả lần chạy gần nhất.
- Bước ghi **Thủ công** là phần chưa có test tự động; tester làm trên trình duyệt (`npm run dev` + API + worker theo `AGENTS.md`).
- Ca mức Integration chạy được bằng tay qua API (Swagger UI tại `http://localhost:8000/docs`) theo đúng các bước; bản tự động dùng CSDL và thư mục tệp riêng cho từng test.
- Chạy toàn bộ: `cd backend && uv run pytest` và `cd frontend && npm test`. Trên Windows đặt `PYTHONIOENCODING=utf-8`.
- Chế độ lỗi của LLM giả lập bật bằng `CWD_LLM_FAKE_MODE` (`timeout`, `quota`, `unavailable`, `invalid_output`, `cite_unknown_evidence`).
- Trạng thái: **Pass** · **Một phần** (phần tự động đạt, còn bước chưa chạy) · **Chưa có** (chờ task) · **Bị chặn** (chờ OQ/PQ).

## 2. Dữ liệu kiểm thử

Toàn bộ là dữ liệu tổng hợp, không nhạy cảm (BR-015). PDF sinh bằng `backend/tests/pdfs.py`; văn bản không dấu vì font chuẩn của reportlab, để chạy giống nhau trên mọi máy CI.

| Mã | Tên / loại | Nội dung | Nguồn |
|---|---|---|---|
| TD-01 | hop_dong_A.pdf | PDF văn bản 3 trang (sinh bằng `make_pdf`). Tr.1: "Service contract between Company A and Company B. Duration is twenty four months." Tr.2: "Scope of work includes deployment training and support." Tr.3: "Payment terms: the customer pays within thirty days after receiving the invoice. Late payment interest applies." | `test_qa_api.py::CONTRACT` |
| TD-02 | bao_cao.pdf | PDF văn bản 2 trang: "Quarter report revenue", "Second page" | `make_pdf` |
| TD-03 | hop_dong.pdf | PDF văn bản 1 trang: "Contract text" | `make_pdf` |
| TD-04 | a.pdf, b.pdf | PDF văn bản 1 trang: "A" / "B" (hoặc "alpha" / "beta") | `make_pdf` |
| TD-05 | ghi_chu.txt | Tệp văn bản thường, nội dung `plain text, not a pdf` | bytes trong test |
| TD-06 | anh.pdf | Ảnh PNG đổi đuôi: chữ ký `89 50 4E 47 0D 0A 1A 0A` + 32 byte 0 | bytes trong test |
| TD-07 | mat_khau.pdf | PDF 1 trang có mật khẩu (user `secret`, owner `owner`) | `make_encrypted_pdf` |
| TD-08 | hong.pdf | PDF 3 trang bị cắt còn 1/3 số byte đầu | `make_corrupt_pdf` |
| TD-09 | scan.pdf | PDF 3 trang chỉ có hình chữ nhật tô đen, không có lớp chữ (giả lập scan) | `make_blank_pdf(3)` |
| TD-10 | ten_pages.pdf | PDF 10 trang, mỗi trang 60 từ dạng `page{n}word{i}` (để nhận biết từ thuộc trang nào) | `make_pdf` |
| TD-11 | other.pdf | PDF 1 trang: "Unrelated marketing brochure about coffee machines" | `make_pdf` |
| TD-12 | x.pdf | PDF văn bản 1 trang ("some text" / "text" / "x") | `make_pdf` |
| Q-01 | Câu hỏi trong kho | `What are the payment terms for the invoice?` — đáp án ở TD-01 trang 3 | — |
| Q-02 | Câu hỏi ngoài kho | `Thu do nuoc Phap la gi` — kiến thức chung, không có trong kho | — |
| Q-03 | Câu hỏi rỗng | 3 dấu cách `"   "` | — |
| Q-04 | Câu hỏi quá dài | 1001 ký tự `x` (giới hạn tạm 1000, `CWD_MAX_QUESTION_CHARS`) | — |

## 3. Ca kiểm thử chi tiết

| Mã | Tiêu đề | Ưu tiên | Kết quả |
|---|---|---|---|
| [TC-101-01](#tc-101-01) | Upload 1 PDF hiển thị "Đang xử lý" ngay | Cao | Pass |
| [TC-101-02](#tc-101-02) | Trạng thái tự chuyển "Sẵn sàng truy vấn" không cần tải lại | Cao | Một phần |
| [TC-101-03](#tc-101-03) | Upload nhiều file: mỗi file có kết quả riêng | Cao | Pass |
| [TC-103-01](#tc-103-01) | PDF scan / có mật khẩu / hỏng → "Không dùng được" kèm lý do | Cao | Một phần |
| [TC-103-02](#tc-103-02) | File không phải PDF bị từ chối theo nội dung, không theo đuôi | Cao | Pass |
| [TC-103-03](#tc-103-03) | Tài liệu không dùng được không bao giờ được trích dẫn | Cao | Pass |
| [TC-103-04](#tc-103-04) | Lỗi embedding khi xử lý → "Không dùng được", cho phép thử lại | Trung bình | Một phần |
| [TC-103-05](#tc-103-05) | Mỗi job xử lý đúng một lần; job hết hạn khóa được nhận lại | Trung bình | Pass |
| [TC-104-02](#tc-104-02) | Kho rỗng / chưa có tài liệu sẵn sàng: khóa ô hỏi và giải thích | Trung bình | Một phần |
| [TC-104-03](#tc-104-03) | Danh sách tài liệu luôn hiển thị cạnh khung chat | Trung bình | Một phần |
| [TC-104-04](#tc-104-04) | Badge trạng thái có chữ, không chỉ dựa vào màu | Trung bình | Pass |
| [TC-201-01](#tc-201-01) | Hỏi bằng ngôn ngữ tự nhiên nhận câu trả lời văn bản | Cao | Pass |
| [TC-201-02](#tc-201-02) | Nút Gửi khóa khi ô trống, khi đang chờ, khi quá dài | Cao | Pass |
| [TC-201-04](#tc-201-04) | Câu hỏi rỗng bị chặn | Trung bình | Pass |
| [TC-201-05](#tc-201-05) | Câu hỏi quá dài bị chặn, không cắt cụt im lặng | Trung bình | Pass |
| [TC-201-06](#tc-201-06) | Chưa có tài liệu sẵn sàng: không cho hỏi | Trung bình | Pass |
| [TC-201-08](#tc-201-08) | Hỏi trong cuộc trò chuyện không tồn tại | Thấp | Pass |
| [TC-202-01](#tc-202-01) | Câu hỏi kiến thức chung → "không tìm thấy", không gọi LLM | Cao | Một phần |
| [TC-203-01](#tc-203-01) | Câu trả lời luôn kèm tên tài liệu + số trang | Cao | Pass |
| [TC-203-02](#tc-203-02) | LLM trích bằng chứng không tồn tại → bỏ, thành "không tìm thấy" | Cao | Pass |
| [TC-203-03](#tc-203-03) | Mỗi đoạn văn bản thuộc đúng một trang | Cao | Pass |
| [TC-204-01](#tc-204-01) | Ngoài kho: "không tìm thấy" (HTTP 200), hiển thị khác lỗi hệ thống | Cao | Pass |
| [TC-204-02](#tc-204-02) | LLM báo không đủ bằng chứng → "không tìm thấy" | Cao | Pass |
| [TC-204-04](#tc-204-04) | "Không tìm thấy" kèm gợi ý hành động | Trung bình | Một phần |
| [TC-204-05](#tc-204-05) | Lỗi dịch vụ AI là lỗi 5xx, không bao giờ là "không tìm thấy" | Cao | Pass |
| [TC-X-01](#tc-x-01) | Mọi lỗi dùng mô hình chuẩn kèm correlationId | Cao | Pass |
| [TC-X-02](#tc-x-02) | Mọi operation trong openapi.yaml đều có hiện thực | Trung bình | Pass |
| [TC-X-03](#tc-x-03) | Kiểu TypeScript sinh từ OpenAPI không lệch | Trung bình | Pass |
| [TC-X-04](#tc-x-04) | Quy tắc phụ thuộc giữa các lớp | Cao | Pass |
| [TC-X-05](#tc-x-05) | Ghi CSDL lỗi thì không để tệp mồ côi | Trung bình | Pass |
| [TC-X-06](#tc-x-06) | Health và readiness | Thấp | Pass |
| [TC-X-07](#tc-x-07) | Không có lỗ hổng phụ thuộc đã biết | Trung bình | Pass |
| [TC-X-09](#tc-x-09) | Embedding giả lập tất định và chuẩn hóa | Thấp | Pass |

### E1 — Kho tài liệu

#### TC-101-01

**Upload 1 PDF hiển thị "Đang xử lý" ngay**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-101.1 · US-101 · UC-02 |
| Mức / loại | Integration |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); worker **không** chạy |
| Dữ liệu | TD-03 |
| Tự động | `cd backend && uv run pytest tests/test_documents_api.py::test_ac_101_1_upload_one_pdf_shows_processing_immediately` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | `POST /api/v1/documents` (multipart, field `files`) với TD-03 | 202; mảng 1 phần tử: `fileName`=`hop_dong.pdf`, `documentId` khác rỗng, `error`=null |
| 2 | `GET /api/v1/documents` | Có đúng `hop_dong.pdf`, `status`=`PROCESSING`, `id` = `documentId` ở bước 1 |

#### TC-101-02

**Trạng thái tự chuyển "Sẵn sàng truy vấn" không cần tải lại**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-101.2 · US-101 · UC-03 |
| Mức / loại | Integration + E2E |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`) |
| Dữ liệu | TD-02 |
| Tự động | Bước 1–3: `cd backend && uv run pytest tests/test_documents_api.py::test_ac_101_2_status_becomes_ready_after_processing`. Bước 4: thủ công |
| Kết quả gần nhất | **Một phần** — 2026-10-23, `163a7dd`. Bước 4 mới chạy thủ công một lần (T1.6, 2026-10-23), chưa có E2E tự động (T2.7) |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Upload TD-02 | 202, có `documentId` |
| 2 | Cho worker xử lý hết job (tự động: `process_all`; thủ công: `uv run python -m app.worker`) | Job được xử lý, không lỗi |
| 3 | `GET /api/v1/documents` | `bao_cao.pdf`: `status`=`READY`, `pageCount`=2 |
| 4 | **Thủ công trên UI:** mở http://localhost:5173, tải TD-02 lên, **không** bấm tải lại trang | Badge "Đang xử lý" tự đổi thành "Sẵn sàng truy vấn" (polling 2 giây khi còn tài liệu `PROCESSING`) |

#### TC-101-03

**Upload nhiều file: mỗi file có kết quả riêng**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-101.3 · US-101 · UC-02 A1 |
| Mức / loại | Integration |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`) |
| Dữ liệu | TD-04 (a.pdf, b.pdf), TD-05 |
| Tự động | `cd backend && uv run pytest tests/test_documents_api.py::test_ac_101_3_multiple_files_get_independent_results` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Một request `POST /api/v1/documents` chứa 3 file theo thứ tự a.pdf, ghi_chu.txt, b.pdf | 202; 3 kết quả, mỗi kết quả đúng `fileName` |
| 2 | Kiểm kết quả của a.pdf và b.pdf | Có `documentId`, `error`=null |
| 3 | Kiểm kết quả của ghi_chu.txt | `documentId`=null; `error`=`{code: NOT_A_PDF, message: "Chỉ hỗ trợ file PDF."}` |
| 4 | `GET /api/v1/documents` | Chỉ có a.pdf và b.pdf; file lỗi không chặn hai file còn lại |

#### TC-103-01

**PDF scan / có mật khẩu / hỏng → "Không dùng được" kèm lý do**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-103.1 · US-103 · UC-03 E1–E3 |
| Mức / loại | Integration |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`) |
| Dữ liệu | TD-07, TD-08, TD-09 (chạy riêng từng file) |
| Tự động | Bước 1–4: `cd backend && uv run pytest tests/test_ingestion.py::test_ac_103_1_unusable_documents_get_specific_reason` (3 tham số). Bước 5: thủ công |
| Kết quả gần nhất | **Một phần** — 2026-10-23, `163a7dd`. Bước 1–4 đạt. Bước 5 chưa chạy và chưa có test tự động (chuỗi lý do ở `frontend/src/i18n/vi.ts`) — T2.6, T2.7 |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Upload một file | 202, có `documentId` (file vẫn bắt đầu bằng `%PDF-`) |
| 2 | Cho worker xử lý | Không treo, job kết thúc |
| 3 | `GET /api/v1/documents` | `status`=`UNUSABLE`; `unusableReason` = `password` (TD-07) / `corrupt` (TD-08) / `scanned` (TD-09); `retryable`=false |
| 4 | Kiểm bảng `chunks` theo `document_id` | 0 bản ghi: không có nội dung nào được đưa vào truy xuất |
| 5 | **Thủ công trên UI:** xem danh sách tài liệu | Tên file + badge "Không dùng được" + "Lý do: …" đúng loại (vd. "PDF có mật khẩu — hãy mở khóa rồi tải lại") |

#### TC-103-02

**File không phải PDF bị từ chối theo nội dung, không theo đuôi**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-103.2 · US-103 · PRD I-1 |
| Mức / loại | Integration |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`) |
| Dữ liệu | TD-06 |
| Tự động | `cd backend && uv run pytest tests/test_documents_api.py::test_ac_103_2_png_renamed_to_pdf_is_rejected_by_content` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Upload TD-06 (đuôi `.pdf` nhưng nội dung PNG) | 202; kết quả `error.code`=`NOT_A_PDF`, `documentId`=null |
| 2 | `GET /api/v1/documents` | Danh sách rỗng: không tạo tài liệu |

#### TC-103-03

**Tài liệu không dùng được không bao giờ được trích dẫn**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-103.3 · US-103 · BR-003 |
| Mức / loại | Integration |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); TD-01 đã upload và worker xử lý xong (trạng thái `READY`) |
| Dữ liệu | TD-01, TD-11, Q-01 |
| Tự động | `cd backend && uv run pytest tests/test_qa_api.py::test_ac_103_3_unusable_document_is_never_cited` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Chuyển TD-01 sang `UNUSABLE(processing_failed)` (tự động: cập nhật CSDL; thủ công: dùng tài liệu bị lỗi xử lý thật) | TD-01 ở trạng thái `UNUSABLE` |
| 2 | Upload TD-11 và cho worker xử lý | TD-11 `READY` (để kho vẫn có tài liệu sẵn sàng) |
| 3 | Tạo cuộc trò chuyện: `POST /api/v1/conversations`, rồi hỏi Q-01 | Không trích dẫn nào có `documentName`=`hop_dong_A.pdf` |

#### TC-103-04

**Lỗi embedding khi xử lý → "Không dùng được", cho phép thử lại**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | PRD N-4 · US-103 · UC-04 · SAD §4.2 |
| Mức / loại | Integration |
| Ưu tiên | Trung bình |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); adapter embedding bị ép lỗi (tự động: monkeypatch `embed_passages`; chưa có cách bật bằng cấu hình) |
| Dữ liệu | TD-12 |
| Tự động | Bước 1–3: `cd backend && uv run pytest tests/test_ingestion.py::test_embedding_failure_leaves_no_chunks_and_is_retryable` |
| Kết quả gần nhất | **Một phần** — 2026-10-23, `163a7dd`. Bước 4 chờ T2.3 (endpoint retry) và T2.6 (UI) |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Upload TD-12, cho worker xử lý | Job kết thúc, không treo |
| 2 | `GET /api/v1/documents` | `status`=`UNUSABLE`, `unusableReason`=`processing_failed`, `retryable`=true |
| 3 | Kiểm bảng `chunks` | 0 bản ghi (không có trạng thái nửa vời) |
| 4 | `POST /api/v1/documents/{id}/retry`; nút "Thử lại" trên UI | **Chưa có** — T2.3, T2.6 |

#### TC-103-05

**Mỗi job xử lý đúng một lần; job hết hạn khóa được nhận lại**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | SAD §4.2 · SDD §3.7 · T1.3 |
| Mức / loại | Integration |
| Ưu tiên | Trung bình |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`) |
| Dữ liệu | TD-04 (a.pdf, b.pdf), TD-12 |
| Tự động | `cd backend && uv run pytest tests/test_ingestion.py -k "exactly_once or expired_lock"` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Upload a.pdf và b.pdf; gọi `process_next()` 3 lần | Lần 1, 2 trả `True`; lần 3 trả `False` (không xử lý lại) |
| 2 | Upload TD-12; nhận job với khóa 300 giây | Nhận được job |
| 3 | Nhận job lần nữa ngay sau đó | `None`: job đang bị khóa |
| 4 | Đặt `locked_until` của job về quá khứ (giả lập worker chết), rồi nhận job | Nhận lại **đúng job đó** (`job_id` trùng), `attempts`=2 |

#### TC-104-02

**Kho rỗng / chưa có tài liệu sẵn sàng: khóa ô hỏi và giải thích**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-104.2 · PRD E-1, E-2 |
| Mức / loại | Component + E2E |
| Ưu tiên | Trung bình |
| Điều kiện trước | Frontend test (jsdom) hoặc app chạy với CSDL trống |
| Dữ liệu | Danh sách tài liệu dựng trong test |
| Tự động | Bước 1–5: `cd frontend && npm test` (describe `blockedReason`, `Composer` › "khóa ô nhập…"). Bước 6: thủ công |
| Kết quả gần nhất | **Một phần** — 2026-10-23, `163a7dd`. Bước 6 chưa có E2E tự động |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Tính `blockedReason([])` | Chuỗi chứa "tải lên" |
| 2 | `blockedReason([PROCESSING])` | Chuỗi chứa "đang được xử lý" |
| 3 | `blockedReason([UNUSABLE])` | Chuỗi chứa "dùng được" |
| 4 | `blockedReason([UNUSABLE, READY])` | `null` (cho phép hỏi) |
| 5 | Render `Composer` với `blockedReason` = "Hãy tải lên ít nhất một tài liệu PDF để bắt đầu hỏi." | Ô "Câu hỏi của bạn" bị khóa; dòng giải thích hiển thị |
| 6 | **Thủ công:** mở app với kho trống | Thấy empty state "Tải lên file PDF để bắt đầu hỏi đáp…" kèm nút tải lên, không phải danh sách trắng |

#### TC-104-03

**Danh sách tài liệu luôn hiển thị cạnh khung chat**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-104.3 · PRD P-5 |
| Mức / loại | E2E (thủ công) |
| Ưu tiên | Trung bình |
| Điều kiện trước | API, worker, frontend chạy; cửa sổ trình duyệt ≥ 1024 px |
| Dữ liệu | TD-01, Q-01 |
| Tự động | Thủ công |
| Kết quả gần nhất | **Một phần** — 2026-10-23, `163a7dd`. Chạy thủ công lần cuối ngày 2026-10-23 (T1.6); cần E2E tự động |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Tải TD-01 lên, chờ "Sẵn sàng truy vấn" | Tài liệu ở cột trái |
| 2 | Hỏi Q-01 vài lần cho tới khi khung chat phải cuộn | Cột "Kho tài liệu" vẫn hiển thị cạnh khung chat, không bị đẩy đi |

#### TC-104-04

**Badge trạng thái có chữ, không chỉ dựa vào màu**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | UI_UX §9 · US-104 |
| Mức / loại | Component |
| Ưu tiên | Trung bình |
| Điều kiện trước | Frontend test (jsdom) |
| Dữ liệu | 3 trạng thái |
| Tự động | `cd frontend && npm test` (describe "StatusBadge (US-104)") |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Render `StatusBadge` với `READY` | Có chữ "Sẵn sàng truy vấn" |
| 2 | Render với `PROCESSING` | Có chữ "Đang xử lý" |
| 3 | Render với `UNUSABLE` | Có chữ "Không dùng được" |

### E2 — Hỏi đáp

#### TC-201-01

**Hỏi bằng ngôn ngữ tự nhiên nhận câu trả lời văn bản**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-201.1 · US-201 · UC-07 |
| Mức / loại | Integration |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); TD-01 đã upload và worker xử lý xong (trạng thái `READY`) |
| Dữ liệu | TD-01, Q-01 |
| Tự động | `cd backend && uv run pytest tests/test_qa_api.py::test_ac_201_1_and_203_1_answer_cites_document_name_and_page` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd`. LLM giả lập: chứng minh luồng, chưa chứng minh chất lượng (AC-201.3) |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Tạo cuộc trò chuyện: `POST /api/v1/conversations` | 201, trả `id` cuộc trò chuyện |
| 2 | `POST /api/v1/conversations/{id}/messages` với `{"text": Q-01}` | 200; `kind`=`ANSWER`; `text` chứa "thirty days" |

#### TC-201-02

**Nút Gửi khóa khi ô trống, khi đang chờ, khi quá dài**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-201.2 · PRD §4.1 #3 |
| Mức / loại | Component |
| Ưu tiên | Cao |
| Điều kiện trước | Frontend test (jsdom) |
| Dữ liệu | "hỏi" |
| Tự động | `cd frontend && npm test` (describe "Composer (US-201)") |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Render `Composer`, ô nhập trống | Nút "Gửi" bị khóa |
| 2 | Gõ "hỏi" | Nút "Gửi" bật |
| 3 | Render lại với `waiting`=true | Nút "Gửi" bị khóa (không gửi trùng khi đang chờ) |
| 4 | Gõ "Điều khoản thanh toán?" rồi Enter | `onSubmit` nhận đúng chuỗi; ô nhập được xóa |
| 5 | Gõ "a", Shift+Enter, "b" | Không gửi (xuống dòng) |

#### TC-201-04

**Câu hỏi rỗng bị chặn**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | PRD I-5 · US-201 |
| Mức / loại | Integration + Component |
| Ưu tiên | Trung bình |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); TD-01 đã upload và worker xử lý xong (trạng thái `READY`) |
| Dữ liệu | Q-03 |
| Tự động | `cd backend && uv run pytest tests/test_qa_api.py::test_invalid_question_returns_422` (tham số `QUESTION_EMPTY`) |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Tạo cuộc trò chuyện: `POST /api/v1/conversations`, rồi gửi Q-03 | 422; `error.code`=`QUESTION_EMPTY`; body theo mô hình lỗi chuẩn |
| 2 | UI: ô nhập trống | Nút "Gửi" bị khóa (TC-201-02 bước 1) |

#### TC-201-05

**Câu hỏi quá dài bị chặn, không cắt cụt im lặng**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | PRD I-6 · US-201 |
| Mức / loại | Integration + Component |
| Ưu tiên | Trung bình |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); TD-01 đã upload và worker xử lý xong (trạng thái `READY`) |
| Dữ liệu | Q-04 |
| Tự động | `cd backend && uv run pytest tests/test_qa_api.py::test_invalid_question_returns_422` (tham số `QUESTION_TOO_LONG`); `cd frontend && npm test` ("đánh dấu lỗi khi vượt giới hạn ký tự") |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd`. `details` đã kiểm tay ngày 2026-10-23 (trả `{actual: 1001, limit: 1000}`); test tự động chưa assert phần này, nên bổ sung |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Tạo cuộc trò chuyện: `POST /api/v1/conversations`, rồi gửi Q-04 | 422; `error.code`=`QUESTION_TOO_LONG`; `details` = `{actual: 1001, limit: 1000}` |
| 2 | UI: dán 1001 ký tự vào ô nhập | Ô có `aria-invalid="true"`; nút "Gửi" bị khóa |

#### TC-201-06

**Chưa có tài liệu sẵn sàng: không cho hỏi**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | PRD E-2 · PQ-04 (theo đề xuất "không") |
| Mức / loại | Integration |
| Ưu tiên | Trung bình |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); kho trống |
| Dữ liệu | "Anything?" |
| Tự động | `cd backend && uv run pytest tests/test_qa_api.py::test_no_ready_documents_returns_409` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd`. Hành vi theo đề xuất của PRD; PO chưa chốt PQ-04 |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Tạo cuộc trò chuyện: `POST /api/v1/conversations`, rồi gửi "Anything?" | 409; `error.code`=`NO_READY_DOCUMENTS` |
| 2 | UI | Ô nhập bị khóa kèm lý do (TC-104-02) |

#### TC-201-08

**Hỏi trong cuộc trò chuyện không tồn tại**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | SDD §3.6 |
| Mức / loại | Integration |
| Ưu tiên | Thấp |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`) |
| Dữ liệu | — |
| Tự động | `cd backend && uv run pytest tests/test_qa_api.py::test_unknown_conversation_returns_404` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | `POST /api/v1/conversations/does-not-exist/messages` với `{"text": "hi"}` | 404; `error.code`=`NOT_FOUND_RESOURCE` |

#### TC-202-01

**Câu hỏi kiến thức chung → "không tìm thấy", không gọi LLM**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-202.1 · US-202 · SDD §3.8 cổng 1 |
| Mức / loại | Integration |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); TD-01 đã upload và worker xử lý xong (trạng thái `READY`) |
| Dữ liệu | TD-01, Q-02 |
| Tự động | Bước 1–3: `cd backend && uv run pytest tests/test_qa_api.py::test_ac_204_1_out_of_scope_question_is_not_found_without_calling_llm` |
| Kết quả gần nhất | **Một phần** — 2026-10-23, `163a7dd`. Embedding giả lập dựa trên trùng từ nên ca này dễ đạt hơn thực tế (RT-06) |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Ghi lại số lần LLM đã được gọi | — |
| 2 | Tạo cuộc trò chuyện: `POST /api/v1/conversations`, rồi hỏi Q-02 | 200 (không phải lỗi); `kind`=`NOT_FOUND`; `text`=null; `citations`=[] |
| 3 | So số lần gọi LLM | Không đổi: cổng 1 chặn trước khi gọi LLM |
| 4 | Lặp lại với LLM thật và câu hỏi ép trả lời ngoài kho | **Chưa chạy** — T3.3, OQ-009 |

#### TC-203-01

**Câu trả lời luôn kèm tên tài liệu + số trang**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-203.1 · US-203 · BR-008 · SDD D-06 |
| Mức / loại | Integration + Component |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); TD-01 đã upload và worker xử lý xong (trạng thái `READY`) |
| Dữ liệu | TD-01, Q-01 |
| Tự động | `cd backend && uv run pytest tests/test_qa_api.py::test_ac_201_1_and_203_1_answer_cites_document_name_and_page`; `cd frontend && npm test` ("câu trả lời luôn hiển thị tên tài liệu và số trang") |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Tạo cuộc trò chuyện: `POST /api/v1/conversations`, rồi hỏi Q-01 | 200; `kind`=`ANSWER` |
| 2 | Kiểm `citations` | Đúng 1 phần tử: `documentName`=`hop_dong_A.pdf`, `page`=3, `documentDeleted`=false, `documentId` khác rỗng |
| 3 | UI: render `AnswerMessage` có trích dẫn `hop_dong_A.pdf`, trang 7 | Hiển thị chip "hop_dong_A.pdf, tr.7" |

#### TC-203-02

**LLM trích bằng chứng không tồn tại → bỏ, thành "không tìm thấy"**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | SDD D-06 · §3.8 cổng 3 |
| Mức / loại | Integration |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); TD-01 đã upload và worker xử lý xong (trạng thái `READY`); `CWD_LLM_FAKE_MODE=cite_unknown_evidence` |
| Dữ liệu | TD-01, Q-01 |
| Tự động | `cd backend && uv run pytest tests/test_qa_api.py::test_citation_to_unknown_evidence_is_dropped_and_becomes_not_found` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Tạo cuộc trò chuyện: `POST /api/v1/conversations`, rồi hỏi Q-01 | 200; `kind`=`NOT_FOUND`: không hiển thị nhận định có trích dẫn giả |

#### TC-203-03

**Mỗi đoạn văn bản thuộc đúng một trang**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | BR-008 · SDD A1 · T1.3 |
| Mức / loại | Unit + Integration |
| Ưu tiên | Cao |
| Điều kiện trước | Unit: không cần môi trường. Integration: API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); tham số chia đoạn 20 từ, chồng 2 từ |
| Dữ liệu | Unit: 3 trang (25 từ, trống, 5 từ); TD-10 |
| Tự động | `cd backend && uv run pytest tests/test_units.py -k chunker`; `cd backend && uv run pytest tests/test_ingestion.py::test_text_pdf_ready_and_every_chunk_belongs_to_exactly_one_page` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Unit: `chunk_pages` 3 trang, `max_words`=10, `overlap_words`=2 | Trang của các đoạn = [1, 1, 1, 3] (bỏ trang trống); 2 từ cuối đoạn 1 = 2 từ đầu đoạn 2; `ordinal` = [0, 1, 2, 3] |
| 2 | Unit: `max_words`=5, `overlap_words`=5 | `ValueError` nêu `max_words` |
| 3 | Integration: upload TD-10, cho worker xử lý | `READY`, `pageCount`=10 |
| 4 | Kiểm mọi bản ghi `chunks` | > 10 đoạn; mỗi đoạn có 1 ≤ `page` ≤ 10 và **chỉ** chứa từ `page{page}word*` |

#### TC-204-01

**Ngoài kho: "không tìm thấy" (HTTP 200), hiển thị khác lỗi hệ thống**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-204.1 · US-204 · UC-10 |
| Mức / loại | Integration + Component |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); TD-01 đã upload và worker xử lý xong (trạng thái `READY`) |
| Dữ liệu | TD-01, Q-02 |
| Tự động | `cd backend && uv run pytest tests/test_qa_api.py::test_ac_204_1_out_of_scope_question_is_not_found_without_calling_llm`; `cd frontend && npm test` ("không tìm thấy và lỗi hệ thống có thông điệp khác nhau") |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Tạo cuộc trò chuyện: `POST /api/v1/conversations`, rồi hỏi Q-02 | 200; `kind`=`NOT_FOUND`; không có nội dung suy đoán (`text`=null) |
| 2 | UI: render `NotFoundMessage` và `ErrorMessage` cạnh nhau | "Không tìm thấy thông tin này…" là thông báo thường; lỗi có `role="alert"` với chữ "không phải kết quả" |
| 3 | Bấm "Gửi lại" ở thông báo lỗi | Gọi `onRetry` |

#### TC-204-02

**LLM báo không đủ bằng chứng → "không tìm thấy"**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | SDD §3.8 cổng 2 · US-204 |
| Mức / loại | Unit |
| Ưu tiên | Cao |
| Điều kiện trước | Không cần môi trường (stub repository, retrieval, LLM) |
| Dữ liệu | 1 evidence điểm 0.9 (> ngưỡng 0.2) |
| Tự động | `cd backend && uv run pytest tests/test_units.py::test_gate_2_insufficient_evidence_is_not_found` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | `QaService.ask` với LLM stub trả `INSUFFICIENT_EVIDENCE` | Kết quả `NOT_FOUND` |

#### TC-204-04

**"Không tìm thấy" kèm gợi ý hành động**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | AC-204.3 |
| Mức / loại | E2E (thủ công) |
| Ưu tiên | Trung bình |
| Điều kiện trước | App chạy; TD-01 `READY` |
| Dữ liệu | Q-02 |
| Tự động | Thủ công |
| Kết quả gần nhất | **Một phần** — 2026-10-23, `163a7dd`. Chuỗi gợi ý đã có (`vi.notFoundBody`) nhưng chưa có assertion tự động |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Hỏi Q-02 trên UI | Thông báo "Không tìm thấy thông tin này trong các tài liệu hiện có." |
| 2 | Đọc phần dưới thông báo | Có gợi ý "Bạn có thể diễn đạt lại câu hỏi hoặc kiểm tra danh sách tài liệu ở bên trái…" |
| 3 | Kiểm danh sách tài liệu | Đang hiển thị ở cột trái, xem được ngay |

#### TC-204-05

**Lỗi dịch vụ AI là lỗi 5xx, không bao giờ là "không tìm thấy"**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | PRD N-3 · SDD §3.7 · US-204, US-208 |
| Mức / loại | Integration |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); TD-01 đã upload và worker xử lý xong (trạng thái `READY`); `CWD_LLM_FAKE_MODE` = `timeout` / `quota` / `unavailable` (chạy riêng từng giá trị) |
| Dữ liệu | TD-01, Q-01 |
| Tự động | `cd backend && uv run pytest tests/test_qa_api.py::test_ai_failure_is_an_error_never_not_found` (3 tham số) |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Tạo cuộc trò chuyện: `POST /api/v1/conversations`, rồi hỏi Q-01 | `timeout` → 504 `AI_TIMEOUT`; `quota` → 503 `AI_QUOTA`; `unavailable` → 503 `AI_UNAVAILABLE` |
| 2 | Kiểm body lỗi | Theo mô hình lỗi chuẩn, `correlationId` khác rỗng; **không** phải 200 `NOT_FOUND` |

### Xuyên suốt

#### TC-X-01

**Mọi lỗi dùng mô hình chuẩn kèm correlationId**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | SDD §3.6 · AGENTS.md |
| Mức / loại | Integration |
| Ưu tiên | Cao |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`) |
| Dữ liệu | Các request sai |
| Tự động | `cd backend && uv run pytest tests/test_units.py -k "correlation_id or framework_errors"` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | `POST /api/v1/conversations/x/messages` với body `{}` | 422 `VALIDATION_ERROR`; `correlationId` = header `X-Correlation-Id` |
| 2 | Gửi JSON có byte không hợp lệ (`\xff\xfe`) | 400 `BAD_REQUEST`, có `correlationId` |
| 3 | `GET /api/v1/khong-ton-tai` | 404 `NOT_FOUND_RESOURCE`, có `correlationId` |
| 4 | `DELETE /api/v1/conversations` | 405 `METHOD_NOT_ALLOWED`, có `correlationId` |

#### TC-X-02

**Mọi operation trong openapi.yaml đều có hiện thực**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | T0.2 |
| Mức / loại | Contract |
| Ưu tiên | Trung bình |
| Điều kiện trước | Không cần dữ liệu |
| Dữ liệu | `docs/04-design/api/openapi.yaml` |
| Tự động | `cd backend && uv run pytest tests/test_units.py::test_implementation_covers_every_operation_in_design_openapi` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | So `paths` của thiết kế với `/openapi.json` của app | Danh sách thiếu rỗng (5/5 operation) |

#### TC-X-03

**Kiểu TypeScript sinh từ OpenAPI không lệch**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | T0.2 |
| Mức / loại | Contract |
| Ưu tiên | Trung bình |
| Điều kiện trước | Repo sạch |
| Dữ liệu | — |
| Tự động | `cd frontend && npm run gen:api && git diff --exit-code src/api/schema.d.ts` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | `npm run gen:api` | Sinh lại `src/api/schema.d.ts` |
| 2 | `git diff --exit-code src/api/schema.d.ts` | Exit code 0 (không có thay đổi) |

#### TC-X-04

**Quy tắc phụ thuộc giữa các lớp**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | SDD §3.3 · AGENTS.md |
| Mức / loại | Kiến trúc |
| Ưu tiên | Cao |
| Điều kiện trước | — |
| Dữ liệu | — |
| Tự động | `cd backend && uv run lint-imports` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | `uv run lint-imports` | 3 contract KEPT, 0 broken (module nghiệp vụ không import adapter, API, DB, framework) |

#### TC-X-05

**Ghi CSDL lỗi thì không để tệp mồ côi**

| Thuộc tính | Giá trị |
|---|---|
| Truy vết | T1.2 |
| Mức / loại | Integration |
| Ưu tiên | Trung bình |
| Điều kiện trước | API chạy với CSDL và thư mục tệp trống; adapter giả lập (`CWD_LLM_ADAPTER=fake`, `CWD_EMBEDDING_ADAPTER=fake`); ép `add_with_job` ném lỗi (monkeypatch) |
| Dữ liệu | TD-12 |
| Tự động | `cd backend && uv run pytest tests/test_documents_api.py::test_no_orphan_file_when_database_write_fails` |
| Kết quả gần nhất | **Pass** — 2026-10-23, `163a7dd` |

| # | Bước | Kết quả mong đợi |
|---|---|---|
| 1 | Upload TD-12 | 500 `INTERNAL_ERROR` theo mô hình lỗi chuẩn |
| 2 | Liệt kê thư mục kho tệp | Rỗng: tệp đã ghi được xóa lại |

#### TC-X-06

**Health và readiness**

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

#### TC-X-07

**Không có lỗ hổng phụ thuộc đã biết**

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

#### TC-X-09

**Embedding giả lập tất định và chuẩn hóa**

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

## 4. Ca kiểm thử khung (chưa chạy)

Kịch bản và kết quả mong đợi ở [Master_Test_Plan.md §4.3](Master_Test_Plan.md). Viết bước chi tiết khi task tương ứng bắt đầu (TDD: viết ca trước khi code).

| Mã | Tiêu đề | Nhóm | Truy vết | Trạng thái | Đang chờ |
|---|---|---|---|---|---|
| TC-101-04 | 3 nhân viên BD upload 15 PDF không cần hỗ trợ | E1 | AC-101.4 | Chưa có | T5.5 (UAT) |
| TC-101-05 | Mất mạng khi đang upload | E1 | PRD N-1 | Chưa có | T2.6 |
| TC-101-06 | Upload trùng nội dung | E1 | PRD I-4 | Bị chặn | PQ-03, T2.5 |
| TC-102-01 | Kho ở dung lượng tối đa vẫn trích đúng tài liệu | E1 | AC-102.1 | Bị chặn | OQ-004, T5.1 |
| TC-102-02 | File vượt kích thước/số trang bị từ chối trước khi xử lý | E1 | AC-102.2 | Chưa có | T2.1 (giá trị tạm OQ-004) |
| TC-102-03 | Kho đầy | E1 | AC-102.3 | Chưa có | T2.1 |
| TC-104-01 | 5 tài liệu, 1 lỗi: đúng 4 sẵn sàng, 1 không dùng được | E1 | AC-104.1 | Chưa có | T2.7 |
| TC-105-01 | Xóa tài liệu X → 3 câu hỏi về X đều "không tìm thấy" | E1 | AC-005 | Chưa có | T2.4, T2.7 |
| TC-105-02 | Xóa trong một giao dịch | E1 | US-105 | Chưa có | T2.4 |
| TC-105-03 | Hộp thoại xác nhận xóa | E1 | PRD §4.1 #8 | Chưa có | T2.6 |
| TC-201-03 | Tỷ lệ đúng nhóm "một tài liệu" | E2 | AC-201.3 | Bị chặn | OQ-002, T0.8, T1.8 |
| TC-201-07 | Mất mạng khi chờ câu trả lời | E2 | PRD N-2 | Chưa có | T3.8 |
| TC-202-02 | SME rà nhận định không có căn cứ | E2 | AC-202.2 | Bị chặn | OQ-002, T3.10 |
| TC-202-03 | Prompt injection qua câu hỏi và nội dung PDF | E2 | PRD I-7, G-11 | Chưa có | T3.3, T5.2 |
| TC-203-04 | % trích dẫn đúng trang trên bộ câu hỏi chuẩn | E2 | AC-203.2 | Bị chặn | OQ-002, T1.8 |
| TC-203-05 | Trích dẫn đứng cạnh nhận định | E2 | AC-203.3 | Chưa có | T3.8 |
| TC-203-06 | Không xác định được trang | E2 | PRD C-2 | Bị chặn | PQ-05 |
| TC-204-03 | MET-005 trên ≥ 10 câu ngoài kho | E2 | AC-204.2 | Bị chặn | OQ-002, T1.8 |
| TC-204-06 | Timeout cứng, retry, circuit breaker cho AI | E2 | SAD §4.2 | Chưa có | T3.4 |
| TC-205-01 | Bấm trích dẫn mở đúng trang | E2 | US-205 | Bị chặn | PQ-01, T3.8, T3.9 |
| TC-206-01 | Tổng hợp từ nhiều tài liệu, trích dẫn đủ | E2 | AC-206.1/.2 | Bị chặn | OQ-002, T3.1, T3.10 |
| TC-206-02 | Hai tài liệu mâu thuẫn | E2 | AC-206.3 | Bị chặn | PQ-02, T3.3 |
| TC-207-01 | Hỏi tiếp nối, cuộc trò chuyện mới | E2 | AC-011 | Chưa có | T3.5 |
| TC-208-01 | Thời gian phản hồi | E2 | AC-208.1 | Bị chặn | OQ-004, OQ-006, T5.1 |
| TC-208-02 | Chờ lâu: thông báo + Hủy | E2 | AC-208.2, PRD N-3 | Chưa có | T3.8 |
| TC-209-01 | Trả lời đúng ngôn ngữ câu hỏi | E2 | AC-209.1/.2 | Bị chặn | OQ-007, T3.6 |
| TC-301-01 | Chưa đăng nhập/không có quyền: 10/10 bị từ chối | E3 | AC-301.1 | Bị chặn | OQ-008, T4.1, T4.2 |
| TC-301-02 | Có quyền: 10/10 truy cập được | E3 | AC-301.2 | Bị chặn | OQ-008, T4.1 |
| TC-301-03 | Hết phiên giữ câu hỏi đang nhập | E3 | AC-301.3 | Bị chặn | OQ-008, T4.1 |
| TC-301-04 | Vai trò BD gọi /stats → 403 | E3 | SAD STRIDE | Chưa có | T4.2 |
| TC-302-01 | Cấu hình khớp văn bản phê duyệt | E3 | AC-302.1 | Bị chặn | OQ-009, T4.3 |
| TC-302-02 | Chỉ gọi ra tên miền được phép | E3 | AC-302.2 | Bị chặn | OQ-009, T4.3 |
| TC-302-03 | Chuỗi đánh dấu không xuất hiện trong log/analytics/stack trace | E3 | G-10 | Chưa có | T4.3 (xem L1-04) |
| TC-401-01 | Đánh giá 10 câu trả lời | E4 | AC-016 | Chưa có | T4.5 |
| TC-402-01 | Thống kê tuần khớp 100% | E4 | AC-017 | Chưa có | T4.7 |
| TC-402-02 | Sự kiện analytics đủ thuộc tính, không có nội dung | E4 | PRD §5.2, G-14 | Chưa có | T4.6 |
| TC-X-08 | Quét secret (gitleaks) | X | Phase 7 L0 | Chưa có | Xem log GitHub Actions |

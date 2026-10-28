# Test Case Specification — "Chat với tài liệu" (MVP)

> **Chuẩn:** IEEE 829-2008, Test Case Specification · **Kế hoạch:** [Master_Test_Plan.md](Master_Test_Plan.md) §4.3 (mã TC-* giữ nguyên) · **Bản thực thi:** [Test_Cases.xlsx](Test_Cases.xlsx) (cùng nội dung, có cột ghi kết quả từng lần chạy)
> **Dành cho:** QA, Dev, Reviewer, agent kiểm thử. Từ 2026-10-28 **mỗi ca kiểm thử là một file** trong [test-cases/](test-cases/README.md) (bản chuẩn); file này là **mục lục + dữ liệu kiểm thử chung**. Khi sửa ca, sửa file ca rồi cập nhật bản Excel.
> **Ứng dụng kiểm thử:** http://localhost:5173 — mỗi file ca có phần *Nhiệm vụ của agent*: thực thi, thu bằng chứng (ảnh, video, network, log) và viết báo cáo vào `test-runs/`.

| Mục | Giá trị |
|---|---|
| Mã / Version | TCS-CWD-001 / 0.1 — Draft |
| Ngày | 2026-10-23 |
| Phạm vi | 33 ca **chi tiết** (đã chạy ở lát cắt 1: 26 đạt, 7 một phần) + 37 ca **khung** (chờ task hoặc OQ/PQ) = 70 ca |
| Lần chạy gần nhất | 2026-10-23, commit `163a7dd`, Agent (L0) — xem [Test_Report_Slice1.md](Test_Report_Slice1.md) |

## 1. Cách đọc và cách chạy

- Mỗi file ca có: truy vết, mức kiểm thử, ưu tiên, **điều kiện trước**, **dữ liệu** (mã ở §2), **các bước** kèm kết quả mong đợi, cách chạy tự động, kết quả lần chạy gần nhất, và **nhiệm vụ của agent** (bước tại http://localhost:5173, bằng chứng bắt buộc, báo cáo). Quy trình chung: [test-cases/README.md](test-cases/README.md).
- Bước ghi **Thủ công** là phần chưa có test tự động; tester làm trên trình duyệt (`npm run dev` + API + worker theo `AGENTS.md`).
- Ca mức Integration chạy được bằng tay qua API (Swagger UI tại `http://localhost:8000/docs`) theo đúng các bước; bản tự động dùng CSDL và thư mục tệp riêng cho từng test.
- Chạy toàn bộ: `cd backend && uv run pytest` và `cd frontend && npm test`. Trên Windows đặt `PYTHONIOENCODING=utf-8`.
- Chế độ lỗi của LLM giả lập bật bằng `CWD_LLM_FAKE_MODE` (`timeout`, `quota`, `unavailable`, `invalid_output`, `cite_unknown_evidence`).
- Trạng thái: **Pass** · **Một phần** (phần tự động đạt, còn bước chưa chạy) · **Chưa có** (chờ task) · **Bị chặn** (chờ OQ/PQ).

## 2. Dữ liệu kiểm thử

Toàn bộ là dữ liệu tổng hợp, không nhạy cảm (BR-015). Sinh thành file để test trên giao diện: `cd backend && uv run python -m tests.make_test_data <thư-mục>` (mỗi mã TD một thư mục con, vd. `TD-02/bao_cao.pdf`; thêm `TD-07b/hop_dong_A_khoa.pdf` = TD-01 có mật khẩu, dùng cho TC-103-03 trên giao diện). PDF sinh bằng `backend/tests/pdfs.py`; văn bản không dấu vì font chuẩn của reportlab, để chạy giống nhau trên mọi máy CI.

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

## 3. Ca kiểm thử chi tiết (33 ca — thực thi được)

Cột *Thực thi*: cách agent chạy ca tại http://localhost:5173 ([test-cases/README.md §5](test-cases/README.md#5-chế-độ-thực-thi-theo-ca)).

| Mã | Tiêu đề | Nhóm | Thực thi tại http://localhost:5173 | Kết quả gần nhất |
|---|---|---|---|---|
| [TC-101-01](test-cases/TC-101-01.md) | Upload 1 PDF hiển thị "Đang xử lý" ngay | E1 — Kho tài liệu | Giao diện + API | Pass |
| [TC-101-02](test-cases/TC-101-02.md) | Trạng thái tự chuyển "Sẵn sàng truy vấn" không cần tải lại | E1 — Kho tài liệu | Giao diện + API | Pass ([báo cáo](test-runs/2026-10-28_TC-101-02/report.md)) |
| [TC-101-03](test-cases/TC-101-03.md) | Upload nhiều file: mỗi file có kết quả riêng | E1 — Kho tài liệu | Giao diện + API | Pass |
| [TC-103-01](test-cases/TC-103-01.md) | PDF scan / có mật khẩu / hỏng → "Không dùng được" kèm lý do | E1 — Kho tài liệu | Giao diện + API | Một phần |
| [TC-103-02](test-cases/TC-103-02.md) | File không phải PDF bị từ chối theo nội dung, không theo đuôi | E1 — Kho tài liệu | Giao diện + API | Pass |
| [TC-103-03](test-cases/TC-103-03.md) | Tài liệu không dùng được không bao giờ được trích dẫn | E1 — Kho tài liệu | Giao diện + API | Pass |
| [TC-103-04](test-cases/TC-103-04.md) | Lỗi embedding khi xử lý → "Không dùng được", cho phép thử lại | E1 — Kho tài liệu | Lệnh / unit test | Một phần |
| [TC-103-05](test-cases/TC-103-05.md) | Mỗi job xử lý đúng một lần; job hết hạn khóa được nhận lại | E1 — Kho tài liệu | Lệnh / unit test | Pass |
| [TC-104-02](test-cases/TC-104-02.md) | Kho rỗng / chưa có tài liệu sẵn sàng: khóa ô hỏi và giải thích | E1 — Kho tài liệu | Giao diện + API | Một phần |
| [TC-104-03](test-cases/TC-104-03.md) | Danh sách tài liệu luôn hiển thị cạnh khung chat | E1 — Kho tài liệu | Giao diện + API | Một phần |
| [TC-104-04](test-cases/TC-104-04.md) | Badge trạng thái có chữ, không chỉ dựa vào màu | E1 — Kho tài liệu | Giao diện + API | Pass |
| [TC-201-01](test-cases/TC-201-01.md) | Hỏi bằng ngôn ngữ tự nhiên nhận câu trả lời văn bản | E2 — Hỏi đáp | Giao diện + API | Pass |
| [TC-201-02](test-cases/TC-201-02.md) | Nút Gửi khóa khi ô trống, khi đang chờ, khi quá dài | E2 — Hỏi đáp | Giao diện + API | Pass |
| [TC-201-04](test-cases/TC-201-04.md) | Câu hỏi rỗng bị chặn | E2 — Hỏi đáp | Giao diện + API | Pass |
| [TC-201-05](test-cases/TC-201-05.md) | Câu hỏi quá dài bị chặn, không cắt cụt im lặng | E2 — Hỏi đáp | Giao diện + API | Pass |
| [TC-201-06](test-cases/TC-201-06.md) | Chưa có tài liệu sẵn sàng: không cho hỏi | E2 — Hỏi đáp | Giao diện + API | Pass |
| [TC-201-08](test-cases/TC-201-08.md) | Hỏi trong cuộc trò chuyện không tồn tại | E2 — Hỏi đáp | API | Pass |
| [TC-202-01](test-cases/TC-202-01.md) | Câu hỏi kiến thức chung → "không tìm thấy", không gọi LLM | E2 — Hỏi đáp | Giao diện + API | Một phần |
| [TC-203-01](test-cases/TC-203-01.md) | Câu trả lời luôn kèm tên tài liệu + số trang | E2 — Hỏi đáp | Giao diện + API | Pass |
| [TC-203-02](test-cases/TC-203-02.md) | LLM trích bằng chứng không tồn tại → bỏ, thành "không tìm thấy" | E2 — Hỏi đáp | Giao diện + API | Pass |
| [TC-203-03](test-cases/TC-203-03.md) | Mỗi đoạn văn bản thuộc đúng một trang | E2 — Hỏi đáp | Lệnh / unit test | Pass |
| [TC-204-01](test-cases/TC-204-01.md) | Ngoài kho: "không tìm thấy" (HTTP 200), hiển thị khác lỗi hệ thống | E2 — Hỏi đáp | Giao diện + API | Pass |
| [TC-204-02](test-cases/TC-204-02.md) | LLM báo không đủ bằng chứng → "không tìm thấy" | E2 — Hỏi đáp | Lệnh / unit test | Pass |
| [TC-204-04](test-cases/TC-204-04.md) | "Không tìm thấy" kèm gợi ý hành động | E2 — Hỏi đáp | Giao diện + API | Một phần |
| [TC-204-05](test-cases/TC-204-05.md) | Lỗi dịch vụ AI là lỗi 5xx, không bao giờ là "không tìm thấy" | E2 — Hỏi đáp | Giao diện + API | Pass |
| [TC-X-01](test-cases/TC-X-01.md) | Mọi lỗi dùng mô hình chuẩn kèm correlationId | Xuyên suốt | API | Pass |
| [TC-X-02](test-cases/TC-X-02.md) | Mọi operation trong openapi.yaml đều có hiện thực | Xuyên suốt | Lệnh / unit test | Pass |
| [TC-X-03](test-cases/TC-X-03.md) | Kiểu TypeScript sinh từ OpenAPI không lệch | Xuyên suốt | Lệnh / unit test | Pass |
| [TC-X-04](test-cases/TC-X-04.md) | Quy tắc phụ thuộc giữa các lớp | Xuyên suốt | Lệnh / unit test | Pass |
| [TC-X-05](test-cases/TC-X-05.md) | Ghi CSDL lỗi thì không để tệp mồ côi | Xuyên suốt | Lệnh / unit test | Pass |
| [TC-X-06](test-cases/TC-X-06.md) | Health và readiness | Xuyên suốt | API | Pass |
| [TC-X-07](test-cases/TC-X-07.md) | Không có lỗ hổng phụ thuộc đã biết | Xuyên suốt | Lệnh / unit test | Pass |
| [TC-X-09](test-cases/TC-X-09.md) | Embedding giả lập tất định và chuẩn hóa | Xuyên suốt | Lệnh / unit test | Pass |

## 4. Ca kiểm thử khung (37 ca — chưa thực thi)

Kịch bản và kết quả mong đợi ở từng file và [Master_Test_Plan.md §4.3](Master_Test_Plan.md). Viết bước chi tiết khi task tương ứng bắt đầu (TDD: viết ca trước khi code).

| Mã | Kịch bản | Nhóm | Trạng thái | Đang chờ |
|---|---|---|---|---|
| [TC-101-04](test-cases/TC-101-04.md) | 3 nhân viên BD, mỗi người 5 PDF mẫu | E1 | ⏳ | T5.5 (UAT) |
| [TC-101-05](test-cases/TC-101-05.md) | Mất mạng khi đang upload | E1 | ⏳ | T2.6 |
| [TC-101-06](test-cases/TC-101-06.md) | Upload trùng nội dung | E1 | ⛔ PQ-03 | T2.5 |
| [TC-102-01](test-cases/TC-102-01.md) | Kho ở dung lượng tối đa, hỏi câu có đáp án ở tài liệu X | E1 | ⛔ OQ-004 | T5.1 |
| [TC-102-02](test-cases/TC-102-02.md) | File vượt kích thước/số trang | E1 | ⏳ (giá trị tạm của OQ-004) | T2.1 |
| [TC-102-03](test-cases/TC-102-03.md) | Kho đầy, upload thêm | E1 | ⏳ | T2.1 |
| [TC-104-01](test-cases/TC-104-01.md) | 5 tài liệu, 1 lỗi | E1 | ⏳ | T2.7 |
| [TC-105-01](test-cases/TC-105-01.md) | Xóa tài liệu X, hỏi 3 câu chỉ có trong X | E1 | ⏳ | T2.4, T2.7 |
| [TC-105-02](test-cases/TC-105-02.md) | Lỗi giữa chừng khi xóa | E1 | ⏳ | T2.4 |
| [TC-105-03](test-cases/TC-105-03.md) | Bấm xóa | E1 | ⏳ | T2.6 |
| [TC-201-03](test-cases/TC-201-03.md) | Bộ câu hỏi chuẩn nhóm "một tài liệu" | E2 | ⛔ OQ-002, DEP-002 | T1.8, T0.8 |
| [TC-201-07](test-cases/TC-201-07.md) | Mất mạng khi chờ | E2 | ⏳ | T3.8 |
| [TC-202-02](test-cases/TC-202-02.md) | SME rà mọi nhận định trong bộ câu hỏi chuẩn | E2 | ⛔ OQ-002 | T3.10 |
| [TC-202-03](test-cases/TC-202-03.md) | Câu hỏi/PDF chứa chỉ dẫn "bỏ qua tài liệu…" | E2 | ⏳ | T3.3 (bộ đầu), T5.2 (≥ 30 ca) |
| [TC-203-04](test-cases/TC-203-04.md) | Bộ câu hỏi chuẩn | E2 | ⛔ OQ-002 | T1.8 |
| [TC-203-05](test-cases/TC-203-05.md) | Nhận định có trích dẫn riêng | E2 | ⏳ | T3.8 |
| [TC-203-06](test-cases/TC-203-06.md) | Không xác định được trang | E2 | ⛔ PQ-05 | — |
| [TC-204-03](test-cases/TC-204-03.md) | ≥ 10 câu ngoài kho trong bộ chuẩn | E2 | ⛔ OQ-002 | T1.8 |
| [TC-204-06](test-cases/TC-204-06.md) | Lỗi AI tạm thời | E2 | ⏳ | T3.4 |
| [TC-205-01](test-cases/TC-205-01.md) | Bấm trích dẫn | E2 | ⛔ PQ-01 | T3.8, T3.9 |
| [TC-206-01](test-cases/TC-206-01.md) | Câu hỏi cần ≥ 2 tài liệu | E2 | ⛔ OQ-002 | T3.1, T3.10 |
| [TC-206-02](test-cases/TC-206-02.md) | Hai tài liệu mâu thuẫn | E2 | ⛔ PQ-02 | T3.3 |
| [TC-207-01](test-cases/TC-207-01.md) | 5 chuỗi hội thoại kịch bản | E2 | ⏳ | T3.5 |
| [TC-208-01](test-cases/TC-208-01.md) | Kho tối đa, chạy bộ câu hỏi chuẩn | E2 | ⛔ OQ-004, OQ-006 | T5.1 |
| [TC-208-02](test-cases/TC-208-02.md) | Chờ quá ngưỡng | E2 | ⏳ | T3.8 |
| [TC-209-01](test-cases/TC-209-01.md) | Hỏi theo từng ngôn ngữ được chốt | E2 | ⛔ OQ-007 | T3.6 |
| [TC-301-01](test-cases/TC-301-01.md) | Chưa đăng nhập / không có quyền, gọi **mọi** route | E3 | ⛔ OQ-008 (hiện dùng user dev cố định) | T4.1, T4.2 |
| [TC-301-02](test-cases/TC-301-02.md) | Tài khoản có quyền | E3 | ⛔ OQ-008 | T4.1 |
| [TC-301-03](test-cases/TC-301-03.md) | Phiên hết hạn khi đang gõ | E3 | ⛔ OQ-008 | T4.1 |
| [TC-301-04](test-cases/TC-301-04.md) | Vai trò BD gọi `/stats/*` | E3 | ⏳ | T4.2 |
| [TC-302-01](test-cases/TC-302-01.md) | Rà cấu hình triển khai | E3 | ⛔ OQ-009 | T4.3, T5.8 |
| [TC-302-02](test-cases/TC-302-02.md) | Ứng dụng gọi ra ngoài | E3 | ⛔ OQ-009 | T4.3 |
| [TC-302-03](test-cases/TC-302-03.md) | Upload/hỏi với **chuỗi đánh dấu** duy nhất, quét log + analytics + stack trace | E3 | ⏳ (hiện chỉ kiểm bằng review code) | T4.3 |
| [TC-401-01](test-cases/TC-401-01.md) | Đánh giá 10 câu trả lời | E4 | ⏳ | T4.5 |
| [TC-402-01](test-cases/TC-402-01.md) | Tuần thử nghiệm có kịch bản | E4 | ⏳ | T4.7 |
| [TC-402-02](test-cases/TC-402-02.md) | Sinh từng sự kiện analytics | E4 | ⏳ | T4.6 |
| [TC-X-08](test-cases/TC-X-08.md) | Quét secret | Xuyên suốt | ⏳ (chỉ chạy được trên GitHub) | gitleaks trong CI |

## 5. Báo cáo thực thi

Mỗi lần thực thi một ca: `test-runs/<YYYY-MM-DD>_<TC>/report.md` theo [mẫu](test-cases/TEST_REPORT_TEMPLATE.md), kèm `screenshots/`, `video/`, `network/`, `logs/`.

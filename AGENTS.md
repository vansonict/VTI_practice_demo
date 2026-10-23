# AGENTS.md — hướng dẫn cho người và agent viết code trong repo này

## Nguồn sự thật

Đọc `docs/` trước khi viết code. Thứ tự ưu tiên khi có mâu thuẫn:

1. Yêu cầu: [`docs/01-requirements/PRD.md`](docs/01-requirements/PRD.md) §3 (story + tiêu chí Given-When-Then), [BRD](docs/01-requirements/BRD.md)
2. Kiến trúc: [`docs/03-architecture/SAD.md`](docs/03-architecture/SAD.md); chi tiết view: [`docs/04-design/blueprint/SDD_Blueprint.md`](docs/04-design/blueprint/SDD_Blueprint.md)
3. Hợp đồng API: [`docs/04-design/api/openapi.yaml`](docs/04-design/api/openapi.yaml) (thiết kế là nguồn chuẩn, code phải khớp)
4. Giao diện: [`docs/04-design/UI_UX_design/`](docs/04-design/UI_UX_design/UI_UX_Design.md)
5. Quyết định kỹ thuật: [`docs/05-implementation/adr/`](docs/05-implementation/adr/README.md); công việc: [`docs/05-implementation/tasks/`](docs/05-implementation/tasks/README.md)

Không tự đưa ra giá trị cho các mục `[TBD: OQ-xxx]`; dùng giá trị tạm trong cấu hình và ghi rõ là tạm.

## Stack

| Phần | Công nghệ | Thư mục |
|---|---|---|
| Backend API + worker | Python 3.12, FastAPI, SQLAlchemy 2, pypdf, numpy; quản lý gói bằng uv | `backend/` |
| Frontend | React + TypeScript + Vite, TanStack Query, openapi-fetch | `frontend/` |
| CSDL | **Tạm: SQLite + tìm vector bằng numpy** (ADR-006). Đích: PostgreSQL + pgvector | — |
| AI | Adapter giả lập (`FakeLlm`, `FakeEmbedding`) cho tới khi OQ-009 chốt | `backend/app/adapters/` |

## Chạy và kiểm tra

```bash
# Backend
cd backend
uv sync
uv run uvicorn app.main:app --port 8000      # API
uv run python -m app.worker                  # worker xử lý tài liệu (tiến trình riêng)
uv run ruff format --check . && uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest --cov

# Frontend
cd frontend
npm ci
npm run dev                                  # http://localhost:5173, proxy /api -> :8000
npm run typecheck && npm run lint && npm test && npm run build
npm run gen:api                              # sinh lại kiểu khi openapi.yaml đổi
```

Trên Windows, đặt `PYTHONIOENCODING=utf-8` để in tiếng Việt ra terminal.

## Kiến trúc và quy tắc phụ thuộc (kiểm tự động bằng `lint-imports`)

```
app/api       → REST, mô hình lỗi chuẩn, correlationId
app/container → composition root: chọn adapter theo cấu hình, nối service (nơi duy nhất biết mọi lớp)
app/modules   → nghiệp vụ: documents, ingestion, retrieval, qa   ← chỉ import app.ports, app.shared
app/ports     → giao diện LlmPort, EmbeddingPort, FileStorePort, PdfExtractor
app/adapters  → hiện thực port                                   ← chỉ import app.ports, app.shared
app/db        → SQLAlchemy: bảng + repository hiện thực Protocol của module
```

- Module nghiệp vụ **không** import adapter, API, DB, FastAPI, SQLAlchemy, pypdf, SDK nhà cung cấp AI.
- Đổi adapter bằng biến môi trường `CWD_*` (xem `backend/app/config.py`), không sửa code lõi.

## Quy ước

- **TDD theo tiêu chí chấp nhận:** mỗi AC trong PRD §3 có ít nhất một test; tên test mang mã AC khi có (`test_ac_101_1_...`).
- **Commit:** Conventional Commits, ghi mã story/task: `feat(qa): ... (US-203, T1.5)`. Commit nhỏ, mỗi commit CI xanh.
- **Lỗi API:** luôn trả `{ "error": { code, message, details, correlationId } }`; mã lỗi theo OpenAPI.
- **Hỏi đáp:** kết quả `NOT_FOUND` (không có thông tin trong kho) là HTTP 200; lỗi dịch vụ AI là `AI_*` 5xx — **không bao giờ** trộn hai loại này.
- **Trích dẫn** do hệ thống dựng từ `evidenceId` của đoạn đã truy xuất, không lấy từ văn bản mô hình trả (SDD D-06).
- **Giao diện:** dùng class và token của bản mẫu (`frontend/src/styles/app.css`); chuỗi hiển thị đặt trong `src/i18n/vi.ts`; trạng thái luôn có icon + chữ.
- Tham số `[Initial]` để trong cấu hình, không hard-code.
- Sau mỗi story: cập nhật [`docs/05-implementation/traceability.md`](docs/05-implementation/traceability.md) và dòng Trạng thái của file task.

## Điều cấm

- Không ghi nội dung tài liệu, câu hỏi, câu trả lời vào log hoặc analytics (G-10). Log chỉ chứa ID, số lượng, thời gian.
- Không commit dữ liệu thật của đội BD, khóa API, file `.env`.
- Không gọi dịch vụ AI bên ngoài khi chưa có phê duyệt OQ-009; không gửi PDF gốc, tên tệp, định danh người dùng ra ngoài.
- Không để tài liệu ở trạng thái khác `READY` xuất hiện trong truy xuất hay trích dẫn.
- Agent không tự approve, merge hay deploy; mọi thay đổi qua pull request có người review khác tác giả.

# Architecture Decision Records

Mỗi quyết định kỹ thuật quan trọng một file. Mẫu: Bối cảnh · Quyết định · Phương án đã cân nhắc · Hệ quả. Trạng thái: Proposed → Accepted (hoặc Superseded by ADR-xxx).

| ADR | Quyết định | Trạng thái | Còn chờ |
|---|---|---|---|
| [ADR-001](ADR-001-backend-python-fastapi.md) | Backend Python 3.12 + FastAPI, SQLAlchemy/Alembic, worker dùng bảng job, uv, pytest, ruff, mypy, import-linter | Accepted | — |
| [ADR-002](ADR-002-frontend-react-typescript-vite.md) | Frontend React + TypeScript + Vite, TanStack Query, client sinh từ OpenAPI, pdf.js, Vitest, Playwright | Accepted | — |
| [ADR-003](ADR-003-pdf-library.md) | Đọc PDF bằng pypdf (BSD), PyMuPDF dự phòng (AGPL) | Proposed | IT review giấy phép; chạy lại spike trên tài liệu thật (T0.8) |
| [ADR-004](ADR-004-embedding-model.md) | Embedding `multilingual-e5-base` (768 chiều) chạy nội bộ | Proposed | OQ-007; đo thông lượng ở T1.7 |
| [ADR-005](ADR-005-packaging-runtime.md) | Container cho mọi tiến trình, Docker Compose cho dev, Nginx reverse proxy | Proposed | IT xác nhận công cụ container (giấy phép Docker Desktop) |
| [ADR-006](ADR-006-temporary-sqlite.md) | Tạm dùng SQLite + tìm vector bằng numpy cho lát cắt đầu | Accepted (tạm thời) | Thay bằng PostgreSQL + pgvector khi có container (T0.3, T0.6) |

Spike hỗ trợ ADR-003: [`spikes/pdf-extraction/`](../../../spikes/pdf-extraction/README.md).

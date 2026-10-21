# ADR-001: Backend dùng Python 3.12 + FastAPI

**Trạng thái:** Accepted — chủ dự án chọn ngày 2026-10-21 (task [T0.1](../tasks/T0.1-tech-stack-adr.md))

## Bối cảnh

- SAD chốt kiểu kiến trúc (modular monolith, ports & adapters, một tiến trình API + một tiến trình worker, PostgreSQL + vector) nhưng chưa chọn ngôn ngữ ([SAD §1.2, §2](../../03-architecture/SAD.md)).
- Lõi nghiệp vụ cần: đọc PDF theo từng trang, chạy mô hình embedding trong hạ tầng của tổ chức, làm việc với vector trong PostgreSQL, sinh/kiểm tra OpenAPI, kiểm tra quy tắc phụ thuộc giữa module ([SDD §3.3](../../04-design/blueprint/SDD_Blueprint.md)).

## Quyết định

| Hạng mục | Lựa chọn | Ghi chú |
|---|---|---|
| Ngôn ngữ | Python 3.12 | |
| Web framework | FastAPI | Sinh OpenAPI từ mã; dùng để đối chiếu với `openapi.yaml` thiết kế ở T0.2 (thiết kế là nguồn chuẩn) |
| Kiểm tra dữ liệu | Pydantic v2 | Schema request/response và cấu hình |
| Truy cập CSDL | SQLAlchemy 2 + psycopg 3 + pgvector (Python) | |
| Migration | Alembic | |
| Worker | Tiến trình Python riêng, cùng codebase, lấy job từ bảng `processing_jobs` (`FOR UPDATE SKIP LOCKED`) | Không dùng Celery/broker (SDD D-05) |
| Quản lý gói | uv (có lockfile) | |
| Test | pytest (+ pytest-asyncio nếu dùng async) | |
| Lint / format / kiểu | ruff, mypy | |
| Quy tắc phụ thuộc | import-linter | Kiểm 4 quy tắc của SDD §3.3 trong CI |

## Phương án đã cân nhắc

| Phương án | Lý do không chọn |
|---|---|
| TypeScript + Node (NestJS/Fastify) | Một ngôn ngữ cho cả hai phía, nhưng thư viện PDF và chạy mô hình embedding nội bộ yếu hơn; embedding gần như chắc phải tách sang một service Python, thành hai ngôn ngữ backend |
| Java + Spring Boot | Mạnh cho hệ thống lớn, nhưng khởi động MVP chậm hơn; embedding nội bộ vẫn cần service riêng |
| C# + ASP.NET Core | Phù hợp nếu đội quen .NET; nhiều thư viện PDF tốt có giấy phép thương mại; embedding nội bộ vẫn cần service riêng |

## Hệ quả

- **Tích cực:** một ngôn ngữ cho API, worker và dịch vụ embedding; hệ sinh thái PDF/ML tốt nhất; OpenAPI có sẵn.
- **Tiêu cực:** đội cần kỷ luật kiểu (mypy) và quy tắc phụ thuộc để giữ ranh giới module; hiệu năng CPU của Python thấp hơn JVM/.NET nhưng không phải điểm nghẽn (điểm nghẽn là dịch vụ AI và embedding).
- **Việc tiếp theo:** T0.4 dựng cấu trúc thư mục và import-linter; T0.5 đưa ruff, mypy, pytest, import-linter vào CI.

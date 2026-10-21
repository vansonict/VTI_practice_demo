# ADR-005: Đóng gói bằng container, chạy dev bằng Docker Compose

**Trạng thái:** Proposed — chờ IT xác nhận công cụ container được phép dùng trên máy dev và môi trường đích (OQ-009, DEP-003)

## Bối cảnh

- SAD chọn mỗi tiến trình một container, một máy chủ chạy nhiều container cho MVP, chưa cần bộ điều phối cụm ([SAD §5.1](../../03-architecture/SAD.md)).
- Môi trường dev phải chạy được bằng một lệnh (T0.6).
- Máy dev hiện tại (2026-10-21) **chưa cài Docker hoặc công cụ container nào**.

## Quyết định

| Thành phần | Image gốc | Ghi chú |
|---|---|---|
| `api` | `python:3.12-slim` | FastAPI + uvicorn |
| `worker` | Cùng image với `api`, lệnh khởi động khác | Một codebase (ADR-001) |
| `embedding` | `python:3.12-slim` + sentence-transformers, trọng số tải sẵn khi build | Không truy cập internet khi chạy (ADR-004) |
| `db` | `pgvector/pgvector` (PostgreSQL 16 có sẵn extension vector) | Volume riêng |
| `web` | Build bằng `node` (Vite), phục vụ bằng `nginx` | Nginx cũng là reverse proxy: TLS, giới hạn kích thước body, chuyển `/api` tới `api` |
| File store | Volume gắn vào `api` và `worker` | Thay bằng object storage nếu OQ-009 yêu cầu |

- Dev: Docker Compose (một file `compose.yaml` + `.env.example`).
- Test/pilot: cùng image, cấu hình qua biến môi trường; nơi chạy theo OQ-009.

## Phương án đã cân nhắc

| Phương án | Lý do không chọn |
|---|---|
| Chạy trực tiếp trên máy (không container) | Mỗi máy dev cài khác nhau; khó tái lập PostgreSQL + vector và dịch vụ embedding |
| Kubernetes ngay từ MVP | Quá nặng cho một nút (SAD §5.1) |
| Caddy thay Nginx | Tương đương; chọn Nginx vì phổ biến hơn với đội vận hành |

## Hệ quả

- **Lưu ý giấy phép:** Docker Desktop yêu cầu giấy phép trả phí với tổ chức vượt ngưỡng quy mô do Docker quy định. Nếu tổ chức thuộc diện này, dùng **Podman** (tương thích file compose) hoặc Docker Engine trên WSL2. IT cần xác nhận.
- **Việc tiếp theo:** cài công cụ container trên máy dev trước T0.6; T0.6 viết `compose.yaml`; T4.9 dùng cùng image cho test/pilot.

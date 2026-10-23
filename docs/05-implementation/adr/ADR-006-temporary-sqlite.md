# ADR-006: Tạm dùng SQLite và tìm vector bằng numpy cho lát cắt đầu

**Trạng thái:** Accepted (tạm thời) — chủ dự án chọn ngày 2026-10-23. **Bị thay thế** khi có công cụ container (ADR-005) và hoàn thành T0.3 với PostgreSQL + pgvector.

## Bối cảnh

- Kiến trúc chọn PostgreSQL + pgvector ([SAD §2.3](../../03-architecture/SAD.md)), chạy bằng container ([ADR-005](ADR-005-packaging-runtime.md)).
- Máy dev hiện chưa có Docker/Podman (chờ IT xác nhận giấy phép); pgvector trên Windows phải tự biên dịch.
- Không muốn để việc thiếu hạ tầng chặn lát cắt đầu (upload → xử lý → hỏi → trả lời có trích dẫn).

## Quyết định

- Module nghiệp vụ truy cập dữ liệu **chỉ qua repository Protocol**; hiện thực bằng SQLAlchemy trong `backend/app/db/`.
- Lát cắt này dùng **SQLite** (tạo schema bằng `metadata.create_all`, không có migration) và **tìm cosine bằng numpy** trên toàn bộ đoạn của tài liệu `READY` (`SqlChunkSearchRepository`).
- Vector lưu dạng `float32` nhị phân; bản PostgreSQL dùng cột `vector(768)` (ADR-004).
- Nhận job: SQLite tuần tự hóa ghi nên dùng UPDATE có điều kiện; bản PostgreSQL dùng `FOR UPDATE SKIP LOCKED`.

## Phương án đã cân nhắc

| Phương án | Lý do không chọn |
|---|---|
| Chờ cài Docker rồi mới làm | Chặn toàn bộ Phase 6 vì một phụ thuộc hạ tầng |
| Cài PostgreSQL trực tiếp trên Windows | pgvector cần tự biên dịch (Visual Studio Build Tools); dễ lỗi, khác môi trường đích |
| Chỉ dùng repository trong bộ nhớ | Không kiểm được giao dịch, khóa ngoại, cascade |

## Hệ quả

- **Tích cực:** chạy và test được đầu-cuối ngay; ranh giới repository buộc module nghiệp vụ không phụ thuộc CSDL.
- **Tiêu cực / nợ kỹ thuật:**
  - Tìm vector quét toàn bộ đoạn — chỉ chấp nhận được với dữ liệu dev nhỏ.
  - Chưa có migration (Alembic) và chưa kiểm chỉ mục HNSW/GIN.
  - Hành vi đồng thời của worker trên PostgreSQL chưa được test.
- **Việc phải làm để thay thế:** T0.3 (schema PostgreSQL + Alembic), T0.6 (môi trường container), viết `PgChunkSearchRepository` dùng pgvector, chạy lại toàn bộ test trên PostgreSQL trong CI.

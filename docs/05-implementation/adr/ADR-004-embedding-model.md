# ADR-004: Mô hình embedding — multilingual-e5-base chạy nội bộ (tạm chọn)

**Trạng thái:** Proposed — chờ OQ-007 (ngôn ngữ) và số đo thông lượng ở T1.7

## Bối cảnh

- Embedding phải chạy **trong hạ tầng của tổ chức** để toàn văn tài liệu không rời hạ tầng ([SAD A-06](../../03-architecture/SAD.md), [SDD D-08](../../04-design/blueprint/SDD_Blueprint.md)).
- Ngôn ngữ tài liệu và câu hỏi chưa chốt (OQ-007); tài liệu dự kiến có tiếng Việt, có thể có tiếng Anh. Có thể có câu hỏi chéo ngôn ngữ (hỏi tiếng Việt trên tài liệu tiếng Anh), nên mô hình phải **đa ngôn ngữ**.
- Số chiều vector quyết định kiểu cột `chunks.embedding` (T0.3). Đổi mô hình khác số chiều = migration + xử lý lại toàn bộ tài liệu.
- Chưa có GPU được cấp; mô hình nên chạy được trên CPU ở quy mô một đội.

## Ứng viên

Thông tin dưới đây theo công bố của nhà phát triển mô hình; **chưa đo trên máy của dự án** (sẽ đo ở T1.7).

| Mô hình | Số chiều | Độ dài đầu vào tối đa | Kích thước | Giấy phép | Nhận xét |
|---|---|---|---|---|---|
| `intfloat/multilingual-e5-small` | 384 | 512 token | Nhỏ | MIT | Nhanh nhất trên CPU, chất lượng thấp hơn bản base |
| **`intfloat/multilingual-e5-base`** | **768** | 512 token | Trung bình | MIT | Cân bằng chất lượng/tốc độ trên CPU |
| `BAAI/bge-m3` | 1024 | 8192 token | Lớn | MIT | Chất lượng đa ngôn ngữ tốt, đầu vào dài; nặng hơn đáng kể trên CPU |

## Quyết định

- Tạm chọn **`intfloat/multilingual-e5-base`** (768 chiều). Đoạn văn bản ở SDD A1 (`[Initial]` 500–800 token) phải được giới hạn ≤ 512 token để không bị cắt; tham số chia đoạn ở T1.3 cập nhật tương ứng.
- Theo hướng dẫn của mô hình e5: thêm tiền tố `query: ` cho câu hỏi và `passage: ` cho đoạn tài liệu.
- Chạy bằng sentence-transformers trong một dịch vụ HTTP nội bộ (container riêng, không truy cập internet khi chạy; tải sẵn trọng số vào image).
- **T0.3 dùng `vector(768)`**, nhưng đặt số chiều trong một hằng số migration để đổi được.

## Phương án đã cân nhắc

| Phương án | Lý do không chọn (tạm thời) |
|---|---|
| multilingual-e5-small | Chọn nếu T1.7 cho thấy bản base quá chậm trên CPU |
| bge-m3 | Chọn nếu eval (T3.10) cho thấy chất lượng truy xuất của e5-base không đạt và có tài nguyên; đầu vào dài cho phép đoạn lớn hơn |
| Dịch vụ embedding bên ngoài | Gửi toàn văn tài liệu ra ngoài hạ tầng, trái SAD A-06; chỉ cân nhắc nếu OQ-009 cho phép và có ADR mới |

## Hệ quả

- **Tích cực:** không phụ thuộc mạng ngoài; không có chi phí theo lượt; giấy phép MIT.
- **Tiêu cực:** cần CPU/RAM cho dịch vụ embedding; đổi mô hình tốn công xử lý lại tài liệu.
- **Việc tiếp theo:** T1.7 đo thông lượng (đoạn/giây) và độ trễ cho một câu hỏi trên CPU; T3.10 so sánh chất lượng truy xuất nếu cần đổi mô hình; xác nhận lại khi OQ-007 chốt.

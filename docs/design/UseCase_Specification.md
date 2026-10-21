# Use Case Specification — "Chat với tài liệu" (MVP)

> **Chuẩn:** UML 2.0 · checklist [UseCase_Document_UML2.0_Checklist.xlsx](../../References/design/UseCase_Document_UML2.0_Checklist.xlsx)
> **Diagram:** [UseCase_ChatVoiTaiLieu.drawio](UseCase_ChatVoiTaiLieu.drawio) · **Nguồn:** [BRD.md](../requirements/BRD.md), [PRD.md](../requirements/PRD.md)
> Giá trị chưa chốt ghi `[TBD: OQ-xxx]` (OQ của BRD §12). Mô tả theo nghiệp vụ, không mô tả giao diện.

## 1. Document metadata

| Mục | Giá trị |
|---|---|
| Mã tài liệu | UCS-CWD-001 |
| Version / Ngày | 0.1 / 2026-10-19 |
| Trạng thái | **Draft** |
| Tác giả | Business Analyst — [TBD: OQ-014] (soạn với sự hỗ trợ của AI) |
| Stakeholder cần duyệt | Quản lý/Sponsor (STK-002), đại diện BD (STK-001), IT/Bảo mật (STK-004), Delivery team (STK-003) — [TBD: OQ-014, OQ-015] |

## 2. Actors

| Actor | Loại | Vai trò |
|---|---|---|
| Người dùng đã được cấp quyền | Primary (trừu tượng) | Tổng quát hóa của Nhân viên BD và Quản lý; là người đăng nhập vào hệ thống |
| Nhân viên BD | Primary (kế thừa Người dùng đã được cấp quyền) | Quản lý tài liệu và đặt câu hỏi |
| Quản lý / Sponsor | Primary (kế thừa Người dùng đã được cấp quyền) | Xem thống kê sử dụng để quyết định go / no-go |
| Dịch vụ AI | Secondary (hệ thống ngoài) | Hiểu câu hỏi và soạn câu trả lời từ nội dung tìm được. Nơi xử lý và nhà cung cấp `[TBD: OQ-009]` |
| Dịch vụ đăng nhập (IdP) | Secondary (hệ thống ngoài) | Xác thực danh tính. Có hay không `[TBD: OQ-008]` |

**System boundary:** ứng dụng web "Chat với tài liệu". Ngoài boundary: việc dùng câu trả lời vào quyết định kinh doanh (BRD §5.4) và các hạng mục Out of scope ở BRD §5.2.

## 3. Danh mục use case

| ID | Tên | Ưu tiên | Truy vết |
|---|---|---|---|
| UC-01 | Đăng nhập | P0 | BR-014, US-301 |
| UC-02 | Upload tài liệu PDF | P0 | BR-001, BR-002, US-101, US-102 |
| UC-03 | Kiểm tra và xử lý tài liệu | P0 | BR-002, BR-003 |
| UC-04 | Báo tài liệu không dùng được | P0 | BR-003, US-103 |
| UC-05 | Xem danh sách tài liệu và trạng thái | P0 | BR-004, US-104 |
| UC-06 | Xóa tài liệu | P1 | BR-005, US-105 |
| UC-07 | Hỏi đáp trên kho tài liệu | P0 | BR-006, 007, 010, 012, 013; US-201, 202, 206, 208, 209 |
| UC-08 | Tìm nội dung liên quan | P0 | BR-010, US-206 |
| UC-09 | Soạn câu trả lời có căn cứ kèm trích dẫn | P0 | BR-007, BR-008, US-202, US-203 |
| UC-10 | Thông báo "không tìm thấy" | P0 | BR-009, US-204 |
| UC-11 | Hỏi tiếp nối trong cùng phiên | P1 | BR-011, US-207 |
| UC-12 | Mở trang nguồn để đối chiếu | P1 | PRD US-205 (chưa có BR; đề xuất BR-018, PQ-01) |
| UC-13 | Đánh giá câu trả lời | P1 | BR-016, US-401 |
| UC-14 | Xem thống kê sử dụng theo tuần | P1 | BR-017, US-402 |

## 4. Quan hệ giữa các use case

| Loại | Từ | Đến | Điều kiện / Lý do |
|---|---|---|---|
| Generalization | Nhân viên BD, Quản lý | Người dùng đã được cấp quyền | Cùng được đăng nhập (UC-01) |
| `«include»` | UC-02 | UC-03 | Mọi file upload đều phải qua kiểm tra và xử lý |
| `«include»` | UC-07 | UC-08 | Mọi câu hỏi đều cần tìm nội dung liên quan trong kho |
| `«include»` | UC-07 | UC-09 | Mọi câu hỏi đều qua bước soạn kết quả; bước này tự đánh giá nội dung tìm được có đủ căn cứ hay không |
| `«extend»` | UC-04 → UC-03 | | Khi file không dùng được |
| `«extend»` | UC-10 → UC-07 | | Khi UC-09 xác định kho không đủ căn cứ: kết quả "không tìm thấy" thay cho câu trả lời |
| `«extend»` | UC-11 → UC-07 | | Khi câu hỏi tham chiếu câu hỏi/trả lời trước |
| `«extend»` | UC-12 → UC-07 | | Khi người dùng muốn kiểm chứng một trích dẫn |
| `«extend»` | UC-13 → UC-07 | | Khi người dùng muốn phản hồi về câu trả lời |

> Đăng nhập (UC-01) là điều kiện tiên quyết của mọi use case của Người dùng đã được cấp quyền, thể hiện bằng pre-condition, không vẽ `«include»` từng use case để tránh rối sơ đồ.

---

## 5. Đặc tả từng use case

### UC-01 Đăng nhập

| Mục | Nội dung |
|---|---|
| Mô tả | Người dùng chứng minh danh tính để được vào kho tài liệu và chức năng hỏi đáp. |
| Primary actor | Người dùng đã được cấp quyền |
| Secondary actor | Dịch vụ đăng nhập `[TBD: OQ-008]` |
| Trigger | Người dùng truy cập hệ thống khi chưa có phiên hợp lệ, hoặc phiên hết hạn |
| Pre-condition | Người dùng đã được cấp quyền truy cập (BR-014) |
| Post-condition (thành công) | Phiên hợp lệ được tạo; người dùng vào được các chức năng theo vai trò |
| Post-condition (thất bại) | Không có phiên; không nội dung tài liệu nào bị tiết lộ |

**Main success scenario**
1. Người dùng truy cập hệ thống.
2. Hệ thống yêu cầu xác thực.
3. Người dùng cung cấp thông tin xác thực.
4. Hệ thống (có thể thông qua dịch vụ đăng nhập) kiểm tra thông tin xác thực và quyền truy cập.
5. Hệ thống tạo phiên và cho người dùng vào hệ thống.

**Alternate flows**
- A1 (rẽ từ bước 1): người dùng còn phiên hợp lệ → hệ thống bỏ qua bước 2–5.

**Exception flows**
- E1 (bước 4): thông tin xác thực sai → hệ thống từ chối và thông báo, cho thử lại.
- E2 (bước 4): tài khoản hợp lệ nhưng chưa được cấp quyền → hệ thống từ chối, không cho vào bất kỳ chức năng nào.
- E3 (bước 4): dịch vụ đăng nhập không phản hồi → hệ thống thông báo lỗi hệ thống, không cho vào.
- E4 (sau bước 5, khi dùng hệ thống): phiên hết hạn → quay lại bước 2; nội dung câu hỏi đang nhập được giữ lại nếu có thể.

| Business rules | Chỉ người được cấp quyền mới truy cập kho và hỏi đáp (BR-014) |
|---|---|
| NFR | 10/10 truy cập không được phép bị từ chối; 10/10 truy cập được phép thành công (AC-014). Phương thức xác thực `[TBD: OQ-008]` |
| Data | Định danh người dùng, thông tin xác thực, vai trò |

---

### UC-02 Upload tài liệu PDF

| Mục | Nội dung |
|---|---|
| Mô tả | Nhân viên BD tự đưa một hoặc nhiều tài liệu PDF vào kho mà không cần hỗ trợ kỹ thuật. |
| Primary actor | Nhân viên BD |
| Trigger | Nhân viên BD chọn đưa tài liệu vào kho |
| Pre-condition | Đã đăng nhập (UC-01); kho chưa đạt giới hạn số tài liệu `[TBD: OQ-004]` |
| Post-condition (thành công) | Tài liệu có mặt trong kho ở trạng thái "Sẵn sàng truy vấn" |
| Post-condition (thất bại) | Tài liệu không ở trạng thái "Sẵn sàng truy vấn"; không ảnh hưởng tài liệu khác trong kho |

**Main success scenario**
1. Nhân viên BD chọn một hoặc nhiều file PDF.
2. Hệ thống ghi nhận từng file và đặt trạng thái "Đang xử lý".
3. Hệ thống thực hiện UC-03 cho từng file.
4. Hệ thống đặt trạng thái "Sẵn sàng truy vấn" cho file xử lý thành công và thông báo cho nhân viên BD.

**Alternate flows**
- A1 (bước 1): chọn nhiều file → mỗi file được xử lý và báo trạng thái riêng; file lỗi không làm dừng file khác.
- A2 (bước 1): file trùng tên/nội dung với file đã có → cho người dùng chọn thay thế hoặc giữ cả hai `[TBD: PQ-03]`.

**Exception flows**
- E1 (bước 2): file không phải PDF → từ chối, nêu "Chỉ hỗ trợ PDF".
- E2 (bước 2): file vượt giới hạn dung lượng/số trang `[TBD: OQ-004]` → từ chối trước khi xử lý, nêu giá trị thực và giới hạn.
- E3 (bước 2): kho đã đầy → từ chối, hướng dẫn xóa tài liệu cũ (UC-06).
- E4 (bước 1–3): mất kết nối → file ở trạng thái "Upload thất bại", cho thử lại; không để "Đang xử lý" vô hạn.
- E5 (bước 3): file không dùng được → xem UC-04.

| Business rules | Chỉ chấp nhận PDF (CON-003); người dùng tự thực hiện (BR-001) |
|---|---|
| NFR | 15/15 tài liệu mẫu dạng văn bản đạt "Sẵn sàng truy vấn" khi 3 nhân viên BD tự làm (AC-001); thời gian xử lý tối đa `[TBD]`; dữ liệu chỉ lưu trong phạm vi được duyệt (BR-015) |
| Data | File PDF; tên tài liệu; kích thước; số trang; người tải lên; thời điểm; trạng thái |

---

### UC-03 Kiểm tra và xử lý tài liệu

| Mục | Nội dung |
|---|---|
| Mô tả | Hệ thống kiểm tra tính dùng được của file và làm cho nội dung file có thể được tra cứu. Use case được gọi từ UC-02, không do người dùng khởi tạo trực tiếp. |
| Primary actor | Nhân viên BD (thông qua UC-02) |
| Trigger | UC-02 bước 3 |
| Pre-condition | File đã được ghi nhận ở trạng thái "Đang xử lý" |
| Post-condition (thành công) | Nội dung tài liệu dùng được để trả lời câu hỏi; trạng thái "Sẵn sàng truy vấn" |
| Post-condition (thất bại) | Trạng thái "Không dùng được" kèm lý do; nội dung file không bao giờ xuất hiện trong câu trả lời (AC-103.3) |

**Main success scenario**
1. Hệ thống kiểm tra file là PDF hợp lệ, không mật khẩu, không hỏng.
2. Hệ thống xác định file có nội dung văn bản trích xuất được.
3. Hệ thống trích nội dung theo từng trang, giữ liên kết tới tên tài liệu và số trang.
4. Hệ thống làm cho nội dung tra cứu được và trả kết quả thành công cho UC-02.

**Alternate flows**
- A1 (bước 2): file có chỗ không trích xuất được (bảng biểu, hình) nhưng đa số trang có văn bản → xử lý phần trích xuất được; giới hạn này được nêu trong hướng dẫn (RSK-003).

**Exception flows**
- E1 (bước 1): file có mật khẩu hoặc hỏng → thực hiện UC-04, lý do tương ứng.
- E2 (bước 2): file là ảnh scan → thực hiện UC-04, lý do "PDF dạng ảnh scan" (OCR bị hoãn, BRD §5.3).
- E3 (bước 3–4): xử lý thất bại giữa chừng hoặc quá thời hạn → UC-04, lý do "xử lý thất bại", cho thử lại.

| Business rules | Tài liệu không dùng được không bao giờ được hiển thị là sẵn sàng (BR-003) |
|---|---|
| NFR | Phải đạt dung lượng kho `[TBD: OQ-004]`; thời gian xử lý `[TBD]` |
| Data | Nội dung từng trang; số trang; tên tài liệu; kết quả kiểm tra |

---

### UC-04 Báo tài liệu không dùng được

| Mục | Nội dung |
|---|---|
| Mô tả | Hệ thống thông báo cho người dùng tên file và lý do cụ thể khi tài liệu không thể dùng để truy vấn. |
| Primary actor | Nhân viên BD |
| Trigger | Điều kiện lỗi tại UC-03 (extension point: file lỗi) |
| Pre-condition | UC-03 đã xác định file không dùng được |
| Post-condition (thành công) | Người dùng biết tên file và lý do; file mang trạng thái "Không dùng được" |
| Post-condition (thất bại) | Nếu không gửi được thông báo, file vẫn mang trạng thái "Không dùng được" và được hiển thị trong danh sách (UC-05) |

**Main success scenario**
1. Hệ thống đặt trạng thái "Không dùng được" cho file.
2. Hệ thống thông báo cho nhân viên BD tên file và lý do cụ thể (không phải PDF, quá lớn, ảnh scan, có mật khẩu, hỏng, xử lý thất bại).
3. Hệ thống giữ file trong danh sách để người dùng xóa (UC-06) hoặc thử lại.

**Alternate flows**
- A1 (bước 3): người dùng chọn thử lại với lỗi xử lý thất bại → quay lại UC-03.

**Exception flows**
- E1 (bước 2): không xác định được nguyên nhân → thông báo "không xác định được nguyên nhân" và vẫn bắt buộc đặt "Không dùng được". Hệ thống không bao giờ để file lỗi ở trạng thái sẵn sàng.

| Business rules | BR-003, AC-103.1: thông báo luôn có tên file và lý do |
|---|---|
| NFR | 3/3 loại file lỗi mẫu (scan, mật khẩu, hỏng) đều được báo đúng (AC-003) |
| Data | Tên file; mã lý do; thông điệp lý do |

---

### UC-05 Xem danh sách tài liệu và trạng thái

| Mục | Nội dung |
|---|---|
| Mô tả | Nhân viên BD xem các tài liệu đang có trong kho và biết tài liệu nào đã sẵn sàng truy vấn. |
| Primary actor | Nhân viên BD |
| Trigger | Nhân viên BD vào hệ thống hoặc cần biết phạm vi tra cứu |
| Pre-condition | Đã đăng nhập |
| Post-condition (thành công) | Người dùng thấy đủ danh sách và trạng thái đúng thực tế |
| Post-condition (thất bại) | Không thay đổi dữ liệu nào |

**Main success scenario**
1. Nhân viên BD yêu cầu xem danh sách tài liệu.
2. Hệ thống trả về toàn bộ tài liệu trong kho, mỗi tài liệu có tên và trạng thái (Đang xử lý / Sẵn sàng truy vấn / Không dùng được).

**Alternate flows**
- A1 (bước 2): kho rỗng → hệ thống thông báo chưa có tài liệu và hướng dẫn upload (UC-02).
- A2 (bước 2): chưa có tài liệu nào sẵn sàng → hệ thống thông báo tài liệu đang được xử lý.

**Exception flows**
- E1 (bước 2): không lấy được danh sách → thông báo lỗi hệ thống, cho thử lại; không hiển thị danh sách cũ như dữ liệu hiện tại.

| Business rules | Danh sách phải khớp trạng thái thực: ví dụ 5 tài liệu gồm 1 lỗi → 4 sẵn sàng, 1 không dùng được (AC-004). Phạm vi chia sẻ kho `[TBD: OQ-010]` |
|---|---|
| NFR | Trạng thái cập nhật mà không cần người dùng làm mới thủ công |
| Data | Tên tài liệu; trạng thái; lý do (nếu lỗi); thời điểm upload |

---

### UC-06 Xóa tài liệu

| Mục | Nội dung |
|---|---|
| Mô tả | Nhân viên BD loại một tài liệu khỏi kho để nội dung đó không còn được dùng khi trả lời. |
| Primary actor | Nhân viên BD |
| Trigger | Nhân viên BD chọn xóa một tài liệu |
| Pre-condition | Đã đăng nhập; tài liệu tồn tại trong kho |
| Post-condition (thành công) | Tài liệu và nội dung của nó không còn được dùng để trả lời; không câu trả lời nào trích dẫn nó |
| Post-condition (thất bại) | Tài liệu vẫn như trước khi xóa |

**Main success scenario**
1. Nhân viên BD chọn tài liệu cần xóa.
2. Hệ thống nêu tên tài liệu và hệ quả, yêu cầu xác nhận.
3. Nhân viên BD xác nhận.
4. Hệ thống xóa tài liệu và nội dung liên quan.
5. Hệ thống cập nhật danh sách (UC-05).

**Alternate flows**
- A1 (bước 3): người dùng hủy → không thay đổi gì.

**Exception flows**
- E1 (bước 4): xóa thất bại → thông báo lỗi, tài liệu giữ nguyên trạng thái trước đó; không để tình trạng tài liệu "đã xóa" nhưng nội dung vẫn dùng được.
- E2 (bước 4): tài liệu đang được xử lý (UC-03) → hệ thống hủy việc xử lý rồi xóa `[TBD]`.

| Business rules | Sau khi xóa, 3/3 câu hỏi có đáp án chỉ nằm trong tài liệu đó đều nhận "không tìm thấy" (AC-005). Ai được xóa tài liệu của người khác `[TBD: OQ-010]` |
|---|---|
| NFR | Việc xóa phải có hiệu lực với câu hỏi kế tiếp |
| Data | Mã tài liệu; người thực hiện; thời điểm |

---

### UC-07 Hỏi đáp trên kho tài liệu

| Mục | Nội dung |
|---|---|
| Mô tả | Nhân viên BD đặt câu hỏi bằng ngôn ngữ tự nhiên và nhận câu trả lời tổng hợp từ các tài liệu trong kho, kèm nguồn. |
| Primary actor | Nhân viên BD |
| Secondary actor | Dịch vụ AI (qua UC-09) |
| Trigger | Nhân viên BD gửi một câu hỏi |
| Pre-condition | Đã đăng nhập; kho có ít nhất một tài liệu "Sẵn sàng truy vấn" |
| Post-condition (thành công) | Người dùng nhận câu trả lời kèm trích dẫn, hoặc thông báo "không tìm thấy" |
| Post-condition (thất bại) | Người dùng nhận thông báo lỗi hệ thống (khác với "không tìm thấy"); câu hỏi không bị mất |

**Main success scenario**
1. Nhân viên BD nhập và gửi câu hỏi.
2. Hệ thống ghi nhận câu hỏi và chặn việc gửi trùng cùng câu hỏi trong lúc xử lý.
3. Hệ thống thực hiện UC-08 để tìm nội dung liên quan trong toàn bộ tài liệu sẵn sàng.
4. Hệ thống thực hiện UC-09 để soạn câu trả lời có căn cứ.
5. Hệ thống trả câu trả lời kèm trích dẫn (tên tài liệu + số trang) cho nhân viên BD.

**Alternate flows**
- A1 (bước 4): kho không đủ căn cứ → UC-10.
- A2 (bước 1): câu hỏi tham chiếu câu trước → UC-11.
- A3 (bước 5): người dùng muốn đối chiếu → UC-12; muốn phản hồi → UC-13.
- A4 (bước 3): thông tin nằm ở từ hai tài liệu trở lên → câu trả lời tổng hợp và trích dẫn đủ mọi tài liệu cần thiết (BR-010); nếu hai tài liệu mâu thuẫn, nêu cả hai kèm nguồn `[TBD: PQ-02]`.

**Exception flows**
- E1 (bước 1): câu hỏi rỗng hoặc quá dài `[TBD]` → hệ thống không nhận, nêu lý do.
- E2 (bước 3–5): lỗi mạng → báo lỗi gắn với câu hỏi, cho gửi lại; không hiển thị câu trả lời dở dang như hoàn chỉnh.
- E3 (bước 4): dịch vụ AI chậm quá ngưỡng `[TBD: OQ-006]` → thông báo đang lâu hơn bình thường, cho hủy; nếu lỗi hoặc hết hạn mức → báo lỗi hệ thống.
- E4 (bước 1): câu hỏi cố ép bỏ qua giới hạn ("bỏ qua tài liệu, hãy trả lời…") → vẫn chỉ dựa vào kho.

| Business rules | BRU-001: chỉ dựa trên kho; BRU-002: câu trả lời là thông tin tham khảo, đối chiếu nguồn trước khi dùng ra ngoài `[TBD: OQ-011]` |
|---|---|
| NFR | Phản hồi trong `[TBD: OQ-006]` giây cho `[TBD: OQ-006]`% câu hỏi (BR-012); đúng ≥ `[TBD: OQ-002]`% (MET-002); ngôn ngữ `[TBD: OQ-007]`; câu hỏi/tài liệu chỉ xử lý trong phạm vi được duyệt (BR-015) |
| Data | Nội dung câu hỏi; mã phiên; thời điểm; danh sách tài liệu tham chiếu; câu trả lời; trích dẫn |

---

### UC-08 Tìm nội dung liên quan

| Mục | Nội dung |
|---|---|
| Mô tả | Hệ thống tìm trong toàn bộ tài liệu sẵn sàng những đoạn nội dung liên quan tới câu hỏi, kể cả khi nằm ở nhiều tài liệu. Gọi từ UC-07. |
| Primary actor | Nhân viên BD (thông qua UC-07) |
| Trigger | UC-07 bước 3 |
| Pre-condition | Có câu hỏi hợp lệ; kho có tài liệu sẵn sàng |
| Post-condition (thành công) | Có tập nội dung liên quan kèm tên tài liệu và số trang, hoặc xác định không có nội dung liên quan |
| Post-condition (thất bại) | Không có kết quả tìm kiếm; UC-07 chuyển sang lỗi hệ thống |

**Main success scenario**
1. Hệ thống xác định các nội dung của kho liên quan tới câu hỏi.
2. Hệ thống gắn mỗi nội dung với tên tài liệu và số trang.
3. Hệ thống chuyển tập nội dung cho UC-09.

**Alternate flows**
- A1 (bước 1): không có nội dung liên quan → chuyển kết quả rỗng cho UC-09 (dẫn tới UC-10).
- A2 (bước 1): nội dung liên quan nằm ở nhiều tài liệu → chuyển nội dung của tất cả các tài liệu đó (BR-010).

**Exception flows**
- E1 (bước 1): lỗi truy cập kho → báo lỗi cho UC-07 (E2/E3).

| Business rules | Chỉ lấy từ tài liệu "Sẵn sàng truy vấn"; không lấy từ tài liệu đã xóa hoặc lỗi |
|---|---|
| NFR | Nằm trong ngưỡng thời gian của BR-012 |
| Data | Câu hỏi; ngữ cảnh phiên; đoạn nội dung; tên tài liệu; số trang |

---

### UC-09 Soạn câu trả lời có căn cứ kèm trích dẫn

| Mục | Nội dung |
|---|---|
| Mô tả | Dịch vụ AI đánh giá nội dung tìm được có đủ căn cứ không và soạn câu trả lời chỉ dựa trên nội dung đó, kèm trích dẫn. Gọi từ UC-07. |
| Primary actor | Nhân viên BD (thông qua UC-07) |
| Secondary actor | Dịch vụ AI |
| Trigger | UC-07 bước 4 |
| Pre-condition | UC-08 đã hoàn tất |
| Post-condition (thành công) | Có câu trả lời với trích dẫn đúng, hoặc kết luận kho không đủ căn cứ (kích hoạt UC-10) |
| Post-condition (thất bại) | Không có kết quả; UC-07 chuyển sang lỗi hệ thống |

**Main success scenario**
1. Hệ thống đánh giá nội dung tìm được có đủ để trả lời câu hỏi.
2. Dịch vụ AI soạn câu trả lời chỉ từ các nội dung đó.
3. Hệ thống gắn trích dẫn (tên tài liệu + số trang) vào câu trả lời.
4. Hệ thống trả câu trả lời cho UC-07.

**Alternate flows**
- A1 (bước 1): nội dung không đủ căn cứ → không soạn câu trả lời, kích hoạt UC-10.
- A2 (bước 3): không xác định được số trang → ghi "không xác định trang", không bịa số trang `[TBD: PQ-05]`.

**Exception flows**
- E1 (bước 2): dịch vụ AI lỗi/quá hạn mức/quá thời gian → báo lỗi hệ thống cho UC-07, không giả làm "không tìm thấy".

| Business rules | BRU-001 (chỉ từ kho); 100% câu trả lời có nội dung phải có trích dẫn (AC-008) |
|---|---|
| NFR | Trích dẫn đúng trang ≥ `[TBD: OQ-002]`% (AC-008); số nhận định không truy được về kho ≤ `[TBD: OQ-002]` (AC-007); chỉ gửi dữ liệu tới dịch vụ AI được STK-004 duyệt (BR-015); chi phí theo hạn mức (RSK-006, OQ-013) |
| Data | Câu hỏi; nội dung liên quan; câu trả lời; danh sách trích dẫn |

---

### UC-10 Thông báo "không tìm thấy"

| Mục | Nội dung |
|---|---|
| Mô tả | Khi kho không chứa thông tin, hệ thống báo rõ thay vì đưa ra câu trả lời. |
| Primary actor | Nhân viên BD |
| Trigger | UC-09 xác định kho không đủ căn cứ (extension point của UC-07) |
| Pre-condition | UC-07 đang xử lý một câu hỏi hợp lệ |
| Post-condition (thành công) | Người dùng nhận thông báo không tìm thấy, không kèm nội dung suy đoán |
| Post-condition (thất bại) | — (nếu không hiển thị được, áp dụng exception của UC-07) |

**Main success scenario**
1. Hệ thống thông báo "Không tìm thấy thông tin trong các tài liệu hiện có".
2. Hệ thống gợi ý diễn đạt lại câu hỏi hoặc kiểm tra danh sách tài liệu (UC-05).

**Alternate flows**
- A1 (bước 2): kho không có tài liệu sẵn sàng → thông báo kho chưa có tài liệu dùng được thay vì "không tìm thấy".

**Exception flows**
- E1 (bước 1): không được dùng kiến thức bên ngoài kho để lấp chỗ trống, kể cả với câu hỏi kiến thức chung (AC-202.1).

| Business rules | BR-009, BRU-001 |
|---|---|
| NFR | ≥ `[TBD: OQ-002]`% câu hỏi ngoài kho được báo đúng, tối thiểu 10 câu (AC-009, MET-005). Phân biệt rõ với lỗi hệ thống |
| Data | Câu hỏi; loại kết quả |

---

### UC-11 Hỏi tiếp nối trong cùng phiên

| Mục | Nội dung |
|---|---|
| Mô tả | Người dùng hỏi tiếp bằng cách tham chiếu câu hỏi hoặc câu trả lời trước mà không phải nhắc lại ngữ cảnh. |
| Primary actor | Nhân viên BD |
| Trigger | Người dùng gửi câu hỏi có đại từ/tham chiếu ngầm (ví dụ "còn thời hạn của nó thì sao?") |
| Pre-condition | Phiên có ít nhất một lượt hỏi–đáp trước đó |
| Post-condition (thành công) | Câu hỏi được hiểu đúng ngữ cảnh và được trả lời theo UC-07 |
| Post-condition (thất bại) | Câu hỏi được xử lý như câu hỏi độc lập hoặc hệ thống yêu cầu làm rõ |

**Main success scenario**
1. Nhân viên BD gửi câu hỏi tiếp nối.
2. Hệ thống đối chiếu câu hỏi với ngữ cảnh các lượt trước trong phiên.
3. Hệ thống tiếp tục UC-07 với câu hỏi đã được bổ sung ngữ cảnh.

**Alternate flows**
- A1 (bước 1): người dùng bắt đầu cuộc trò chuyện mới → xóa ngữ cảnh (có xác nhận).

**Exception flows**
- E1 (bước 2): không xác định được đối tượng được nhắc tới → hệ thống yêu cầu người dùng nói rõ, không đoán.

| Business rules | Ngữ cảnh chỉ tồn tại trong phiên hiện tại; lịch sử nhiều phiên bị hoãn (BRD §5.3) |
|---|---|
| NFR | ≥ 4/5 câu hỏi tiếp nối trong kịch bản mẫu đúng ngữ cảnh (AC-011) |
| Data | Chuỗi hỏi–đáp của phiên |

---

### UC-12 Mở trang nguồn để đối chiếu

| Mục | Nội dung |
|---|---|
| Mô tả | Người dùng xem đúng trang của tài liệu được trích dẫn để tự kiểm chứng. |
| Primary actor | Nhân viên BD |
| Trigger | Người dùng chọn một trích dẫn trong câu trả lời |
| Pre-condition | Câu trả lời có trích dẫn; tài liệu nguồn vẫn còn trong kho |
| Post-condition (thành công) | Người dùng thấy đúng trang nguồn |
| Post-condition (thất bại) | Người dùng vẫn thấy tên tài liệu và số trang trong trích dẫn |

**Main success scenario**
1. Nhân viên BD chọn một trích dẫn.
2. Hệ thống hiển thị tài liệu nguồn tại đúng trang được trích dẫn.

**Alternate flows**
- A1 (bước 2): người dùng đã xem xong → quay lại câu trả lời mà không mất phiên hỏi đáp.

**Exception flows**
- E1 (bước 2): tài liệu nguồn đã bị xóa (UC-06) → thông báo tài liệu không còn trong kho, không hiển thị liên kết chết.
- E2 (bước 2): không mở được trang → vẫn hiển thị tên tài liệu và số trang.

| Business rules | BRU-002: đối chiếu nguồn trước khi dùng thông tin ra bên ngoài `[TBD: OQ-011]`. Quyết định có thêm BR-018 không `[TBD: PQ-01]` |
|---|---|
| NFR | Thời gian mở trang `[TBD]`; chỉ người được cấp quyền mới xem được nội dung |
| Data | Mã tài liệu; số trang |

---

### UC-13 Đánh giá câu trả lời

| Mục | Nội dung |
|---|---|
| Mô tả | Người dùng đánh giá một câu trả lời là hữu ích hay không hữu ích, làm dữ liệu cho chỉ số MET-004. |
| Primary actor | Nhân viên BD |
| Trigger | Người dùng chọn đánh giá cho một câu trả lời |
| Pre-condition | Câu trả lời đã được hiển thị |
| Post-condition (thành công) | Đánh giá được lưu và xuất hiện trong thống kê (UC-14) |
| Post-condition (thất bại) | Không có đánh giá nào được ghi; người dùng được báo và có thể thử lại |

**Main success scenario**
1. Nhân viên BD chọn "hữu ích" hoặc "không hữu ích".
2. Hệ thống ghi nhận đánh giá gắn với câu trả lời đó.
3. Hệ thống xác nhận đã ghi nhận.

**Alternate flows**
- A1 (bước 1): người dùng đổi đánh giá → hệ thống thay đánh giá cũ bằng đánh giá mới.
- A2 (bước 1): người dùng chọn "không hữu ích" → có thể nhập thêm nhận xét tùy chọn.

**Exception flows**
- E1 (bước 2): ghi nhận thất bại → thông báo, cho thử lại.

| Business rules | Mỗi người dùng có một đánh giá hiệu lực cho mỗi câu trả lời |
|---|---|
| NFR | 10/10 đánh giá thử nghiệm xuất hiện trong thống kê (AC-016); không lưu nội dung câu hỏi/trả lời ngoài phạm vi được duyệt |
| Data | Mã câu trả lời; mã người dùng; đánh giá; nhận xét (tùy chọn); thời điểm |

---

### UC-14 Xem thống kê sử dụng theo tuần

| Mục | Nội dung |
|---|---|
| Mô tả | Quản lý xem số người dùng hoạt động và số câu hỏi theo tuần trong giai đoạn pilot để quyết định go / no-go. |
| Primary actor | Quản lý / Sponsor |
| Trigger | Quản lý cần xem mức sử dụng |
| Pre-condition | Đã đăng nhập với vai trò Quản lý |
| Post-condition (thành công) | Quản lý thấy số liệu đúng theo tuần |
| Post-condition (thất bại) | Không thay đổi dữ liệu nào |

**Main success scenario**
1. Quản lý yêu cầu xem thống kê.
2. Hệ thống tổng hợp số người dùng hoạt động (MET-003), số câu hỏi và tỷ lệ "hữu ích" (MET-004) theo từng tuần.
3. Hệ thống hiển thị kết quả cho quản lý.

**Alternate flows**
- A1 (bước 2): chưa có dữ liệu trong tuần → hiển thị 0 và nêu chưa có hoạt động.

**Exception flows**
- E1 (bước 2): không tổng hợp được → thông báo lỗi hệ thống.
- E2 (bước 1): người dùng không phải Quản lý → từ chối truy cập.

| Business rules | "Người dùng hoạt động" = người đặt ít nhất 1 câu hỏi trong tuần (MET-003). Quản lý có xem được nội dung câu hỏi của từng người hay chỉ số tổng hợp `[TBD: OQ-009]` |
|---|---|
| NFR | Số liệu khớp 100% kịch bản thử nghiệm một tuần (AC-017) |
| Data | Số người dùng hoạt động/tuần; số câu hỏi/tuần; số đánh giá hữu ích/không hữu ích |

---

## 6. Assumptions

| ID | Giả định | Nguồn |
|---|---|---|
| ASM-001 | Phần lớn PDF có văn bản trích xuất được (không phải ảnh scan) | BRD §10 |
| ASM-002 | Chỉ đội BD dùng MVP, ở quy mô một đội | BRD §10 |
| ASM-003 | Chính sách cho phép xử lý tài liệu bằng một dịch vụ AI | BRD §10 |
| ASM-004 | Người dùng có trình duyệt và mạng | BRD §10 |
| ASM-UC-01 | `[Unverified]` Quản lý không thực hiện upload/hỏi đáp trong MVP; nếu có, cần vẽ thêm association | Suy luận từ BR-017 |
| ASM-UC-02 | `[Unverified]` Quyền xóa tài liệu thuộc về người dùng BD nào phụ thuộc phạm vi chia sẻ kho | OQ-010 |

## 7. Open issues

| ID | Vấn đề | Liên quan | Owner |
|---|---|---|---|
| OQ-008 | MVP có đăng nhập không, qua dịch vụ nào? | UC-01, UC-14 | Sponsor |
| OQ-009 | Chính sách dữ liệu và nhà cung cấp AI | UC-07, UC-09, UC-13 | IT/Bảo mật |
| OQ-004 | Giới hạn kho, kích thước, số trang | UC-02, UC-03 | BD lead |
| OQ-006 | Ngưỡng thời gian phản hồi | UC-07 | Sponsor / BD lead |
| OQ-007 | Ngôn ngữ hỏi và tài liệu | UC-07 | BD lead |
| OQ-010 | Kho dùng chung hay riêng | UC-05, UC-06 | Sponsor |
| OQ-011 | BRU-002 có được chấp thuận không | UC-07, UC-12 | Sponsor |
| PQ-01…PQ-05 | Các quyết định mở ở mức PRD (BR-018, mâu thuẫn giữa tài liệu, upload trùng, trích dẫn không có trang) | Xem PRD §7 | Product owner |

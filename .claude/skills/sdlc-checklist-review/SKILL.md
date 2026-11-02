---
name: sdlc-checklist-review
description: Review một artifact SDLC (BRD, PRD, use case, SAD, blueprint/SDD, API, database, UI/UX, test plan…) theo checklist .xlsx trong References/ — đọc checklist, chấm từng mục trung thực (Done / In Progress / N/A kèm ghi chú), ghi kết quả vào BẢN SAO checklist đặt cạnh artifact, sửa những gì sửa được rồi chấm lại. Dùng khi người dùng nói "review theo checklist", "kiểm tra theo @References/…Checklist.xlsx", "đánh giá tài liệu", "audit", hoặc ở bước VERIFY của bất kỳ phase nào.
---

# Review artifact theo checklist

Checklist là cách người duyệt biết tài liệu đủ hay chưa. Giá trị của review nằm ở **sự trung thực**: một mục "Done" không có căn cứ còn tệ hơn "In Progress" có ghi chú, vì nó che rủi ro khỏi người duyệt.

## Các bước

1. **Đọc checklist** (không sửa file gốc):
   ```bash
   python .claude/skills/sdlc-checklist-review/scripts/checklist_xlsx.py read "References/design/SAD_IEEE_1016_Checklist.xlsx"
   ```
   In ra từng dòng: số dòng, nhóm, mục, câu hỏi, trạng thái hiện tại, và danh sách giá trị Status hợp lệ (thường `Pending, In Progress, Done, N/A`).

2. **Đọc artifact** cần review đầy đủ (không chấm dựa trên trí nhớ về lúc viết).

3. **Chấm từng mục** — ghi chú phải chỉ được bằng chứng (ID, §, tên file, log). Ba mức của khoá (Pass / Partial / Fail) ánh xạ vào cột Status của checklist:

   | Mức | Status trong file | Khi nào | Ghi chú bắt buộc |
   |---|---|---|---|
   | **Pass** | Done | Có nội dung đáp ứng | Vị trí: "§2.5: 5 interface ngoài, mỗi cái có giao thức, xác thực, hành vi khi lỗi" |
   | **Partial** | In Progress | Có một phần, hoặc chờ quyết định | Phần thiếu + **owner + hạn** + mã OQ/task: "Chưa có kích cỡ — chờ OQ-004 (BD lead, 30/10)" |
   | **Fail** | Pending (giữ nguyên) | Chưa có, hoặc sai | Thiếu gì, sửa ở đâu |
   | Không áp dụng | N/A | Mục không hợp với artifact | Lý do: "desktop-first, không có yêu cầu mobile" |

   Phân biệt "tài liệu chưa có" với "đã có nhưng chưa kiểm thực tế" (vd. tỷ lệ tương phản tính tay nhưng chưa chạy công cụ — đó là Partial, không phải Pass).
   Điều kiện qua cổng: **0 Fail, mọi Partial có owner + hạn.** Chấm checklist "cho có" rồi vẫn baseline là điều khoá yêu cầu tránh.

4. **Sửa những gì sửa được ngay** trong artifact (thiếu mục, link sai, mâu thuẫn với tài liệu khác), rồi chấm lại. Nói rõ với người dùng mục nào đã sửa sau review.

5. **Ghi kết quả vào bản sao** cạnh artifact, tên `<Loại>_Checklist_Review.xlsx` (hoặc theo quy ước có sẵn trong thư mục):
   ```bash
   python .claude/skills/sdlc-checklist-review/scripts/checklist_xlsx.py fill \
     "References/design/SAD_IEEE_1016_Checklist.xlsx" "docs/03-architecture/SAD_Checklist_Review.xlsx" results.json
   ```
   `results.json`: `{"2": ["Done", "ghi chú"], "3": ["In Progress", "ghi chú"], ...}` — khóa là số dòng Excel lấy từ bước 1. Script giữ nguyên định dạng, validation và màu trạng thái của file gốc, rồi in bảng đếm Done/In Progress/N/A để đối chiếu.

6. **Báo cáo cho người dùng:** số mục Pass / Partial / Fail / N/A, các mục Partial (vì sao, owner, hạn), những gì đã sửa trong lúc review, và kết luận có đạt điều kiện cổng không. Nhắc rằng đây là **review của agent**, không thay cho phê duyệt.

## Ai chấm

Người viết artifact dễ "thấy điều mình muốn thấy". Khi có thể, giao bước chấm cho sub-agent **`sdlc-auditor`** (`.claude/agents/sdlc-auditor.md`): nó đọc artifact và checklist trong context riêng, chỉ chấm và ghi bản sao, không sửa artifact. Agent chính sau đó sửa theo phát hiện (Fix) và gọi auditor chấm lại.

## Lưu ý

- Checklist chấm *tài liệu*, không chỉ sơ đồ: checklist use case đòi đặc tả từng use case, không chỉ file `.drawio`.
- Nếu checklist có mục rõ ràng không hợp với loại artifact (vd. mục "multi-agent network" trong dự án không có agent), chấm N/A kèm lý do thay vì bỏ trống.
- Không dùng Excel/LibreOffice nếu không có; script chỉ cần Python chuẩn.

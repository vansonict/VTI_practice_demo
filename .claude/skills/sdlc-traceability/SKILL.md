---
name: sdlc-traceability
description: Lập và kiểm ma trận truy vết (traceability.md, RTM.md) nối BR → FR → US → (UC) → TC → evidence, tìm ID mồ côi, link hỏng, ca kiểm thử không có bằng chứng, và chuẩn bị demo "truy từ BR tới bằng chứng trong 2 phút". Dùng khi người dùng nói "truy vết", "traceability", "RTM", "ma trận yêu cầu – test", "kiểm orphan", "BR nào chưa có test", "chuẩn bị nghiệm thu/demo", hoặc sau khi thêm/sửa yêu cầu, story, task, ca kiểm thử.
---

# Truy vết BR → FR → US → TC → evidence

Truy vết là thứ biến một chồng tài liệu thành một chuỗi kiểm chứng được: người duyệt mở một yêu cầu bất kỳ và đi tới bằng chứng test của nó. Nghiệm thu khoá chấm 20% vào tiêu chí này ("liền mạch, 0 orphan").

## 1. Thu thập ID

Quét `docs/` lấy ID theo tiền tố mà dự án dùng (đọc vài file để biết quy ước, đừng giả định):

| Loại | Thường gặp | Nguồn |
|---|---|---|
| Mục tiêu / yêu cầu nghiệp vụ | `BO-`, `BR-` | BRD |
| Yêu cầu chức năng / phi chức năng | `FR-`, `NFR-` (có dự án dùng AC- trong BRD thay FR) | PRD/SRS |
| Story / use case | `US-`, `UC-` | PRD, User stories, use case |
| Thiết kế / task | `DE-`, `ADR-`, `T` | SDD, adr/, tasks/ |
| Ca kiểm thử | `TC-` | test-cases/, TEST_CASES.md |
| Bằng chứng | đường dẫn `evidence/…`, `test-runs/<ngày>_<TC>/report.md` | |

```bash
grep -rhoE "\b(BR|FR|NFR|US|UC|TC)-[0-9A-Z.-]+" docs | sort | uniq -c | sort -k2
```

## 2. Lập / cập nhật ma trận

`RTM.md` (hoặc `traceability.md` nếu dự án đã có) — một dòng cho mỗi yêu cầu:

| BR | FR / AC | US | UC | TC | Kết quả gần nhất | Bằng chứng |
|---|---|---|---|---|---|---|
| BR-008 | AC-008 | US-203 | UC-09 | TC-203-01 | Pass (ngày) | `test-runs/<ngày>_TC-203-01/report.md` |

Lấy liên kết từ chính tài liệu (bảng truy vết của BRD/PRD, dòng "Truy vết" trong task và ca kiểm thử), không suy diễn từ tên.

## 3. Kiểm

- **Mồ côi xuôi:** BR không có US; US (P0/P1) không có TC; TC đã chạy không có bằng chứng.
- **Mồ côi ngược:** US/TC trỏ tới ID không tồn tại; task không truy về story.
- **Link hỏng:** mọi đường dẫn tương đối trong ma trận mở được (viết script nhỏ kiểm `fs.existsSync`/`Path.exists`).
- **Khớp số liệu:** kết quả trong RTM khớp "Kết quả gần nhất" của file ca và báo cáo chạy.
- Ca bị chặn bởi OQ/task: không phải mồ côi, nhưng ghi rõ "Bị chặn — OQ-xxx".

## 4. Báo cáo

Số yêu cầu đã phủ / tổng, danh sách mồ côi theo loại, link hỏng, đề xuất sửa (file nào, thêm gì). Sửa những gì là lỗi ghi chép (thiếu link, sai ID); thiếu test thật thì tạo việc, không bịa bằng chứng.

## Demo "BR → bằng chứng < 2 phút"

Chọn 1 BR P0, chuẩn bị đường đi: BRD (dòng BR) → PRD (story + AC) → file TC → báo cáo chạy → ảnh/video. Kiểm từng link mở được trước buổi demo.

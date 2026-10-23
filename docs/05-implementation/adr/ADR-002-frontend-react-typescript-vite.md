# ADR-002: Frontend dùng React + TypeScript + Vite

**Trạng thái:** Accepted — chủ dự án chọn ngày 2026-10-21 (task [T0.1](../tasks/T0.1-tech-stack-adr.md))

## Bối cảnh

- SAD chọn SPA, không SSR/CDN; trạng thái dữ liệu lấy từ server qua REST, polling trạng thái tài liệu ([SAD §2.1, A-01, A-02](../../03-architecture/SAD.md)).
- Thiết kế UI/UX có bản mẫu HTML/CSS/JS thuần với design token trong khối `:root` ([UI_UX_Design.md](../../04-design/UI_UX_design/UI_UX_Design.md)); cần trình xem PDF mở đúng trang (UC-12).

## Quyết định

| Hạng mục | Lựa chọn | Ghi chú |
|---|---|---|
| Framework | React + TypeScript | |
| Build/dev server | Vite | Build tĩnh, phục vụ qua reverse proxy |
| Server state | TanStack Query | Bộ nhớ đệm yêu cầu, polling khi có tài liệu `PROCESSING` |
| Routing | React Router | 3 màn hình S01–S03 |
| API client | Sinh kiểu từ `openapi.yaml` (openapi-typescript + openapi-fetch) | Frontend và backend dùng chung hợp đồng T0.2 |
| Styling | Stylesheet toàn cục port nguyên từ bản mẫu (`src/styles/app.css`: token `:root` + class) | Cập nhật 2026-10-23: dùng lại 1:1 class đã duyệt thay vì CSS Modules; không dùng framework CSS |
| Trình xem PDF | pdf.js (`pdfjs-dist`) | Mở đúng trang được trích dẫn |
| Test component | Vitest + Testing Library | |
| E2E | Playwright | Kèm kiểm accessibility bằng axe (T5.3) |
| i18n | Chuỗi giao diện tách ra file theo ngôn ngữ | Chờ OQ-007 |

## Phương án đã cân nhắc

| Phương án | Lý do không chọn |
|---|---|
| Vue 3 + TypeScript + Vite | Nhẹ, dễ học; hệ sinh thái nhỏ hơn React một chút; không có lợi thế rõ ràng cho dự án này |
| Angular | Cấu trúc chặt, hợp đội lớn; nặng hơn cho MVP 3 màn hình |
| Giữ HTML/JS thuần như bản mẫu | Không có quản lý trạng thái, test và kiểu dữ liệu; khó bảo trì khi thêm tính năng |

## Hệ quả

- **Tích cực:** chuyển từ bản mẫu sang component trực tiếp; kiểu dữ liệu API sinh tự động nên lệch hợp đồng bị phát hiện khi build.
- **Tiêu cực:** cần quy trình sinh lại client mỗi khi `openapi.yaml` đổi (gắn vào CI ở T0.5).
- **Việc tiếp theo:** T0.4 tạo `frontend/` và đưa token vào `styles/tokens`; T1.6 hiện thực S02.

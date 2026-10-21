# Software Blueprint Design (SDD) — "Chat với tài liệu" (MVP)

> **Chuẩn:** IEEE 1016-2009 · **Prompt:** [bluePrint_design_prompt.md](../../../References/design/bluePrint_design_prompt.md) · **Checklist review:** [BluePrint_Design_IEEE_1016_2009_Checklist.xlsx](../../../References/design/BluePrint_Design_IEEE_1016_2009_Checklist.xlsx) → kết quả ở [Blueprint_Checklist_Review.xlsx](Blueprint_Checklist_Review.xlsx)
> **Đầu vào:** [BRD.md](../../01-requirements/BRD.md) · [PRD.md](../../01-requirements/PRD.md) · [UseCase_Specification.md](../../02-analysis/UseCase_Specification.md) · [UseCase_ChatVoiTaiLieu.drawio](../../02-analysis/UseCase_ChatVoiTaiLieu.drawio)
> **Thứ tự tài liệu:** SDD này được viết trước [SAD.md](../../03-architecture/SAD.md), nên các quyết định D-01…D-11 ra đời ở đây. Sau khi có SAD, **SAD là nguồn cho quyết định kiến trúc/hạ tầng** (pattern, triển khai, bảo mật, độ tin cậy); SDD là nguồn cho chi tiết view (ER, API, thuật toán). Khi có mâu thuẫn, đồng bộ cả hai.
> **Quy ước:** `[TBD: OQ-xxx]` = chờ quyết định theo Open Question của BRD §12; `[Proposed]` = lựa chọn thiết kế của tài liệu này, chưa được stakeholder xác nhận; `[Initial]` = tham số khởi điểm, phải hiệu chỉnh bằng bộ câu hỏi chuẩn (DEP-002). Mọi con số không có nguồn trong BRD/PRD đều thuộc một trong ba nhóm này, **không** phải requirement.

---

## 1. Context & Subject

### 1.1 System Identification

| Attribute | Value |
|---|---|
| **System Name** | "Chat với tài liệu" (MVP) |
| **SDD Version** | v0.1 (Draft) |
| **Document Date** | 2026-10-21 |
| **Document Owner** | Software Architect — [TBD: OQ-014] (soạn với sự hỗ trợ của AI) |
| **Mã tài liệu** | SDD-CWD-001 |

**Revision History**

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 2026-10-21 | Architect (draft) | Bản nháp đầu tiên từ BRD v0.1, PRD v0.1, UCS v0.1 |

**Mô tả hệ thống.** Ứng dụng web cho phép đội phát triển kinh doanh (BD) tự đưa tài liệu PDF vào một kho tài liệu, đặt câu hỏi bằng ngôn ngữ tự nhiên và nhận câu trả lời chỉ dựa trên nội dung kho, kèm tên tài liệu và số trang để kiểm chứng. Khi kho không đủ căn cứ, hệ thống báo "không tìm thấy" thay vì trả lời. Quản lý xem thống kê sử dụng theo tuần để quyết định go / no-go sau pilot. Hệ thống gồm 17 business requirement (BR-001…017), 14 use case (UC-01…14).

**Subject của thiết kế (Design Subject).** Toàn bộ phần mềm trong system boundary của use case diagram: web client, backend, kho dữ liệu và các adapter tới dịch vụ ngoài. Mục tiêu thiết kế theo thứ tự ưu tiên:
1. **Câu trả lời có căn cứ và kiểm chứng được** (BR-007, 008, 009; RSK-001).
2. **Dữ liệu chỉ đi trong phạm vi được duyệt** (BR-015; RSK-002).
3. **Đơn giản đủ để làm MVP** (CON-001): tối thiểu thành phần vận hành, thay thế được dịch vụ AI mà không đổi lõi.

### 1.2 System Scope and External Boundaries

| Boundary Type | Description |
|---|---|
| **System Purpose** | Rút ngắn thời gian BD tra cứu thông tin trải trên nhiều PDF (BO-001) và cho câu trả lời tin cậy, kiểm chứng được (BO-002), đồng thời tạo dữ liệu đo lường cho quyết định đầu tư (BO-003). |
| **External Systems** | (1) Dịch vụ AI sinh câu trả lời — secondary actor, nhà cung cấp `[TBD: OQ-009]`. (2) Dịch vụ tạo embedding — có thể là mô hình tự lưu trữ hoặc dịch vụ ngoài `[TBD: OQ-009]`. (3) Dịch vụ đăng nhập (IdP) — chỉ khi OQ-008 yêu cầu. |
| **User Types** | Nhân viên BD (STK-001), Quản lý/Sponsor (STK-002). Người vận hành/IT là người quản trị hệ thống, không tương tác qua ứng dụng. |
| **External Interfaces** | Giao diện web (HTTPS) cho người dùng; REST/HTTPS tới dịch vụ AI và embedding (qua adapter); OIDC tới IdP (nếu có). Không có API công khai cho bên thứ ba. |
| **Trust Boundaries** | **TB-1** trình duyệt người dùng ↔ ứng dụng (internet/mạng nội bộ). **TB-2** ứng dụng ↔ dịch vụ AI/embedding bên ngoài: dữ liệu rời khỏi hạ tầng của tổ chức, phải được STK-004 duyệt (BR-015). **TB-3** ứng dụng ↔ IdP. **TB-4** nội dung PDF là *dữ liệu không tin cậy*, kể cả khi do người dùng hợp lệ tải lên (có thể chứa chỉ dẫn độc hại, xem §3.8). |
| **Deployment Environment** | `[TBD: OQ-009, DEP-003]`. Thiết kế không phụ thuộc đám mây cụ thể: đóng gói container, chạy được trên máy chủ nội bộ hoặc đám mây được duyệt. |

### 1.3 Assumptions and Constraints

| Type | Description |
|---|---|
| **Technical Constraints** | CON-002 ứng dụng web; CON-003 chỉ PDF; CON-004 tương tác qua chat với AI. Ràng buộc kiến trúc từ thiết kế: không ép nhà cung cấp AI cụ thể (xem D-04). |
| **Business Constraints** | CON-001 MVP; CON-005 timeline `[TBD: OQ-012]` và ngân sách `[TBD: OQ-013]`; chi phí AI tính theo lượng dùng (RSK-006). |
| **Environmental Assumptions** | ASM-003 được phép dùng dịch vụ AI; ASM-004 người dùng có trình duyệt và mạng; DEP-003 có môi trường hosting được duyệt. Độ trễ và độ sẵn sàng của dịch vụ AI do nhà cung cấp quyết định, nằm ngoài kiểm soát (xem R-03). |
| **Data Assumptions** | ASM-001 phần lớn PDF có văn bản trích xuất được (không phải scan); số tài liệu, số trang tối đa `[TBD: OQ-004]`; ngôn ngữ `[TBD: OQ-007]`; kho dùng chung hay riêng `[TBD: OQ-010]`; chính sách lưu giữ/xóa dữ liệu `[TBD: OQ-009]`. Thiết kế giả định **một kho dùng chung cho cả đội BD** `[Proposed]` vì đây là phương án đơn giản nhất, dữ liệu mô hình vẫn để sẵn `owner_id` để mở rộng. |

---

## 2. Stakeholders & Concerns

### 2.1 Stakeholder Identification

| Stakeholder | Role/Title | Primary Interest |
|---|---|---|
| Nhân viên BD (STK-001) | Người dùng chính | Câu trả lời nhanh, đầy đủ, kiểm chứng được; tự upload |
| Quản lý/Sponsor (STK-002) | Business owner | Bằng chứng giá trị, chi phí AI trong ngân sách |
| IT/Bảo mật (STK-004) | Compliance | Bảo vệ dữ liệu, kiểm soát truy cập, kiểm toán; có quyền chặn triển khai |
| Chủ sở hữu tài liệu (STK-005) | Nội bộ/đối tác | Tài liệu chỉ dùng bởi người có quyền |
| Delivery team (STK-003) | Developer, QA | Dễ xây dựng, dễ test, dễ thay đổi |
| Vận hành | DevOps/IT ops | Dễ triển khai, giám sát, sao lưu, kiểm soát chi phí AI |
| BD lead / SME | Nghiệm thu | Chấm chất lượng bằng bộ câu hỏi chuẩn |

### 2.2 Stakeholder Concerns (IEEE 1016-2009)

| ID | Stakeholder | Concern | Priority | Acceptance Criteria (nguồn) |
|---|---|---|---|---|
| CN-01 | BD, SME | Câu trả lời đúng và trích dẫn đúng trang | High | MET-002 ≥ `[TBD: OQ-002]`%; trích dẫn đúng trang ≥ `[TBD: OQ-002]`% (AC-006, AC-008) |
| CN-02 | BD, Sponsor | Không bịa thông tin; báo "không tìm thấy" khi thiếu căn cứ | High | MET-005 ≥ `[TBD: OQ-002]`% trên ≥ 10 câu ngoài kho (AC-009); 100% câu trả lời có nội dung kèm trích dẫn (AC-008) |
| CN-03 | BD | Thời gian phản hồi | High | `[TBD: OQ-006]` giây cho `[TBD: OQ-006]`% câu hỏi (AC-012) |
| CN-04 | IT/Bảo mật | Dữ liệu chỉ xử lý/lưu trong phạm vi được duyệt | High | Cấu hình thực khớp văn bản phê duyệt (AC-015) |
| CN-05 | IT/Bảo mật, STK-005 | Chỉ người được cấp quyền truy cập | High | 10/10 từ chối, 10/10 cho phép (AC-014) |
| CN-06 | BD | Không tưởng nhầm tài liệu lỗi đã được tra cứu | High | 3/3 loại file lỗi được báo đúng (AC-003); danh sách khớp trạng thái (AC-004) |
| CN-07 | BD | Tự upload không cần hỗ trợ kỹ thuật | High | 15/15 file mẫu sẵn sàng (AC-001) |
| CN-08 | Sponsor | Số liệu pilot chính xác | Med | Khớp 100% kịch bản (AC-017); 10/10 đánh giá được ghi (AC-016) |
| CN-09 | Sponsor, Ops | Chi phí AI nằm trong ngân sách, có giới hạn | Med | Hạn mức và cảnh báo `[TBD: OQ-013]` |
| CN-10 | Delivery team | Thay nhà cung cấp AI/embedding mà không viết lại lõi | Med | Đổi adapter không đổi code ngoài lớp adapter (xem §3.3) |
| CN-11 | Delivery team | Test được chất lượng trả lời lặp lại | Med | Bộ câu hỏi chuẩn chạy tự động, đo được MET-002/005 |
| CN-12 | Ops | Triển khai, sao lưu, phục hồi đơn giản | Med | Tài liệu vận hành; khôi phục dữ liệu theo RPO/RTO `[TBD]` |
| CN-13 | BD | Hỏi tiếp nối trong phiên | Low | ≥ 4/5 kịch bản đúng ngữ cảnh (AC-011) |

### 2.3 Quality Attribute Scenarios

Định dạng sáu phần: Source · Stimulus · Artifact · Environment · Response · Response Measure.

| Quality Attribute | Scenario |
|---|---|
| **Performance** (CN-03) | **Source:** nhân viên BD. **Stimulus:** gửi một câu hỏi. **Artifact:** pipeline hỏi đáp (DE-QA). **Environment:** kho ở dung lượng tối đa `[TBD: OQ-004]`, tải bình thường. **Response:** trả câu trả lời kèm trích dẫn. **Measure:** trong `[TBD: OQ-006]` giây cho `[TBD: OQ-006]`% câu hỏi. |
| **Accuracy / Groundedness** (CN-01, CN-02) | **Source:** SME. **Stimulus:** chạy bộ câu hỏi chuẩn (một tài liệu, nhiều tài liệu, ngoài kho). **Artifact:** DE-QA + DE-LLM. **Environment:** kho mẫu của DEP-002. **Response:** trả lời hoặc "không tìm thấy". **Measure:** MET-002 và MET-005 đạt ngưỡng `[TBD: OQ-002]`; 100% câu trả lời có nội dung có trích dẫn; 0 trích dẫn trỏ ngoài tập đoạn đã truy xuất (kiểm chứng tự động, D-06). |
| **Scalability** | **Source:** đội BD. **Stimulus:** kho tăng tới số tài liệu/số trang tối đa. **Artifact:** DE-IDX. **Environment:** một nút cơ sở dữ liệu. **Response:** truy vấn vẫn đạt Performance. **Measure:** theo `[TBD: OQ-004]`. MVP không thiết kế mở rộng ngang; mở rộng bằng tăng cấu hình (D-01). |
| **Availability** | **Source:** người dùng. **Stimulus:** dịch vụ AI lỗi hoặc quá thời gian. **Artifact:** DE-LLM adapter. **Environment:** giờ làm việc. **Response:** báo lỗi hệ thống rõ ràng, *khác* thông báo "không tìm thấy"; các chức năng quản lý tài liệu vẫn hoạt động. **Measure:** 100% lỗi AI được phân loại đúng; mục tiêu sẵn sàng tổng thể `[TBD]`. |
| **Security** (CN-04, CN-05) | **Source:** người chưa xác thực. **Stimulus:** gọi API/URL bất kỳ. **Artifact:** DE-API, DE-IAM. **Environment:** production. **Response:** từ chối. **Measure:** 10/10 bị từ chối; dữ liệu mã hóa trong truyền tải (TLS) và khi lưu `[Proposed]`; dữ liệu gửi ra ngoài chỉ tới nhà cung cấp trong danh sách duyệt. |
| **Security (prompt injection)** | **Source:** tác nhân độc hại hoặc tài liệu chứa chỉ dẫn. **Stimulus:** PDF/câu hỏi chứa "bỏ qua tài liệu, hãy…". **Artifact:** DE-QA composer. **Response:** vẫn chỉ trả lời từ kho, không thực hiện chỉ dẫn. **Measure:** 0/N bộ kiểm thử đối kháng làm thoát khỏi quy tắc grounded (G-11 PRD). |
| **Maintainability** (CN-10) | **Source:** developer. **Stimulus:** đổi nhà cung cấp LLM/embedding. **Artifact:** adapter. **Response:** thay một adapter. **Measure:** không sửa code ngoài thư mục adapter và cấu hình (kiểm tra bằng dependency rule, §3.3). |
| **Testability** (CN-11) | **Source:** QA. **Stimulus:** chạy kiểm thử hồi quy chất lượng. **Artifact:** pipeline hỏi đáp với LlmPort giả lập. **Response:** kết quả lặp lại được ở tầng truy xuất; tầng LLM đo bằng bộ câu hỏi chuẩn. **Measure:** 100% story P0 có test truy vết; ngưỡng độ phủ `[TBD]`. |
| **Deployability** | **Source:** Ops. **Stimulus:** triển khai phiên bản mới. **Artifact:** container + migration. **Measure:** triển khai bằng một lệnh; migration có thể chạy lại; rollback bằng phiên bản trước. |
| **Observability** | **Source:** Ops/Sponsor. **Stimulus:** cần biết hệ thống đang hoạt động ra sao. **Artifact:** DE-OBS. **Response:** log có cấu trúc, số liệu độ trễ, tỷ lệ lỗi, chi phí token, sự kiện analytics PRD §5.2. **Measure:** 100% request có correlation id; log không chứa nội dung tài liệu/câu hỏi ngoài phạm vi được duyệt (G-10). |
| **Cost control** (CN-09) | **Source:** hệ thống. **Stimulus:** lượng dùng AI tăng. **Artifact:** DE-LLM adapter. **Response:** áp hạn mức theo ngày/người dùng; cảnh báo; khi hết hạn mức báo "dịch vụ tạm thời không khả dụng". **Measure:** hạn mức `[TBD: OQ-013]`. |

### 2.4 UX/UI Quality Attribute Scenarios

Giá trị cụ thể nêu ở đây là `[Proposed]` trừ khi có nguồn; PRD chưa chốt mức WCAG, breakpoint, trình duyệt hỗ trợ.

| Quality Attribute | UX/UI Scenario |
|---|---|
| **Usability** | Nhân viên BD lần đầu, không hướng dẫn, upload 5 PDF mẫu và đạt "Sẵn sàng" với 0 lỗi thao tác (AC-001 bản đo thực tế: 15/15). |
| **Accessibility** | Upload, gửi câu hỏi, mở trích dẫn, đánh giá đều thao tác được bằng bàn phím; trạng thái không chỉ truyền đạt bằng màu. Mức WCAG: 2.1 AA `[Proposed]`. |
| **Performance** | Khung giao diện tải được trong `[TBD]` giây trên mạng văn phòng; chỉ báo "đang xử lý" hiển thị trong ≤ 300 ms sau khi gửi câu hỏi `[Proposed]`. |
| **Responsiveness** | Ưu tiên desktop (PRD P-4). Mobile web không là yêu cầu `[TBD: PQ-06]`; bố cục không gây cuộn ngang ở chiều rộng ≥ 1024 px `[Proposed]`. |
| **Visual Consistency** | Ba trạng thái tài liệu và hai loại kết quả (trả lời, không tìm thấy) luôn dùng cùng một kiểu hiển thị trên mọi màn hình. |
| **Error Recovery** | Mọi lỗi gắn với tác vụ gây ra nó và có hành động khắc phục (Thử lại, Gửi lại, Xóa); không mất câu hỏi đang nhập khi lỗi hoặc hết phiên (AC-301.3). |
| **Feedback & Affordance** | Upload hiển thị trạng thái từng file; câu hỏi đang xử lý hiển thị chỉ báo và chặn gửi trùng (AC-201.2). |
| **Information Architecture** | Danh sách tài liệu luôn hiển thị cạnh khung chat (PRD P-5); mọi chức năng P0 đạt được trong 1 màn hình. |
| **Internationalization** | Ngôn ngữ giao diện và ngôn ngữ trả lời theo `[TBD: OQ-007]`; mọi chuỗi giao diện đặt ngoài mã nguồn để thêm ngôn ngữ không cần sửa logic. |
| **Mobile Experience** | Không thuộc phạm vi MVP (CON-002, PRD P-4). |

### 2.5 UX/UI Constraints Matrix

| UX/UI Constraint | Requirement | Tool/Standard | Verification Method |
|---|---|---|---|
| **Color Contrast** | Tối thiểu 4.5:1 cho chữ thường `[Proposed]` | WCAG 2.1 AA | Kiểm tra tự động + thủ công |
| **Typography** | Chữ nội dung ≥ 16 px, cho phép phóng to `[Proposed]` | Design system `[TBD]` | Design audit |
| **Touch Targets** | Không áp dụng trong MVP (desktop-first) | — | — |
| **Loading States** | Hiển thị chỉ báo trong ≤ 300 ms cho upload, xử lý tài liệu, chờ trả lời | UX best practice | Giám sát hiệu năng phía client |
| **Error Messaging** | Rõ ràng, nêu cách khắc phục, không lộ chi tiết kỹ thuật; lỗi hệ thống luôn khác "không tìm thấy" | UX writing | Content review |
| **Empty States** | Kho rỗng, chưa có tài liệu sẵn sàng, phiên mới, không tìm thấy: mỗi trạng thái có hướng dẫn bước tiếp theo (PRD §4.2 E-1…E-4) | UX best practice | UI inventory |
| **Notifications** | Thông báo gắn vị trí tác vụ, không dùng pop-up chặn thao tác | UX best practice | User testing |
| **Help & Onboarding** | Dòng mô tả phạm vi cố định; hướng dẫn ngắn về giới hạn (scan, bảng biểu) và nguyên tắc đối chiếu nguồn (G-15 PRD, BRU-002) | UX best practice | Chỉ số hoàn thành tác vụ |

---

## 3. Design Views (IEEE 1016-2009 Core)

**Tổng quan kiến trúc.** *Modular monolith* gồm một web client, một backend theo module, một worker xử lý tài liệu nền (chạy cùng codebase), một cơ sở dữ liệu quan hệ có tìm kiếm vector và một kho tệp. Tất cả tích hợp bên ngoài qua *ports & adapters*. Lý do ở §5.

### 3.0 Context View

```mermaid
flowchart LR
    BD["Nhân viên BD"] -->|HTTPS| APP
    MG["Quản lý / Sponsor"] -->|HTTPS| APP
    subgraph TBH["Hạ tầng của tổ chức (TB-1)"]
      APP["Hệ thống 'Chat với tài liệu'<br/>web client + backend + worker<br/>DB + kho tệp"]
    end
    APP -->|"REST/HTTPS (TB-2)<br/>câu hỏi + đoạn nội dung liên quan"| LLM["Dịch vụ AI sinh câu trả lời<br/>[TBD: OQ-009]"]
    APP -->|"REST/HTTPS hoặc nội bộ (TB-2)<br/>nội dung tài liệu để tạo embedding"| EMB["Dịch vụ embedding<br/>[TBD: OQ-009]"]
    APP -->|"OIDC (TB-3)"| IDP["Dịch vụ đăng nhập<br/>[TBD: OQ-008]"]
```

Dữ liệu qua TB-2: *nội dung đoạn văn bản, câu hỏi và (khi hỏi tiếp nối) các lượt hỏi–đáp trước trong phiên* — không gửi file PDF gốc, không gửi định danh người dùng. Đây là mức tối thiểu `[Proposed]` để giảm phơi nhiễm; STK-004 quyết định cuối cùng (OQ-009).

### 3.1 Composition View

**Purpose:** cách hệ thống được ghép từ các đơn vị nhỏ hơn. **Concerns:** CN-10, CN-11 (Maintainability, Testability, Modularity).

| ID | Element | Type | Parent | Responsibility | Dependencies | Trace |
|---|---|---|---|---|---|---|
| DE-00 | Hệ thống Chat với tài liệu | System | — | Toàn bộ | — | BRD |
| DE-WEB | Web Client (SPA) | Subsystem | DE-00 | Giao diện: quản lý tài liệu, chat, xem nguồn, thống kê | DE-API | UC-01…14 |
| DE-WEB-1 | Document Panel | Module | DE-WEB | Upload, danh sách, trạng thái, xóa | DE-DOC (API) | UC-02,05,06 |
| DE-WEB-2 | Chat Panel | Module | DE-WEB | Gửi câu hỏi, hiển thị trả lời, trích dẫn, đánh giá | DE-QA (API) | UC-07,10,11,13 |
| DE-WEB-3 | Source Viewer | Module | DE-WEB | Hiển thị đúng trang PDF được trích dẫn | DE-DOC (API) | UC-12 |
| DE-WEB-4 | Stats Page | Module | DE-WEB | Thống kê tuần cho Quản lý | DE-ANA (API) | UC-14 |
| DE-WEB-5 | Auth Shell & Telemetry | Module | DE-WEB | Đăng nhập, giữ phiên, phát sự kiện analytics | DE-IAM, DE-ANA (API) | UC-01 |
| DE-SRV | Backend Application | Subsystem | DE-00 | Logic nghiệp vụ, REST API | DE-DB, DE-FS, adapters | — |
| DE-API | API Layer | Module | DE-SRV | Định tuyến, xác thực yêu cầu, kiểm tra đầu vào, mô hình lỗi chuẩn | DE-IAM | mọi UC |
| DE-IAM | Identity & Access | Module | DE-SRV | Xác thực, phiên, vai trò (BD, Quản lý), AuthPort | IdP adapter (tùy chọn) | UC-01, BR-014 |
| DE-DOC | Document Library | Module | DE-SRV | Nhận file, kiểm tra sơ bộ, trạng thái tài liệu, xóa, cấp file cho Source Viewer | DE-FS, DE-DB, DE-ING (qua hàng đợi) | UC-02,04,05,06,12 |
| DE-ING | Ingestion Worker | Module | DE-SRV | Kiểm tra PDF, trích văn bản theo trang, chia đoạn, tạo embedding, lập chỉ mục | DE-FS, DE-IDX, EmbeddingPort | UC-03,04 |
| DE-IDX | Index & Retrieval | Module | DE-SRV | Lưu đoạn + vector; truy xuất kết hợp ngữ nghĩa và từ khóa | DE-DB, EmbeddingPort | UC-08 |
| DE-QA | Q&A Orchestrator | Module | DE-SRV | Hội thoại, viết lại câu hỏi tiếp nối, truy xuất, soạn trả lời, kiểm chứng trích dẫn, cổng "không tìm thấy" | DE-IDX, LlmPort, DE-DB | UC-07,09,10,11 |
| DE-FB | Feedback | Module | DE-SRV | Lưu đánh giá câu trả lời | DE-DB | UC-13 |
| DE-ANA | Analytics & Stats | Module | DE-SRV | Thu sự kiện (PRD §5.2), tổng hợp thống kê tuần | DE-DB | UC-14, BR-016/017 |
| DE-LLM | LLM Adapter | Adapter | DE-SRV | Gọi dịch vụ AI, phân loại lỗi, hạn mức, đo chi phí | Dịch vụ AI | BR-007, BR-015 |
| DE-EMB | Embedding Adapter | Adapter | DE-SRV | Tạo vector cho đoạn và câu hỏi | Dịch vụ embedding | BR-006, BR-010 |
| DE-OBS | Cross-cutting: Config, Logging, Audit, Metrics | Module | DE-SRV | Cấu hình, log có cấu trúc, nhật ký kiểm toán, số liệu | — | CN-12, G-10 |
| DE-DB | Relational DB + vector search | Data store | DE-00 | Dữ liệu nghiệp vụ, đoạn, vector, sự kiện | — | §3.5 |
| DE-FS | File Store | Data store | DE-00 | Lưu PDF gốc | — | UC-02, UC-12 |

```mermaid
flowchart TD
    Root["DE-00 Hệ thống"] --> WEB["DE-WEB Web Client"]
    Root --> SRV["DE-SRV Backend"]
    Root --> DATA["Kho dữ liệu"]
    WEB --> W1["Document Panel"]
    WEB --> W2["Chat Panel"]
    WEB --> W3["Source Viewer"]
    WEB --> W4["Stats Page"]
    WEB --> W5["Auth Shell & Telemetry"]
    SRV --> API["API Layer"]
    SRV --> IAM["Identity & Access"]
    SRV --> DOC["Document Library"]
    SRV --> ING["Ingestion Worker"]
    SRV --> IDX["Index & Retrieval"]
    SRV --> QA["Q&A Orchestrator"]
    SRV --> FB["Feedback"]
    SRV --> ANA["Analytics & Stats"]
    SRV --> AD["Adapters: LLM, Embedding, IdP"]
    SRV --> OBS["Config / Logging / Audit / Metrics"]
    DATA --> DB["DE-DB Relational + vector"]
    DATA --> FS["DE-FS File Store"]
```

### 3.2 Logical View (cấu trúc tĩnh)

**Concerns:** Understandability, Maintainability. Các kiểu dữ liệu lưu trữ chi tiết ở §3.5; dưới đây là mô hình miền và các giao diện (port).

```mermaid
classDiagram
    class User {
        id
        displayName
        role
        active
    }
    class Document {
        id
        name
        sizeBytes
        pageCount
        status
        unusableReason
        uploadedBy
        uploadedAt
    }
    class Chunk {
        id
        documentId
        page
        ordinal
        text
        embedding
    }
    class Conversation {
        id
        userId
        startedAt
    }
    class Message {
        id
        conversationId
        role
        kind
        text
        latencyMs
    }
    class Citation {
        messageId
        chunkId
        documentId
        page
    }
    class Feedback {
        messageId
        userId
        rating
        comment
    }
    class ProcessingJob {
        id
        documentId
        state
        attempts
        lastError
    }
    User "1" --> "*" Document : uploads
    Document "1" --> "*" Chunk : contains
    User "1" --> "*" Conversation : owns
    Conversation "1" --> "*" Message
    Message "1" --> "*" Citation
    Citation "*" --> "1" Chunk
    Message "1" --> "0..*" Feedback
    Document "1" --> "*" ProcessingJob
```

**Ports (giao diện nội bộ mà lõi phụ thuộc vào)**

| Port | Phương thức | Adapter mặc định `[Proposed]` | Lỗi chuẩn hóa |
|---|---|---|---|
| `LlmPort` | `compose(question, evidence[], history[]) → ComposedAnswer` | Adapter tới dịch vụ AI được duyệt | `LlmTimeout`, `LlmQuotaExceeded`, `LlmUnavailable`, `LlmInvalidOutput` |
| `EmbeddingPort` | `embed(texts[]) → vectors[]` | Mô hình đa ngôn ngữ chạy trong hạ tầng của tổ chức (giữ nội dung tài liệu trong nội bộ) | `EmbeddingUnavailable` |
| `AuthPort` | `authenticate(credentials) → Principal` | Tài khoản cấp bởi quản trị (local); thêm OIDC khi OQ-008 yêu cầu | `InvalidCredentials`, `NotAuthorized` |
| `FileStorePort` | `put / open / delete(docId)` | Thư mục lưu trữ có mã hóa hoặc object storage được duyệt | `StorageUnavailable` |
| `Clock`, `IdGenerator` | tiện ích kiểm thử | — | — |

`ComposedAnswer` = `{ status: ANSWERED | INSUFFICIENT_EVIDENCE, claims[ {text, evidenceIds[]} ] }`.

### 3.3 Dependency View

**Quy tắc phụ thuộc (có kiểm tra tự động trong CI `[Proposed]`):**
1. `DE-API` → module nghiệp vụ → *ports*. Module nghiệp vụ **không** import adapter, framework web hay SDK nhà cung cấp.
2. Adapter chỉ import port mà nó hiện thực.
3. Module nghiệp vụ không import lẫn nhau trực tiếp ngoài đồ thị dưới đây; giao tiếp bất đồng bộ giữa DE-DOC và DE-ING qua hàng đợi công việc.
4. Chỉ `DE-IDX` và repository của từng module truy cập bảng của mình.

```mermaid
flowchart TD
    WEB["DE-WEB"] -->|REST| API
    API["DE-API"] --> IAM["DE-IAM"]
    API --> DOC["DE-DOC"]
    API --> QA["DE-QA"]
    API --> FB["DE-FB"]
    API --> ANA["DE-ANA"]
    DOC -. "job queue" .-> ING["DE-ING"]
    ING --> IDX["DE-IDX"]
    QA --> IDX
    ING --> EP(["EmbeddingPort"])
    IDX --> EP
    QA --> LP(["LlmPort"])
    IAM --> AP(["AuthPort"])
    DOC --> FP(["FileStorePort"])
    ING --> FP
    LLM["DE-LLM adapter"] -.implements.-> LP
    EMB["DE-EMB adapter"] -.implements.-> EP
    IDPA["IdP / Local adapter"] -.implements.-> AP
    FSA["FileStore adapter"] -.implements.-> FP
    FB --> DB[("DE-DB")]
    ANA --> DB
    IDX --> DB
    DOC --> DB
    QA --> DB
```

**Phụ thuộc bên ngoài:** dịch vụ AI, dịch vụ embedding, IdP, thư viện đọc PDF theo trang, hệ quản trị CSDL có tìm kiếm vector. Mỗi phụ thuộc có một điểm tích hợp duy nhất (adapter hoặc repository).

### 3.4 Interaction View (tương tác động)

**Concerns:** CN-01, CN-02, CN-03, CN-06. Ba kịch bản chính.

**(a) Upload và xử lý tài liệu (UC-02, 03, 04)**

```mermaid
sequenceDiagram
    actor BD as Nhân viên BD
    participant W as Web Client
    participant A as API / DE-DOC
    participant S as FileStore
    participant D as DB
    participant Q as Job queue
    participant G as DE-ING Worker
    participant E as EmbeddingPort
    BD->>W: Chọn file PDF
    W->>A: POST /documents (multipart)
    A->>A: Kiểm tra: là PDF? kích thước? kho còn chỗ?
    alt không hợp lệ
        A-->>W: 4xx lý do cụ thể (không phải PDF / quá lớn / kho đầy)
    else hợp lệ
        A->>S: Lưu file gốc
        A->>D: Tạo Document(status=PROCESSING) + ProcessingJob
        A->>Q: Đưa job
        A-->>W: 202 Accepted + documentId
        Q->>G: Nhận job
        G->>S: Mở file
        G->>G: Kiểm tra mật khẩu / hỏng / có văn bản?
        alt không dùng được
            G->>D: status=UNUSABLE + reason
        else dùng được
            G->>G: Trích văn bản theo trang, chia đoạn
            G->>E: embed(đoạn[])
            E-->>G: vectors
            G->>D: Lưu Chunk + vector; status=READY
        end
        loop mỗi 2 giây [Initial]
            W->>A: GET /documents
            A-->>W: danh sách + trạng thái
        end
    end
```

**(b) Hỏi đáp (UC-07, 08, 09, 10)**

```mermaid
sequenceDiagram
    actor BD as Nhân viên BD
    participant W as Web Client
    participant A as API
    participant Q as DE-QA
    participant I as DE-IDX
    participant L as LlmPort
    participant D as DB
    BD->>W: Gửi câu hỏi
    W->>A: POST /conversations/{id}/messages
    A->>Q: ask(userId, text)
    Q->>D: Lưu Message(USER)
    Q->>Q: Viết lại câu hỏi độc lập nếu có tham chiếu (UC-11)
    Q->>I: retrieve(câu hỏi độc lập, chỉ tài liệu READY)
    I-->>Q: evidence[] (đoạn + tài liệu + trang + điểm)
    alt không đoạn nào qua ngưỡng liên quan
        Q->>D: Message(NOT_FOUND)
        Q-->>A: NOT_FOUND
    else có evidence
        Q->>L: compose(câu hỏi, evidence, history)
        alt lỗi AI (timeout / quota / unavailable)
            L-->>Q: lỗi chuẩn hóa
            Q->>D: Message(ERROR, loại lỗi)
            Q-->>A: ERROR (khác NOT_FOUND)
        else INSUFFICIENT_EVIDENCE hoặc trích dẫn không hợp lệ
            L-->>Q: kết quả
            Q->>D: Message(NOT_FOUND)
            Q-->>A: NOT_FOUND
        else ANSWERED và trích dẫn hợp lệ
            L-->>Q: claims + evidenceIds
            Q->>Q: Kiểm chứng trích dẫn ⊆ evidence; ánh xạ sang (tài liệu, trang)
            Q->>D: Message(ANSWER) + Citation[]
            Q-->>A: ANSWER + citations
        end
    end
    A-->>W: Kết quả
    W->>W: Hiển thị theo loại (trả lời / không tìm thấy / lỗi)
```

**(c) Mở nguồn và đánh giá (UC-12, 13):** `GET /documents/{id}/file` (kiểm tra quyền, truyền tệp) và `PUT /messages/{id}/feedback`, tương tác một bước, không vẽ riêng.

### 3.5 Information View (dữ liệu lưu trữ)

**Concerns:** CN-04, CN-05, CN-06, CN-08. Cơ sở dữ liệu quan hệ có phần mở rộng tìm kiếm vector `[Proposed]` (D-02). Kiểu dữ liệu dưới đây ở mức logic; schema vật lý do bước thiết kế CSDL chi tiết quyết định.

```mermaid
erDiagram
    USERS ||--o{ DOCUMENTS : uploads
    DOCUMENTS ||--o{ CHUNKS : contains
    DOCUMENTS ||--o{ PROCESSING_JOBS : has
    USERS ||--o{ CONVERSATIONS : owns
    CONVERSATIONS ||--o{ MESSAGES : has
    MESSAGES ||--o{ CITATIONS : cites
    CHUNKS ||--o{ CITATIONS : referenced_by
    MESSAGES ||--o{ FEEDBACK : rated_by
    USERS ||--o{ FEEDBACK : gives
    USERS ||--o{ ANALYTICS_EVENTS : emits
    USERS ||--o{ AUDIT_LOG : acts
```

| Bảng | Trường chính | Ràng buộc / ghi chú |
|---|---|---|
| `users` | `id`, `display_name`, `external_subject` (nếu IdP), `password_hash` (nếu local), `role` ∈ {BD, MANAGER}, `active` | Vai trò xác định quyền UC-14 |
| `documents` | `id`, `name`, `size_bytes`, `page_count`, `status` ∈ {PROCESSING, READY, UNUSABLE}, `unusable_reason`, `content_hash`, `file_ref`, `uploaded_by`, `uploaded_at`, `deleted_at` | `content_hash` phục vụ phát hiện trùng (PQ-03); xóa mềm ngắn hạn rồi xóa cứng, hoặc xóa cứng ngay `[TBD: OQ-009]` |
| `chunks` | `id`, `document_id`, `page`, `ordinal`, `text`, `embedding` (vector), `tsv` (chỉ mục từ khóa) | Xóa theo `document_id` khi xóa tài liệu; mọi truy vấn lọc `documents.status = READY` |
| `processing_jobs` | `id`, `document_id`, `state` ∈ {QUEUED, RUNNING, DONE, FAILED}, `attempts`, `last_error`, `updated_at` | Dùng làm hàng đợi (D-05) |
| `conversations` | `id`, `user_id`, `started_at` | Ngữ cảnh chỉ trong phiên; không có tính năng xem lịch sử nhiều phiên (BRD §5.3) |
| `messages` | `id`, `conversation_id`, `role`, `kind` ∈ {ANSWER, NOT_FOUND, ERROR}, `text`, `error_type`, `latency_ms`, `created_at` | `text` chỉ lưu khi chính sách cho phép `[TBD: OQ-009]`; nếu không, chỉ lưu metadata |
| `citations` | `message_id`, `chunk_id`, `document_id`, `page`, `position` | `page` là bản sao tại thời điểm trả lời, để trích dẫn không đổi dù chỉ mục thay đổi |
| `feedback` | `message_id`, `user_id`, `rating`, `comment`, `updated_at` | Khóa `(message_id, user_id)`: một đánh giá hiệu lực mỗi người (UC-13) |
| `analytics_events` | `id`, `name`, `user_ref`, `session_id`, `properties` (JSON), `occurred_at` | Danh sách sự kiện theo PRD §5.2; `user_ref` băm/ẩn danh theo OQ-009; không chứa nội dung |
| `audit_log` | `id`, `actor`, `action`, `target`, `occurred_at` | Đăng nhập thành công/thất bại, upload, xóa, truy cập bị từ chối |

**Lưu giữ & bảo vệ:** PDF gốc lưu trong DE-FS; mã hóa khi lưu và phân quyền truy cập tệp theo ứng dụng `[Proposed]`; sao lưu CSDL và kho tệp `[TBD]`. Thời gian lưu giữ, quyền xóa vĩnh viễn `[TBD: OQ-009]`. Dữ liệu tăng theo `[TBD: OQ-004]`.

**Vòng đời chỉ mục:** thêm tài liệu → chỉ mục tăng; xóa tài liệu → xóa `chunks` trong cùng giao dịch với `documents`, để câu hỏi ngay sau đó không còn thấy nội dung (AC-005).

### 3.6 Interface View

**Concerns:** CN-05, CN-06, CN-10. Giao diện bên ngoài là REST/JSON qua HTTPS, xác thực bằng phiên (cookie an toàn, `HttpOnly`, `SameSite`) `[Proposed]`. Chi tiết OpenAPI sẽ có ở bước API design; dưới đây là hợp đồng mức thiết kế.

| Method | Path | Mô tả | Quyền | UC / BR |
|---|---|---|---|---|
| POST | `/auth/login` | Đăng nhập (hoặc bắt đầu OIDC) | Công khai | UC-01 / BR-014 |
| POST | `/auth/logout` | Kết thúc phiên | Đã đăng nhập | UC-01 |
| GET | `/me` | Người dùng + vai trò hiện tại | Đã đăng nhập | UC-01 |
| POST | `/documents` | Upload một hoặc nhiều PDF; `202` kèm `documentId` cho từng file, hoặc lỗi theo từng file | BD | UC-02 / BR-001, 002 |
| GET | `/documents` | Danh sách + trạng thái + lý do | BD | UC-05 / BR-004 |
| POST | `/documents/{id}/retry` | Xử lý lại tài liệu lỗi xử lý | BD | UC-04 |
| DELETE | `/documents/{id}` | Xóa tài liệu | BD (phạm vi `[TBD: OQ-010]`) | UC-06 / BR-005 |
| GET | `/documents/{id}/file` | Truyền PDF cho Source Viewer (hỗ trợ range/trang) | BD | UC-12 |
| POST | `/conversations` | Bắt đầu phiên mới (xóa ngữ cảnh) | BD | UC-11 |
| POST | `/conversations/{id}/messages` | Gửi câu hỏi → `{kind, text, citations[{documentId, documentName, page}], messageId}` | BD | UC-07…10 / BR-006…013 |
| PUT | `/messages/{id}/feedback` | Đặt/đổi đánh giá | BD | UC-13 / BR-016 |
| GET | `/stats/weekly` | Thống kê theo tuần | MANAGER | UC-14 / BR-017 |
| POST | `/events` | Nhận sự kiện analytics từ client (danh sách đóng) | Đã đăng nhập | PRD §5.2 |
| GET | `/healthz` | Kiểm tra sống/sẵn sàng | Nội bộ | CN-12 |

**Mô hình lỗi chuẩn:** `{ "error": { "code", "message", "details?" , "correlationId" } }`. Mã lỗi chính:

| Code | HTTP | Ý nghĩa | Tương ứng |
|---|---|---|---|
| `AUTH_REQUIRED` / `FORBIDDEN` | 401 / 403 | Chưa xác thực / không đủ quyền | AC-014 |
| `NOT_A_PDF`, `FILE_TOO_LARGE`, `TOO_MANY_PAGES`, `LIBRARY_FULL` | 422 / 413 | Từ chối trước xử lý | PRD I-1, I-3 |
| `QUESTION_EMPTY` / `QUESTION_TOO_LONG` | 422 | Câu hỏi không hợp lệ | I-5, I-6 |
| `AI_TIMEOUT`, `AI_QUOTA`, `AI_UNAVAILABLE` | 504 / 503 | Lỗi dịch vụ AI, **không** được trả thành NOT_FOUND | N-3, N-6 |
| `NO_READY_DOCUMENTS` | 409 | Chưa có tài liệu sẵn sàng | E-1, E-2 |
| `DOCUMENT_GONE` | 410 | Tài liệu nguồn đã bị xóa | UC-12 E1 |

`NOT_FOUND` (không có thông tin trong kho) là *kết quả hợp lệ* (HTTP 200, `kind=NOT_FOUND`), không phải lỗi.

**Giao diện tới hệ thống ngoài:** xem Ports ở §3.2. Dữ liệu gửi qua `LlmPort`: câu hỏi độc lập + các đoạn bằng chứng (văn bản, kèm mã đoạn); *không* gửi tên người dùng hay file gốc. Qua `EmbeddingPort`: văn bản đoạn/câu hỏi.

### 3.7 State Dynamics View

**Concerns:** CN-06. Hai thành phần có trạng thái rời rạc.

**Trạng thái tài liệu (Document)**

```mermaid
stateDiagram-v2
    [*] --> PROCESSING: upload hợp lệ
    PROCESSING --> READY: trích xuất + lập chỉ mục xong
    PROCESSING --> UNUSABLE: scan / mật khẩu / hỏng / xử lý thất bại
    UNUSABLE --> PROCESSING: retry (chỉ khi lỗi xử lý)
    READY --> [*]: xóa
    UNUSABLE --> [*]: xóa
    PROCESSING --> [*]: xóa (hủy job)
```

Bất biến: chỉ tài liệu `READY` xuất hiện trong truy xuất và trích dẫn (BR-003, AC-103.3). Upload bị từ chối trước xử lý (không phải PDF, quá lớn, kho đầy) không tạo bản ghi `documents`.

**Trạng thái xử lý một câu hỏi (Message)**

```mermaid
stateDiagram-v2
    [*] --> RECEIVED: câu hỏi hợp lệ
    RECEIVED --> RETRIEVING
    RETRIEVING --> NOT_FOUND: không đoạn nào qua ngưỡng
    RETRIEVING --> COMPOSING: có bằng chứng
    COMPOSING --> NOT_FOUND: INSUFFICIENT_EVIDENCE hoặc trích dẫn không hợp lệ
    COMPOSING --> ANSWERED: trích dẫn hợp lệ
    RETRIEVING --> ERROR: lỗi truy xuất
    COMPOSING --> ERROR: lỗi/timeout/quota AI
    ANSWERED --> [*]
    NOT_FOUND --> [*]
    ERROR --> [*]
```

`ERROR` là trạng thái riêng, không bao giờ đồng nhất với `NOT_FOUND` (PRD N-3).

### 3.8 Algorithm View

**Concerns:** CN-01, CN-02. Tham số đánh dấu `[Initial]` phải hiệu chỉnh trên bộ câu hỏi chuẩn.

**A1 — Xử lý tài liệu (DE-ING)**

```
input: documentId
1. mở file; nếu không đọc được hoặc hỏng           → UNUSABLE(corrupt)
2. nếu có mật khẩu                                   → UNUSABLE(password)
3. với mỗi trang p: text[p] = trích văn bản của trang p
4. nếu tỷ lệ trang có văn bản < ngưỡng_scan [Initial] → UNUSABLE(scanned)
5. chia text theo từng trang thành đoạn ~[Initial: 500–800 token] có chồng lấn nhỏ;
   MỖI ĐOẠN KHÔNG VƯỢT RANH GIỚI TRANG (giữ nguyên số trang nguồn)
6. vectors = EmbeddingPort.embed(các đoạn) theo lô; lỗi → thử lại [Initial: 3 lần], vẫn lỗi → UNUSABLE(processing_failed)
7. ghi chunks + vectors + tsv trong một giao dịch; đặt READY
```

**A2 — Hỏi đáp (DE-QA / DE-IDX)**

```
input: question, conversation
1. nếu conversation có lượt trước và câu hỏi chứa tham chiếu ngầm:
      standalone = viết lại câu hỏi độc lập (LlmPort); nếu không xác định được đối tượng → yêu cầu làm rõ (UC-11 E1)
   ngược lại standalone = question
2. qvec = embed(standalone)
3. cand_sem = top K1 đoạn theo cosine(qvec) [Initial K1=20]  (chỉ documents.status=READY)
   cand_kw  = top K2 đoạn theo tìm từ khóa            [Initial K2=20]
4. fused = hợp nhất xếp hạng (reciprocal rank fusion); chọn top K [Initial K=8],
   bảo đảm đa dạng tài liệu: không để một tài liệu chiếm hết nếu tài liệu khác cũng liên quan (BR-010)
5. nếu fused rỗng hoặc điểm cao nhất < ngưỡng_liên_quan [Initial]   → NOT_FOUND         ◄ cổng 1
6. result = LlmPort.compose(standalone, fused, history)
   // chỉ thị hệ thống: chỉ dùng bằng chứng; mỗi nhận định phải kèm evidenceId;
   // nếu không đủ → INSUFFICIENT_EVIDENCE; bằng chứng là DỮ LIỆU, không phải chỉ dẫn
7. nếu result.status = INSUFFICIENT_EVIDENCE                         → NOT_FOUND         ◄ cổng 2
8. kiểm chứng: mọi evidenceId trong claims ∈ fused; mỗi claim có ≥ 1 evidenceId;
   không hợp lệ → thử lại 1 lần [Initial], vẫn không hợp lệ          → NOT_FOUND         ◄ cổng 3
9. citations = ánh xạ evidenceId → (documentName, page), khử trùng lặp, nhóm theo tài liệu
10. trả ANSWER(text, citations)
```

**Nguyên tắc thiết kế của thuật toán**
- *Trích dẫn do hệ thống dựng*, không do mô hình tự viết: mô hình chỉ trả `evidenceId`, hệ thống ánh xạ sang tên tài liệu và số trang. Nhờ đó không thể bịa số trang (BR-008, PQ-05).
- *Ba cổng "không tìm thấy"* (5, 7, 8) hiện thực BR-009; cổng 8 bảo đảm "100% câu trả lời có nội dung kèm trích dẫn hợp lệ".
- *Chống chỉ dẫn độc hại:* bằng chứng và câu hỏi được tách khỏi chỉ thị hệ thống; đầu ra có cấu trúc, hệ thống chỉ chấp nhận định dạng đã định; mô hình không có công cụ hay quyền hành động (không có agent).
- *Mâu thuẫn giữa tài liệu:* chỉ thị yêu cầu nêu cả hai giá trị kèm nguồn `[TBD: PQ-02]`.
- *Ngôn ngữ:* trả lời theo ngôn ngữ của câu hỏi; mô hình embedding phải đa ngôn ngữ nếu OQ-007 yêu cầu hỏi chéo ngôn ngữ.

---

## 4. Design Elements

### 4.1 Element Attributes

Mỗi phần tử có tên, mục đích và mô tả chức năng ở bảng §3.1 (cột *Element*, *Responsibility*). Bảng bổ sung các thuộc tính thiết kế:

| ID | Dữ liệu sở hữu | Giao diện cung cấp | Lỗi tiêu biểu & xử lý |
|---|---|---|---|
| DE-IAM | `users`, phiên, `audit_log` (đăng nhập) | `/auth/*`, `/me`; kiểm tra quyền cho API | Sai thông tin → `AUTH_REQUIRED`, ghi audit |
| DE-DOC | `documents`, `processing_jobs` (tạo) | `/documents*` | Từ chối sớm; mất kết nối → file không kẹt `PROCESSING` (job có hạn thời gian) |
| DE-ING | `chunks` (ghi) | Không có API; nhận job | Thử lại có giới hạn rồi `UNUSABLE` |
| DE-IDX | `chunks` (đọc) | `retrieve(query, k)` nội bộ | Lỗi → `ERROR` ở DE-QA |
| DE-QA | `conversations`, `messages`, `citations` | `/conversations*` | Phân loại ANSWER / NOT_FOUND / ERROR |
| DE-FB | `feedback` | `/messages/{id}/feedback` | Ghi thất bại → báo, cho thử lại |
| DE-ANA | `analytics_events` | `/events`, `/stats/weekly` | Mất sự kiện không ảnh hưởng nghiệp vụ chính |
| DE-LLM | Cấu hình hạn mức, bộ đếm token | `LlmPort` | Xem §3.2 lỗi chuẩn hóa |
| DE-EMB | — | `EmbeddingPort` | Thử lại có giới hạn |

### 4.2 Resource Allocation

Dung lượng thực tế phụ thuộc OQ-004 (số tài liệu/trang) và OQ-008 (số người dùng); chưa có, nên bảng dưới là *cách phân bổ*, không phải kích cỡ.

| Tài nguyên | Phần tử sử dụng | Phân bổ thiết kế | Cách xác định kích cỡ |
|---|---|---|---|
| CPU | DE-ING (trích văn bản), API | Tách tiến trình worker khỏi tiến trình API để upload nặng không làm chậm hỏi đáp | Đo thời gian xử lý với tài liệu cỡ tối đa `[TBD: OQ-004]` |
| GPU / bộ nhớ mô hình | DE-EMB nếu mô hình embedding tự lưu trữ | Một tiến trình embedding dùng chung cho DE-ING và DE-IDX; có thể chạy CPU nếu đủ hiệu năng | Đo thông lượng embedding với kho tối đa |
| RAM | DE-DB (chỉ mục vector) | Chỉ mục vector nên nằm gọn trong bộ nhớ của máy CSDL | Số đoạn × số chiều × kích thước phần tử |
| Lưu trữ | DE-DB, DE-FS | Tách đĩa/volume cho CSDL và kho tệp; có sao lưu | Tổng dung lượng PDF + chỉ mục `[TBD: OQ-004]` |
| Mạng ra ngoài | DE-LLM, DE-EMB (nếu ngoài) | Chỉ cho phép tên miền của nhà cung cấp được duyệt (danh sách cho phép) | Danh sách do STK-004 duyệt |
| Ngân sách token AI | DE-LLM | Hạn mức theo ngày/người dùng; đo token mỗi câu hỏi | `[TBD: OQ-013]` |
| Đồng thời xử lý tài liệu | DE-ING | Số worker và số job song song có giới hạn cấu hình, mặc định thấp `[Initial]` | Theo thời gian chờ chấp nhận được trước khi "Sẵn sàng" `[TBD]` |

---

## 5. Design Rationale

### 5.1 Decision Documentation

| ID | Quyết định | Lý do | Concern | Phụ thuộc |
|---|---|---|---|---|
| D-01 | **Modular monolith** + một worker cùng codebase | MVP (CON-001), đội nhỏ, ít thành phần để vận hành; ranh giới module (§3.3) giữ khả năng tách sau | CN-10, CN-12 | — |
| D-02 | **CSDL quan hệ có tìm kiếm vector** cho dữ liệu nghiệp vụ + đoạn + vector + từ khóa | Một kho duy nhất, giao dịch xóa tài liệu và đoạn nhất quán (AC-005), ít thành phần vận hành; quy mô MVP `[TBD: OQ-004]` không cần hệ vector chuyên dụng | CN-06, CN-12 | OQ-004 |
| D-03 | **Truy xuất kết hợp ngữ nghĩa + từ khóa** | Câu hỏi nghiệp vụ thường chứa mã/tên riêng/số liệu mà vector khó khớp; từ khóa bổ trợ | CN-01 | OQ-007 |
| D-04 | **Ports & adapters** cho LLM, embedding, xác thực, tệp | Nhà cung cấp AI chưa chốt (OQ-009); thay adapter không đổi lõi | CN-04, CN-10 | OQ-009 |
| D-05 | **Hàng đợi công việc lưu trong CSDL** thay vì hệ thống message riêng | Giảm thành phần vận hành; đủ cho lưu lượng upload của một đội; chuyển sang hệ thống hàng đợi chuyên dụng khi cần | CN-12 | OQ-004 |
| D-06 | **Trích dẫn do hệ thống dựng và kiểm chứng**, mô hình chỉ trả mã bằng chứng; ba cổng "không tìm thấy" | Đáp ứng trực tiếp BR-008, BR-009, RSK-001; số trang không thể bịa | CN-01, CN-02 | — |
| D-07 | **Upload bất đồng bộ + trạng thái rõ ràng** | Xử lý tài liệu có thể lâu; người dùng phải thấy "Đang xử lý" và biết khi nào dùng được (BR-003, BR-004) | CN-06, CN-07 | — |
| D-08 | **Embedding chạy trong hạ tầng của tổ chức** `[Proposed]`, chỉ đoạn liên quan được gửi tới dịch vụ AI | Giảm phơi nhiễm dữ liệu qua TB-2; tài liệu toàn văn không rời hạ tầng | CN-04 | OQ-009 |
| D-09 | **Kho dùng chung một tập tài liệu** cho đội BD, mô hình dữ liệu giữ `uploaded_by` | Phương án đơn giản nhất, khớp BRU-003 chưa chốt; đổi sang kho riêng theo người/dự án chỉ cần thêm phạm vi vào truy vấn | CN-05 | OQ-010 |
| D-10 | **Trả lời không streaming trong MVP** | Cần kiểm chứng trích dẫn *trước khi* hiển thị (cổng 8); streaming trước khi kiểm chứng sẽ phá bảo đảm grounded. Có thể bổ sung sau cho phần văn bản đã kiểm chứng | CN-01, CN-03 | OQ-006 |
| D-11 | **Không dùng agent/công cụ tự động** cho mô hình AI | Giảm bề mặt tấn công prompt injection; mô hình chỉ nhận và trả văn bản có cấu trúc | CN-04 | — |

### 5.2 Alternatives Considered

| Quyết định | Phương án bị loại | Lý do loại |
|---|---|---|
| D-01 | Microservices (mỗi module một dịch vụ) | Chi phí vận hành và tích hợp quá lớn cho MVP một đội, không có yêu cầu mở rộng ngang độc lập (OQ-004) |
| D-02 | CSDL vector chuyên dụng riêng + CSDL quan hệ | Thêm một thành phần, mất giao dịch chung khi xóa tài liệu; chỉ cần khi quy mô vượt khả năng một nút |
| D-02/D-03 | Chỉ tìm kiếm từ khóa | Không xử lý được câu hỏi diễn đạt khác với văn bản |
| D-03 | Chỉ vector | Yếu với mã hợp đồng, tên riêng, số liệu |
| D-05 | Hệ thống message broker riêng | Không cần ở quy mô MVP |
| D-06 | Cho mô hình tự viết tên tài liệu và số trang | Có thể bịa trích dẫn, trái BR-008 |
| D-07 | Xử lý đồng bộ ngay trong request upload | File lớn dễ hết thời gian; không phản ánh được trạng thái từng file |
| D-08 | Gửi toàn bộ PDF tới dịch vụ AI để hỏi trực tiếp | Dữ liệu rời hạ tầng nhiều hơn, khó giới hạn phạm vi theo kho và khó trích dẫn trang chính xác, chi phí cao theo kích thước tài liệu |
| Mô hình AI | Tinh chỉnh (fine-tune) mô hình trên tài liệu | Tài liệu thay đổi thường xuyên, không có cách xóa chọn lọc, không có trích dẫn nguồn |
| OCR trong MVP | Đưa OCR vào ngay | Hoãn theo BRD §5.3; xem R-02. Kiến trúc để chỗ: bước 4 của A1 có thể gọi OCR thay vì `UNUSABLE(scanned)` |

### 5.3 Assumptions & Constraints (thiết kế)

| ID | Nội dung | Rủi ro nếu sai |
|---|---|---|
| R-01 | Dịch vụ AI chấp nhận trả đầu ra có cấu trúc (mã bằng chứng) và tuân thủ chỉ thị "chỉ dùng bằng chứng" ở mức đủ để đạt MET-005 | Tỷ lệ "không tìm thấy" thấp hơn target; giảm bằng ba cổng và hiệu chỉnh bằng bộ câu hỏi chuẩn |
| R-02 | PDF chủ yếu là văn bản (ASM-001); bảng biểu trích xuất được ở mức chấp nhận được | Nội dung trong bảng/ảnh không tra cứu được (RSK-003); phải đưa OCR/xử lý bảng vào phạm vi |
| R-03 | Độ trễ dịch vụ AI nằm trong ngưỡng OQ-006 | Không đạt BR-012; có thể cần mô hình nhanh hơn hoặc giảm số đoạn gửi đi |
| R-04 | Quy mô một nút CSDL đủ cho OQ-004 | Cần tách chỉ mục vector hoặc mở rộng |
| R-05 | Một kho dùng chung chấp nhận được (OQ-010) | Cần phạm vi theo người/dự án; ảnh hưởng truy vấn, quyền xóa |
| R-06 | Chính sách OQ-009 cho phép gửi *đoạn nội dung* (không phải PDF) tới dịch vụ AI | Phải chuyển sang mô hình tự lưu trữ; ảnh hưởng chất lượng, hạ tầng GPU, chi phí |
| R-07 | Có thể không cần đăng nhập nếu OQ-008 kết luận như vậy | Phải sửa BR-014 trong BRD trước; module IAM giảm còn cấp phát vai trò |

---

## 6. Traceability & QA

### 6.1 Requirements Traceability

**Yêu cầu → phần tử thiết kế → view**

| BR | UC | Phần tử thiết kế | View |
|---|---|---|---|
| BR-001 | UC-02 | DE-WEB-1, DE-DOC, DE-FS | 3.1, 3.4a, 3.6 |
| BR-002 | UC-02, 03 | DE-DOC (kiểm tra giới hạn), DE-ING, DE-IDX | 3.4a, 3.8 A1, 4.2 |
| BR-003 | UC-03, 04 | DE-ING (A1 bước 1–4), trạng thái `UNUSABLE` | 3.7, 3.8 A1 |
| BR-004 | UC-05 | DE-DOC, `documents.status` | 3.5, 3.6 |
| BR-005 | UC-06 | DE-DOC, xóa `chunks` cùng giao dịch | 3.5, 3.7 |
| BR-006 | UC-07 | DE-QA, DE-IDX, LlmPort | 3.4b, 3.8 A2 |
| BR-007 | UC-09 | Cổng 2 và 3, chỉ thị grounded, D-06 | 3.8 A2 |
| BR-008 | UC-09 | Dựng trích dẫn từ `evidenceId`, bảng `citations` | 3.5, 3.8 A2 bước 8–9 |
| BR-009 | UC-10 | Ba cổng "không tìm thấy" | 3.7, 3.8 A2 |
| BR-010 | UC-08 | Truy xuất đa tài liệu, đa dạng hóa top-K | 3.8 A2 bước 4 |
| BR-011 | UC-11 | Viết lại câu hỏi độc lập, `conversations` | 3.4b, 3.8 A2 bước 1 |
| BR-012 | UC-07 | Kiến trúc đồng bộ ngắn nhất, D-10, giám sát độ trễ | 2.3, 3.8 |
| BR-013 | UC-07 | Embedding đa ngôn ngữ, ngôn ngữ trả lời theo câu hỏi | 3.8, 4.2 |
| BR-014 | UC-01 | DE-IAM, DE-API (mọi route có kiểm tra quyền) | 3.6 |
| BR-015 | — | D-04, D-08, danh sách cho phép mạng, log không chứa nội dung | 1.2, 3.0, 4.2 |
| BR-016 | UC-13 | DE-FB, bảng `feedback` | 3.5, 3.6 |
| BR-017 | UC-14 | DE-ANA, `analytics_events`, `/stats/weekly` | 3.5, 3.6 |

**Concern → thiết kế**

| Concern | Nơi đáp ứng |
|---|---|
| CN-01, CN-02 | §3.8, D-06, §2.3 Accuracy |
| CN-03 | D-10, §2.3 Performance (ngưỡng `[TBD: OQ-006]`) |
| CN-04, CN-05 | §1.2 trust boundaries, §3.0, §3.6 quyền, D-04, D-08 |
| CN-06 | §3.7, D-07 |
| CN-07 | §2.4 Usability, §3.4a |
| CN-08 | §3.5 `analytics_events`, DE-ANA |
| CN-09 | DE-LLM hạn mức, §4.2 |
| CN-10, CN-11 | §3.3 quy tắc phụ thuộc, D-01, D-04 |
| CN-12 | DE-OBS, D-01, D-05 |
| CN-13 | UC-11, §3.8 A2 bước 1 |

### 6.2 Completeness Check

| Hạng mục | Kết quả |
|---|---|
| BR có phần tử thiết kế | 17/17 |
| Use case có phần tử thiết kế | 14/14 (UC-12 chưa có BR gốc; PQ-01) |
| Concern có nơi đáp ứng | 13/13 |
| Phần tử thiết kế có BR/UC truy vết | 100% (cột Trace §3.1) |
| Yêu cầu phi chức năng có số liệu đo | **Chưa đủ:** CN-01, 02, 03, 05 phụ thuộc OQ-002, OQ-006 |

**Điểm chưa quyết định được, ảnh hưởng thiết kế**

| OQ | Ảnh hưởng thiết kế |
|---|---|
| OQ-009 | Chọn nhà cung cấp AI/embedding, nơi triển khai, lưu giữ và quyền xóa dữ liệu, có lưu nội dung câu hỏi hay không → quyết định cuối D-04, D-08, `messages.text` |
| OQ-008 | Có cần DE-IAM đầy đủ và adapter OIDC hay không |
| OQ-004 | Kích cỡ hạ tầng, ngưỡng D-02, D-05 |
| OQ-006 | Ngưỡng hiệu năng; có cần xem lại D-10 |
| OQ-007 | Mô hình embedding đa ngôn ngữ, ngôn ngữ giao diện |
| OQ-010 | Phạm vi kho (D-09) |
| OQ-002, OQ-003 | Hiệu chỉnh tham số `[Initial]` ở §3.8 và nghiệm thu |
| PQ-01…PQ-06 | Xem PRD §7 |

---

## 7. Open Issues cho bước kế tiếp

1. Xác nhận các quyết định `[Proposed]` D-01…D-11 với Engineering và IT/Bảo mật.
2. Chốt OQ-009 trước khi bắt đầu hiện thực bất kỳ adapter nào.
3. Thiết kế chi tiết: OpenAPI (§3.6), schema CSDL vật lý (§3.5), sơ đồ triển khai (§4.2).
4. Dựng bộ câu hỏi chuẩn (DEP-002) để hiệu chỉnh tham số `[Initial]` trước khi chốt ngưỡng nghiệm thu.

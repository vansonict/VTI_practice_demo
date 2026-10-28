# Cấu trúc tài liệu dự án

Sắp xếp theo giai đoạn của quy trình; thứ tự số cũng là thứ tự tạo tài liệu.

| Thư mục | Giai đoạn | Nội dung |
|---|---|---|
| [01-requirements/](01-requirements/) | Yêu cầu | [BRD.md](01-requirements/BRD.md), [PRD.md](01-requirements/PRD.md), [User_Stories.md](01-requirements/User_Stories.md) (backlog cho PO, kèm ảnh màn hình), review BRD |
| [02-analysis/](02-analysis/) | Phân tích hành vi | Use case: [diagram (.drawio)](02-analysis/UseCase_ChatVoiTaiLieu.drawio), [đặc tả](02-analysis/UseCase_Specification.md), review |
| [03-architecture/](03-architecture/) | Kiến trúc | [SAD.md](03-architecture/SAD.md), review |
| [04-design/](04-design/) | Thiết kế chi tiết | [blueprint/](04-design/blueprint/) (SDD, IEEE 1016), [UI_UX_design/](04-design/UI_UX_design/) (HTML prototype + đặc tả). Sau này: API, database |
| [05-implementation/](05-implementation/) | Kế hoạch triển khai | [Implementation_Plan.md](05-implementation/Implementation_Plan.md): giai đoạn, mốc, DoD, kiểm thử; [tasks/](05-implementation/tasks/README.md): 51 task chi tiết sẵn sàng phát triển; [adr/](05-implementation/adr/README.md): quyết định kỹ thuật; [traceability.md](05-implementation/traceability.md): yêu cầu ↔ code ↔ test |
| [06-verification/](06-verification/) | Kiểm chứng (Phase 7) | [Master_Test_Plan.md](06-verification/Master_Test_Plan.md) (IEEE 829, 70 ca kiểm thử truy vết tới AC), [test-cases/](06-verification/test-cases/README.md) (mỗi ca một file, kèm nhiệm vụ agent: chạy tại http://localhost:5173, ảnh + video + báo cáo vào `test-runs/`), [Test_Case_Specification.md](06-verification/Test_Case_Specification.md) (mục lục + dữ liệu test) + [Test_Cases.xlsx](06-verification/Test_Cases.xlsx), [Test_Report_Slice1.md](06-verification/Test_Report_Slice1.md) (kết quả L0, coverage, agent review L1), review theo checklist |

Prompt và checklist nguồn nằm ở `References/` (`Analysis/`, `design/`, `verification/`). Mỗi tài liệu có file `*_Review.xlsx` cùng thư mục ghi kết quả review theo checklist.

> Thứ tự tạo thực tế: BRD → PRD → Use case → SDD (blueprint) → SAD → UI/UX. Thứ tự chuẩn là SAD trước SDD; xem ghi chú đầu [SAD.md](03-architecture/SAD.md).


**Mã nguồn:** `backend/` (Python/FastAPI), `frontend/` (React). Hướng dẫn cho người và agent viết code: [AGENTS.md](../AGENTS.md).

# Bản đồ 8 chặng — BRD đến Test Report

Nguồn: Day 10 Agentic SDLC Capstone (VTI). Mỗi chặng **một prompt sinh, một checklist chấm, một cổng**. Prompt/checklist tính từ `References/` (repo [SDLC-Prompt-Checklist](https://github.com/minhtrantrong/SDLC-Prompt-Checklist)).

| Chặng | Thư mục | Artifact | Prompt | Checklist | Cổng (điều kiện qua) | Người duyệt |
|---|---|---|---|---|---|---|
| 0 Intake | `docs/01-intake/` | `intent.md` (7 mục: Problem, Proposed outcome, Affected users, Constraints, Success measures, Out of scope, Open questions), `glossary.md`, `stakeholders.md`, `sources.md` | AI_SDLC-SOP §5.1 + prompt ngắn | 7 mục intent | Intent có **risk tier** (Low/Medium/High) | PO |
| 1 Requirements | `docs/02-requirements/` | `BRD.md` (+ `interviews/*.md`) | `Analysis/BRD_Prompt_IEEE_standard.md` (+ elicitation prompt nếu có) | `Analysis/BRD_IEEE_29148_Checklist.xlsx` | Audit **0 Fail** | Sponsor + PO |
| 2 Analysis | `docs/03-analysis/` | `PRD.md` (hoặc SRS), `USER_STORIES.md`, use case (`.drawio` + đặc tả), `traceability.md` | `Analysis/PRD_Prompt_IEEE_standard.md`, `design/useCase_prompt.md` | `PRD_IEEE_29148`, `design/UseCase_Document_UML2.0_Checklist.xlsx` | **Traceability liền** BR → FR → US | PO + Tech Lead |
| 3 Design | `docs/04-design/` | `SAD.md`, `adr/ADR-*.md`, `blueprint.md`, `diagrams/`, `api/openapi.yaml`, `data/model.md`, `UI_UX_design/` | `design/SAD_Prompt_IEEE_standard.md`, `bluePrint_design_prompt.md`, `apiDesign_prompt.md`, `databaseDesign_*_prompt.md`, `UI-UX-Design_prompt.md`, `<loại>Diagram_prompt.md` | `SAD_IEEE_1016`, `BluePrint_Design_IEEE_1016_2009`, `API_Design_IEEE-1016-2009`, `Database_Design`, `UI_UX_Design_IEEE-1016-2009`, `<Loại>_Diagram_UML2.0` | **0 mâu thuẫn chặn** sau audit chéo giữa các view | Architect + Tech Lead (+ IT/Bảo mật; PO cho UI/UX) |
| 4 Planning | `docs/05-planning/` | `PLAN.md`, `tasks/T-*.md` | prompt planning của khoá | task DoD + traceability | Mọi task có truy vết, phụ thuộc, DoD | PO + Tech Lead |
| 5 Build | mã nguồn + PR | commit + PR | prompt task + `CLAUDE.md`/`AGENTS.md` | `Code_Review_IEEE_1028` | **Test xanh thật** (chạy lại được) | Tech Lead; Reviewer ≠ tác giả |
| 6 Test | `docs/07-verification/` | `TEST_PLAN.md`, `TEST_CASES.md` (hoặc `test-cases/TC-*.md`), `RTM.md`, `evidence/` (hoặc `test-runs/`) | `verification/testPlan_prompt.md` | `verification/Test_Plan_IEEE_829_Checklist.xlsx` | **RTM có bằng chứng** cho từng TC | QA Lead |
| 7 Report | `docs/07-verification/` | `TEST_REPORT.md` | prompt test report (IEEE 829) | IEEE 829 + evidence log | **GO/NO-GO có ký** của con người; số liệu khớp bằng chứng; nêu rõ điều chưa kiểm được | Sponsor/PO + QA Lead |

**Ngoài 8 chặng (vận hành sau capstone):** Review chính thức (PR, reviewer ≠ tác giả), Release (con người bấm deploy), Operate, Decommission — xem master prompt.

**Ghi chú thực tế (dự án mẫu):**
- Repo mẫu dùng `docs/01-requirements … 06-verification`; repo mới nên theo bảng trên. Giữ cấu trúc đang có của repo, không đổi giữa chừng.
- `SAD_prompt.md` bị cắt, `SAD_Prompt_with_template_.md` cần template ngoài → dùng `SAD_Prompt_IEEE_standard.md`. `testPlan_prompt.md` bị cắt ở §6.2.
- Prompt không có trong `References/` → nói rõ, viết prompt 6 khối theo chuẩn tương ứng (IEEE 29148 / 1016 / 829 / 1028, UML 2.0), lưu vào `docs/prompts/`.

## Nghiệm thu cuối (Day 10)

| Tiêu chí | Trọng số | Mức đạt | Cách kiểm |
|---|---|---|---|
| Đủ artifact | 20% | 8/8 đúng thư mục, có owner + ngày | `ls docs/` |
| Truy vết | 20% | BR → FR → US → TC → evidence liền mạch | `RTM.md` |
| Checklist | 20% | 0 Fail; Partial có owner + hạn | file audit |
| Bằng chứng | 20% | log/ảnh mở được, tái lập được | `evidence/` |
| Prompt tái dùng | 10% | nằm trong repo, người khác chạy lại được | `docs/prompts/` hoặc skill |
| Harness | 10% | ≥ 1 skill, ≥ 1 sub-agent, memory gọn | `.claude/` |

Demo: mở một file bất kỳ, truy từ BR đến test case và bằng chứng trong < 2 phút.

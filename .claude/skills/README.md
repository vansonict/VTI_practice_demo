# Harness Agentic SDLC cho người mới

Bộ skill và sub-agent của dự án (Claude Code tự nạp từ `.claude/` khi mở repo). Đúc kết từ dự án "Chat với tài liệu" và tài liệu **Day 10 — Agentic SDLC Capstone** (8 chặng BRD → Test Report; mỗi chặng một prompt, một checklist, một cổng). Quy trình đầy đủ: [`Agentic_SDLC_Master_Prompt.md`](../../Agentic_SDLC_Master_Prompt.md).

| Thành phần | Loại | Dùng khi | Gọi thử |
|---|---|---|---|
| [sdlc-phase](sdlc-phase/SKILL.md) | Skill | Làm một chặng 0–7: chuẩn bị prompt 6 khối → Generate → Audit → Fix → cổng | "Làm chặng 1: tạo BRD theo @References/Analysis/BRD_Prompt_IEEE_standard.md" |
| [sdlc-checklist-review](sdlc-checklist-review/SKILL.md) | Skill | Chấm artifact theo checklist .xlsx (Pass/Partial/Fail), ghi bản sao | "Review SAD theo @References/design/SAD_IEEE_1016_Checklist.xlsx" |
| [sdlc-traceability](sdlc-traceability/SKILL.md) | Skill | Lập/kiểm RTM BR → FR → US → TC → evidence, tìm mồ côi, chuẩn bị demo | "Kiểm truy vết, BR nào chưa có test?" |
| [sdlc-approval-gate](sdlc-approval-gate/SKILL.md) | Skill | Cuối chặng: kiểm điều kiện cổng, Gate Summary, hỏi người duyệt, ghi `docs/APPROVALS.md` | "Trình PO duyệt chặng 2" |
| [sdlc-test-run](sdlc-test-run/SKILL.md) | Skill | Chạy ca TC-* có video/ảnh/network, báo cáo; tổng hợp TEST_REPORT | "Chạy TC-201-01 và tạo test report" |
| [sdlc-auditor](../agents/sdlc-auditor.md) | Sub-agent | Chấm checklist / audit truy vết / audit chéo trong context riêng (người viết ≠ người chấm) | Skill khác tự giao; hoặc "dùng sdlc-auditor chấm BRD" |

Gõ `/<tên-skill>` để gọi trực tiếp, hoặc mô tả việc cần làm — Claude tự chọn.

**Một chặng điển hình:** `sdlc-phase` → (Audit) `sdlc-auditor` + `sdlc-checklist-review` → Fix → `sdlc-traceability` → `sdlc-approval-gate` → dừng chờ người duyệt.

**Bốn lớp harness (Day 10):** Memory (`CLAUDE.md`/`AGENTS.md` — luật dự án) · Skill (quy trình) · MCP (`.mcp.json` — chỉ server cần) · Sub-agent (chia việc). Hook (`.claude/settings.json`) giữ luật cứng — chưa cấu hình trong repo này.

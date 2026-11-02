---
name: sdlc-phase
description: Chạy một chặng của Agentic SDLC (0 Intake, 1 Requirements/BRD, 2 Analysis/PRD-User story-Use case, 3 Design/SAD-ADR-Blueprint-API-DB-UI/UX-sơ đồ, 4 Planning/PLAN-task, 5 Build/commit-PR, 6 Test/test plan-case-RTM, 7 Report/test report) theo vòng Generate → Audit → Fix (SPECIFY→GENERATE→VERIFY→REFINE), mỗi artifact một prompt + một checklist + một cổng người duyệt. Dùng skill này bất cứ khi nào người dùng muốn tạo hoặc làm lại một tài liệu SDLC (BRD, PRD, SRS, user story, use case, SAD, blueprint, ADR, OpenAPI, CSDL, UI/UX, plan, task, test plan, test report), nói "làm chặng/phase X", "bước tiếp theo", "tạo … theo @References/…", hoặc là người mới hỏi bắt đầu dự án từ đâu — kể cả khi họ không nhắc tới chữ "phase".
---

# Chạy một chặng Agentic SDLC

Mỗi chặng tạo artifact trong `docs/` (không phải trong chat — phiên sau chỉ đọc file), tự chấm theo checklist, rồi **dừng chờ con người duyệt**. Agent không tự baseline, không tự duyệt, không tự kết luận GO.

Quy trình đầy đủ (luật, thư mục, người duyệt, bài học): [`Agentic_SDLC_Master_Prompt.md`](../../../Agentic_SDLC_Master_Prompt.md) ở gốc repo. Bản đồ 8 chặng (artifact, prompt, checklist, cổng): [references/phase-map.md](references/phase-map.md).

## Năm nguyên tắc (Day 10)

1. **Artifact-first** — kết quả nằm trong `docs/`; chat chỉ để trao đổi.
2. **Một cặp cho một artifact** — prompt sinh bản nháp, checklist chấm. Không có checklist thì không có bằng chứng chất lượng.
3. **Truy vết bằng ID** — BR → FR → US → TC → evidence; đứt ở đâu sửa ở đó.
4. **Cổng con người** — agent chuẩn bị, con người quyết.
5. **Bằng chứng thật** — log, ảnh, output lệnh; lời agent không phải bằng chứng.

## 1. Xác định đang ở đâu

1. Đọc `docs/README.md` và `docs/APPROVALS.md` (nếu có). Xác định chặng cần làm.
2. Kiểm cổng vào: artifact chặng trước có chưa, đã có dòng **Approve** trong `APPROVALS.md` chưa. Nếu chưa: nói rõ, hỏi người dùng (a) xin duyệt chặng trước bằng `sdlc-approval-gate` hay (b) làm tiếp và ghi rủi ro. Làm trên nền chưa duyệt dễ phải làm lại.
3. Tìm prompt + checklist cho artifact trong `References/` (bảng ở phase-map). Thiếu prompt → viết prompt theo mục 2 trước khi sinh.

## 2. Chuẩn bị prompt (6 khối)

Prompt phải **chạy lại được bởi người khác và cho cùng cấu trúc**. Nếu prompt chuẩn thiếu khối nào, bổ sung; lưu prompt đã dùng vào `docs/prompts/<chặng>-<artifact>.prompt.md` (có version) để tái dùng.

| Khối | Viết gì | Ví dụ |
|---|---|---|
| Vai trò | Ai, chuẩn nào, giọng nào | Senior BA, IEEE 29148 |
| Input | File cụ thể, không "tài liệu của tôi" | `docs/02-requirements/BRD.md` |
| Việc | 3–5 bước, bắt đầu bằng động từ | Tách FR/NFR, gán ID, kiểm mâu thuẫn |
| Ràng buộc | Điều cấm, ngưỡng, chuẩn | Không bịa nguồn; thiếu → OQ-xxx |
| Đầu ra | Đường dẫn + cấu trúc + ngôn ngữ | `docs/03-analysis/PRD.md` |
| Tự kiểm | Checklist + điều kiện dừng | `PRD_IEEE_29148_Checklist.xlsx`, 0 Fail |

Thiếu "Đầu ra" thì kết quả trôi vào chat; thiếu "Tự kiểm" thì không có cổng. Một prompt chỉ cho **một** artifact — không trộn BRD, SAD, test plan. Không dán cả repo hay tài liệu 100 trang: chỉ các file input cần thiết.

## 3. Vòng Generate → Audit → Fix cho từng artifact

| Bước | Làm gì | Vì sao |
|---|---|---|
| **Specify** | Đọc input đã duyệt + prompt. Liệt kê đầu vào thiếu; **hỏi thay vì đoán**. Prompt bị cắt/mơ hồ → nói rõ, nêu cấu trúc sẽ dùng. | Prompt trong References từng bị cắt giữa chừng |
| **Generate** | Sinh artifact theo prompt; ID ổn định (BR-, FR-, US-, UC-, ADR-, T-, TC-); đầu file ghi **owner + ngày + version + trạng thái Draft**; ghi truy vết về chặng trước. | Nghiệm thu đòi mỗi file có owner + ngày |
| **Audit** | Kiểm xác định trước (link hỏng, ID trùng/mồ côi, render sơ đồ/HTML), rồi chấm checklist bằng `sdlc-checklist-review` — ưu tiên giao cho sub-agent `sdlc-auditor` (context riêng, người viết ≠ người chấm). Chặng 3: **audit chéo** SAD ↔ blueprint ↔ API ↔ DB ↔ UI. | Lỗi máy tìm được thì không để người duyệt tìm |
| **Fix** | Sửa mục chưa đạt có thể sửa; mục cần quyết định → `[TBD: OQ-xxx]` có owner + hạn. Audit lại. Dừng khi **0 Fail** và mọi Partial có owner + hạn. | Đó là điều kiện cổng |

## 4. Quy tắc nội dung

- Không bịa: thiếu số liệu → `[TBD: OQ-xxx]`; suy luận → `[Unverified]`; lựa chọn agent chưa duyệt → `[Proposed]`; tham số khởi điểm → `[Initial]`.
- Quyết định thuộc con người (stack, phạm vi, cài phần mềm, dữ liệu thật, chi phí) → hỏi bằng 2–4 lựa chọn có khuyến nghị.
- Đúng người đọc: bản cho PO viết ngôn ngữ nghiệp vụ; bản cho Dev/QA đủ chi tiết kỹ thuật. Một artifact phục vụ cả hai → hai bản (vd. PRD + `USER_STORIES.md` bản PO).
- Thứ tự chặng 3: SAD → ADR → blueprint → API → DB → UI/UX → sơ đồ. Chi tiết trước kiến trúc gây trùng lặp, mâu thuẫn.
- Cập nhật `traceability.md` / `RTM.md` khi thêm ID (dùng `sdlc-traceability` để kiểm 0 orphan).
- Không sửa file gốc trong `References/`. Không tạo thư mục song song cho cùng một việc; cập nhật `docs/README.md`.
- **Không kịp thì cắt bề rộng, không cắt bằng chứng:** chọn 1 feature và chạy trọn các chặng.

## 5. Kết thúc chặng

1. Tóm tắt: artifact (link), kết quả audit (Pass / Partial / Fail), OQ mới, rủi ro.
2. Gọi `sdlc-approval-gate` để lập Gate Summary và hỏi đúng người duyệt.
3. **Dừng.** Không sang chặng sau khi chưa có quyết định. Không commit/push nếu chưa được yêu cầu.

## Chặng đặc thù

- **5 Build:** đọc `CLAUDE.md`/`AGENTS.md`; mỗi task: tiêu chí chấp nhận → test trước → code vertical slice → lint/type/test **xanh thật** → chạy app và thao tác như người dùng → commit + PR (Conventional Commits, có mã US/T). Review theo `Code_Review_IEEE_1028`. Lỗi tìm được → test hồi quy đỏ trước, xanh sau. **Không làm test xanh bằng cách sửa test.**
- **6 Test, 7 Report:** thực thi ca có bằng chứng bằng `sdlc-test-run`; RTM phải có link bằng chứng cho mỗi TC; `TEST_REPORT.md` có GO/NO-GO do con người ký.

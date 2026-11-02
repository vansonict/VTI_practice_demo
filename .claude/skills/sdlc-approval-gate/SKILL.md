---
name: sdlc-approval-gate
description: Cổng phê duyệt cuối mỗi phase Agentic SDLC — lập Gate Summary (artifact, kết quả checklist, câu hỏi mở, rủi ro, đề xuất), hỏi đúng người có trách nhiệm duyệt, ghi quyết định vào docs/APPROVALS.md và chặn việc sang phase sau khi chưa được duyệt. Dùng khi kết thúc một phase, khi người dùng nói "xin duyệt", "trình PO/sponsor/tech lead", "phê duyệt", "approve", "sign-off", "đã duyệt BRD", "ghi nhận phê duyệt", hoặc khi họ muốn sang phase tiếp theo mà phase trước chưa có phê duyệt.
---

# Cổng phê duyệt phase

Nguyên tắc: **người tạo ≠ người duyệt.** Agent chuẩn bị mọi thứ để người duyệt quyết định nhanh và đúng, rồi ghi lại quyết định — nhưng không tự duyệt, không tự suy ra "chắc là đồng ý", và không đi tiếp khi chưa có câu trả lời rõ ràng. Sổ phê duyệt là bằng chứng kiểm toán: phase sau dựa vào nó để biết nền đã ổn định chưa.

## 1. Lập Gate Summary

Đọc lại artifact của phase (không dựa vào trí nhớ) và tạo tóm tắt theo mẫu:

```markdown
## Gate Summary — Phase <N> <tên> (<ngày>)

**Đề xuất của agent:** Approve / Approve with conditions / Reject — <một câu lý do>
**Người duyệt cần:** <vai trò — tên nếu biết> (xem bảng người duyệt)

**Điều kiện cổng:** <điều kiện của chặng> → Đạt / Chưa đạt (<vì sao>)

| Artifact | Version · owner · ngày | Link | Audit |
|---|---|---|---|
| BRD | 0.2 · BA · 2026-10-20 | docs/…/BRD.md | 14 Pass · 3 Partial (có owner + hạn) · 0 Fail · 1 N/A |

**Mục chưa đạt / câu hỏi mở ảnh hưởng phase sau:** OQ-001 (owner, hạn) …
**Rủi ro nếu duyệt bây giờ:** …
**Điều kiện đề xuất (nếu Approve with conditions):** …
```

Viết bằng ngôn ngữ của người duyệt: Sponsor/PO cần giá trị, phạm vi, rủi ro; Tech Lead/Architect cần quyết định kỹ thuật và nợ kỹ thuật. Ngắn gọn: người duyệt đọc trong 2 phút.

## 2. Điều kiện cổng và người duyệt theo chặng

Kiểm điều kiện cổng **trước** khi trình duyệt; chưa đạt thì Gate Summary đề xuất Reject hoặc Approve with conditions và nói rõ vì sao.

| Chặng | Điều kiện qua cổng (Day 10) | Người duyệt bắt buộc | Tham vấn |
|---|---|---|---|
| 0 Intake | Intent đủ 7 mục, có **risk tier** | PO | Sponsor |
| 1 Requirements | Audit BRD **0 Fail**, Partial có owner + hạn | Sponsor + PO | Đại diện người dùng; IT/Bảo mật nếu dữ liệu nhạy cảm |
| 2 Analysis | **Traceability liền** BR → FR → US; P0 có Given-When-Then | PO + Tech Lead | QA Lead |
| 3 Design | **0 mâu thuẫn chặn** sau audit chéo SAD/blueprint/API/DB/UI; audit 0 Fail | Architect + Tech Lead; IT/Bảo mật (dữ liệu, xác thực, dịch vụ ngoài); PO (UI/UX) | QA Lead |
| 4 Planning | Mọi task có truy vết, phụ thuộc, DoD | PO + Tech Lead | PM |
| 5 Build (mỗi task/PR) | **Test xanh thật**, chạy lại được; review theo Code_Review_IEEE_1028 | Tech Lead; Reviewer ≠ tác giả | PO (demo) |
| 6 Test | **RTM có bằng chứng** cho mỗi TC đã chạy | QA Lead | Reviewer |
| 7 Report | `TEST_REPORT.md` có **GO/NO-GO**, số liệu khớp bằng chứng, nêu rõ điều chưa kiểm được | Sponsor/PO + QA Lead (**ký** GO/NO-GO) | Tech Lead |
| Release (sau capstone) | Artifact = commit đã review; có rollback | Release owner | Sponsor, Ops |

**GO/NO-GO là quyết định của con người.** Agent chỉ đề xuất kèm số liệu và bằng chứng; ghi "Đề xuất của agent: GO/NO-GO" chứ không ghi "Kết luận: GO".

Tên người cụ thể: lấy từ `docs/APPROVALS.md` (mục "Người duyệt") hoặc tài liệu dự án; nếu chưa có, hỏi người dùng và ghi lại.

## 3. Hỏi phê duyệt

- Hỏi bằng lựa chọn rõ ràng: **Approve** / **Approve with conditions** / **Reject (kèm yêu cầu sửa)**. Nếu công cụ hỏi lựa chọn có sẵn, dùng nó.
- Hỏi người dùng **họ có phải người duyệt đó không** hoặc họ chuyển tiếp ý kiến của ai. Ghi đúng tên/vai trò người quyết định, không ghi tên người dùng nếu họ chỉ chuyển lời.
- Một người không thể duyệt artifact do chính họ viết ở các phase yêu cầu reviewer độc lập (Phase 8): nói rõ nếu gặp trường hợp này.

## 4. Ghi vào `docs/APPROVALS.md`

Tạo file nếu chưa có (đầu file: bảng "Người duyệt theo vai trò" để điền tên). Thêm một dòng cho mỗi quyết định, không sửa dòng cũ:

| Phase | Artifact (version) | Người duyệt (vai trò) | Quyết định | Điều kiện / ghi chú | Ngày | Commit |
|---|---|---|---|---|---|---|

Sau đó:
- **Approve:** đổi trạng thái artifact sang *Baseline* (bảng Document control/Version của tài liệu), thêm dòng version history.
- **Approve with conditions:** mỗi điều kiện thành OQ hoặc task có owner + hạn; nhắc lại ở Gate Summary phase sau.
- **Reject:** liệt kê yêu cầu sửa; quay lại REFINE (skill `sdlc-phase`). Không sang phase sau.
- Commit hash: điền nếu artifact đã được commit; nếu chưa, ghi "chưa commit" — không tự commit khi người dùng chưa yêu cầu.

## 5. Khi người dùng muốn bỏ qua cổng

Nếu người dùng muốn làm tiếp khi phase trước chưa duyệt: nói ngắn gọn rủi ro (phải làm lại nếu phase trước đổi), ghi dòng "Tiếp tục chưa duyệt — chấp nhận rủi ro bởi <tên>" vào `APPROVALS.md`, rồi làm theo yêu cầu. Quyết định là của họ; việc của agent là để lại dấu vết.

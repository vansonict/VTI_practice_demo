---
name: sdlc-test-run
description: Thực thi một ca kiểm thử (TC-*) trên ứng dụng đang chạy (mặc định http://localhost:5173) và nộp báo cáo kèm bằng chứng — video toàn phiên, ảnh sau mỗi bước, request/response API, log — vào docs/…/test-runs/<ngày>_<TC>/. Dùng khi người dùng nói "chạy TC-…", "test ca …", "thực thi test case", "làm ví dụ cho TC-…", "tạo test report có evidence", "kiểm thử trên giao diện", hoặc ở Phase 7 Verify. Cũng dùng khi cần viết bước chi tiết cho một ca khung trước khi thực thi.
---

# Thực thi ca kiểm thử có bằng chứng

Không có bằng chứng thì không có Pass. Mục đích của skill là để người duyệt (QA Lead) tin được kết quả mà không phải chạy lại: mọi kết luận gắn với ảnh, video, network hoặc log cụ thể.

Trong repo mẫu, quy trình chi tiết nằm ở `docs/06-verification/test-cases/README.md`, helper ở `frontend/e2e/evidence.mjs`, ví dụ hoàn chỉnh `frontend/e2e/run-TC-101-02.mjs` → `docs/06-verification/test-runs/2026-10-28_TC-101-02/report.md`. Đọc chúng trước khi bắt đầu; nếu repo khác chưa có, dùng các file đó làm mẫu để tạo.

## 1. Đọc ca kiểm thử

- Mở `test-cases/<TC>.md`: điều kiện trước, dữ liệu, bảng bước gốc, bảng thao tác giao diện (U1, U2…), chế độ thực thi (Giao diện + API / API / Lệnh–unit test).
- **Ca khung** (chưa có bước chi tiết, chờ task/OQ): không thực thi. Nếu task đã xong, viết bước chi tiết trước theo cấu trúc ca mẫu rồi mới chạy; nếu vẫn bị chặn, báo "Bị chặn" và lý do.

## 2. Môi trường sạch

Mỗi ca một thư mục dữ liệu mới, để kết quả không phụ thuộc ca trước:

```bash
RUN_DATA=$(mktemp -d)
cd backend && uv run python -m tests.make_test_data "$RUN_DATA/td"
export CWD_DATABASE_URL="sqlite:///$RUN_DATA/app.db" CWD_FILE_STORE_DIR="$RUN_DATA/files" PYTHONIOENCODING=utf-8
# CWD_LLM_FAKE_MODE=<chế độ> nếu ca yêu cầu
uv run uvicorn app.main:app --port 8000 &   ;   uv run python -m app.worker &   # bỏ worker nếu ca yêu cầu
cd ../frontend && npm run dev &
```

Kiểm `http://localhost:8000/readyz` = 200 và trang chủ mở được trước khi chạy. Lần đầu trên máy: `npx playwright-core install ffmpeg` (ghi video). Ghi commit (`git rev-parse --short HEAD`, thêm "+ thay đổi chưa commit" nếu working tree bẩn), biến `CWD_*`, phiên bản Python/Node/Chrome vào `logs/env.txt`.

## 3. Viết và chạy script

Tạo `frontend/e2e/run-<TC>.mjs` dùng `startSession(tcId)` của helper:

- `await s.step("U1", "mo-ta-ngan")` **sau mỗi bước** → ảnh + mốc thời gian video.
- `await s.api(method, path, body)` cho bước API → tự lưu `network/`.
- Đọc giá trị thực tế từ DOM/JSON và in ra (badge, số đếm, thời gian, mã lỗi) — báo cáo cần số liệu thật, không chép lại "kết quả mong đợi".
- Với điều kiện thời gian (polling, trạng thái chờ), đo và ghi số mili-giây; kiểm "không tải lại trang" bằng đếm điều hướng.
- `await s.finish({ observations })` → `video/session.webm`, `logs/steps.json`, `logs/browser-console.log`.

Ca chỉ có lệnh/unit test: chạy lệnh "Tự động" của ca, lưu output đầy đủ vào `logs/automated.log`; ảnh/video ghi "Không áp dụng" kèm lý do.

Luôn chạy thêm phần "Tự động" của ca (pytest/vitest) và lưu vào `logs/automated.log`; chép đoạn log API/worker của phiên vào `logs/`.

## 4. Đánh giá

- So **từng bước** thực tế với kết quả mong đợi ở cả bảng bước gốc và bảng giao diện. Mở và nhìn ít nhất các ảnh then chốt trước khi kết luận.
- Sai khác → **Fail**: ảnh lỗi, console, log backend, cách tái hiện. Không sửa code để test qua; không tự đổi "Kết quả mong đợi" — ghi vào mục "Sai lệch" để người duyệt quyết định.
- Nghi ngờ lỗi chập chờn (race, timing): chạy lại 2–3 lần với cùng điều kiện và ghi tỉ lệ tái hiện.
- Chỉ sửa lỗi khi người dùng yêu cầu: commit riêng, test hồi quy **đỏ trước khi sửa, xanh sau khi sửa**, rồi chạy lại ca.
- Lỗi console không liên quan (vd. favicon 404): ghi chú mức Low, không làm ca Fail.

## 5. Báo cáo và cập nhật

1. `test-runs/<YYYY-MM-DD>_<TC>/report.md` theo `test-cases/TEST_REPORT_TEMPLATE.md`: kết luận, môi trường, bảng bước (mong đợi / thực tế / đạt / bằng chứng có link ảnh và mốc video), sai lệch, lỗi, ghi chú. Kết luận Pass gắn với mã chưa commit thì ghi rõ và đề xuất chạy lại sau commit.
2. Cập nhật dòng "Kết quả gần nhất" trong file ca, cột kết quả ở mục lục `Test_Case_Specification.md`, và **RTM/traceability** (link bằng chứng cho TC này) — dùng `sdlc-traceability` để kiểm không còn TC đã chạy mà thiếu bằng chứng.
3. Video > 10 MB: không commit, lưu nơi khác và ghi link.
4. Dừng các tiến trình đã khởi động, xóa `$RUN_DATA`.
5. Báo người dùng: kết luận, số liệu chính, link báo cáo, lỗi phát hiện. Không commit nếu chưa được yêu cầu. Phê duyệt kết quả là việc của QA Lead (skill `sdlc-approval-gate`).

## Tổng hợp thành TEST_REPORT (chặng 7)

Khi chạy xong một đợt ca, tổng hợp `TEST_REPORT.md` (IEEE 829): phạm vi, số ca Pass/Fail/Bị chặn, lỗi theo mức độ, độ phủ AC/BR từ RTM, **điều chưa kiểm được và vì sao**, rủi ro còn lại, và **đề xuất** GO/NO-GO kèm lý do. Mọi con số phải đếm được từ `test-runs/`/`evidence/` — đếm bằng script, không đếm tay. Để trống dòng ký GO/NO-GO cho con người.

Đừng làm: sửa test hoặc đổi kết quả mong đợi để "xanh"; báo Pass dựa trên test của lần chạy trước; gộp ca bị chặn vào số Pass.

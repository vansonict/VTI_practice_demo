# Ca kiểm thử — mỗi ca một file

> **Ứng dụng kiểm thử:** **http://localhost:5173** (frontend React; mọi đường dẫn `/api/*` được Vite proxy tới backend `http://localhost:8000`).
> Mục lục và dữ liệu kiểm thử: [Test_Case_Specification.md](../Test_Case_Specification.md) · Kế hoạch: [Master_Test_Plan.md](../Master_Test_Plan.md)

Mỗi file `TC-*.md` gồm hai phần:

1. **Đặc tả**: truy vết, điều kiện trước, dữ liệu, bước + kết quả mong đợi, lệnh tự động, kết quả gần nhất.
2. **Nhiệm vụ của agent**: cách thực thi trên http://localhost:5173, bằng chứng bắt buộc (ảnh chụp, video, network, log), và báo cáo phải nộp.

Có 33 ca **chi tiết** (thực thi được ngay) và 37 ca **khung** (chờ task hoặc quyết định OQ/PQ; agent không thực thi, chỉ báo cáo "Bị chặn" nếu được yêu cầu).

## 1. Quy tắc chung cho agent

- **Mỗi lần thực thi một ca tạo một báo cáo** kèm bằng chứng. Không có bằng chứng thì không được ghi Pass.
- Ca có thao tác giao diện: **ghi video toàn phiên** và **chụp màn hình sau mỗi bước** (U1, U2…). Ca chỉ có API: lưu request/response và chụp trang JSON khi là GET. Ca không có giao diện (lệnh, unit test): lưu log đầy đủ, ghi "Không áp dụng" cho ảnh/video kèm lý do.
- Chỉ dùng dữ liệu tổng hợp TD-*/Q-*. Không dùng dữ liệu thật của đội BD (BR-015).
- **Không sửa code để test qua.** Khi kết quả khác mong đợi: ghi Fail, đính kèm ảnh lỗi + `logs/browser-console.log` + log backend, mô tả cách tái hiện. Nếu người dùng yêu cầu sửa, sửa ở commit riêng kèm test hồi quy rồi chạy lại ca.
- Môi trường phải **sạch cho mỗi ca** (thư mục dữ liệu mới), trừ khi ca ghi khác.
- Agent không tự đổi "Kết quả mong đợi". Nếu cho rằng đặc tả sai, ghi vào mục "Sai lệch" của báo cáo để người duyệt quyết định.

## 2. Chuẩn bị môi trường

Lần đầu trên máy:

```bash
cd frontend && npm ci && npx playwright-core install ffmpeg   # ffmpeg dùng để ghi video
cd ../backend && uv sync
```

Mỗi lần chạy một ca (PowerShell hoặc bash; ví dụ bash):

```bash
RUN_DATA=$(mktemp -d)                                  # thư mục dữ liệu mới
cd backend
uv run python -m tests.make_test_data "$RUN_DATA/td"   # sinh TD-*/… (vd. $RUN_DATA/td/TD-02/bao_cao.pdf)
export CWD_DATABASE_URL="sqlite:///$RUN_DATA/app.db" CWD_FILE_STORE_DIR="$RUN_DATA/files" PYTHONIOENCODING=utf-8
# export CWD_LLM_FAKE_MODE=timeout                     # chỉ khi ca yêu cầu chế độ lỗi của LLM giả lập
uv run uvicorn app.main:app --port 8000 &              # API
uv run python -m app.worker &                          # worker — bỏ qua nếu ca yêu cầu "worker không chạy"
cd ../frontend && npm run dev &                        # http://localhost:5173
```

Kiểm môi trường trước khi bắt đầu: `http://localhost:8000/readyz` trả 200 và `http://localhost:5173` mở được. Ghi `git rev-parse --short HEAD` và các biến `CWD_*` đã đặt vào `logs/env.txt`.

Sau khi xong: dừng 3 tiến trình, xóa `$RUN_DATA`.

## 3. Thu thập bằng chứng

Dùng helper [`frontend/e2e/evidence.mjs`](../../../frontend/e2e/evidence.mjs) (Playwright + Chrome đã cài trên máy). Viết script cho ca trong `frontend/e2e/run-<TC>.mjs`, chạy bằng `node`. **Ví dụ hoàn chỉnh:** [run-TC-101-02.mjs](../../../frontend/e2e/run-TC-101-02.mjs) → [báo cáo mẫu](../test-runs/2026-10-28_TC-101-02/report.md).

```js
import { startSession } from "./evidence.mjs";

const s = await startSession("TC-101-02");          // tạo docs/06-verification/test-runs/<ngày>_TC-101-02/
await s.page.goto(s.baseUrl);                        // http://localhost:5173
await s.page.locator("input[type=file]").setInputFiles("<RUN_DATA>/td/TD-02/bao_cao.pdf");
await s.page.getByText("Đang xử lý").waitFor();
await s.step("U1", "tai-len-dang-xu-ly");            // screenshots/01_U1_tai-len-dang-xu-ly.png + mốc thời gian video
await s.page.getByText("Sẵn sàng truy vấn").waitFor({ timeout: 15000 });
await s.step("U2", "tu-chuyen-san-sang");
const r = await s.api("POST", "/api/v1/conversations/x/messages", { text: "hi" }); // gọi API, tự lưu vào network/
await s.finish({ verdict: "Pass" });                 // lưu video/session.webm, logs/steps.json, logs/browser-console.log
```

Helper tự động:

| Bằng chứng | Vị trí | Ghi chú |
|---|---|---|
| Video toàn phiên | `video/session.webm` | 1280×860; mốc thời gian từng bước ở `logs/steps.json` |
| Ảnh sau mỗi bước | `screenshots/NN_<bước>_<mô-tả>.png` | Toàn trang |
| Request/response `/api` | `network/NN_<METHOD>_<path>.json` | Kèm `x-correlation-id`; body file nhị phân được lược |
| Console trình duyệt | `logs/browser-console.log` | Lỗi JS, cảnh báo |

Agent tự thêm: `logs/automated.log` (output lệnh pytest/vitest của ca), `logs/env.txt`, log backend liên quan (`logs/api.log`, `logs/worker.log`, chỉ đoạn của phiên). Không đưa nội dung tài liệu thật vào bằng chứng.

**Dung lượng:** video một ca thường dưới 1 MB. Nếu video lớn hơn 10 MB, không commit; lưu ở nơi lưu trữ của đội và ghi link trong báo cáo.

## 4. Báo cáo

Tạo `docs/06-verification/test-runs/<YYYY-MM-DD>_<TC>/report.md` theo [TEST_REPORT_TEMPLATE.md](TEST_REPORT_TEMPLATE.md), rồi:

- Cập nhật dòng **"Kết quả gần nhất"** trong file ca: `**Pass/Fail/Một phần/Bị chặn** — <ngày>, <commit>, [báo cáo](../test-runs/<thư-mục>/report.md)`.
- Cập nhật cột kết quả trong [Test_Case_Specification.md](../Test_Case_Specification.md) §3 và [traceability](../../05-implementation/traceability.md) nếu trạng thái đổi.
- Khi chạy nhiều ca một lượt: thêm một dòng tổng hợp vào báo cáo kiểm thử của lát cắt (ví dụ [Test_Report_Slice1.md](../Test_Report_Slice1.md)).

## 5. Chế độ thực thi theo ca

| Chế độ | Ý nghĩa | Ca |
|---|---|---|
| **Giao diện + API** | Thao tác tại http://localhost:5173, ghi video + ảnh, kèm kiểm phản hồi API | 101-01, 101-02, 101-03, 103-01, 103-02, 103-03, 104-02, 104-03, 104-04, 201-01, 201-02, 201-04, 201-05, 201-06, 202-01, 203-01, 203-02, 204-01, 204-04, 204-05 |
| **API** | Không có màn hình tương ứng; gọi API qua trình duyệt, chụp JSON | 201-08, X-01, X-06 |
| **Lệnh / unit test** | Không quan sát được trên giao diện; bằng chứng là log | 103-04, 103-05, 203-03, 204-02, X-02, X-03, X-04, X-05, X-07, X-09 |

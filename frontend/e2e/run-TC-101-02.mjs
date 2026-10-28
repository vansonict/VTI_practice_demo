// Script thực thi TC-101-02 (tạm, có thể giữ làm mẫu). Dữ liệu: TD-02/bao_cao.pdf
import fs from "node:fs";
import path from "node:path";
import { startSession } from "./evidence.mjs";

const TD = process.argv[2];
const s = await startSession("TC-101-02");
const obs = {};
let navigations = 0;
s.page.on("framenavigated", (f) => { if (f === s.page.mainFrame()) navigations++; });

// U1 — mở trang, tải bao_cao.pdf lên
await s.page.goto(s.baseUrl);
await s.page.getByText("Chưa có tài liệu nào").waitFor();
await s.step("U0", "kho-trong-truoc-khi-tai-len");
const tUpload = Date.now();
await s.page.locator("input[type=file]").setInputFiles(path.join(TD, "TD-02", "bao_cao.pdf"));
const item = s.page.locator(".doc-item", { hasText: "bao_cao.pdf" });
await item.getByText("Đang xử lý").waitFor({ timeout: 5000 });
obs.u1_badge = (await item.locator(".badge").innerText()).trim();
obs.u1_ms = Date.now() - tUpload;
await s.step("U1", "dang-xu-ly");

// U2 — không tải lại trang, chờ tối đa 15 giây
await item.getByText("Sẵn sàng truy vấn").waitFor({ timeout: 15000 });
obs.u2_ms = Date.now() - tUpload;
obs.u2_badge = (await item.locator(".badge").innerText()).trim();
obs.u2_meta = (await item.locator(".doc-meta").innerText()).replace(/\s+/g, " ").trim();
obs.navigations_before_u3 = navigations;
await s.step("U2", "tu-chuyen-san-sang");

// U3 — tiêu đề cột kho
obs.u3_count = (await s.page.locator(".sidebar-title .small").innerText()).trim();
await s.step("U3", "dem-tai-lieu");

// Bước 3 của đặc tả — GET /api/v1/documents (mở trong trình duyệt để chụp JSON)
await s.page.goto(new URL("/api/v1/documents", s.baseUrl).toString());
obs.step3_json = JSON.parse(await s.page.locator("body").innerText());
await s.step("S3", "api-documents-json");

obs.network = fs.readdirSync(path.join(s.dir, "network"));
await s.finish({ observations: obs });
console.log(JSON.stringify(obs, null, 2));

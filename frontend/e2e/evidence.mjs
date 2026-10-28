/**
 * Phiên thu thập bằng chứng cho một ca kiểm thử (docs/06-verification/test-cases/README.md §3).
 *
 *   import { startSession } from "./evidence.mjs";
 *   const s = await startSession("TC-101-02");
 *   await s.page.goto(s.baseUrl);
 *   await s.step("U1", "mo-trang-chu");              // chụp screenshots/01_U1_mo-trang-chu.png + mốc thời gian video
 *   ...
 *   await s.finish({ verdict: "Pass" });             // đóng trình duyệt, lưu video, log, steps.json
 *
 * Kết quả: docs/06-verification/test-runs/<YYYY-MM-DD>_<TC>/{screenshots,video,network,logs}/
 * Trình duyệt: Chrome đã cài trên máy (channel "chrome"); đổi bằng biến CHROME_PATH nếu cần.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "playwright-core";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");

export async function startSession(tcId, { baseUrl = process.env.BASE_URL ?? "http://localhost:5173", headless = true } = {}) {
  const date = new Date().toISOString().slice(0, 10);
  const dir = path.join(repoRoot, "docs", "06-verification", "test-runs", `${date}_${tcId}`);
  for (const sub of ["screenshots", "video", "network", "logs"]) fs.mkdirSync(path.join(dir, sub), { recursive: true });

  const browser = await chromium.launch({
    headless,
    ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : { channel: "chrome" }),
  });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 860 },
    recordVideo: { dir: path.join(dir, "video"), size: { width: 1280, height: 860 } },
  });
  const page = await context.newPage();
  const started = Date.now();
  const console_ = [];
  const steps = [];
  let shot = 0;
  let call = 0;

  page.on("console", (m) => console_.push(`[${elapsed(started)}] ${m.type()}: ${m.text()}`));
  page.on("pageerror", (e) => console_.push(`[${elapsed(started)}] pageerror: ${e.message}`));
  // Ghi mọi request/response /api làm bằng chứng network
  const save = (method, url, postData, status, correlationId, body) => {
    const name = `${String(++call).padStart(2, "0")}_${method}_${new URL(url).pathname.replace(/[^\w]+/g, "_")}.json`;
    const payload = {
      at: elapsed(started),
      request: { method, url, body: summarize(postData) },
      response: { status, headers: { "x-correlation-id": correlationId }, body },
    };
    fs.writeFileSync(path.join(dir, "network", name), JSON.stringify(payload, null, 2));
  };
  const record = async (response) => {
    const req = response.request();
    if (!new URL(req.url()).pathname.startsWith("/api/")) return;
    const body = await response.json().catch(async () => response.text().catch(() => "<không đọc được>"));
    save(req.method(), req.url(), req.postData(), response.status(), response.headers()["x-correlation-id"], body);
  };
  page.on("response", (r) => void record(r));

  return {
    baseUrl,
    dir,
    page,
    context,
    /** Chụp màn hình sau một bước và ghi mốc thời gian trong video. */
    async step(id, slug, note = "") {
      const file = `${String(++shot).padStart(2, "0")}_${id}_${slug}.png`;
      await page.screenshot({ path: path.join(dir, "screenshots", file), fullPage: true });
      steps.push({ id, file: `screenshots/${file}`, videoAt: elapsed(started), note });
      return file;
    },
    /** Gọi API qua cùng trình duyệt (cookie, proxy) và lưu bằng chứng. */
    async api(method, urlPath, data) {
      const res = await page.request.fetch(new URL(urlPath, baseUrl).toString(), {
        method,
        data,
        headers: data !== undefined ? { "Content-Type": "application/json" } : undefined,
      });
      const body = await res.json().catch(() => null);
      save(method, res.url(), data === undefined ? null : JSON.stringify(data), res.status(), res.headers()["x-correlation-id"], body);
      return { status: res.status(), headers: res.headers(), body };
    },
    async finish(extra = {}) {
      const video = page.video();
      await context.close();
      await browser.close();
      if (video) fs.renameSync(await video.path(), path.join(dir, "video", "session.webm"));
      fs.writeFileSync(path.join(dir, "logs", "browser-console.log"), console_.join("\n") + "\n");
      fs.writeFileSync(path.join(dir, "logs", "steps.json"), JSON.stringify({ tcId, baseUrl, steps, ...extra }, null, 2));
      return dir;
    },
  };
}

function elapsed(t0) {
  const s = Math.round((Date.now() - t0) / 100) / 10;
  return `${Math.floor(s / 60)}:${(s % 60).toFixed(1).padStart(4, "0")}`;
}

// Multipart (file PDF) không ghi nội dung nhị phân vào bằng chứng
function summarize(postData) {
  if (!postData) return null;
  return postData.length > 2000 ? `<${postData.length} byte, đã lược>` : postData;
}

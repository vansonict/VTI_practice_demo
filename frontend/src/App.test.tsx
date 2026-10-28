import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { App } from "./App";

const processingDoc = {
  id: "d1",
  name: "bao_cao.pdf",
  sizeBytes: 10,
  pageCount: null,
  status: "PROCESSING",
  unusableReason: null,
  retryable: false,
  uploadedBy: "dev-user",
  uploadedAt: "2026-10-28T00:00:00Z",
};

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

describe("App — upload ngay khi trang vừa mở (TC-101-01/02, hồi quy 2026-10-28)", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("tài liệu vừa tải lên hiện 'Đang xử lý' dù request danh sách ban đầu trả về dữ liệu cũ sau khi upload xong", async () => {
    let releaseFirstList!: () => void;
    let listCalls = 0;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: Request) => {
        if (input.method === "POST") return json([{ fileName: "bao_cao.pdf", documentId: "d1", error: null }], 202);
        listCalls += 1;
        if (listCalls === 1) {
          // Request ban đầu: chỉ trả về (danh sách rỗng, đã cũ) sau khi upload đã xong
          await new Promise<void>((r) => (releaseFirstList = r));
          return json([]);
        }
        return json([processingDoc]);
      }),
    );
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const { container } = render(
      <QueryClientProvider client={client}>
        <App />
      </QueryClientProvider>,
    );
    const input = container.querySelector<HTMLInputElement>("input[type=file]")!;

    await userEvent.upload(input, new File(["%PDF-1.4"], "bao_cao.pdf", { type: "application/pdf" }));
    releaseFirstList();

    expect(await screen.findByText("bao_cao.pdf")).toBeInTheDocument();
    expect(screen.getByText("Đang xử lý")).toBeInTheDocument();
  });
});

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import type { DocumentDto, MessageDto } from "../api/client";
import { blockedReason } from "./ChatPanel";
import { Composer, MAX_QUESTION_CHARS } from "./Composer";
import { AnswerMessage, ErrorMessage, NotFoundMessage } from "./Messages";
import { StatusBadge } from "./StatusBadge";

const doc = (status: DocumentDto["status"]): DocumentDto => ({
  id: status,
  name: `${status}.pdf`,
  sizeBytes: 1,
  status,
  retryable: false,
  uploadedBy: "u",
  uploadedAt: "2026-10-23T00:00:00Z",
});

describe("StatusBadge (US-104)", () => {
  it.each([
    ["READY", "Sẵn sàng truy vấn"],
    ["PROCESSING", "Đang xử lý"],
    ["UNUSABLE", "Không dùng được"],
  ] as const)("hiển thị chữ cho trạng thái %s, không chỉ dựa vào màu", (status, label) => {
    render(<StatusBadge status={status} />);
    expect(screen.getByText(label)).toBeInTheDocument();
  });
});

describe("Composer (US-201)", () => {
  it("gửi bằng Enter và xóa ô nhập", async () => {
    const onSubmit = vi.fn();
    render(<Composer onSubmit={onSubmit} blockedReason={null} waiting={false} />);

    await userEvent.type(screen.getByLabelText("Câu hỏi của bạn"), "Điều khoản thanh toán?{Enter}");

    expect(onSubmit).toHaveBeenCalledWith("Điều khoản thanh toán?");
    expect(screen.getByLabelText("Câu hỏi của bạn")).toHaveValue("");
  });

  it("Shift+Enter xuống dòng, không gửi", async () => {
    const onSubmit = vi.fn();
    render(<Composer onSubmit={onSubmit} blockedReason={null} waiting={false} />);

    await userEvent.type(screen.getByLabelText("Câu hỏi của bạn"), "a{Shift>}{Enter}{/Shift}b");

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("nút Gửi bị khóa khi ô trống, khi đang chờ và khi quá dài", async () => {
    const { rerender } = render(<Composer onSubmit={vi.fn()} blockedReason={null} waiting={false} />);
    expect(screen.getByRole("button", { name: /Gửi/ })).toBeDisabled();

    await userEvent.type(screen.getByLabelText("Câu hỏi của bạn"), "hỏi");
    expect(screen.getByRole("button", { name: /Gửi/ })).toBeEnabled();

    rerender(<Composer onSubmit={vi.fn()} blockedReason={null} waiting />);
    expect(screen.getByRole("button", { name: /Gửi/ })).toBeDisabled();
  });

  it("đánh dấu lỗi khi vượt giới hạn ký tự", async () => {
    render(<Composer onSubmit={vi.fn()} blockedReason={null} waiting={false} />);
    const box = screen.getByLabelText("Câu hỏi của bạn");

    await userEvent.click(box);
    await userEvent.paste("x".repeat(MAX_QUESTION_CHARS + 1));

    expect(box).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByRole("button", { name: /Gửi/ })).toBeDisabled();
  });

  it("khóa ô nhập và giải thích khi chưa có tài liệu sẵn sàng (E-1, E-2)", () => {
    render(<Composer onSubmit={vi.fn()} blockedReason="Hãy tải lên ít nhất một tài liệu PDF để bắt đầu hỏi." waiting={false} />);

    expect(screen.getByLabelText("Câu hỏi của bạn")).toBeDisabled();
    expect(screen.getByText("Hãy tải lên ít nhất một tài liệu PDF để bắt đầu hỏi.")).toBeInTheDocument();
  });
});

describe("blockedReason", () => {
  it("phân biệt kho rỗng, đang xử lý, không có tài liệu dùng được, và sẵn sàng", () => {
    expect(blockedReason([])).toMatch(/tải lên/);
    expect(blockedReason([doc("PROCESSING")])).toMatch(/đang được xử lý/);
    expect(blockedReason([doc("UNUSABLE")])).toMatch(/dùng được/);
    expect(blockedReason([doc("UNUSABLE"), doc("READY")])).toBeNull();
  });
});

describe("Kết quả hỏi đáp (US-203, US-204)", () => {
  const answer: MessageDto = {
    id: "m1",
    conversationId: "c1",
    role: "ASSISTANT",
    kind: "ANSWER",
    text: "Khách hàng thanh toán trong 30 ngày.",
    citations: [{ documentId: "d1", documentName: "hop_dong_A.pdf", page: 7, documentDeleted: false }],
    createdAt: "2026-10-23T00:00:00Z",
  };

  it("câu trả lời luôn hiển thị tên tài liệu và số trang", () => {
    render(<AnswerMessage message={answer} />);
    expect(screen.getByText("hop_dong_A.pdf, tr.7")).toBeInTheDocument();
  });

  it("không tìm thấy và lỗi hệ thống có thông điệp khác nhau", async () => {
    const onRetry = vi.fn();
    render(
      <>
        <NotFoundMessage />
        <ErrorMessage onRetry={onRetry} />
      </>,
    );

    expect(screen.getByText(/Không tìm thấy thông tin này/)).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("không phải kết quả");
    await userEvent.click(screen.getByRole("button", { name: /Gửi lại/ }));
    expect(onRetry).toHaveBeenCalled();
  });
});

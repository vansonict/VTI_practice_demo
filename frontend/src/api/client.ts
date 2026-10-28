/** Client API sinh kiểu từ docs/04-design/api/openapi.yaml (`npm run gen:api`). */
import createClient from "openapi-fetch";

import type { components, paths } from "./schema";

export type DocumentDto = components["schemas"]["Document"];
export type UploadResultDto = components["schemas"]["UploadResult"];
export type MessageDto = components["schemas"]["Message"];
export type CitationDto = components["schemas"]["Citation"];
export type ApiErrorBody = components["schemas"]["ErrorResponse"]["error"];

// URL tuyệt đối theo origin hiện tại (dev: Vite proxy /api); cần cho fetch trong môi trường test
export const api = createClient<paths>({
  baseUrl: globalThis.location?.origin ?? "",
  fetch: (request) => globalThis.fetch(request), // đọc fetch lúc gọi (test có thể thay thế)
});

export class ApiError extends Error {
  constructor(
    readonly code: string,
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

function toError(error: unknown, status: number): ApiError {
  const body = (error as { error?: ApiErrorBody } | undefined)?.error;
  return new ApiError(body?.code ?? "NETWORK_ERROR", body?.message ?? "Không kết nối được máy chủ.", status);
}

export async function listDocuments(): Promise<DocumentDto[]> {
  const { data, error, response } = await api.GET("/api/v1/documents");
  const status = response.status;
  if (error || !data) throw toError(error, status);
  return data;
}

export async function uploadDocuments(files: File[]): Promise<UploadResultDto[]> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f, f.name));
  const { data, error, response } = await api.POST("/api/v1/documents", {
    // multipart: gửi FormData nguyên trạng
    body: form as unknown as { files: string[] },
    bodySerializer: (b) => b as unknown as FormData,
  });
  const status = response.status;
  if (error || !data) throw toError(error, status);
  return data;
}

export async function createConversation(): Promise<string> {
  const { data, error, response } = await api.POST("/api/v1/conversations");
  const status = response.status;
  if (error || !data) throw toError(error, status);
  return data.id;
}

export async function askQuestion(conversationId: string, text: string): Promise<MessageDto> {
  const { data, error, response } = await api.POST("/api/v1/conversations/{conversationId}/messages", {
    params: { path: { conversationId } },
    body: { text },
  });
  const status = response.status;
  if (error || !data) throw toError(error, status);
  return data;
}

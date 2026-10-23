import type { MessageDto } from "../api/client";
import { vi } from "../i18n/vi";
import { Icon } from "./Icon";

/** Ba loại kết quả luôn khác nhau rõ ràng: trả lời / không tìm thấy / lỗi (UI/UX §6, SDD §3.7). */
export function AnswerMessage({ message }: { message: MessageDto }) {
  return (
    <div className="msg msg-bot">
      <span className="msg-label">{vi.assistant}</span>
      <div className="bubble">
        <p>{message.text}</p>
        <div className="citations">
          <span className="small muted">{vi.sources}</span>
          {message.citations.map((c) => (
            <span key={`${c.documentId}-${c.page}`} className="cite">
              <Icon name="book" />
              {vi.citation(c.documentName, c.page)}
            </span>
          ))}
        </div>
        <p className="hint">{vi.verifyHint}</p>
      </div>
    </div>
  );
}

export function NotFoundMessage() {
  return (
    <div className="msg msg-bot">
      <span className="msg-label">{vi.assistant}</span>
      <div className="bubble bubble-notfound">
        <p style={{ fontWeight: 600 }}>
          <Icon name="info" /> {vi.notFoundTitle}
        </p>
        <p>{vi.notFoundBody}</p>
      </div>
    </div>
  );
}

export function ErrorMessage({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="msg msg-bot">
      <span className="msg-label">{vi.assistant}</span>
      <div className="bubble bubble-error" role="alert">
        <p style={{ fontWeight: 600 }}>
          <Icon name="alert" /> {vi.errorTitle}
        </p>
        <button type="button" className="btn btn-sm" onClick={onRetry}>
          <Icon name="refresh" /> {vi.resend}
        </button>
      </div>
    </div>
  );
}

export function UserMessage({ text }: { text: string }) {
  return (
    <div className="msg msg-user">
      <span className="msg-label">{vi.you}</span>
      <div className="bubble">{text}</div>
    </div>
  );
}

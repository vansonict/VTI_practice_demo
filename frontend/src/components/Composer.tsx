import { useState } from "react";

import { vi } from "../i18n/vi";
import { Icon } from "./Icon";

export const MAX_QUESTION_CHARS = 1000; // [TBD] khớp CWD_MAX_QUESTION_CHARS của backend

type Props = {
  onSubmit: (text: string) => void;
  /** Lý do khóa ô nhập (không có tài liệu sẵn sàng…); null = cho phép hỏi */
  blockedReason: string | null;
  waiting: boolean;
};

/** Ô nhập câu hỏi: Enter gửi, Shift+Enter xuống dòng, bộ đếm ký tự (UI/UX §7 Composer). */
export function Composer({ onSubmit, blockedReason, waiting }: Props) {
  const [text, setText] = useState("");
  const tooLong = text.length > MAX_QUESTION_CHARS;
  const canSend = !blockedReason && !waiting && text.trim().length > 0 && !tooLong;

  const submit = () => {
    if (!canSend) return;
    onSubmit(text.trim());
    setText("");
  };

  return (
    <div className="composer">
      <div className="composer-inner">
        <div className="composer-row">
          <div className="field" style={{ flex: 1 }}>
            <label htmlFor="question" className="sr-only">
              {vi.questionLabel}
            </label>
            <textarea
              id="question"
              className="input"
              rows={2}
              placeholder={vi.questionPlaceholder}
              value={text}
              disabled={blockedReason !== null}
              aria-invalid={tooLong}
              aria-describedby="composerHint counter"
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit();
                }
              }}
            />
          </div>
          <button type="button" className="btn btn-primary" style={{ minHeight: 44 }} disabled={!canSend} onClick={submit}>
            <Icon name="send" /> {vi.send}
          </button>
        </div>
        <div className="composer-meta">
          <span id="composerHint" className="hint">
            {blockedReason ?? vi.hintReady}
          </span>
          <span id="counter" className={`hint counter${tooLong ? " is-over" : ""}`}>
            {text.length}/{MAX_QUESTION_CHARS}
          </span>
        </div>
      </div>
    </div>
  );
}

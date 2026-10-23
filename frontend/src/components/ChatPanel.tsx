import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { askQuestion, createConversation, type DocumentDto, type MessageDto } from "../api/client";
import { vi } from "../i18n/vi";
import { Composer } from "./Composer";
import { Icon } from "./Icon";
import { AnswerMessage, ErrorMessage, NotFoundMessage, UserMessage } from "./Messages";

type Turn = { id: number; question: string; result?: MessageDto; failed?: boolean };

export function blockedReason(documents: DocumentDto[]): string | null {
  if (documents.length === 0) return vi.hintNoDocs;
  if (documents.some((d) => d.status === "READY")) return null;
  if (documents.some((d) => d.status === "PROCESSING")) return vi.hintProcessing;
  return vi.hintNoUsable;
}

/** Khung chat S02 (US-201, 203, 204). Hỏi tiếp, chờ lâu + Hủy, xem nguồn thuộc T3.8. */
export function ChatPanel({ documents }: { documents: DocumentDto[] }) {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [announce, setAnnounce] = useState("");

  const ask = useMutation({
    mutationFn: async ({ question }: { id: number; question: string }) => {
      const cid = conversationId ?? (await createConversation());
      if (!conversationId) setConversationId(cid);
      return askQuestion(cid, question);
    },
    onSuccess: (result, { id }) => {
      setTurns((ts) => ts.map((t) => (t.id === id ? { ...t, result } : t)));
      setAnnounce(vi.answerReady);
    },
    onError: (_e, { id }) => setTurns((ts) => ts.map((t) => (t.id === id ? { ...t, failed: true } : t))),
  });

  const submit = (question: string) => {
    const id = Date.now();
    setTurns((ts) => [...ts, { id, question }]);
    ask.mutate({ id, question });
  };
  const retry = (turn: Turn) => {
    setTurns((ts) => ts.map((t) => (t.id === turn.id ? { ...t, failed: false } : t)));
    ask.mutate({ id: turn.id, question: turn.question });
  };
  const readyCount = documents.filter((d) => d.status === "READY").length;

  return (
    <section className="chat" aria-labelledby="chatHeading">
      <div className="chat-head">
        <h1 id="chatHeading" style={{ fontSize: "var(--fs-lg)" }}>
          {vi.chatTitle}
        </h1>
      </div>
      <p className="scope-note">
        <Icon name="info" /> {vi.scopeNote}
      </p>
      <div className="thread" role="log" aria-label={vi.chatTitle} tabIndex={0}>
        {turns.length === 0 ? (
          <div className="empty">
            <Icon name="chat" />
            <h2>{vi.chatEmptyTitle}</h2>
            <p className="muted">{vi.chatEmptyBody}</p>
          </div>
        ) : (
          <div className="thread-inner">
            {turns.map((t) => (
              <div key={t.id} className="stack">
                <UserMessage text={t.question} />
                {t.failed ? (
                  <ErrorMessage onRetry={() => retry(t)} />
                ) : !t.result ? (
                  <div className="msg msg-bot status-line" role="status">
                    <Icon name="loader" spin /> <span>{vi.searching(readyCount)}</span>
                  </div>
                ) : t.result.kind === "ANSWER" ? (
                  <AnswerMessage message={t.result} />
                ) : t.result.kind === "NOT_FOUND" ? (
                  <NotFoundMessage />
                ) : (
                  <ErrorMessage onRetry={() => retry(t)} />
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      <Composer onSubmit={submit} blockedReason={blockedReason(documents)} waiting={ask.isPending} />
      <div className="sr-only" role="status" aria-live="polite">
        {announce}
      </div>
    </section>
  );
}

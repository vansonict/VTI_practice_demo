import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { uploadDocuments, type DocumentDto } from "../api/client";
import { vi } from "../i18n/vi";
import { Icon } from "./Icon";
import { StatusBadge } from "./StatusBadge";

/** Cột kho tài liệu (S02, US-101/103/104). Xóa, retry, kho đầy thuộc T2.6. */
export function DocumentPanel({ documents }: { documents: DocumentDto[] }) {
  const queryClient = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [rejected, setRejected] = useState<string[]>([]);

  const upload = useMutation({
    mutationFn: uploadDocuments,
    onSuccess: (results) => {
      setRejected(results.filter((r) => r.error).map((r) => `${r.fileName}: ${r.error?.message}`));
      void queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (e: Error) => setRejected([e.message]),
  });

  const send = (files: FileList | null) => {
    if (files && files.length > 0) upload.mutate(Array.from(files));
  };
  const ready = documents.filter((d) => d.status === "READY").length;

  return (
    <aside className="sidebar" aria-labelledby="docsHeading">
      <div className="sidebar-head">
        <div className="sidebar-title">
          <h2 id="docsHeading">{vi.library}</h2>
          <span className="small muted" aria-live="polite">
            {vi.docCount(documents.length, ready)}
          </span>
        </div>
        <div
          className={`dropzone${dragOver ? " is-dragover" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            send(e.dataTransfer.files);
          }}
        >
          <span className="muted small">{vi.dropHint}</span>
          <button type="button" className="btn btn-primary" onClick={() => inputRef.current?.click()}>
            <Icon name="upload" /> {vi.uploadButton}
          </button>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,application/pdf"
            multiple
            hidden
            data-testid="file-input"
            onChange={(e) => {
              send(e.target.files);
              e.target.value = "";
            }}
          />
          <span className="hint">{vi.uploadLimitHint}</span>
        </div>
        {rejected.length > 0 && (
          <div role="alert" className="stack">
            {rejected.map((m) => (
              <div key={m} className="notice notice-error">
                <Icon name="alert" />
                <span>{m}</span>
              </div>
            ))}
          </div>
        )}
      </div>
      <ul className="doc-list" aria-label={vi.library}>
        {documents.length === 0 ? (
          <li>
            <div className="empty">
              <Icon name="file" />
              <h3>{vi.emptyLibraryTitle}</h3>
              <p className="muted">{vi.emptyLibraryBody}</p>
            </div>
          </li>
        ) : (
          documents.map((d) => (
            <li key={d.id} className="doc-item">
              <div className="doc-row">
                <span className="doc-name">{d.name}</span>
              </div>
              <div className="doc-meta">
                <StatusBadge status={d.status} />
                {d.pageCount != null && <span className="small muted">{vi.pages(d.pageCount)}</span>}
              </div>
              {d.status === "UNUSABLE" && d.unusableReason && (
                <p className="doc-reason">
                  {vi.reasonPrefix}
                  {vi.reasons[d.unusableReason] ?? d.unusableReason}
                </p>
              )}
            </li>
          ))
        )}
      </ul>
    </aside>
  );
}

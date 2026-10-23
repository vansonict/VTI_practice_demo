import { useQuery } from "@tanstack/react-query";

import { listDocuments } from "./api/client";
import { ChatPanel } from "./components/ChatPanel";
import { DocumentPanel } from "./components/DocumentPanel";
import { Icon } from "./components/Icon";
import { vi } from "./i18n/vi";

const POLL_MS = 2000; // [Initial] polling khi còn tài liệu PROCESSING (SAD A-02)

/** S02 — Không gian làm việc. Đăng nhập (S01) và thống kê (S03) thuộc GĐ4. */
export function App() {
  const { data: documents = [] } = useQuery({
    queryKey: ["documents"],
    queryFn: listDocuments,
    refetchInterval: (q) => (q.state.data?.some((d) => d.status === "PROCESSING") ? POLL_MS : false),
  });

  return (
    <>
      <a className="skip-link" href="#question">
        Bỏ qua tới khung nhập câu hỏi
      </a>
      <header className="app-header">
        <div className="brand">
          <Icon name="chat" />
          {vi.appName}
        </div>
      </header>
      <main className="workspace">
        <DocumentPanel documents={documents} />
        <ChatPanel documents={documents} />
      </main>
    </>
  );
}

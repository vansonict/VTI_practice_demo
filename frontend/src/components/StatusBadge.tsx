import type { DocumentDto } from "../api/client";
import { vi } from "../i18n/vi";
import { Icon } from "./Icon";

const STYLE = {
  READY: { cls: "badge-ready", icon: "check" as const },
  PROCESSING: { cls: "badge-processing", icon: "loader" as const },
  UNUSABLE: { cls: "badge-unusable", icon: "alert" as const },
};

/** Trạng thái tài liệu: màu + icon + chữ, không chỉ dựa vào màu (UI/UX §9). */
export function StatusBadge({ status }: { status: DocumentDto["status"] }) {
  const s = STYLE[status];
  return (
    <span className={`badge ${s.cls}`}>
      <Icon name={s.icon} spin={status === "PROCESSING"} />
      {vi.status[status]}
    </span>
  );
}

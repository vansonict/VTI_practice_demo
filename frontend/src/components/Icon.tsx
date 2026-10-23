/** Bộ icon của bản mẫu thiết kế (stroke 2px, bo tròn). Luôn đi kèm chữ hoặc aria-label ở nơi dùng. */
const PATHS: Record<string, string> = {
  file: "M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8zM14 3v5h5",
  check: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM8 12.5l2.8 2.8L16 9.8",
  loader: "M12 3a9 9 0 1 0 9 9",
  alert: "M12 3 2.5 20h19zM12 10v4M12 17.5v.01",
  info: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 11v5M12 7.5v.01",
  upload: "M12 16V4M7 9l5-5 5 5M4 20h16",
  send: "M4 12 20 4l-5 16-3-6.5z",
  book: "M5 4h10a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3zM5 17a3 3 0 0 1 3-3h10",
  chat: "M4 5h16v11H9l-5 4z",
  refresh: "M20 11a8 8 0 0 0-14-4L4 9M4 4v5h5M4 13a8 8 0 0 0 14 4l2-2M20 20v-5h-5",
};

export function Icon({ name, spin = false }: { name: keyof typeof PATHS; spin?: boolean }) {
  return (
    <svg className={`icon${spin ? " spin" : ""}`} viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d={PATHS[name]} />
    </svg>
  );
}

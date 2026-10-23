"""FileStore trên hệ thống tệp cục bộ (dev). Ghi nguyên tử: ghi tệp tạm rồi đổi tên."""

import os
from pathlib import Path

from app.ports.filestore import StorageUnavailable
from app.shared.ids import new_id


class LocalFileStore:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def put(self, data: bytes) -> str:
        ref = new_id()
        tmp = self._root / f"{ref}.tmp"
        try:
            tmp.write_bytes(data)
            os.replace(tmp, self._root / ref)
        except OSError as exc:
            raise StorageUnavailable(str(exc)) from exc
        return ref

    def read(self, file_ref: str) -> bytes:
        try:
            return self._path(file_ref).read_bytes()
        except OSError as exc:
            raise StorageUnavailable(str(exc)) from exc

    def delete(self, file_ref: str) -> None:
        self._path(file_ref).unlink(missing_ok=True)

    def _path(self, file_ref: str) -> Path:
        if not file_ref.isalnum():  # chặn đường dẫn lạ; ref luôn là hex do put() sinh
            raise ValueError("file_ref không hợp lệ")
        return self._root / file_ref

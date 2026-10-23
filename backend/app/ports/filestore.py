"""FileStorePort (SDD §3.2, SAD §2.5 EI-4). Tên tệp lưu trữ là ID, không dùng tên người dùng."""

from typing import Protocol


class StorageUnavailable(Exception):
    pass


class FileStorePort(Protocol):
    def put(self, data: bytes) -> str: ...

    def read(self, file_ref: str) -> bytes: ...

    def delete(self, file_ref: str) -> None: ...

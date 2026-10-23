from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.app import create_app
from app.config import Settings
from app.container import Container, build_container


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", file_store_dir=tmp_path / "files")


@pytest.fixture
def container(settings: Settings) -> Container:
    return build_container(settings)


@pytest.fixture
def client(container: Container) -> Iterator[TestClient]:
    with TestClient(create_app(container=container)) as c:
        yield c


def upload(client: TestClient, *files: tuple[str, bytes]) -> list[dict[str, object]]:
    resp = client.post("/api/v1/documents", files=[("files", (n, d, "application/pdf")) for n, d in files])
    assert resp.status_code == 202, resp.text
    result: list[dict[str, object]] = resp.json()
    return result


def process_all(container: Container) -> int:
    n = 0
    while container.ingestion.process_next():
        n += 1
    return n


def documents_by_name(client: TestClient) -> dict[str, dict[str, object]]:
    return {d["name"]: d for d in client.get("/api/v1/documents").json()}

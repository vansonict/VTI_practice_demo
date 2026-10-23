"""Điểm vào worker xử lý tài liệu: `python -m app.worker` (tiến trình riêng, cùng codebase — ADR-001)."""

import logging
import time

from app.config import get_settings
from app.container import build_container

POLL_SECONDS = 1.0


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    container = build_container(get_settings())
    logging.getLogger(__name__).info("worker_started")
    while True:
        if not container.ingestion.process_next():
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()

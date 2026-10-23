"""Cấu hình đọc từ biến môi trường (tiền tố CWD_). Giá trị [Initial] hiệu chỉnh ở T3.10."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CWD_", env_file=".env", extra="ignore")

    # Lưu trữ — SQLite là tạm thời cho tới khi có PostgreSQL + pgvector (ADR-006)
    database_url: str = "sqlite:///./data/app.db"
    file_store_dir: Path = Path("./data/files")

    # Người dùng dev cố định cho tới khi có xác thực (T4.1)
    dev_user_id: str = "dev-user"

    # Adapter (đổi bằng cấu hình, không sửa code — SDD D-04)
    llm_adapter: str = "fake"  # fake
    llm_fake_mode: str = "normal"  # normal | timeout | quota | unavailable | invalid_output | cite_unknown_evidence
    embedding_adapter: str = "fake"  # fake
    embedding_dim: int = 768  # ADR-004

    # Giới hạn [TBD: OQ-004] — giá trị tạm
    max_question_chars: int = 1000

    # Xử lý tài liệu [Initial]
    chunk_max_words: int = 350  # ≈ 450–500 token, dưới giới hạn 512 token của mô hình (ADR-004)
    chunk_overlap_words: int = 35
    job_lock_seconds: int = 300
    scanned_text_ratio: float = 0.5

    # Truy xuất và trả lời [Initial]
    retrieval_top_k: int = 8
    relevance_threshold: float = 0.2


def get_settings() -> Settings:
    return Settings()

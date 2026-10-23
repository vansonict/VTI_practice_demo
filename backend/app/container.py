"""Composition root: chọn adapter theo cấu hình và nối các service. Nơi duy nhất biết mọi lớp."""

from dataclasses import dataclass

from sqlalchemy import Engine

from app.adapters.fake_embedding import FakeEmbedding
from app.adapters.fake_llm import FakeLlm
from app.adapters.local_filestore import LocalFileStore
from app.adapters.pypdf_extractor import PypdfExtractor
from app.config import Settings
from app.db.repositories import (
    SqlChunkSearchRepository,
    SqlConversationRepository,
    SqlDocumentRepository,
    SqlIngestionRepository,
)
from app.db.session import init_schema, make_engine, make_session_factory
from app.modules.documents.service import DocumentService
from app.modules.ingestion.service import IngestionParams, IngestionService
from app.modules.qa.service import QaParams, QaService
from app.modules.retrieval.service import RetrievalService
from app.ports.embedding import EmbeddingPort
from app.ports.llm import LlmPort


@dataclass
class Container:
    settings: Settings
    engine: Engine
    documents: DocumentService
    ingestion: IngestionService
    qa: QaService
    llm: LlmPort
    embedding: EmbeddingPort


def build_container(settings: Settings, llm: LlmPort | None = None) -> Container:
    engine = make_engine(settings.database_url)
    init_schema(engine)
    sf = make_session_factory(engine)
    files = LocalFileStore(settings.file_store_dir)

    if settings.embedding_adapter != "fake":
        raise ValueError(f"Embedding adapter chưa hỗ trợ: {settings.embedding_adapter} (adapter thật làm ở T1.7)")
    embedding = FakeEmbedding(settings.embedding_dim)
    if llm is None:
        if settings.llm_adapter != "fake":
            raise ValueError(f"LLM adapter chưa hỗ trợ: {settings.llm_adapter} (chờ OQ-009, T3.7)")
        llm = FakeLlm(settings.llm_fake_mode)

    doc_repo = SqlDocumentRepository(sf)
    retrieval = RetrievalService(SqlChunkSearchRepository(sf), embedding, settings.retrieval_top_k)
    return Container(
        settings=settings,
        engine=engine,
        documents=DocumentService(doc_repo, files),
        ingestion=IngestionService(
            SqlIngestionRepository(sf),
            files,
            PypdfExtractor(),
            embedding,
            IngestionParams(
                settings.chunk_max_words,
                settings.chunk_overlap_words,
                settings.job_lock_seconds,
                settings.scanned_text_ratio,
            ),
        ),
        qa=QaService(
            SqlConversationRepository(sf),
            doc_repo,
            retrieval,
            llm,
            QaParams(settings.max_question_chars, settings.relevance_threshold),
        ),
        llm=llm,
        embedding=embedding,
    )

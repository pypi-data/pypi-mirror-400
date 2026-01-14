import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from datetime import UTC, datetime
from typing import Literal

from sifts.constants import EMBEDDING_MODEL, PREDICTION_MODEL_VERSION
from sifts_io.db import DatabaseBackend, EmbeddingRecord, SnippetFacet
from sifts_io.inference import EmbeddingBackend, InferenceBackend, SnippetPrediction

type PredictionHandler = Callable[[SnippetFacet], Awaitable[SnippetPrediction | None]]


LOGGER = logging.getLogger(__name__)


type PredictionHandlingPolicy = Literal["fresh", "cached", "fallback"]
type EmbeddingPolicy = Literal["cached", "compute_if_missing"]


def _inference_handler(
    inference_backend: InferenceBackend,
    db_backend: DatabaseBackend,
) -> PredictionHandler:
    async def _handler(snippet: SnippetFacet) -> SnippetPrediction | None:
        embedding_record = await db_backend.get_embedding(
            model=EMBEDDING_MODEL,
            code_hash=snippet.code_hash,
        )
        if embedding_record is None:
            LOGGER.debug("No embedding found for snippet %s", snippet.code_hash)
            return None

        return await inference_backend.infer(embedding_record.embedding)

    return _handler


def _database_handler(db_backend: DatabaseBackend) -> PredictionHandler:
    async def handler(snippet: SnippetFacet) -> SnippetPrediction | None:
        snippet_content_hash = snippet.code_hash

        prediction_raw = await db_backend.get_prediction_by_snippet_hash(
            code_hash=snippet_content_hash,
            version=PREDICTION_MODEL_VERSION,
        )
        if prediction_raw is None:
            return None

        label = prediction_raw.get("PREDICTION_LABEL")
        score = prediction_raw.get("PREDICTION_SCORE")
        if label is None or score is None:
            return None

        return SnippetPrediction(label=label, score=score, index=0)

    return handler


def _fallback_handler(
    db_backend: DatabaseBackend,
    inference_backend: InferenceBackend,
) -> PredictionHandler:
    async def handler(snippet: SnippetFacet) -> SnippetPrediction | None:
        from_db = await _database_handler(db_backend=db_backend)(snippet)
        if from_db is not None:
            return from_db
        LOGGER.debug(
            "No prediction found in DynamoDB for hash %s, trying fresh inference", snippet.code_hash
        )

        return await _inference_handler(
            inference_backend=inference_backend,
            db_backend=db_backend,
        )(snippet)

    return handler


async def _get_or_compute_embedding(
    snippet: SnippetFacet,
    db_backend: DatabaseBackend,
    embedding_backend: EmbeddingBackend,
    embedding_policy: EmbeddingPolicy,
) -> list[float] | None:
    embedding_record = await db_backend.get_embedding(
        model=EMBEDDING_MODEL,
        code_hash=snippet.code_hash,
    )
    if embedding_record is not None:
        return embedding_record.embedding

    if embedding_policy == "cached":
        LOGGER.debug("No cached embedding found for snippet %s (policy=cached)", snippet.code_hash)
        return None

    if not snippet.text:
        LOGGER.debug("No text available for snippet %s to compute embedding", snippet.code_hash)
        return None

    LOGGER.debug("Computing embedding for snippet %s", snippet.code_hash)
    result = await embedding_backend.embed_single(snippet.text)
    embedding = result.to_union()
    if embedding is None:
        LOGGER.warning("Failed to compute embedding for snippet %s", snippet.code_hash)
        return None

    embedding_record = EmbeddingRecord(
        code_hash=snippet.code_hash,
        model=EMBEDDING_MODEL,
        embedding=embedding,
        created_at=datetime.now(UTC),
    )

    async def single_embedding_gen() -> AsyncGenerator[EmbeddingRecord, None]:
        yield embedding_record

    await db_backend.batch_insert_embeddings(
        embeddings=single_embedding_gen(),
        model=EMBEDDING_MODEL,
    )

    return embedding


def _fallback_with_embedding_handler(
    db_backend: DatabaseBackend,
    inference_backend: InferenceBackend,
    embedding_backend: EmbeddingBackend,
    embedding_policy: EmbeddingPolicy,
) -> PredictionHandler:
    async def handler(snippet: SnippetFacet) -> SnippetPrediction | None:
        from_db = await _database_handler(db_backend=db_backend)(snippet)
        if from_db is not None:
            return from_db

        LOGGER.debug(
            "No prediction found in DB for hash %s, trying fresh inference", snippet.code_hash
        )

        embedding = await _get_or_compute_embedding(
            snippet, db_backend, embedding_backend, embedding_policy
        )
        if embedding is None:
            return None

        return await inference_backend.infer(embedding)

    return handler


def get_prediction_handler(
    policy: PredictionHandlingPolicy,
    inference_backend: InferenceBackend,
    db_backend: DatabaseBackend | None = None,
    embedding_backend: EmbeddingBackend | None = None,
    embedding_policy: EmbeddingPolicy = "cached",
) -> PredictionHandler:
    match policy:
        case "fresh":
            if db_backend is None:
                msg = "Backend is required for fresh policy to fetch embeddings"
                raise ValueError(msg)
            if embedding_policy == "compute_if_missing" and embedding_backend is not None:
                return _fallback_with_embedding_handler(
                    db_backend=db_backend,
                    inference_backend=inference_backend,
                    embedding_backend=embedding_backend,
                    embedding_policy=embedding_policy,
                )
            return _inference_handler(
                inference_backend=inference_backend,
                db_backend=db_backend,
            )
        case "cached":
            if db_backend is None:
                msg = "Backend is required for cached policy"
                raise ValueError(msg)
            return _database_handler(db_backend=db_backend)
        case "fallback":
            if db_backend is None:
                msg = "Backend is required for fallback policy"
                raise ValueError(msg)
            if embedding_policy == "compute_if_missing" and embedding_backend is not None:
                return _fallback_with_embedding_handler(
                    db_backend=db_backend,
                    inference_backend=inference_backend,
                    embedding_backend=embedding_backend,
                    embedding_policy=embedding_policy,
                )
            return _fallback_handler(db_backend=db_backend, inference_backend=inference_backend)

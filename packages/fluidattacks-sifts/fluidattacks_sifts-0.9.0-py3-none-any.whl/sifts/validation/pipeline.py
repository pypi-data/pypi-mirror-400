import asyncio
import hashlib
import logging
from collections.abc import AsyncGenerator, Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import aiofiles
import pandas as pd
import voyageai.error
from fluidattacks_core.aio import merge_async_generators
from fluidattacks_core.serializers.syntax import (
    TREE_SITTER_FUNCTION_DECLARATION_MAP,
    InvalidFileType,
    get_language_from_path,
    parse_content_tree_sitter,
    query_nodes_by_language,
)
from snowflake.ml.registry import Registry
from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException
from tree_sitter import Node
from voyageai.client_async import AsyncClient

from sifts.constants import SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_USER_PRIVATE_KEY
from sifts_io.db.base import DatabaseBackend
from sifts_io.db.types import EmbeddingRecord, PredictionRecord, SnippetFacet
from sifts_io.file_system import iter_candidate_files
from snowflake_utils import get_session
from taxonomy import TaxonomyIndex

LOGGER = logging.getLogger(__name__)

EMBEDDING_MODEL = "voyage-code-3"
PREDICTION_VERSION = "V12"
MAX_TOKENS = 120_000
VOYAGE_MAX_BATCH_SIZE = 1000

SNOWFLAKE_DB = "SIFTS"
SNOWFLAKE_SCHEMA = "SIFTS_CANDIDATES"
PREDICTIONS_MODEL_MAP = {
    "V11": "SIFTS_CANDIDATES_SUBCATEGORIES_SERVICE",
    "V12": "SIFTS_CANDIDATES_TYPOLOGY_SERVICE",
}


def _setup_snowflake_session() -> Session:
    """Create Snowflake session for predictions."""
    return get_session(
        snowflake_account=SNOWFLAKE_ACCOUNT,
        snowflake_ml_db=SNOWFLAKE_DB,
        snowflake_ml_schema=SNOWFLAKE_SCHEMA,
        snowflake_ml_user=SNOWFLAKE_USER,
        snowflake_ml_private_key_path=SNOWFLAKE_USER_PRIVATE_KEY,
    )


def _is_top_level_function(node: Node, function_node_names: set[str]) -> bool:
    parent = node.parent
    while parent:
        if parent.type in function_node_names:
            return False
        parent = parent.parent
    return True


async def _process_file_for_functions(
    file_path: Path,
    working_dir: Path | None = None,
) -> AsyncGenerator[tuple[str, Node], None]:
    language = get_language_from_path(str(file_path))
    if not language:
        return
    try:
        async with aiofiles.open(file=file_path, mode="rb") as f:
            content = await f.read()
            try:
                tree = parse_content_tree_sitter(content, language)
            except (OSError, ValueError, InvalidFileType):
                return
    except FileNotFoundError:
        return

    function_node_names = TREE_SITTER_FUNCTION_DECLARATION_MAP[language]
    function_nodes = query_nodes_by_language(
        language,
        tree,
        TREE_SITTER_FUNCTION_DECLARATION_MAP,
    )
    if len(content.splitlines()) > 2000:  # noqa: PLR2004
        return
    if (
        len(function_nodes) > 1
        and len({node.start_point[0] for node in (y for x in function_nodes.values() for y in x)})
        == 1
    ):
        return
    for node in (y for x in function_nodes.values() for y in x):
        if _is_top_level_function(node, set(function_node_names)):
            if working_dir:
                yield (str(file_path.relative_to(working_dir)), node)
            else:
                yield (str(file_path), node)


def _compute_code_sha256(normalized_code: str) -> str:
    return hashlib.sha3_256(normalized_code.encode("utf-8")).hexdigest()


def _generate_snippet_hash(
    group_name: str,
    root_nickname: str,
    commit: str,
    path: str,
    node: Node,
) -> str:
    parts = [
        group_name,
        root_nickname,
        commit,
        path,
        node.type,
        str(node.start_byte),
        str(node.end_byte),
        str(node.start_point[0]),
        str(node.start_point[1]),
        str(node.end_point[0]),
        str(node.end_point[1]),
    ]
    hasher = hashlib.sha3_256()
    for part in parts:
        hasher.update(part.encode("utf-8"))
    return hasher.hexdigest()


async def extract_snippets(
    db_backend: DatabaseBackend,
    working_dir: Path,
    group_name: str,
    root_nickname: str,
    commit: str,
) -> int:
    LOGGER.info("Step 1: Extracting snippets from %s", working_dir)

    async def snippet_generator() -> AsyncGenerator[SnippetFacet, None]:
        file_generators = [
            _process_file_for_functions(file_path, working_dir)
            for file_path, _ in iter_candidate_files(working_dir, exclude_patterns=[])
        ]

        async for path, node in merge_async_generators(file_generators, limit=5):
            if not node.text:
                continue
            text = node.text.decode(errors="ignore")
            code_hash = _compute_code_sha256(text)
            snippet_hash_id = _generate_snippet_hash(group_name, root_nickname, commit, path, node)
            yield SnippetFacet(
                snippet_hash_id=snippet_hash_id,
                group_name=group_name,
                root_nickname=root_nickname,
                commit=commit,
                path=path,
                start_byte=node.start_byte,
                end_byte=node.end_byte,
                start_line=node.start_point[0] + 1,
                start_column=node.start_point[1],
                end_line=node.end_point[0] + 1,
                end_column=node.end_point[1],
                node_type=node.type,
                code_hash=code_hash,
                created_at=datetime.now(UTC),
                text=None,
                language=None,
                name=None,
            )

    count = await db_backend.batch_insert_snippets(
        snippet_generator(), group_name=group_name, root_nickname=root_nickname
    )
    LOGGER.info("Extracted %d snippets", count)
    return count


def build_embedding_generator(
    snippets: list[SnippetFacet],
    working_dir: Path,
    voyage_client: AsyncClient,
) -> Callable[[], AsyncGenerator[EmbeddingRecord, None]]:
    async def embedding_generator() -> AsyncGenerator[EmbeddingRecord, None]:
        batch_snippets: list[SnippetFacet] = []
        batch_texts: list[str] = []

        for snippet in snippets:
            file_path = working_dir / snippet.path
            try:
                with file_path.open("rb") as f:
                    f.seek(snippet.start_byte)
                    code = f.read(snippet.end_byte - snippet.start_byte).decode(
                        "utf-8", errors="ignore"
                    )
            except (OSError, ValueError):
                continue

            if not code:
                continue

            token_count = voyage_client.count_tokens([*batch_texts, code], model=EMBEDDING_MODEL)
            should_flush = (token_count > MAX_TOKENS and batch_texts) or (
                len(batch_texts) >= VOYAGE_MAX_BATCH_SIZE
            )

            if should_flush:
                async for emb in _generate_embedding_batch(
                    batch_snippets, batch_texts, voyage_client
                ):
                    yield emb
                batch_snippets = []
                batch_texts = []

            batch_snippets.append(snippet)
            batch_texts.append(code)

        if batch_snippets:
            async for emb in _generate_embedding_batch(batch_snippets, batch_texts, voyage_client):
                yield emb

    return embedding_generator


async def generate_embeddings(
    db_backend: DatabaseBackend,
    working_dir: Path,
    group_name: str,
    root_nickname: str,
) -> int:
    LOGGER.info("Step 2: Generating embeddings")

    snippets_needing_embeddings: list[SnippetFacet] = []
    buffer: list[SnippetFacet] = []
    buffer_hashes: list[str] = []

    async for snippet in db_backend.stream_snippets(
        group_name=group_name, root_nickname=root_nickname
    ):
        buffer.append(snippet)
        buffer_hashes.append(snippet.code_hash)

        if len(buffer) >= 100:  # noqa: PLR2004
            existing = await db_backend.batch_get_embeddings(
                model=EMBEDDING_MODEL, code_hashes=buffer_hashes
            )
            snippets_needing_embeddings.extend(s for s in buffer if s.code_hash not in existing)
            buffer.clear()
            buffer_hashes.clear()

    if buffer:
        existing = await db_backend.batch_get_embeddings(
            model=EMBEDDING_MODEL, code_hashes=buffer_hashes
        )
        snippets_needing_embeddings.extend(s for s in buffer if s.code_hash not in existing)

    if not snippets_needing_embeddings:
        LOGGER.info("All snippets already have embeddings")
        return 0

    LOGGER.info("Found %d snippets needing embeddings", len(snippets_needing_embeddings))

    voyage_client = AsyncClient()
    embedding_generator = build_embedding_generator(
        snippets=snippets_needing_embeddings,
        working_dir=working_dir,
        voyage_client=voyage_client,
    )

    count = await db_backend.batch_insert_embeddings(embedding_generator(), model=EMBEDDING_MODEL)
    LOGGER.info("Generated %d embeddings", count)
    return count


async def _generate_embedding_batch(
    batch_snippets: list[SnippetFacet],
    batch_texts: list[str],
    voyage_client: AsyncClient,
) -> AsyncGenerator[EmbeddingRecord, None]:
    if not batch_texts:
        return

    while True:
        try:
            embeddings = await voyage_client.embed(batch_texts, model=EMBEDDING_MODEL)
            break
        except voyageai.error.RateLimitError:
            LOGGER.warning("Rate limit exceeded, waiting 60 seconds")
            await asyncio.sleep(60)
        except voyageai.error.AuthenticationError:
            LOGGER.exception("Authentication error")
            return
        except (
            voyageai.error.ServiceUnavailableError,
            voyageai.error.APIConnectionError,
            voyageai.error.APIError,
        ):
            LOGGER.exception("Service unavailable or connection error")
            return
        except voyageai.error.TryAgain:
            continue

    for snippet, emb in zip(batch_snippets, embeddings.embeddings, strict=True):
        emb_list = [float(x) for x in cast("Sequence[float]", emb)]
        yield EmbeddingRecord(
            code_hash=snippet.code_hash,
            model=EMBEDDING_MODEL,
            embedding=emb_list,
            created_at=datetime.now(UTC),
        )


async def generate_predictions(
    db_backend: DatabaseBackend,
    snowflake_session: Session,
    group_name: str,
    root_nickname: str,
) -> int:
    LOGGER.info("Step 3: Generating predictions")

    code_hashes: set[str] = set()
    async for snippet in db_backend.stream_snippets(
        group_name=group_name, root_nickname=root_nickname
    ):
        code_hashes.add(snippet.code_hash)

    if not code_hashes:
        LOGGER.info("No snippets found")
        return 0

    existing_predictions = await db_backend.batch_get_predictions(
        version=PREDICTION_VERSION, code_hashes=list(code_hashes)
    )
    predicted_hashes = {p.get("code_hash") for p in existing_predictions if p.get("code_hash")}
    missing_hashes = code_hashes - predicted_hashes

    if not missing_hashes:
        LOGGER.info("All snippets already have predictions")
        return 0

    LOGGER.info("Found %d snippets needing predictions", len(missing_hashes))

    taxonomy_index = await TaxonomyIndex.load()

    async def prediction_generator() -> AsyncGenerator[PredictionRecord, None]:
        embeddings: list[EmbeddingRecord] = []
        async for emb in db_backend.stream_embeddings(
            model=EMBEDDING_MODEL, code_hashes=missing_hashes
        ):
            embeddings.append(emb)

            if len(embeddings) >= 1000:  # noqa: PLR2004
                async for pred in _classify_batch(embeddings, snowflake_session, taxonomy_index):
                    yield pred
                embeddings = []

        if embeddings:
            async for pred in _classify_batch(embeddings, snowflake_session, taxonomy_index):
                yield pred

    count = await db_backend.batch_insert_predictions(
        prediction_generator(), version=PREDICTION_VERSION
    )
    LOGGER.info("Generated %d predictions", count)
    return count


async def _classify_batch(
    embeddings: list[EmbeddingRecord],
    session: Session,
    taxonomy_index: TaxonomyIndex | None,
) -> AsyncGenerator[PredictionRecord, None]:
    if not embeddings:
        return

    def _classify_blocking() -> list[PredictionRecord]:
        sample_df = pd.DataFrame({"embeddings": [emb.embedding for emb in embeddings]})
        registry = Registry(
            session=session,
            database_name=SNOWFLAKE_DB,
            schema_name=SNOWFLAKE_SCHEMA,
        )
        mv = registry.get_model("CANDIDATE_CLASSIFIER").version(PREDICTION_VERSION)
        result_pd = pd.DataFrame(
            mv.run(sample_df, service_name=PREDICTIONS_MODEL_MAP[PREDICTION_VERSION])
        )

        predictions: list[PredictionRecord] = []
        for i in range(len(result_pd)):
            subcategory: str = result_pd["PREDICTION_LABEL"][i]
            score: float = result_pd["PREDICTION_SCORE"][i]

            category = "Unknown"
            if taxonomy_index:
                for _category, subcategories in taxonomy_index._taxonomy.items():
                    if subcategory in subcategories:
                        category = _category
                        break

            predictions.append(
                PredictionRecord(
                    code_hash=embeddings[i].code_hash,
                    version=PREDICTION_VERSION,
                    prediction_label=subcategory,
                    prediction_score=score,
                    category=category,
                    subcategory=subcategory,
                    created_at=datetime.now(UTC),
                )
            )

        return predictions

    try:
        predictions = await asyncio.to_thread(_classify_blocking)
        for pred in predictions:
            yield pred
    except SnowparkSQLException:
        LOGGER.exception("Snowflake classification failed")


async def run_validation_pipeline(
    db_backend: DatabaseBackend,
    working_dir: Path,
    group_name: str,
    root_nickname: str,
    commit: str,
) -> None:
    LOGGER.info("Starting validation pipeline for %s/%s", group_name, root_nickname)

    await extract_snippets(db_backend, working_dir, group_name, root_nickname, commit)

    await generate_embeddings(db_backend, working_dir, group_name, root_nickname)
    snowflake_session = _setup_snowflake_session()

    await generate_predictions(db_backend, snowflake_session, group_name, root_nickname)

    LOGGER.info("Validation pipeline completed")

import logging
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path

from aioboto3 import Session
from tree_sitter import Node

import sifts
from common_types import Language as SiftsLanguage
from sifts.analysis.code_parser import analyze_method_node
from sifts.analysis.prediction import get_prediction_handler
from sifts.analysis.types import TreeExecutionContext
from sifts.config import SiftsConfig
from sifts.core.parallel_utils import merge_async_generators
from sifts.core.parsing import process_file_for_functions
from sifts.core.repository import get_repo_head_hash
from sifts.cpg import load_cpg_graph_binary
from sifts_io.db.ctags_tinydb import create_tiny_db_from_ctags
from sifts_io.db.types import AnalysisFacet
from sifts_io.file_system import (
    find_projects,
    generate_exclusions,
    get_valid_file_paths,
    should_exclude,
)

SESSION = Session()
LOGGER = logging.getLogger(__name__)


async def analyze_project(
    *,
    config: SiftsConfig,
    context: TreeExecutionContext,
    exclude: list[str] | None = None,
) -> AsyncGenerator[AnalysisFacet | None, None]:
    function_iter = (
        iter_functions_from_line_config(context, config, exclude)
        if config.lines_to_check is not None
        else iter_functions_from_project(
            context,
            config,
            exclude,
        )
    )
    if config.enable_navigation and not await load_cpg_graph_binary(
        context.working_dir,
        context.language,
        tuple(Path(x) for x in exclude or []),
        group=config.group_name,
        repo_nickname=config.root_nickname,
        storage=context.storage,
    ):
        LOGGER.info("No CPG graph found for project %s", config.root_dir)
        return

    function_pairs = []
    async for where, method_node in function_iter:
        function_pairs.append((where, method_node))
    if not function_pairs:
        return
    LOGGER.info("Number of functions to analyze: %s", len(function_pairs))

    prediction_handler = get_prediction_handler(
        policy=config.prediction_policy,
        inference_backend=config.get_inference_backend(),
        db_backend=config.get_database(),
        embedding_backend=config.get_embedding_backend(),
        embedding_policy=config.embedding_policy,
    )

    function_coroutines = [
        analyze_method_node(
            method_node=method_node,
            where=where,
            context=context,
            config=config,
            prediction_handler=prediction_handler,
        )
        for where, method_node in function_pairs
    ]

    async for result in merge_async_generators(
        function_coroutines, limit=config.method_node_analysis_concurrency
    ):
        if result is not None:
            yield result


async def get_valid_functions(
    file_path: Path,
    lines: list[int],
) -> list[Node]:
    # Convert from 1-based (input) to 0-based (tree-sitter) for comparison
    lines_0based = [line - 1 for line in lines]
    result: list[Node] = []
    async for _, node in process_file_for_functions(file_path):
        if any(x for x in lines_0based if node.start_point[0] <= x <= node.end_point[0]):
            result.append(node)
    return result


async def iter_functions_from_line_config(
    context: TreeExecutionContext,
    config: SiftsConfig,
    exclude: list[str] | None = None,
) -> AsyncGenerator[tuple[Path, Node], None]:
    """Async generator that yields functions to analyze based on line configs."""
    exclusions = list(exclude) if exclude is not None else generate_exclusions()
    exclusions.extend(config.exclude_files or [])
    exclusion_paths = [Path(excl) for excl in exclusions]

    for line_config in config.lines_to_check or []:
        file_path = config.root_dir / line_config.file
        if not file_path.is_relative_to(context.working_dir):
            continue

        try:
            rel_path_str = str(file_path.relative_to(context.working_dir))
        except ValueError:
            continue

        if should_exclude(file_path, exclusion_paths, relative_path=rel_path_str):
            continue

        functions = await get_valid_functions(
            file_path,
            line_config.lines,
        )
        for function in functions:
            where = file_path.relative_to(context.working_dir)
            yield (
                where,
                function,
            )


async def iter_functions_from_project(
    context: TreeExecutionContext,
    config: SiftsConfig,
    exclude: list[str] | None = None,
) -> AsyncGenerator[tuple[Path, Node], None]:
    include_patterns = []
    for x in config.include_files or []:
        if (config.root_dir / x).exists():
            if (config.root_dir / x).is_relative_to(context.working_dir):
                include_patterns.append(
                    (config.root_dir / x).relative_to(context.working_dir).as_posix()
                )
        else:
            include_patterns.append(x)

    exclude_patterns = list(set((config.exclude_files or []) + (exclude or [])))

    valid_paths_str = await get_valid_file_paths(
        working_dir=context.working_dir,
        include_patterns=include_patterns if include_patterns else None,
        exclude_patterns=exclude_patterns if exclude_patterns else None,
    )

    for rel_path_str in valid_paths_str:
        rel_path = Path(rel_path_str)
        full_path = (context.working_dir / rel_path).resolve()

        async for _, function_node in process_file_for_functions(
            file_path=full_path,
            working_dir=context.working_dir,
        ):
            try:
                where = full_path.relative_to(config.root_dir)
            except ValueError:
                where = rel_path
            if config.lines_to_skip and any(
                function_node.start_point[0] + 1 <= line <= function_node.end_point[0] + 1
                for lines_config in config.lines_to_skip
                if lines_config.file == where
                for line in lines_config.lines
            ):
                continue
            yield (rel_path, function_node)


@dataclass
class AnalysisContext:
    """Context object for project analysis."""

    config: SiftsConfig


async def process_single_project(
    working_dir: Path,
    language: SiftsLanguage,
    exclude: list[str] | None,
    config: SiftsConfig,
) -> AsyncGenerator[AnalysisFacet, None]:
    """Process a single project and return its vulnerabilities."""
    if config.lines_to_check and not any(
        (config.root_dir / item.file).is_relative_to(working_dir) for item in config.lines_to_check
    ):
        return
    if config.include_files and not any(
        (config.root_dir / item).is_relative_to(working_dir) for item in config.include_files
    ):
        return

    LOGGER.info(
        "Analyzing project %s",
        working_dir.relative_to(Path(config.root_dir)),
    )

    tiny_db, _ = await create_tiny_db_from_ctags(
        working_dir,
        exclude,
        metadata={
            "group_name": config.group_name,
            "root_nickname": config.root_nickname,
            "version": sifts.__version__,
            "commit": get_repo_head_hash(working_dir) or "",
            "uuid": str(uuid.uuid4()),
        },
    )

    context = TreeExecutionContext(
        working_dir=working_dir,
        tiny_db=tiny_db,
        analysis_dir=Path(config.root_dir),
        language=language,
        exclude=[Path(x) for x in exclude or []],
        group=config.group_name,
        repo_nickname=config.root_nickname,
        storage=config.get_storage(),
    )

    try:
        # Get results from analyze_project_tree directly as AsyncGenerator
        async for response in analyze_project(
            context=context,
            config=config,
            exclude=exclude,
        ):
            if response is not None:
                # Process the result and add to our list
                db_backend = config.get_database()
                await db_backend.insert_analysis(response)
                yield response
    except Exception:
        LOGGER.exception(
            "Error in analysis for project %s",
            working_dir.relative_to(Path(config.root_dir)),
        )


async def scan_projects(config: SiftsConfig) -> list[AnalysisFacet]:
    """Scan projects and analyze vulnerabilities."""
    # Setup infrastructure
    db_backend = config.get_database()
    await db_backend.startup()

    projects = find_projects(config.root_dir)

    LOGGER.info("Number of projects: %s", len(projects))

    # Collect analysis results from all projects with concurrency control
    all_results = []

    # Create coroutines for each project
    project_coroutines = [
        process_single_project(working_dir, language, exclude, config)
        for working_dir, language, exclude in projects
    ]

    # Use limited_as_completed to process projects with concurrency limit
    async for project_result in merge_async_generators(
        project_coroutines, limit=config.concurrent_project_analysis
    ):
        try:
            all_results.append(project_result)
        except Exception:
            LOGGER.exception("Error processing project")

    LOGGER.info("Total findings: %d", len(all_results))
    return all_results

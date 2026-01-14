import asyncio
import logging
import os
from pathlib import Path

import bugsnag
import click

from sifts.analysis.orchestrator import scan_projects
from sifts.config import SiftsConfig
from sifts.constants import BUGSNAG_API_KEY
from sifts.core.repository import get_repo_head_hash
from sifts.core.sarif_result import process_sarif_results
from sifts.validation.pipeline import run_validation_pipeline
from taxonomy import TaxonomyIndex

LOGGER = logging.getLogger(__name__)

GROUP_NAME_PH = "validation"
ROOT_NICKNAME_PH = "validation"

bugsnag.configure(
    api_key=BUGSNAG_API_KEY,
    project_root=str(Path(__file__).parent.parent.parent),
    auto_capture_sessions=True,
    app_version=os.getenv("APP_VERSION", "unknown"),
    release_stage=os.getenv("ENVIRONMENT", "production"),
)


@click.command()
@click.argument("working-dir", required=False)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to YAML configuration file",
)
@click.option(
    "--output-path",
    type=click.Path(),
    default="sarif.json",
    help="Path to output SARIF file",
)
@click.option(
    "--skip-pipeline",
    is_flag=True,
    default=False,
    help="Skip the pre-processing pipeline (snippets, embeddings, predictions)",
)
def validation_cli(
    working_dir: str | None,
    config: Path | None,
    output_path: str,
    *,
    skip_pipeline: bool,
) -> None:
    """Run validation and generate SARIF results."""
    if config is not None:
        if working_dir is not None:
            msg = "Cannot specify both --config and working-dir argument"
            raise click.BadParameter(msg)
        LOGGER.info("Running validation with config file: %s", config)
        asyncio.run(_run_config_validation(config, skip_pipeline=skip_pipeline))
    else:
        if working_dir is None:
            msg = "Must specify either --config or working-dir argument"
            raise click.MissingParameter(msg, param_hint="working-dir or --config")
        LOGGER.info("Running validation for %s", working_dir)
        asyncio.run(
            _run_path_validation(Path(working_dir), Path(output_path), skip_pipeline=skip_pipeline)
        )


async def _handle_standalone_sarif(
    config: SiftsConfig,
    output_path: Path,
    commit: str | None = None,
) -> None:
    """Generate and upload SARIF results to remote storage."""
    group_name = config.group_name or GROUP_NAME_PH
    nickname = config.root_nickname or ROOT_NICKNAME_PH

    db_backend = config.get_database()
    await db_backend.startup()
    try:
        result_path, vulnerable_count = await process_sarif_results(
            group_name,
            nickname,
            config=config,
            db_backend=config.get_database(),
            output_path=output_path,
            commit=commit,
        )

        LOGGER.info(
            "SARIF results saved to %s with %d vulnerable findings", result_path, vulnerable_count
        )

    except Exception:
        LOGGER.exception("Error processing SARIF")
        return
    finally:
        try:
            await db_backend.shutdown()
        except (RuntimeError, ConnectionError, OSError) as exc:
            LOGGER.warning("Error closing database backend: %s", exc, exc_info=True)
            bugsnag.notify(
                exc,
                severity="warning",
                context="_handle_standalone_sarif.cleanup",
                metadata={"group_name": group_name, "nickname": nickname},
            )


async def _run_validation_pipeline_steps(
    config: SiftsConfig,
    working_dir: Path,
    group_name: str,
    root_nickname: str,
) -> None:
    """Run the pre-processing pipeline (snippets, embeddings, predictions)."""
    db_backend = config.get_database()
    await db_backend.startup()

    commit = get_repo_head_hash(working_dir) or "unknown"

    await run_validation_pipeline(
        db_backend=db_backend,
        working_dir=working_dir,
        group_name=group_name,
        root_nickname=root_nickname,
        commit=commit,
    )


async def _run_config_validation(
    config_path: Path,
    *,
    skip_pipeline: bool = False,
) -> None:
    """Run validation using a YAML configuration file."""
    config = SiftsConfig.from_yaml(config_path)

    # We're not that fan of entities mutability, we'd prefer immutable config instances.
    # We'll eventually find a workaround that handles the yaml config with overrides, letting the
    # config instance itself immutable.
    config.database_backend = "sqlite"
    config.inference_backend = "local_consumer"
    config.prediction_policy = "fallback"
    config.embedding_policy = "compute_if_missing"
    config.storage_backend = "local"
    config.check_existing_vulns = False
    config.sarif_to_remote = False

    if config.group_name is None:
        config.group_name = GROUP_NAME_PH
    if config.root_nickname is None:
        config.root_nickname = ROOT_NICKNAME_PH

    group_name = config.group_name
    root_nickname = config.root_nickname
    working_dir = config.root_dir

    LOGGER.info("Validation working directory: %s", working_dir)
    LOGGER.info("Using database backend: %s", config.database_backend)
    if config.database_backend == "sqlite":
        LOGGER.info("SQLite database path: %s", config.sqlite_database_path)

    await TaxonomyIndex.load()

    commit = get_repo_head_hash(working_dir) or "unknown"

    if not skip_pipeline:
        LOGGER.info("Running pre-processing pipeline...")
        await _run_validation_pipeline_steps(config, working_dir, group_name, root_nickname)

    LOGGER.info("Running analysis...")
    await scan_projects(config)
    LOGGER.info("Success at scanning project")
    await _handle_standalone_sarif(config, config.output_path, commit=commit)


async def _run_path_validation(
    working_dir: Path,
    output_path: Path,
    *,
    skip_pipeline: bool = False,
) -> None:
    LOGGER.info("Validation working directory: %s", working_dir)

    await TaxonomyIndex.load()

    config = SiftsConfig.create_with_overrides(
        root_dir=working_dir,
        split_subdirectories=False,
        enable_navigation=False,
        include_vulnerabilities_subcategories=["SQL Injection", "Cross-Site Scripting"],
        model="gpt-4.1-mini",
        database_backend="sqlite",
        inference_backend="local_consumer",
        prediction_policy="fallback",
        embedding_policy="compute_if_missing",
        check_existing_vulns=False,
        group_name=GROUP_NAME_PH,
        root_nickname=ROOT_NICKNAME_PH,
        sarif_to_remote=False,
        storage_backend="local",
    )
    LOGGER.info("Using database backend: %s", config.database_backend)
    if config.database_backend == "sqlite":
        LOGGER.info("SQLite database path: %s", config.sqlite_database_path)

    commit = get_repo_head_hash(working_dir) or "unknown"

    if not skip_pipeline:
        LOGGER.info("Running pre-processing pipeline...")
        await _run_validation_pipeline_steps(config, working_dir, GROUP_NAME_PH, ROOT_NICKNAME_PH)

    LOGGER.info("Running analysis...")
    await scan_projects(config)
    LOGGER.info("Success at scanning project")
    await _handle_standalone_sarif(config, output_path, commit=commit)


if __name__ == "__main__":
    validation_cli()

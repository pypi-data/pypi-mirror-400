import asyncio
import json
import logging
import os
import sys
from collections import defaultdict
from pathlib import Path

import aioboto3
import aiohttp
import bugsnag
import click
from botocore.exceptions import BotoCoreError, ClientError
from bugsnag.handlers import BugsnagHandler

from graphql_client import IntegratesApiClient, SiftsGroupRootsGroupRootsGitRoot
from graphql_client.enums import Technique
from sifts.analysis.orchestrator import scan_projects
from sifts.config import LinesConfig, SiftsConfig
from sifts.constants import AI_SAST_EMAIL, BUGSNAG_API_KEY
from sifts.core.report import report_vulnerabilities
from sifts.core.repository import get_repo_head_hash, pull_repositories
from sifts.core.sarif_result import extract_vulnerable_analysis, process_sarif_results
from taxonomy import TaxonomyIndex
from taxonomy.metric import VulnNotFoundError

os.environ["AWS_REGION_NAME"] = os.environ.get("AWS_REGION_NAME", "us-east-1")

LOGGER = logging.getLogger(__name__)

# Configure Bugsnag first before creating handlers
bugsnag.configure(
    api_key=BUGSNAG_API_KEY,
    project_root=str(Path(__file__).parent.parent.parent),
    auto_capture_sessions=True,
    app_version=os.getenv("APP_VERSION", "unknown"),
    release_stage=os.getenv("ENVIRONMENT", "production"),
)

# Add Bugsnag handler to root logger to capture all ERROR level logs
# Must be done after bugsnag.configure() to ensure proper initialization
root_logger = logging.getLogger()
bugsnag_handler = BugsnagHandler()
bugsnag_handler.setLevel(logging.ERROR)
root_logger.addHandler(bugsnag_handler)

# Configure bugsnag to handle async exceptions
bugsnag_middleware = bugsnag.configure().middleware


@click.command()
@click.argument("group-name", required=False)
@click.argument("root", required=False)
@click.option("--reattack", is_flag=True, default=False, help="Re-attack the root")
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
def main_cli(
    group_name: str | None,
    root: str | None,
    config: Path | None,
    output_path: str,
    *,
    reattack: bool,
) -> None:
    if config is not None:
        if group_name is not None or root is not None:
            msg = "Cannot specify both --config and group-name/root arguments"
            raise click.BadParameter(msg)
        exit_code = 0
        try:
            asyncio.run(_run_config_analysis(config, Path(output_path)))
        except KeyboardInterrupt:
            LOGGER.warning("Interrupted by user")
            exit_code = 130
        except Exception as e:
            LOGGER.exception("Error during config-based analysis")
            bugsnag.notify(
                e,
                context="main_cli_config",
                metadata={
                    "config": str(config),
                    "output_path": output_path,
                },
            )
            exit_code = 1
        finally:
            _cleanup_event_loop()
    else:
        if group_name is None or root is None:
            msg = "Must specify either --config or both group-name and root arguments"
            raise click.MissingParameter(msg, param_hint="group-name and root, or --config")
        exit_code = 0
        try:
            asyncio.run(_run_root_analysis(group_name, root, Path(output_path), reattack=reattack))
        except KeyboardInterrupt:
            LOGGER.warning("Interrupted by user")
            exit_code = 130
        except Exception as e:
            LOGGER.exception("Error during root analysis")
            bugsnag.notify(
                e,
                context="main_cli",
                metadata={
                    "group_name": group_name,
                    "root": root,
                    "output_path": output_path,
                },
            )
            exit_code = 1
        finally:
            _cleanup_event_loop()
    if exit_code != 0:
        sys.exit(exit_code)


def _cleanup_event_loop() -> None:
    """Ensure all pending tasks are cleaned up."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            pending = asyncio.all_tasks(loop)
            if pending:
                LOGGER.warning("Cleaning up %d pending tasks", len(pending))
    except RuntimeError:
        pass


async def process_report_in_sqs(key: str, nickname: str, group_name: str) -> None:
    """Submit report to SQS queue. Non-fatal errors are logged and reported to Bugsnag."""
    session = aioboto3.Session()
    try:
        async with session.client("sqs", region_name="us-east-1") as sqs_client:
            await sqs_client.send_message(
                QueueUrl="https://sqs.us-east-1.amazonaws.com/205810638802/integrates_report",
                MessageBody=json.dumps(
                    {
                        "id": key,
                        "task": "report",
                        "kwargs": {
                            "execution_id": key,
                            "commit": None,
                            "commit_date": None,
                            "user_email": "integrates@fluidattacks.com",
                            "root_nickname": nickname,
                            "group_name": group_name,
                        },
                    },
                ),
            )
    except (ClientError, BotoCoreError, aiohttp.ClientError, TimeoutError) as exc:
        LOGGER.exception("Failed to submit report to SQS queue (non-fatal)")
        bugsnag.notify(
            exc,
            severity="error",
            context="process_report_in_sqs",
            metadata={"key": key},
        )


async def _get_root_id(
    integrates_client: IntegratesApiClient, group_name: str, nickname: str
) -> str | None:
    """Get root ID from integrates API."""
    LOGGER.info("Fetching group roots for %s %s", group_name, nickname)
    data = await integrates_client.sifts_group_roots(group_name)
    root_id = next(
        (
            x.id
            for x in data.group.roots or []
            if isinstance(x, SiftsGroupRootsGroupRootsGitRoot)
            and x.nickname.lower() == nickname.lower()
        ),
        None,
    )
    if not root_id:
        LOGGER.error("Root ID not found for group %s and nickname %s", group_name, nickname)
    return root_id


async def _collect_lines_to_skip(
    integrates_client: IntegratesApiClient,
    group_name: str,
    root_nickname: str,
    working_dir: Path,
    include_vulnerabilities_subcategories: list[str],
) -> list[LinesConfig]:
    """Collect lines to skip based on existing vulnerabilities."""
    lines_to_skip: list[LinesConfig] = []
    index = await TaxonomyIndex.load()

    findings_response = await integrates_client.sifts_findings(group_name)
    findings = findings_response.group.findings or []

    for finding in findings:
        if finding is None:
            continue
        try:
            _, subcategory = index.get_vuln_path(finding.title.split(".")[0])
        except VulnNotFoundError:
            continue
        if subcategory not in include_vulnerabilities_subcategories:
            continue

        file_lines: defaultdict[Path, list[int]] = defaultdict(list)

        current_after: str | None = None
        has_next_page = True

        while has_next_page:
            vulnerabilities_response = await integrates_client.sifts_finding_vulnerabilities(
                finding_id=finding.id,
                after=current_after,
            )

            for vulnerability in vulnerabilities_response.finding.vulnerabilities.edges or []:
                if not vulnerability or not vulnerability.node.where.startswith(root_nickname):
                    continue
                file_path = working_dir / vulnerability.node.where.removeprefix(root_nickname + "/")
                if file_path.exists():
                    try:
                        file_lines[file_path.relative_to(working_dir)].append(
                            int(vulnerability.node.specific)
                        )
                    except ValueError:
                        continue

            page_info = vulnerabilities_response.finding.vulnerabilities.page_info
            has_next_page = page_info.has_next_page
            current_after = page_info.end_cursor

        lines_to_skip.extend(
            [LinesConfig(file=file, lines=lines) for file, lines in file_lines.items()]
        )

    return lines_to_skip


async def _generate_and_upload_sarif(
    config: SiftsConfig,
    group_name: str,
    nickname: str,
    output_path: Path,
) -> None:
    """Generate and upload SARIF results to remote storage."""
    db_backend = config.get_database()
    await db_backend.startup()
    try:
        result = await process_sarif_results(
            group_name,
            nickname,
            config=config,
            db_backend=config.get_database(),
            output_path=output_path,
        )
        key, _ = result

        # Only submit to SQS if running in AWS Batch
        if config.sarif_to_remote and os.getenv("AWS_BATCH_JOB_ID"):
            await process_report_in_sqs(key, nickname, group_name)
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
                context="_generate_and_upload_sarif.cleanup",
                metadata={"group_name": group_name, "nickname": nickname},
            )


async def _run_analysis_workflow(
    config: SiftsConfig,
    group_name: str,
    nickname: str,
    _output_path: Path,
    *,
    reattack: bool = False,
) -> None:
    results = await scan_projects(config)
    analysis_results = (
        results
        if reattack
        else (await extract_vulnerable_analysis(config.get_database(), group_name, nickname)) or []
    )
    analysis_results = [x for x in analysis_results if (config.root_dir / x.path).exists()]
    await report_vulnerabilities(
        group_name,
        nickname,
        analysis_results,
        config.get_database(),
        reattack=reattack,
        head_commit_hash=get_repo_head_hash(config.root_dir),
    )


async def _get_reattack_lines_to_check(
    group_name: str,
    nickname: str,
) -> list[LinesConfig]:
    api_client = IntegratesApiClient(
        url="https://app.fluidattacks.com/api",
        headers={
            "Authorization": f"Bearer {os.environ.get('INTEGRATES_API_TOKEN')}",
            "x-integrates-source": "machine",
        },
    )

    vulnerabilities_to_reattack = await api_client.sifts_vulnerabilities_to_reattack(
        group_name=group_name
    )

    return [
        LinesConfig(
            file=Path(vulnerability.where.replace(nickname + "/", "")),
            lines=[int(vulnerability.specific)],
        )
        for vulnerability in vulnerabilities_to_reattack.vulnerabilities_to_reattack or []
        if vulnerability
        and vulnerability.root_nickname == nickname
        and vulnerability.vulnerability_type == "lines"
        and vulnerability.hacker == AI_SAST_EMAIL
        and vulnerability.technique == Technique.AI_SAST
    ]


async def _run_config_analysis(config_path: Path, output_path: Path) -> None:
    config = SiftsConfig.from_yaml(config_path)

    if config.group_name is None or config.root_nickname is None:
        msg = "Configuration file must specify both group_name and root_nickname"
        raise ValueError(msg)

    group_name = config.group_name
    nickname = config.root_nickname
    async with IntegratesApiClient(
        url="https://app.fluidattacks.com/api",
        headers={
            "Authorization": f"Bearer {os.environ.get('INTEGRATES_API_TOKEN')}",
            "x-integrates-source": "machine",
        },
    ) as integrates_client:
        root_id = await _get_root_id(integrates_client, group_name, nickname)
        if not root_id:
            msg = f"Root ID not found for group {group_name} and nickname {nickname}"
            raise ValueError(msg)

        if config.root_dir is None or not config.root_dir.exists() or config.root_dir == Path():
            working_dir = await pull_repositories(group_name, nickname)
            config.root_dir = working_dir
        else:
            working_dir = config.root_dir

        if not config.lines_to_skip and config.include_vulnerabilities_subcategories:
            lines_to_skip = await _collect_lines_to_skip(
                integrates_client,
                group_name,
                nickname,
                working_dir,
                config.include_vulnerabilities_subcategories,
            )
            config.lines_to_skip = lines_to_skip

    LOGGER.info("Scanning projects for %s %s", group_name, nickname)
    LOGGER.info("Using database backend: %s", config.database_backend)
    if config.database_backend == "sqlite":
        LOGGER.info("SQLite database path: %s", config.sqlite_database_path)

    await _run_analysis_workflow(
        config, group_name, nickname, output_path, reattack=bool(config.lines_to_check)
    )


async def _run_root_analysis(
    group_name: str,
    nickname: str,
    output_path: Path,
    *,
    reattack: bool = False,
) -> None:
    """Run the root analysis workflow."""
    async with IntegratesApiClient(
        url="https://app.fluidattacks.com/api",
        headers={
            "Authorization": f"Bearer {os.environ.get('INTEGRATES_API_TOKEN')}",
            "x-integrates-source": "machine",
        },
    ) as integrates_client:
        root_id = await _get_root_id(integrates_client, group_name, nickname)
        if not root_id:
            msg = f"Root ID not found for group {group_name} and nickname {nickname}"
            raise ValueError(msg)

        lines_to_check = (
            await _get_reattack_lines_to_check(group_name, nickname) if reattack else None
        )

        working_dir = await pull_repositories(group_name, nickname)
        include_vulnerabilities_subcategories = ["SQL Injection", "Cross-Site Scripting"]

        lines_to_skip = await _collect_lines_to_skip(
            integrates_client,
            group_name,
            nickname,
            working_dir,
            include_vulnerabilities_subcategories,
        )
    config = SiftsConfig.create_with_overrides(
        root_nickname=nickname,
        group_name=group_name,
        root_dir=working_dir,
        split_subdirectories=False,
        enable_navigation=False,
        include_vulnerabilities_subcategories=include_vulnerabilities_subcategories,
        lines_to_skip=lines_to_skip,
        lines_to_check=lines_to_check,
        model="gpt-4.1-mini",
        database_backend="dynamodb",
    )
    LOGGER.info("Scanning projects for %s %s", group_name, nickname)

    await _run_analysis_workflow(config, group_name, nickname, output_path, reattack=reattack)


if __name__ == "__main__":
    main_cli()

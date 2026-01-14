# Removed direct import - will use database backend from config
import json
import logging
from pathlib import Path
from typing import Any

import aioboto3
import aiofiles
from fluidattacks_core import sarif

import sifts
from sifts.analysis.criteria_data import DEFINES_REQUIREMENTS, DEFINES_VULNERABILITIES
from sifts.config import SiftsConfig
from sifts.core.repository import get_repo_branch, get_repo_head_hash, get_repo_remote
from sifts_io.db import AnalysisFacet, DatabaseBackend, SnippetFacet, VulnerableFacet
from taxonomy import TaxonomyIndex

LOGGER = logging.getLogger(__name__)

SARIF_FIELD_SCHEMA = "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.4.json"
REQUIREMENTS_URI_BASE = "https://db.fluidattacks.com/req"
WEAKNESSES_URI_BASE = "https://db.fluidattacks.com/wek"


def _get_rule(vuln_id: str) -> sarif.ReportingDescriptor:
    content = DEFINES_VULNERABILITIES[vuln_id]

    return sarif.ReportingDescriptor(
        id=vuln_id,
        name=content["en"]["title"],
        full_description=sarif.MultiformatMessageString(
            text=content["en"]["description"],
        ),
        help_uri=(f"{WEAKNESSES_URI_BASE}/{vuln_id}"),
        help=sarif.MultiformatMessageString(
            text=content["en"]["recommendation"],
        ),
        properties={"auto_approve": True},
    )


def _rule_is_present(base: sarif.SarifLog, rule_id: str) -> bool:
    return any(rule.id == rule_id for rule in base.runs[0].tool.driver.rules or [])


def _taxa_is_present(base: sarif.SarifLog, taxa_id: str) -> bool:
    if not base.runs[0].taxonomies:
        return False
    return any(rule.id == taxa_id for rule in base.runs[0].taxonomies[0].taxa or [])


def render_snippet(snippet: SnippetFacet, focus_line: int) -> str:
    snippet_content: str = snippet.text or ""
    # Format snippet highlighting the focus line and limiting the context to a
    # maximum of 10 lines above and 10 lines below the focus line.
    start_line = snippet.start_line

    # Enumerate all lines with their absolute line numbers.
    indexed_lines = list(enumerate(snippet_content.split("\n"), start=start_line))

    # Keep only the lines that are within the desired window.
    indexed_lines = [
        (idx, line) for idx, line in indexed_lines if focus_line - 10 <= idx <= focus_line + 10
    ]

    # Build the final snippet string, marking the focus line.
    return "\n".join(
        f"> {idx} | {line[:120]}" if idx == focus_line else f"  {idx} | {line[:120]}"
        for idx, line in indexed_lines
    )


async def _get_context_region(
    vulnerability: AnalysisFacet,
    vulnerable_line: int,
    config: SiftsConfig,
) -> sarif.Region:
    db_backend = config.get_database()
    snippet = await db_backend.get_snippet_by_hash(
        group_name=vulnerability.group_name,
        root_nickname=vulnerability.root_nickname,
        path=vulnerability.path,
        code_hash=vulnerability.code_hash,
    )
    if snippet:
        region = sarif.Region(
            start_line=max(snippet.start_line, 1),
            end_line=max(snippet.end_line, 1),
            snippet=sarif.ArtifactContent(
                rendered={"text": render_snippet(snippet, vulnerable_line)},
                text=snippet.text or "",
            ),
            start_column=max(snippet.start_column, 1),
            end_column=max(snippet.end_column, 1),
            source_language=snippet.language,
        )
    else:
        region = sarif.Region()

    return region


def _get_taxa(requirement_id: str) -> sarif.ReportingDescriptor:
    content = DEFINES_REQUIREMENTS[requirement_id]
    return sarif.ReportingDescriptor(
        id=requirement_id,
        name=content["en"]["title"],
        short_description=sarif.MultiformatMessageString(
            text=content["en"]["summary"],
        ),
        full_description=sarif.MultiformatMessageString(
            text=content["en"]["description"],
        ),
        help_uri=(f"{REQUIREMENTS_URI_BASE}/{requirement_id}"),
    )


async def _get_base(config: SiftsConfig, vulns: list[VulnerableFacet]) -> sarif.SarifLog:  # noqa: C901
    rules = []
    taxonomies = await TaxonomyIndex.load()
    for tax in taxonomies._taxonomy.values():
        for subcategory, entries in tax.items():
            if (
                config.include_vulnerabilities_subcategories
                and subcategory not in config.include_vulnerabilities_subcategories
            ):
                continue
            rules.extend([_get_rule(check["id"]) for check in entries])

    base = sarif.SarifLog(
        version="2.1.0",
        field_schema=(SARIF_FIELD_SCHEMA),
        runs=[
            sarif.Run(
                tool=sarif.Tool(
                    driver=sarif.ToolComponent(
                        name="smells",
                        rules=rules,
                        version="1.0.0",
                        semantic_version="1.0.0",
                        contents=[
                            sarif.Content.LOCALIZED_DATA,
                            sarif.Content.NON_LOCALIZED_DATA,
                        ],
                    ),
                ),
                results=[],
                version_control_provenance=[
                    sarif.VersionControlDetails(
                        repository_uri=get_repo_remote(config.root_dir),
                        revision_id=get_repo_head_hash(
                            config.root_dir,
                        ),
                        branch=get_repo_branch(config.root_dir),
                    ),
                ],
                taxonomies=[
                    sarif.ToolComponent(
                        name="criteria",
                        version="1",
                        information_uri=(REQUIREMENTS_URI_BASE),
                        organization="Fluidattacks",
                        short_description=sarif.MultiformatMessageString(
                            text="The fluidattacks security requirements",
                        ),
                        taxa=[],
                        is_comprehensive=False,
                        contents=[
                            sarif.Content.LOCALIZED_DATA,
                            sarif.Content.NON_LOCALIZED_DATA,
                        ],
                    ),
                ],
                web_responses=[],
            ),
        ],
    )
    for vulnerability in vulns:
        rule_id = vulnerability.suggested_criteria_code
        if not rule_id:
            continue
        db_backend = config.get_database()
        snippet = await db_backend.get_snippet_by_hash(
            group_name=vulnerability.group_name,
            root_nickname=vulnerability.root_nickname,
            path=vulnerability.path,
            code_hash=vulnerability.code_hash,
        )
        if not snippet:
            continue

        result = sarif.Result(
            rule_id=rule_id,
            level="note",
            message=sarif.Message(
                root=sarif.Message1(
                    text=vulnerability.reason,
                ),
            ),
            locations=[
                sarif.Location(
                    physical_location=sarif.PhysicalLocation(
                        root=sarif.PhysicalLocation2(
                            artifact_location=sarif.ArtifactLocation(
                                uri=vulnerability.path,
                            ),
                            region=sarif.Region(
                                start_line=x,
                                source_language=snippet.language,
                            ),
                            context_region=await _get_context_region(vulnerability, x, config),
                        )
                    ),
                )
                for x in vulnerability.vulnerable_lines or []
            ],
            taxa=[],
            fingerprints={"guid": str(vulnerability.digest)},
        )
        # append rule if not is present
        if not _rule_is_present(base, rule_id) and base.runs[0].tool.driver.rules:
            base.runs[0].tool.driver.rules.append(_get_rule(rule_id))

        for taxa_id in DEFINES_VULNERABILITIES[rule_id]["requirements"]:
            if (
                not _taxa_is_present(base, taxa_id)
                and base.runs[0].taxonomies
                and base.runs[0].taxonomies[0].taxa
            ):
                base.runs[0].taxonomies[0].taxa.append(_get_taxa(taxa_id))

        result.taxa = [
            sarif.ReportingDescriptorReference(
                root=sarif.ReportingDescriptorReference1(
                    id=taxa_id,
                    tool_component=sarif.ToolComponentReference(name="criteria"),
                    index=index,
                )
            )
            for index, taxa_id in enumerate(DEFINES_VULNERABILITIES[rule_id]["requirements"])
        ]
        if base.runs[0].results:
            base.runs[0].results.append(result)
        else:
            base.runs[0].results = [result]
    return base


async def get_sarif(vulns: list[VulnerableFacet], config: SiftsConfig) -> dict[str, Any]:
    return (await _get_base(config, vulns)).model_dump(
        mode="json",
        by_alias=True,
        exclude_none=True,
        exclude_unset=True,
    )


async def extract_vulnerable_analysis(
    db_backend: DatabaseBackend, group_name: str, nickname: str, commit: str | None = None
) -> list[VulnerableFacet]:
    analyses = [
        x
        for x in await db_backend.get_analyses_by_root(
            group_name, nickname, sifts.__version__, commit=commit
        )
        if x.vulnerable
    ]
    return [x for x in analyses if isinstance(x, VulnerableFacet)]


async def upload_sarif_to_remote(
    sarif_results: dict[str, Any],
    group_name: str,
    nickname: str,
) -> str:
    async with aioboto3.Session().client("s3") as s3_client:
        key = f"{group_name}_{nickname}_sifts_{sifts.__version__}"
        await s3_client.put_object(
            Bucket="machine.data",
            Key=f"results/{key}.sarif",
            Body=json.dumps(sarif_results, indent=2),
        )
        LOGGER.info("Uploaded SARIF file to %s", f"results/{key}.sarif")
        return key


async def process_sarif_results(  # noqa: PLR0913
    group_name: str,
    nickname: str,
    *,
    config: SiftsConfig,
    db_backend: DatabaseBackend,
    output_path: Path,
    commit: str | None = None,
) -> tuple[str, int]:
    commit_filter = commit if config.sarif_policy == "new_only" else None
    vulnerable_analysis = await extract_vulnerable_analysis(
        db_backend, group_name, nickname, commit=commit_filter
    )
    sarif_results = await get_sarif(vulnerable_analysis, config)
    async with aiofiles.open(output_path, "w") as f:
        await f.write(json.dumps(sarif_results, indent=2))
    if config.sarif_to_remote:
        return await upload_sarif_to_remote(sarif_results, group_name, nickname), len(
            vulnerable_analysis
        )
    return str(output_path.absolute()), len(vulnerable_analysis)

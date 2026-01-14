import io
import json
import os
import re
import secrets
import string
from collections import defaultdict
from collections.abc import AsyncGenerator, Sequence

import yaml

from common_types.vulnerabilities_file import (
    Impact,
    Line,
    Model,
    Origin,
    Source,
    State,
    Technique,
    Tool1,
)
from graphql_client import (
    EvidenceDescriptionType,
    EvidenceType,
    Language,
    SiftsVulnerabilitiesToReattackVulnerabilitiesToReattack,
    Upload,
    VulnerabilityState,
)
from graphql_client.client import IntegratesApiClient
from graphql_client.enums import Technique as GraphQLTechnique
from graphql_client.sifts_finding_vulnerabilities import (
    SiftsFindingVulnerabilitiesFindingVulnerabilitiesEdgesNode,
)
from graphql_client.sifts_findings import SiftsFindingsGroupFindings
from sifts.constants import AI_SAST_EMAIL
from sifts.core.report.finding import get_target_finding
from sifts.core.report.image_utils import to_png
from sifts.core.report.translation import translate_to_spanish
from sifts_io.db import DatabaseBackend
from sifts_io.db.types import AnalysisFacet, SnippetFacet, VulnerableFacet

MAX_SCANNER_DESCRIPTION_LENGTH = 1000


def _sanitize_evidence_description(description: str) -> str:
    allowed_chars = (
        r"a-zA-Z0-9ñáéíóúäëïöüÑÁÉÍÓÚÄËÏÖÜ\s'~:;%@&_$#=¡!¿\,\.\*\-\?\"\[\]\|\(\)\/\{\}\>\+"
    )
    pattern = rf"[{allowed_chars}]"
    sanitized = "".join(re.findall(pattern, description))
    return sanitized.removeprefix("=")


def _truncate_scanner_description(
    description: str, *, max_length: int = MAX_SCANNER_DESCRIPTION_LENGTH
) -> str:
    if len(description) <= max_length:
        return description
    return description[:max_length]


async def _is_vulnerability_already_reported(
    api_client: IntegratesApiClient,
    finding: SiftsFindingsGroupFindings,
    db_backend: DatabaseBackend,
    sifts_vuln: VulnerableFacet,
) -> bool:
    snippet = await db_backend.get_snippet_by_hash(
        group_name=sifts_vuln.group_name,
        root_nickname=sifts_vuln.root_nickname,
        path=sifts_vuln.path,
        code_hash=sifts_vuln.code_hash,
    )
    if not snippet:
        return True
    where_path = f"{sifts_vuln.root_nickname}/{snippet.path}"
    current_after = None
    has_next_page = True
    while has_next_page:
        finding_vulnerabilities = await api_client.sifts_finding_vulnerabilities_by_where(
            finding_id=finding.id,
            where=where_path,
            after=current_after,
        )
        for edge in finding_vulnerabilities.finding.vulnerabilities.edges:
            if not edge:
                continue
            existing_vuln = edge.node
            if (
                existing_vuln.state == VulnerabilityState.VULNERABLE
                and existing_vuln.root_nickname == sifts_vuln.root_nickname
                and existing_vuln.vulnerability_type == "lines"
                and int(existing_vuln.specific) in range(snippet.start_line, snippet.end_line + 1)
            ):
                return True
        if finding_vulnerabilities.finding.vulnerabilities.page_info.has_next_page:
            current_after = finding_vulnerabilities.finding.vulnerabilities.page_info.end_cursor
            has_next_page = True
        else:
            has_next_page = False
    return False


async def _generate_evidence_image_bytes(
    snippet: SnippetFacet,
    focus_line: int,
) -> io.BytesIO:
    rendered_snippet: str = snippet.render_snippet(focus_line=focus_line)
    image = await to_png(string=rendered_snippet)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    return image_bytes


def _generate_evidence_filename(organization: str, group_name: str) -> str:
    random_chars = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
    return f"{organization}-{group_name}-{random_chars}.png"


async def _prepare_evidence_description(
    reason: str,
    language: Language,
) -> str:
    raw_description = await translate_to_spanish(reason) if language == Language.ES else reason
    return _sanitize_evidence_description(raw_description)


async def _set_evidence_description_if_needed(
    *,
    api_client: IntegratesApiClient,
    finding: SiftsFindingsGroupFindings,
    description: str,
) -> None:
    if not finding.evidence.evidence_5 or not finding.evidence.evidence_5.description:
        await api_client.sifts_set_evidence_description(
            finding_id=finding.id,
            description=description,
            evidence_id=EvidenceDescriptionType.EVIDENCE5,
        )


async def _set_evidence_file_if_needed(
    *,
    api_client: IntegratesApiClient,
    finding: SiftsFindingsGroupFindings,
    filename: str,
    image_bytes: io.BytesIO,
) -> None:
    if not finding.evidence.evidence_5 or not finding.evidence.evidence_5.url:
        await api_client.sifts_set_evidence(
            finding_id=finding.id,
            file=Upload(
                filename=filename,
                content=image_bytes,
                content_type="image/png",
            ),
            evidence_id=EvidenceType.EVIDENCE5,
        )


async def _update_evidence_5(
    *,
    api_client: IntegratesApiClient,
    db_backend: DatabaseBackend,
    finding: SiftsFindingsGroupFindings,
    vulnerability: VulnerableFacet,
) -> None:
    snippet = await db_backend.get_snippet_by_hash(
        group_name=vulnerability.group_name,
        root_nickname=vulnerability.root_nickname,
        path=vulnerability.path,
        code_hash=vulnerability.code_hash,
    )
    if not snippet:
        return

    group = await api_client.sifts_get_group(group_name=finding.group_name)
    organization = group.group.organization
    language = group.group.language

    image_bytes = await _generate_evidence_image_bytes(
        snippet=snippet,
        focus_line=vulnerability.vulnerable_lines[0],
    )
    filename = _generate_evidence_filename(
        organization=organization,
        group_name=finding.group_name,
    )

    await _set_evidence_file_if_needed(
        api_client=api_client,
        finding=finding,
        filename=filename,
        image_bytes=image_bytes,
    )

    description = await _prepare_evidence_description(
        reason=vulnerability.reason,
        language=language,
    )
    await _set_evidence_description_if_needed(
        api_client=api_client,
        finding=finding,
        description=description,
    )


async def _get_finding_vulnerabilities(
    api_client: IntegratesApiClient,
    finding_id: str,
    root_nickname: str,
) -> AsyncGenerator[SiftsFindingVulnerabilitiesFindingVulnerabilitiesEdgesNode, None]:
    """Async generator that yields all VULNERABLE vulnerabilities from a finding."""
    current_after = None
    has_next_page = True

    while has_next_page:
        finding_vulnerabilities = await api_client.sifts_finding_vulnerabilities(
            finding_id=finding_id,
            after=current_after,
        )

        for edge in finding_vulnerabilities.finding.vulnerabilities.edges:
            if not edge or not edge.node:
                continue

            existing_vuln = edge.node
            if (
                existing_vuln.state == VulnerabilityState.VULNERABLE
                and existing_vuln.root_nickname == root_nickname
                and existing_vuln.vulnerability_type == "lines"
                and existing_vuln.hacker == AI_SAST_EMAIL
            ):
                yield existing_vuln

        if finding_vulnerabilities.finding.vulnerabilities.page_info.has_next_page:
            current_after = finding_vulnerabilities.finding.vulnerabilities.page_info.end_cursor
        else:
            has_next_page = False


async def _is_vulnerability_still_present(
    vuln_path: str,
    vuln_line: int,
    criteria_code: str | None,
    current_vulnerabilities: list[VulnerableFacet],
    db_backend: DatabaseBackend,
) -> bool:
    """Check if a vulnerability is still present in current analysis."""
    for current_vuln in current_vulnerabilities:
        if current_vuln.path != vuln_path:
            continue
        if not current_vuln.suggested_criteria_code:
            continue
        if criteria_code and current_vuln.suggested_criteria_code != criteria_code:
            continue

        snippet = await db_backend.get_snippet_by_hash(
            group_name=current_vuln.group_name,
            root_nickname=current_vuln.root_nickname,
            path=current_vuln.path,
            code_hash=current_vuln.code_hash,
        )
        if snippet and snippet.start_line <= vuln_line <= snippet.end_line:
            return True
    return False


async def close_obsolete_vulnerabilities(  # noqa: PLR0913
    *,
    api_client: IntegratesApiClient,
    db_backend: DatabaseBackend,
    finding: SiftsFindingsGroupFindings,
    all_vulnerabilities: list[VulnerableFacet],
    root_nickname: str,
    head_commit_hash: str | None,
) -> None:
    """Close vulnerabilities from a finding that are no longer present in the analysis."""
    locations: list[Line] = []
    closed_description = "Vulnerability no longer detected by SIFTS analysis"
    finding_criteria_code = finding.title.split(".")[0] if "." in finding.title else None

    async for existing_vuln in _get_finding_vulnerabilities(api_client, finding.id, root_nickname):
        vuln_path = existing_vuln.where.replace(f"{root_nickname}/", "")
        vuln_line = int(existing_vuln.specific)

        is_still_present = await _is_vulnerability_still_present(
            vuln_path, vuln_line, finding_criteria_code, all_vulnerabilities, db_backend
        )

        if not is_still_present:
            locations.append(
                Line(
                    line=str(vuln_line),
                    path=vuln_path,
                    repo_nickname=root_nickname,
                    source=Source.AI,
                    developer="ai@fluidattacks.com",
                    state=State.CLOSED,
                    tool=Tool1(impact=Impact.direct, name="sifts"),
                    technique=Technique.AI_SAST,
                    origin=Origin.INJECTED,
                    scanner_description=closed_description,
                    scanner_method_name="sifts",
                    commit_hash=head_commit_hash,
                )
            )

    if locations:
        model = Model(lines=locations, inputs=[], ports=[])
        yaml_content = yaml.dump(json.loads(model.model_dump_json()), default_flow_style=False)
        await api_client.sifts_upload_vulnerabilities(
            file=Upload(
                filename="vulnerabilities.yaml",
                content=io.BytesIO(yaml_content.encode(encoding="utf-8")),
                content_type="text/x-yaml",
            ),
            finding_id=finding.id,
        )


async def report_vulnerabilities_to_finding(
    *,
    api_client: IntegratesApiClient,
    db_backend: DatabaseBackend,
    finding: SiftsFindingsGroupFindings,
    vulnerabilities: list[VulnerableFacet],
    root_nickname: str,
) -> None:
    """Report new vulnerabilities to a finding."""
    language = (await api_client.sifts_get_group(group_name=finding.group_name)).group.language
    locations: list[Line] = []
    for vuln in vulnerabilities:
        if await _is_vulnerability_already_reported(api_client, finding, db_backend, vuln):
            continue

        reason = await translate_to_spanish(vuln.reason) if language == Language.ES else vuln.reason
        truncated_reason = _truncate_scanner_description(
            reason, max_length=MAX_SCANNER_DESCRIPTION_LENGTH
        )
        locations.extend(
            Line(
                commit_hash=vuln.commit,
                line=str(line),
                path=vuln.path,
                repo_nickname=root_nickname,
                source=Source.AI,
                developer=AI_SAST_EMAIL,
                state=State.SUBMITTED,
                tool=Tool1(impact=Impact.direct, name="sifts"),
                technique=Technique.AI_SAST,
                origin=Origin.INJECTED,
                scanner_description=truncated_reason,
                scanner_method_name="sifts",
            )
            for line in vuln.vulnerable_lines
        )

    if locations:
        model = Model(lines=locations, inputs=[], ports=[])
        yaml_content = yaml.dump(json.loads(model.model_dump_json()), default_flow_style=False)
        await api_client.sifts_upload_vulnerabilities(
            file=Upload(
                filename="vulnerabilities.yaml",
                content=io.BytesIO(yaml_content.encode(encoding="utf-8")),
                content_type="text/x-yaml",
            ),
            finding_id=finding.id,
        )


async def _approve_vulnerabilities(
    *,
    api_client: IntegratesApiClient,
    finding: SiftsFindingsGroupFindings,
) -> None:
    finding_vulnerabilities_submitted = tuple(
        node.node
        for node in (
            await api_client.sifts_finding_vulnerabilities(finding_id=finding.id)
        ).finding.vulnerabilities.edges
        if node and node.node and node.node.state == VulnerabilityState.SUBMITTED
    )
    await api_client.sifts_approve_vulnerabilities(
        finding_id=finding.id,
        vulnerability_ids=[vulnerability.id for vulnerability in finding_vulnerabilities_submitted],
    )


async def _get_reattack_lines(
    group_name: str,
    nickname: str,
) -> list[SiftsVulnerabilitiesToReattackVulnerabilitiesToReattack]:
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
        vulnerability
        for vulnerability in vulnerabilities_to_reattack.vulnerabilities_to_reattack or []
        if vulnerability is not None
        and vulnerability.root_nickname == nickname
        and vulnerability.vulnerability_type == "lines"
        and vulnerability.hacker == AI_SAST_EMAIL
        and vulnerability.technique is not None
        and vulnerability.technique == GraphQLTechnique.AI_SAST
    ]


async def _is_reattack_vulnerability_still_open(
    reattack_vuln: SiftsVulnerabilitiesToReattackVulnerabilitiesToReattack,
    analysis_results: Sequence[AnalysisFacet],
    nickname: str,
    db_backend: DatabaseBackend,
    api_client: IntegratesApiClient,
) -> bool:
    """Check if a reattack vulnerability is still present in current analysis."""
    if not analysis_results:
        return False

    reattack_path = reattack_vuln.where.replace(f"{nickname}/", "")
    reattack_line = int(reattack_vuln.specific)
    finding_id = reattack_vuln.finding_id

    finding = await api_client.sifts_get_finding(identifier=finding_id)
    if not finding or not finding.finding:
        return False

    finding_title = finding.finding.title
    criteria_code = finding_title.split(".")[0] if "." in finding_title else None

    # Filter to only VulnerableFacet instances
    vulnerable_results = [
        result for result in analysis_results if isinstance(result, VulnerableFacet)
    ]

    return await _is_vulnerability_still_present(
        vuln_path=reattack_path,
        vuln_line=reattack_line,
        criteria_code=criteria_code,
        current_vulnerabilities=vulnerable_results,
        db_backend=db_backend,
    )


async def _classify_reattack_vulnerabilities(
    reattack_lines: Sequence[SiftsVulnerabilitiesToReattackVulnerabilitiesToReattack],
    analysis_results: Sequence[AnalysisFacet],
    nickname: str,
    db_backend: DatabaseBackend,
    api_client: IntegratesApiClient,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    open_vulns_by_finding: dict[str, list[str]] = defaultdict(list)
    closed_vulns_by_finding: dict[str, list[str]] = defaultdict(list)

    for reattack_vuln in reattack_lines:
        finding_id = reattack_vuln.finding_id
        vuln_id = reattack_vuln.id

        is_open = await _is_reattack_vulnerability_still_open(
            reattack_vuln, analysis_results, nickname, db_backend, api_client
        )
        if is_open:
            open_vulns_by_finding[finding_id].append(vuln_id)
        else:
            closed_vulns_by_finding[finding_id].append(vuln_id)

    return open_vulns_by_finding, closed_vulns_by_finding


async def _verify_reattack_results(
    api_client: IntegratesApiClient,
    reattack_lines: Sequence[SiftsVulnerabilitiesToReattackVulnerabilitiesToReattack],
    analysis_results: Sequence[AnalysisFacet],
    nickname: str,
    db_backend: DatabaseBackend,
) -> None:
    open_vulns_by_finding, closed_vulns_by_finding = await _classify_reattack_vulnerabilities(
        reattack_lines, analysis_results, nickname, db_backend, api_client
    )

    all_finding_ids = set(open_vulns_by_finding.keys()) | set(closed_vulns_by_finding.keys())

    for finding_id in all_finding_ids:
        open_vulns = open_vulns_by_finding.get(finding_id, [])
        closed_vulns = closed_vulns_by_finding.get(finding_id, [])

        if open_vulns or closed_vulns:
            await api_client.sifts_verify_vulnerabilities_request(
                finding_id=finding_id,
                justification="Verified by SIFTS reattack analysis",
                open_vulnerabilities=open_vulns,
                closed_vulnerabilities=closed_vulns,
            )


async def _get_all_ai_findings(
    api_client: IntegratesApiClient, group_name: str
) -> list[SiftsFindingsGroupFindings]:
    """Get all AI findings from a group."""
    findings_response = await api_client.sifts_findings(group_name=group_name)
    return [
        finding
        for finding in findings_response.group.findings or []
        if finding and finding.hacker == "ai@fluidattacks.com"
    ]


async def _process_finding_with_new_vulnerabilities(
    api_client: IntegratesApiClient,
    db_backend: DatabaseBackend,
    finding: SiftsFindingsGroupFindings,
    finding_vulnerabilities: list[VulnerableFacet],
    root_nickname: str,
) -> None:
    """Process finding with new vulnerabilities: update evidence, report, and approve."""
    evidence_5 = finding.evidence.evidence_5
    needs_evidence_update = not evidence_5 or not evidence_5.description or not evidence_5.url

    if needs_evidence_update:
        try:
            await _update_evidence_5(
                api_client=api_client,
                db_backend=db_backend,
                finding=finding,
                vulnerability=next(x for x in finding_vulnerabilities if x.vulnerable_lines),
            )
        except StopIteration:
            return

    await report_vulnerabilities_to_finding(
        api_client=api_client,
        db_backend=db_backend,
        finding=finding,
        vulnerabilities=finding_vulnerabilities,
        root_nickname=root_nickname,
    )

    is_draft = evidence_5 is not None and (
        evidence_5.is_draft is True or evidence_5.is_draft is None
    )
    if needs_evidence_update or is_draft:
        await api_client.sifts_approve_evidence(
            finding_id=finding.id,
            evidence_id=EvidenceDescriptionType.EVIDENCE5,
        )
    await _approve_vulnerabilities(api_client=api_client, finding=finding)


async def report_vulnerabilities(  # noqa: PLR0913
    group_name: str,
    nickname: str,
    analysis_results: Sequence[AnalysisFacet],
    db_backend: DatabaseBackend,
    *,
    reattack: bool = False,
    head_commit_hash: str | None = None,
) -> None:
    api_client = IntegratesApiClient(
        url="https://app.fluidattacks.com/api",
        headers={
            "Authorization": f"Bearer {os.environ.get('INTEGRATES_API_TOKEN')}",
            "x-integrates-source": "machine",
        },
    )

    if reattack:
        reattack_lines = await _get_reattack_lines(group_name, nickname)
        await _verify_reattack_results(
            api_client, reattack_lines, analysis_results, nickname, db_backend
        )
        return

    vulnerable_analysis = [r for r in analysis_results if isinstance(r, VulnerableFacet)]
    grouped_vulnerabilities: dict[str, list[VulnerableFacet]] = defaultdict(list)
    for vuln in vulnerable_analysis:
        if not vuln.suggested_criteria_code:
            continue
        grouped_vulnerabilities[vuln.suggested_criteria_code].append(vuln)

    for criteria_code, finding_vulns in grouped_vulnerabilities.items():
        finding = await get_target_finding(api_client, group_name, criteria_code)
        await _process_finding_with_new_vulnerabilities(
            api_client=api_client,
            db_backend=db_backend,
            finding=finding,
            finding_vulnerabilities=finding_vulns,
            root_nickname=nickname,
        )

    all_ai_findings = await _get_all_ai_findings(api_client, group_name)
    for finding in all_ai_findings:
        await close_obsolete_vulnerabilities(
            api_client=api_client,
            db_backend=db_backend,
            finding=finding,
            all_vulnerabilities=vulnerable_analysis,
            root_nickname=nickname,
            head_commit_hash=head_commit_hash,
        )

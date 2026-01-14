from graphql_client.client import IntegratesApiClient
from graphql_client.sifts_findings import SiftsFindingsGroupFindings
from sifts.analysis.criteria_data import DEFINES_VULNERABILITIES
from sifts.constants import AI_SAST_EMAIL
from sifts.core.report.cvss import get_criteria_cvss4_vector


async def _create_finding_internal(
    api_client: IntegratesApiClient, group_name: str, criteria_code: str
) -> None:
    language = (await api_client.sifts_get_group(group_name=group_name)).group.language
    criteria_vulnerability = DEFINES_VULNERABILITIES[criteria_code]
    criteria_finding = criteria_vulnerability[language.value.lower()]

    description = criteria_finding["description"]
    recommendation = criteria_finding["recommendation"]
    threat = criteria_finding["threat"]
    attack_vector_description = criteria_finding["impact"]
    requirements_raw = criteria_vulnerability["requirements"]
    unfulfilled_requirements: list[str] = (
        requirements_raw if isinstance(requirements_raw, list) else []
    )

    cvss_4_vector = get_criteria_cvss4_vector(criteria_vulnerability) or ""

    await api_client.sifts_add_finding(
        group_name=group_name,
        title=f"{criteria_code}. {criteria_finding['title']}",
        description=description,
        recommendation=recommendation,
        threat=threat,
        attack_vector_description=attack_vector_description,
        cvss_4_vector=cvss_4_vector,
        unfulfilled_requirements=unfulfilled_requirements,
        hacker_email=AI_SAST_EMAIL,
    )


async def _search_finding_by_criteria(
    api_client: IntegratesApiClient, group_name: str, criteria_code: str
) -> SiftsFindingsGroupFindings | None:
    findings_response = await api_client.sifts_findings(group_name=group_name)
    for finding in findings_response.group.findings or []:
        if (
            not finding
            or finding.hacker != AI_SAST_EMAIL
            or finding.title.split(".")[0] != criteria_code
        ):
            continue
        return finding
    return None


async def get_target_finding(
    api_client: IntegratesApiClient, group_name: str, criteria_code: str
) -> SiftsFindingsGroupFindings:
    finding = await _search_finding_by_criteria(api_client, group_name, criteria_code)
    if finding:
        return finding
    await _create_finding_internal(api_client, group_name, criteria_code)
    finding = await _search_finding_by_criteria(api_client, group_name, criteria_code)
    if finding:
        return finding
    error_message = f"Failed to create or retrieve finding for criteria {criteria_code}"
    raise RuntimeError(error_message)

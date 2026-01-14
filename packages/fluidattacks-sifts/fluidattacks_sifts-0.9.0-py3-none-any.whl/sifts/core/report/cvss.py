from typing import Any

from cvss import CVSS4, CVSS4Error


def get_criteria_cvss4_vector(criteria_vulnerability: dict[str, Any]) -> str | None:
    base = criteria_vulnerability["score_v4"]["base"]
    threat = criteria_vulnerability["score_v4"]["threat"]
    vector_string = (
        "CVSS:4.0/"
        f"AV:{base['attack_vector']}"
        f"/AC:{base['attack_complexity']}"
        f"/AT:{base['attack_requirements']}"
        f"/PR:{base['privileges_required']}"
        f"/UI:{base['user_interaction']}"
        f"/VC:{base['confidentiality_vc']}"
        f"/VI:{base['integrity_vi']}"
        f"/VA:{base['availability_va']}"
        f"/SC:{base['confidentiality_sc']}"
        f"/SI:{base['integrity_si']}"
        f"/SA:{base['availability_sa']}"
        f"/E:{threat['exploit_maturity']}"
    )
    try:
        cvss4 = CVSS4(vector_string)
    except CVSS4Error:
        return None

    return str(cvss4.clean_vector())

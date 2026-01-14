from taxonomy import ReducedCriteria, str_to_subcategory

reduced_criteria = ReducedCriteria.load_sync()


def generate_candidate_text(candidate_subcategory: str) -> str:
    subcategory = str_to_subcategory(candidate_subcategory)
    description = reduced_criteria.get_criteria(subcategory)
    return f"# Candidate vulnerability: {candidate_subcategory}\n## Description: {description}"

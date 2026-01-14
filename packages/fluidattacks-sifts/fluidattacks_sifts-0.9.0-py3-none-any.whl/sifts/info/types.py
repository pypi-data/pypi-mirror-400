import re
from dataclasses import dataclass


@dataclass
class Version:
    value: str

    @classmethod
    def from_string(cls, value: str) -> "Version":
        if not re.match(r"^(latest|\d+\.\d+(\.\d+)?|V\d+)$", value):
            msg = f"Invalid version: {value!r}"
            raise ValueError(msg)
        return Version(value)


@dataclass
class ComponentsInformation:
    sifts_version: Version
    candidates_model_version: Version
    candidates_dataset_version: Version
    candidates_network_architecture: str
    candidates_model_wrapper: str
    candidates_hyper_parameters: dict[str, int | float]
    sifts_snippets_parser: str
    sifts_llm_model: str
    sifts_llm_model_parameters: str
    sifts_llm_prompt_version: Version

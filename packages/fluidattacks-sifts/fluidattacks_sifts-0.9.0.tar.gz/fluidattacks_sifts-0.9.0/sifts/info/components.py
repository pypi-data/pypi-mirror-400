import json
import os

from snowflake.connector import SnowflakeConnection, connect

import sifts
from sifts.constants import PREDICTION_MODEL_VERSION
from sifts.info.types import ComponentsInformation, Version
from sifts.llm.config_data import MODEL_PARAMETERS

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_AUTHENTICATOR = os.getenv("SNOWFLAKE_AUTHENTICATOR")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_USER_PRIVATE_KEY = os.getenv("SNOWFLAKE_USER_PRIVATE_KEY")


def get_connection() -> SnowflakeConnection:
    """Get a Snowflake connection with the provided credentials."""
    if (
        not SNOWFLAKE_USER
        or not SNOWFLAKE_USER_PRIVATE_KEY
        or not SNOWFLAKE_ACCOUNT
        or not SNOWFLAKE_ROLE
        or not SNOWFLAKE_AUTHENTICATOR
    ):
        msg = "Incomplete requirements for Snowflake connection"
        raise ValueError(msg)
    return connect(
        account=SNOWFLAKE_ACCOUNT,
        authenticator=SNOWFLAKE_AUTHENTICATOR,
        private_key=SNOWFLAKE_USER_PRIVATE_KEY,
        role=SNOWFLAKE_ROLE,
        user=SNOWFLAKE_USER,
    )


MODEL_ARCH = "FULLY_CONNECTED"
MODEL_WRAPPER = "TAXONOMY"
DEFAULT = "DEFAULT"
FALLBACK_VERSION = "latest"


def get_components_information() -> ComponentsInformation:
    return ComponentsInformation(
        sifts_version=Version.from_string(sifts.__version__),
        candidates_model_version=Version.from_string(PREDICTION_MODEL_VERSION),
        candidates_dataset_version=Version.from_string(
            FALLBACK_VERSION
        ),  # Requires a mechanism of retrieval
        candidates_network_architecture=MODEL_ARCH,
        candidates_model_wrapper=MODEL_WRAPPER,
        candidates_hyper_parameters={},  # Will be defined soon
        sifts_snippets_parser=DEFAULT,  # Will be defined soon
        sifts_llm_model=DEFAULT,  # Will be defined soon
        sifts_llm_model_parameters=DEFAULT,  # Will be defined soon
        sifts_llm_prompt_version=Version.from_string(MODEL_PARAMETERS["version"]),
    )


async def persist_version_component_details() -> None:
    components_information = get_components_information()
    connection = get_connection()

    insert_query = """
        INSERT INTO SIFTS.SIFTS_CANDIDATES.SIFTS_VERSION_COMPONENTS (
            SIFTS_VERSION,
            CANDIDATES_MODEL_VERSION,
            CANDIDATES_DATASET_VERSION,
            CANDIDATES_NETWORK_ARCHITECTURE,
            CANDIDATES_MODEL_WRAPPER,
            CANDIDATES_HYPER_PARAMETERS,
            SIFTS_SNIPPETS_PARSER,
            SIFTS_LLM_MODEL,
            SIFTS_LLM_MODEL_PARAMETERS,
            SIFTS_LLM_PROMPT_VERSION,
            SIFTS_STRICT_PROMPT,
            VALIDATION_DATASET_VERSION
        ) VALUES (
            %(sifts_version)s,
            %(candidates_model_version)s,
            %(candidates_dataset_version)s,
            %(candidates_network_architecture)s,
            %(candidates_model_wrapper)s,
            PARSE_JSON(%(candidates_hyper_parameters)s),
            %(sifts_snippets_parser)s,
            %(sifts_llm_model)s,
            %(sifts_llm_model_parameters)s,
            %(sifts_llm_prompt_version)s,
            %(sifts_strict_prompt)s,
            %(validation_dataset_version)s
        )
    """

    params = {
        "sifts_version": components_information.sifts_version.value,
        "candidates_model_version": components_information.candidates_model_version.value,
        "candidates_dataset_version": components_information.candidates_dataset_version.value,
        "candidates_network_architecture": components_information.candidates_network_architecture,
        "candidates_model_wrapper": components_information.candidates_model_wrapper,
        "candidates_hyper_parameters": json.dumps(
            components_information.candidates_hyper_parameters
        ),
        "sifts_snippets_parser": components_information.sifts_snippets_parser,
        "sifts_llm_model": components_information.sifts_llm_model,
        "sifts_llm_model_parameters": components_information.sifts_llm_model_parameters,
        "sifts_llm_prompt_version": components_information.sifts_llm_prompt_version.value,
        "sifts_strict_prompt": False,
        "validation_dataset_version": DEFAULT,
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute(insert_query, params)
        connection.commit()
    finally:
        connection.close()

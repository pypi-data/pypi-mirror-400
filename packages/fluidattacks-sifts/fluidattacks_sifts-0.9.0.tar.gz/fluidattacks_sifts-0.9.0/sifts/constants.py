import os


def _get_artifact(env_var: str) -> str:
    secret = os.environ.get(env_var)
    if not secret:
        msg = f"Expected environment variable: {env_var}"
        raise ValueError(msg)
    return secret


# Snowflake credentials

SNOWFLAKE_ACCOUNT = _get_artifact("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER_PRIVATE_KEY = _get_artifact("SNOWFLAKE_USER_PRIVATE_KEY")
SNOWFLAKE_USER = _get_artifact("SNOWFLAKE_USER")
SNOWFLAKE_ROLE = _get_artifact("SNOWFLAKE_ROLE")
SNOWFLAKE_DATABASE = "SIFTS"
SNOWFLAKE_INFERENCE_SCHEMA = "SIFTS_CANDIDATES"

# Candidates model details

PREDICTION_MODEL_NAME = "CANDIDATE_CLASSIFIER"
PREDICTION_MODEL_VERSION = "V12"
DEFAULT_FUNCTION_NAME = "PREDICT"
INFERENCE_SERVICE_NAME = "SIFTS_CANDIDATES_SUBCATEGORIES_SERVICE"

# Embeddings model

EMBEDDING_MODEL = "voyage-code-3"

# Bugsnag

BUGSNAG_API_KEY = (
    "78f25bb5dab62944e52ceffd694cd7e0"  # Not problem at all with it being public in source code
)

# AI SAST business

AI_SAST_EMAIL = "ai@fluidattacks.com"

import os

from platformdirs import user_data_dir

DATA_DIR = user_data_dir("sifts", ensure_exists=True)


FI_AWS_OPENSEARCH_HOST = os.environ.get("AWS_OPENSEARCH_HOST", "https://localhost:9200")


FI_AWS_REGION_NAME = "us-east-1"


FI_ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

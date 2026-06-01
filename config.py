import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    aws_region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    bedrock_model_id: str
    dynamodb_table_name: str
    sentiment_threshold: float  # below this score, escalate to human
    api_host: str
    api_port: int


def load_config() -> Config:
    """Load and validate environment variables at startup."""
    missing = []
    for var in ["AWS_REGION", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]:
        if not os.getenv(var):
            missing.append(var)
    if missing:
        raise ValueError(f"Missing env vars: {', '.join(missing)}")

    return Config(
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        bedrock_model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
        dynamodb_table_name=os.getenv("DYNAMODB_TABLE", "support-conversations"),
        sentiment_threshold=float(os.getenv("SENTIMENT_THRESHOLD", "0.3")),
        api_host=os.getenv("API_HOST", "0.0.0.0"),
        api_port=int(os.getenv("API_PORT", "8000")),
    )


config = load_config()

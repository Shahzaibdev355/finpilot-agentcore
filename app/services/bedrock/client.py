import boto3

from app.config.settings import settings


def get_bedrock_runtime_client():
    return boto3.client(
        "bedrock-runtime",
        region_name=settings.aws_region,
    )
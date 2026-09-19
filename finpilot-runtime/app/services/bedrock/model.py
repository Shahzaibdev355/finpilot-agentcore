from app.config.settings import settings
from app.services.bedrock.client import get_bedrock_runtime_client


def invoke_finpilot_model(prompt: str) -> str:
    client = get_bedrock_runtime_client()

    response = client.converse(
        modelId=settings.bedrock_prompt_router_arn,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt,
                    }
                ],
            }
        ],
    )

    return response["output"]["message"]["content"][0]["text"]

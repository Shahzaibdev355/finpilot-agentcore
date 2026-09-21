import json
import uuid

import boto3

from app.config.settings import settings


class SupervisorClient:
    """Client for invoking the deployed FinPilot Supervisor runtime."""

    def __init__(self) -> None:
        self._client = boto3.client(
            "bedrock-agentcore",
            region_name=settings.aws_region,
        )

        self._runtime_arn = settings.supervisor_runtime_arn

    async def invoke(
        self,
        prompt: str,
        session_id: str | None = None,
    ) -> str:
        runtime_session_id = session_id if session_id else str(uuid.uuid4())

        payload = json.dumps(
            {
                "prompt": prompt,
            }
        ).encode("utf-8")

        response = self._client.invoke_agent_runtime(
            agentRuntimeArn=self._runtime_arn,
            runtimeSessionId=runtime_session_id,
            qualifier="DEFAULT",
            contentType="application/json",
            accept="application/json",
            payload=payload,
        )

        if response.get("statusCode") != 200:
            raise RuntimeError(
                f"Supervisor invocation failed with "
                f"status code {response.get('statusCode')}"
            )

        response_body = response["response"].read()

        response_data = json.loads(response_body.decode("utf-8"))

        result = response_data.get("result")

        if not isinstance(result, str):
            raise RuntimeError("Supervisor returned an invalid response.")

        return result

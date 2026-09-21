from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FinPilot"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    aws_region: str = "us-east-1"

    agentcore_memory_id: str
    bedrock_prompt_router_arn: str
    supervisor_runtime_arn: str

    alpha_vantage_api_key: str

    frankfurter_base_url: str = "https://api.frankfurter.dev/v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

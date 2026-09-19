from langgraph_checkpoint_aws import AgentCoreMemorySaver

from app.config.settings import settings


def get_memory_saver() -> AgentCoreMemorySaver:
    return AgentCoreMemorySaver(
        memory_id=settings.agentcore_memory_id,
        region_name=settings.aws_region,
    )

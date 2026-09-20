from bedrock_agentcore.runtime import BedrockAgentCoreApp

from app.agents.supervisor import supervisor_agent


app = BedrockAgentCoreApp()


@app.entrypoint
async def agent_invocation(payload, context):
    user_message = payload.get("prompt", "")

    if not isinstance(user_message, str) or not user_message.strip():
        return {"error": "Invalid input: 'prompt' must be a non-empty string"}

    result = await supervisor_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": context.session_id,
                "actor_id": context.session_id,
            }
        },
    )

    return {"result": result["messages"][-1].content}


if __name__ == "__main__":
    app.run()

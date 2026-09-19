# from langchain_mcp_adapters.client import MultiServerMCPClient


# async def get_mcp_tools():
#     client = MultiServerMCPClient(
#         {
#             "finpilot": {
#                 "command": "uv",
#                 "args": [
#                     "run",
#                     "python",
#                     "-m",
#                     "app.mcp.server",
#                 ],
#                 "transport": "stdio",
#             }
#         }
#     )

#     tools = await client.get_tools()

#     return tools




from langchain_mcp_adapters.client import MultiServerMCPClient


GATEWAY_URL = (
    "https://finplot-finpilot-gateway-7l8kfvonie"
    ".gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
)


async def get_mcp_tools():
    client = MultiServerMCPClient(
        {
            "finpilot": {
                "url": GATEWAY_URL,
                "transport": "streamable_http",
            }
        }
    )

    tools = await client.get_tools()

    return tools

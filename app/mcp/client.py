from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_mcp_tools():
    client = MultiServerMCPClient(
        {
            "finpilot": {
                "command": "uv",
                "args": [
                    "run",
                    "python",
                    "-m",
                    "app.mcp.server",
                ],
                "transport": "stdio",
            }
        }
    )

    tools = await client.get_tools()

    return tools

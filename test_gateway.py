import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


GATEWAY_URL = "https://finplot-finpilot-gateway-7l8kfvonie.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"


async def main():
    async with streamablehttp_client(GATEWAY_URL) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:

            print("Initializing MCP...")
            result = await session.initialize()
            print("MCP initialized successfully!")

            print("\nListing tools...")
            tools = await session.list_tools()

            print(f"\nFound {len(tools.tools)} tools:")

            for tool in tools.tools:
                print(f"- {tool.name}")


if __name__ == "__main__":
    asyncio.run(main())
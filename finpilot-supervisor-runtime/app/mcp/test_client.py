import asyncio

from app.mcp.client import get_mcp_tools


async def main():
    tools = await get_mcp_tools()

    print("\nDiscovered MCP tools:\n")

    for tool in tools:
        print(f"- {tool.name}")
        print(f"  Description: {tool.description}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
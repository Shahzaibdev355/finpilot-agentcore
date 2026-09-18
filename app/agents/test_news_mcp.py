import asyncio

from app.agents.news_agent import create_news_agent


async def main():
    news_agent = await create_news_agent()

    result = await news_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What is the latest financial news about Apple?",
                }
            ]
        }
    )

    print("\nFinal response:")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
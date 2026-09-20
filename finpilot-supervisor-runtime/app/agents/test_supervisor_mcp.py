import asyncio

from app.agents.supervisor import supervisor_agent


async def main():
    test_questions = [
        # "What is Apple's current stock price?",
        "Convert 500 USD to GBP.",
        "What is my current portfolio value and profit?",
        # "What is the latest financial news about Apple?",
        # "Compare Apple and Microsoft based on their financial fundamentals.",
    ]

    config = {
        "configurable": {
            "thread_id": "shahzaib-test-session",
            "actor_id": "shahzaib",
        }
    }

    for question in test_questions:
        print("\n" + "=" * 70)
        print(f"USER: {question}")
        print("=" * 70)

        result = await supervisor_agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ]
            },
            config=config,
        )

        print("\nSUPERVISOR RESPONSE:")
        print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
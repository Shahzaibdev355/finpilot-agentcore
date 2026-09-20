import asyncio

from app.agents.supervisor import supervisor_agent


async def main():
    config = {
        "configurable": {
            "thread_id": "shahzaib-memory-test",
            "actor_id": "shahzaib",
        }
    }

    questions = [
        "For this conversation, assume I am interested in Apple stock. What is Apple's current stock price?",
        "What company did I say I was interested in?",
    ]

    for question in questions:
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

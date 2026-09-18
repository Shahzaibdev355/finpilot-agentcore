from app.services.bedrock.model import invoke_finpilot_model


def main() -> None:
    response = invoke_finpilot_model(
        "What is the difference between revenue and profit?"
    )

    print(response)


if __name__ == "__main__":
    main()
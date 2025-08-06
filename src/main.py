from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="gpt-oss:20b",
    temperature=0,
)


def main() -> None:
    messages = [
        (
            "system",
            "You are a helpful assistant that translates English to French. Translate the user sentence.",  # noqa: E501
        ),
        ("human", "I love programming."),
    ]
    ai_msg = llm.invoke(messages)
    print(ai_msg.content)  # type: ignore[reportUnknownReturnType]


if __name__ == "__main__":
    main()

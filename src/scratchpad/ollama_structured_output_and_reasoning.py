import asyncio
from typing import cast

from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from src.callbacks.add_source_to_messages import AddSourceToMessagesCallback


class Joke(BaseModel):
    setup: str
    punchline: str
    explanation: str


reasoning_llm = ChatOllama(
    model="gpt-oss:20b",
    temperature=0,
    reasoning=True,
    callbacks=[AddSourceToMessagesCallback(source="reasoning")],
)
structured_llm = ChatOllama(
    model="llama3.1",
    callbacks=[AddSourceToMessagesCallback(source="structured_output")],
).with_structured_output(
    schema=Joke,
    method="json_schema",
)


class InitialState(BaseModel):
    topic: str


class StateWithJoke(InitialState):
    joke: Joke


graph = StateGraph(InitialState)


def get_reasoning_prompt(topic: str) -> str:
    return f"Tell me a joke about {topic}."


def get_structured_prompt(response: str) -> str:
    return f"Parse the following response and extract the joke, punchline, and explanation: {response}"


async def generate_joke(state: InitialState) -> StateWithJoke:
    reasoning_prompt = get_reasoning_prompt(state.topic)
    reasoning_response = await reasoning_llm.ainvoke(reasoning_prompt)
    reasoning = cast("str", reasoning_response.content)

    structured_response = structured_llm.invoke(get_structured_prompt(reasoning))
    if isinstance(structured_response, Joke):
        return StateWithJoke(topic=state.topic, joke=structured_response)

    msg = f"Did not get a joke: {structured_response}"
    raise TypeError(msg)


def print_state(state: StateWithJoke) -> None:
    print("Current State:", state)


graph.add_node("generate_joke", generate_joke)
graph.add_node("print_state", print_state)

graph.add_edge(START, "generate_joke")
graph.add_edge("generate_joke", "print_state")
graph.add_edge("print_state", END)

compiled_graph = graph.compile()


async def stream() -> None:
    current_mode = None

    async for mode, chunk in compiled_graph.astream(
        input=InitialState(topic="bananas"),
        stream_mode=["values", "messages"],
    ):
        if mode == "values":
            print("Current State:", chunk)
        elif mode == "messages":
            for message in chunk:
                if isinstance(message, BaseMessage):
                    # Debug: Print the source from additional_kwargs
                    source = message.additional_kwargs.get("source", "NO_SOURCE")
                    print(f"\n[DEBUG] Message source: {source}")
                    print(f"[DEBUG] Additional kwargs: {message.additional_kwargs}")

                    reasoning_content = message.additional_kwargs.get("reasoning_content", "")
                    if reasoning_content:
                        if current_mode is None:
                            print("Thinking:")
                            current_mode = "thinking"
                        print(reasoning_content, end="")  # type: ignore
                    else:
                        if current_mode == "thinking":
                            print("\nDone thinking")
                            current_mode = None
                        print(str(message.content), end="")  # type: ignore


if __name__ == "__main__":
    asyncio.run(stream())

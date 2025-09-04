from typing import Annotated, TypeVar

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Send
from pydantic import BaseModel

K = TypeVar("K")
V = TypeVar("V")


def merge_dicts(dict1: dict[K, V], dict2: dict[K, V]) -> dict[K, V]:
    """Merge two dictionaries, with dict2 values taking precedence."""
    return {**dict1, **dict2}


class InitialState(BaseModel):
    people: list[str]


class StateWithPeopleNameLengths(InitialState):
    people_name_lengths: Annotated[dict[str, int], merge_dicts]


def node_1(state: InitialState) -> None:
    print("Here are the people:", state.people)


def dynamic_node(person: str) -> Command:  # type: ignore
    return Command(
        update={
            "people_name_lengths": {
                person: len(person),
            },
        },
    )


def node_2(state: InitialState) -> list[Send]:
    return [
        Send(
            "dynamic_node",
            p,
        )
        for p in state.people
    ]


def node_3(state: StateWithPeopleNameLengths) -> None:
    print("Here are the people name lengths:", state.people_name_lengths)


builder = StateGraph(InitialState)
builder.add_node("node_1", node_1)
builder.add_node("dynamic_node", dynamic_node)  # type: ignore
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", node_2, ["dynamic_node"])
builder.add_edge("dynamic_node", "node_3")
builder.add_edge("node_3", END)

graph = builder.compile()

graph.invoke({"people": ["Alice", "Bob", "Charlie"]})  # type: ignore

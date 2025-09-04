from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel


class InitialState(BaseModel):
    pass


class FirstNodeResponse(BaseModel):
    foo: str


class StateAfterFirstNode(InitialState, FirstNodeResponse):
    pass


def first_node(state: InitialState) -> FirstNodeResponse:
    return FirstNodeResponse(foo="bar")


class SecondNodeResponse(BaseModel):
    baz: str


class StateAfterSecondNode(StateAfterFirstNode, SecondNodeResponse):
    pass


def second_node(state: StateAfterFirstNode) -> SecondNodeResponse:
    return SecondNodeResponse(baz="qux")


def third_node(state: StateAfterSecondNode) -> None:
    print(state)


graph = StateGraph(InitialState)
graph.add_node("first_node", first_node)
graph.add_node("second_node", second_node)
graph.add_node("third_node", third_node)
graph.add_edge(START, "first_node")
graph.add_edge("first_node", "second_node")
graph.add_edge("second_node", "third_node")
graph.add_edge("third_node", END)
graph = graph.compile()

for chunk in graph.stream(input={}, stream_mode=["updates"]):  # type: ignore
    print(chunk)

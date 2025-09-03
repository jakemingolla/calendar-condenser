# https://langchain-ai.github.io/langgraph/how-tos/streaming/#stream-subgraph-outputs
from typing import TypedDict

from langgraph.graph import START, StateGraph


# Define subgraph
class SubgraphState(TypedDict):
    foo: str  # note that this key is shared with the parent graph state
    bar: str


def subgraph_node_1(state: SubgraphState):  # noqa: ANN201, ARG001
    return {"bar": "bar"}


def subgraph_node_2(state: SubgraphState):  # noqa: ANN201
    return {"foo": state["foo"] + state["bar"]}


subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile()


# Define parent graph
class ParentState(TypedDict):
    foo: str


def node_1(state: ParentState) -> dict[str, str]:
    return {"foo": "hi! " + state["foo"]}


builder = StateGraph(ParentState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", subgraph)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
graph = builder.compile()

for mode, namespace, chunk in graph.stream(
    {"foo": "foo"},
    stream_mode=["values", "updates"],
    subgraphs=True,
):
    print(mode, namespace, chunk)

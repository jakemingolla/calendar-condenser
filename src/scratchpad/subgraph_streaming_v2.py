# https://langchain-ai.github.io/langgraph/how-tos/streaming/#stream-subgraph-outputs
from operator import add
from typing import Annotated, Any, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


# Define subgraph
class SubgraphState(TypedDict):
    person: str


def subgraph_node_1(state: SubgraphState):  # noqa: ANN201
    print("Hello,", state["person"])


subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", END)
subgraph = subgraph_builder.compile()


# Define parent graph
class ParentState(TypedDict):
    foo: str
    greeted_people: Annotated[list[str], add]


def node_1(state: ParentState) -> dict[str, str]:
    return {"foo": "hi! " + state["foo"]}


def invoke_subgraph(person: str) -> dict[str, Any]:
    result = subgraph.invoke(input={"person": person})  # type: ignore
    print("result:", result)
    return {"greeted_people": [result["person"]]}


def node_2(state: ParentState) -> list[Send]:  # noqa: ARG001
    return [
        Send(
            "invoke_subgraph",
            p,
        )
        for p in ["Alice", "Bob", "Charlie"]
    ]


def node_3(state: ParentState) -> None:
    print("foo:", state["foo"])
    print("greeted_people:", state["greeted_people"])


builder = StateGraph(ParentState)
builder.add_node("node_1", node_1)
builder.add_node("invoke_subgraph", invoke_subgraph)  # type: ignore
builder.add_node("node_3", node_3)
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", node_2, ["invoke_subgraph"])
builder.add_edge("invoke_subgraph", "node_3")
graph = builder.compile(checkpointer=MemorySaver())

for mode, namespace, chunk in graph.stream(
    {"foo": "foo"},  # type: ignore
    stream_mode=["values"],
    subgraphs=True,
    config={"configurable": {"thread_id": "123"}},
):
    print(mode, namespace, chunk)

state = graph.get_state({"configurable": {"thread_id": "123"}}, subgraphs=True)
print(state.values)

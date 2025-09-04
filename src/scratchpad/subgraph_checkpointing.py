# type: ignore
# https://github.com/langchain-ai/langgraph/discussions/2759
# Code demonstrating a parent and subgraph setup with LangGraph

from collections.abc import Sequence
from typing import Any, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.types import StreamMode

# Subgraph


class SubgraphState(TypedDict):
    foo: str  # Note that this key is shared with the parent graph state
    bar: str


def subgraph_node_1(state: SubgraphState) -> SubgraphState:
    return {"bar": "bar" + state.get("bar", "")}  # After the first run, "bar" is not there anymore


def subgraph_node_2(state: SubgraphState) -> SubgraphState:
    # This node uses a state key ('bar') that is only available in the subgraph
    # and sends an update on the shared state key ('foo')
    return {"foo": state["foo"] + state["bar"]}


subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node(subgraph_node_1)
subgraph_builder.add_node(subgraph_node_2)
subgraph_builder.add_edge(START, "subgraph_node_1")
subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
subgraph = subgraph_builder.compile(checkpointer=True)


# Parent graph


class State(TypedDict):
    foo: str


def node_1(state: State) -> State:
    return {"foo": "hi! " + state["foo"]}


builder = StateGraph(State)
builder.add_node("node_1", node_1)
# Adding the compiled subgraph as a node to the parent graph
builder.add_node("node_2", subgraph)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")

checkpointer = MemorySaver()
# Pass checkpointer when compiling the parent graph
# LangGraph will automatically propagate the checkpointer to child subgraphs
graph = builder.compile(checkpointer=checkpointer)


def invoke_graph_with_subgraph(
    graph: StateGraph,
    input: dict[str, Any],
    config: RunnableConfig | None = None,
    *,
    stream_mode: StreamMode = "values",
    output_keys: str | Sequence[str] | None = None,
) -> dict[str, Any]:
    """Run the graph with a single input and config.

    Args:
        graph: The graph to run.
        input: Input data for the graph. Can be a dictionary or any other type.
        config: Optional configuration for the graph run.
        stream_mode: Optional[str]. Stream mode for the graph run. Default is "values".
        output_keys: Optional. Output keys to retrieve from the graph run.

    Returns:
        The output of the graph run. If stream_mode is "values", it returns the latest output.
        If stream_mode is not "values", it returns a list of output chunks.

    """
    output_keys = output_keys if output_keys is not None else graph.output_channels
    if stream_mode == "values":
        latest: dict[str, Any] | Any = None
    else:
        chunks = []
    for chunk in graph.stream(
        input,
        config,
        stream_mode=stream_mode,
        output_keys=output_keys,
        subgraphs=True,
    ):
        if stream_mode == "values":
            latest = chunk
        else:
            chunks.append(chunk)
    if stream_mode == "values":
        return latest
    return chunks


config = {"configurable": {"thread_id": "1"}}
result = invoke_graph_with_subgraph(graph, {"foo": "foo"}, config)
print("1", graph.get_state(config).values)
state_with_subgraph = [s for s in graph.get_state_history(config) if s.next == ("node_2",)]
subgraph_config = state_with_subgraph[0].tasks[0].state
print("2", subgraph_config)
print("3", graph.get_state(subgraph_config).values)

result = invoke_graph_with_subgraph(graph, {"foo": "UPDATED"}, config)
print("4", graph.get_state(config).values)
state_with_subgraph = [s for s in graph.get_state_history(config) if s.next == ("node_2",)]
subgraph_config = state_with_subgraph[0].tasks[0].state
print("5", subgraph_config)
print("6", graph.get_state(subgraph_config).values)

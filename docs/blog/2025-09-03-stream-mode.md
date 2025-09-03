# Stream Mode

Author: [@jakemingolla](https://github.com/jakemingolla)

Published: 2025-09-03

## Overview

In [LangGraph][langgraph] you can stream the output of a graph in different modes. This document describes an overview of the different stream modes I've used on this project as well as my current thoughts on how to best utilize them.

## Initial Mode: `values`

Initially, I used the `values` mode to stream the latest state of the graph once each node was executed. I thought this would pair nicely with my work realted to [State Transitions](./2025-08-14-state-transitions.md) to closely couple the backend logic to the frontend UI.

As I progressed through making the front-end to pair with this functionality, I noticed some problems:

1. Nodes which do not make any state changes result in duplicate messages sent to the frontend. I wasn't originally accounting for this in the UI and resulted in lots of duplicate UI elements.

2. A _lot_ of content is in each message, especially as the graph progressed. This made it difficult for my human brain to process the huge amount of content flowing in the stream.

## Side Note: `messages`

The `messages` mode is a special mode that streams the messages generated LLMs in the graph in real-time. This is useful for streaming the reasoning process of an LLM in real-time as opposed to waiting for the entire graph to finish execution. You can specify multiple stream modes at the same time and LangGraph will stream the messages for each mode:

```python

async for mode, chunk in compiled_graph.astream(
    input=InitialState(topic="bananas"),
    stream_mode=["values", "messages"],
):
    if mode == "values":
        print("Current State:", chunk)
    elif mode == "messages":
        for message in chunk:
            if isinstance(message, AIMessageChunk):
                print(message.content, end="")  # AI message chunks can come in multiple parts
```

## New Mode: `updates`

I'm going to try and use the `updates` mode to stream solely the changes to the state of the graph rather than the entire state as each node completes. This will allow me to more closely couple the backend logic to the frontend UI while reducing the amount of content in each message.

<!-- References -->
[langgraph]: https://langchain-ai.github.io/langgraph/
[stream modes]: https://langchain-ai.github.io/langgraph/how-tos/streaming/#supported-stream-modes

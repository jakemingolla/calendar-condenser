from langchain_openai import ChatOpenAI

reasoning = {
    "effort": "medium",  # 'low', 'medium', or 'high'
    "summary": "auto",  # 'detailed', 'auto', or None
}

llm = ChatOpenAI(
    model="o4-mini",
    reasoning=reasoning,
    output_version="responses/v1",
)
response = llm.invoke("What is 3^3?")

# Response text
print(f"Output: {response.text()}")

# Reasoning summaries
for block in response.content:
    if block["type"] == "reasoning":  # type: ignore
        for summary in block["summary"]:  # type: ignore
            print(summary["text"])  # type: ignore

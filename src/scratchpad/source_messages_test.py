from langchain_ollama import ChatOllama
from pydantic import BaseModel

from src.callbacks.add_source_to_messages import AddSourceToMessagesCallback


class Country(BaseModel):
    name: str
    capital: str
    languages: list[str]


structured_llm = ChatOllama(
    model="llama3.1",
    callbacks=[AddSourceToMessagesCallback(source="structured_output")],
).with_structured_output(schema=Country, method="json_schema")
unstructured_llm = ChatOllama(
    model="llama3.1",
    callbacks=[AddSourceToMessagesCallback(source="unstructured_output")],
)

response = structured_llm.invoke("Tell me about Canada.")
print(response)  # type: ignore

print("\n=== STREAMING CHUNKS ===")
for chunk in unstructured_llm.stream("Tell me about Canada. Limit your response to 100 words."):
    print(chunk)

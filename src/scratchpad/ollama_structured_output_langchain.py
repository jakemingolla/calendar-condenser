from langchain_ollama import ChatOllama
from pydantic import BaseModel


class Country(BaseModel):
    name: str
    capital: str
    languages: list[str]


structured_llm = ChatOllama(model="llama3.1").with_structured_output(schema=Country, method="json_schema")

response = structured_llm.invoke("Tell me about Canada.")
print(response)  # type: ignore

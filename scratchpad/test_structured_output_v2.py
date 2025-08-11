from langchain_ollama import ChatOllama
from pydantic import BaseModel


class Add(BaseModel):
    a: int
    b: int


llm = ChatOllama(model="llama3.1")
response = llm.with_structured_output(Add, method="json_schema").invoke("a=1, b=2")

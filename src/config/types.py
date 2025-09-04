from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    openai_api_key: SecretStr = Field(description="The API key for the OpenAI API.")
    skip_llm_messages: bool = Field(default=False, description="If True, skip LLM messages to speed up the UI.")

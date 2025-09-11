from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    openai_api_key: SecretStr = Field(description="The API key for the OpenAI API.")
    default_model: str = Field(
        default="gpt-4o-mini",
        description="The default model to use for the OpenAI API.",
    )
    rescheduling_agent_model: str = Field(
        default="gpt-5",
        description="The model to use for the rescheduling agent.",
    )

    include_llm_messages: bool = Field(
        default=False,
        description="If False, skip LLM messages in the UI to speed up graph execution.",
    )

    delay_seconds_load_calendar: float = Field(
        default=0,
        description="The number of seconds to delay the loading of the calendar. Simulates network latency.",
    )
    delay_seconds_load_invitees: float = Field(
        default=0,
        description="The number of seconds to delay the loading of the invitees. Simulates network latency.",
    )
    delay_seconds_load_user: float = Field(
        default=0,
        description="The number of seconds to delay the loading of the user. Simulates network latency.",
    )
    delay_seconds_get_rescheduling_proposals: float = Field(
        default=0,
        description="The number of seconds to delay the getting of the rescheduling proposals. Simulates network latency.",
    )
    delay_seconds_update_calendar: float = Field(
        default=0,
        description="The number of seconds to delay the updating of the calendar. Simulates network latency.",
    )

    delay_seconds_send_rescheduling_proposal_to_invitee_send_message: float = Field(
        default=0,
        description="The number of seconds to delay the sending of the message. Simulates network latency.",
    )
    delay_seconds_send_rescheduling_proposal_to_invitee_receive_message: float = Field(
        default=0,
        description="The number of seconds to delay the receiving of the message. Simulates network latency.",
    )

    mock_messaging_platform_positive_response_probability: float = Field(
        default=0.5,
        ge=0,  # Greater than or equal to 0
        le=1,  # Less than or equal to 1
        description="The probability of the mock messaging platform returning a positive response.",
    )
    mock_messaging_platform_unlock_time_min_seconds: int = Field(
        default=2,
        ge=0,  # Greater than or equal to 0
        description="The minimum number of seconds to delay the unlocking of the message. Simulates network latency.",
    )
    mock_messaging_platform_unlock_time_max_seconds: int = Field(
        default=5,
        ge=0,  # Greater than or equal to 0
        description="The maximum number of seconds to delay the unlocking of the message. Simulates network latency.",
    )

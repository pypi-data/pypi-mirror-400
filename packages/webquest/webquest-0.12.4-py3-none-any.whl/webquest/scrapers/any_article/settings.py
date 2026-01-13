from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnyArticleSettings(BaseSettings):
    """
    Configuration settings for the Any Article scraper.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    character_limit: int = Field(
        5000, description="The maximum number of characters to parse."
    )
    parser_model: str = Field(
        "gpt-5-mini", description="The OpenAI model to use for parsing."
    )
    openai_api_key: SecretStr | None = Field(
        None, description="The API key for OpenAI."
    )

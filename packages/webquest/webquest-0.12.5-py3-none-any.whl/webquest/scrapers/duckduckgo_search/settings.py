from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DuckDuckGoSearchSettings(BaseSettings):
    """
    Configuration settings for the DuckDuckGo search scraper.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    result_limit: int = Field(
        10, description="The maximum number of results to return."
    )
    character_limit: int = Field(
        1000, description="The maximum number of characters to parse."
    )

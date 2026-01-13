from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class YouTubeTranscriptSettings(BaseSettings):
    """
    Configuration settings for the YouTube transcript scraper.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    character_limit: int = Field(
        5000, description="The maximum number of characters to parse."
    )

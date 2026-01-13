from pydantic import BaseModel, Field


class YouTubeSearchRequest(BaseModel):
    """
    Represents a request to search YouTube.
    """

    query: str = Field(..., description="The search query.")

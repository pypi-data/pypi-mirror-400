from pydantic import BaseModel, Field


class GoogleNewsSearchRequest(BaseModel):
    """
    Represents a request to search Google News.
    """

    query: str = Field(..., description="The search query.")

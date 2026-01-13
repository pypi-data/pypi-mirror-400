from pydantic import BaseModel, Field


class DuckDuckGoSearchRequest(BaseModel):
    """
    Represents a request to search DuckDuckGo.
    """

    query: str = Field(..., description="The search query.")

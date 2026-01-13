from pydantic import BaseModel, Field


class Page(BaseModel):
    """
    Represents a web page found in DuckDuckGo search results.
    """

    site: str = Field(..., description="The name of the website.")
    url: str = Field(..., description="The URL of the page.")
    title: str = Field(..., description="The title of the page.")
    description: str = Field(..., description="The description of the page.")


class DuckDuckGoSearchResponse(BaseModel):
    """
    Represents the response from a DuckDuckGo search.
    """

    pages: list[Page] = Field(..., description="The list of pages found.")

from pydantic import BaseModel, Field


class Article(BaseModel):
    """
    Represents a news article found in Google News.
    """

    site: str = Field(..., description="The name of the news site.")
    url: str = Field(..., description="The URL of the article.")
    title: str = Field(..., description="The title of the article.")
    published_at: str = Field(..., description="The publication date of the article.")


class GoogleNewsSearchResponse(BaseModel):
    """
    Represents the response from a Google News search.
    """

    articles: list[Article] = Field(..., description="The list of articles found.")

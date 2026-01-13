from pydantic import BaseModel, Field


class AnyArticleRequest(BaseModel):
    """
    Represents a request to extract an article from a web page.
    """

    url: str = Field(
        ..., description="The URL of the web page to extract the article from."
    )

from pydantic import BaseModel, Field


class AnyArticleResponse(BaseModel):
    """
    Represents the extracted article content.
    """

    publisher: str = Field(..., description="The name of the publisher.")
    title: str = Field(..., description="The title of the article.")
    published_at: str = Field(..., description="The publication date of the article.")
    authors: list[str] = Field(..., description="The list of authors of the article.")
    content: str = Field(..., description="The main content of the article.")

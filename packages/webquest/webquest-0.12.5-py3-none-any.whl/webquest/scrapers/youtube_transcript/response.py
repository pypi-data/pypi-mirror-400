from pydantic import BaseModel, Field


class YouTubeTranscriptResponse(BaseModel):
    """
    Represents the extracted transcript of a YouTube video.
    """

    transcript: str = Field(..., description="The transcript of the video.")

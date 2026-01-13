from pydantic import BaseModel, Field


class YouTubeTranscriptRequest(BaseModel):
    """
    Represents a request to extract the transcript of a YouTube video.
    """

    video_id: str = Field(..., description="The ID of the YouTube video.")

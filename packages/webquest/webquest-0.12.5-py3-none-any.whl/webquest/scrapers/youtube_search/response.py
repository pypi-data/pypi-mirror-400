from pydantic import BaseModel, Field


class Video(BaseModel):
    """
    Represents a YouTube video.
    """

    id: str = Field(..., description="The video ID.")
    url: str = Field(..., description="The URL of the video.")
    title: str = Field(..., description="The title of the video.")
    description: str = Field(..., description="The description of the video.")
    published_at: str = Field(..., description="The publication date of the video.")
    views: str = Field(..., description="The number of views.")
    channel_id: str = Field(..., description="The channel ID.")
    channel_url: str = Field(..., description="The URL of the channel.")
    channel_name: str = Field(..., description="The name of the channel.")


class Channel(BaseModel):
    """
    Represents a YouTube channel.
    """

    id: str = Field(..., description="The channel ID.")
    url: str = Field(..., description="The URL of the channel.")
    name: str = Field(..., description="The name of the channel.")
    description: str | None = Field(None, description="The description of the channel.")
    subscribers: str = Field(..., description="The number of subscribers.")


class Post(BaseModel):
    """
    Represents a YouTube community post.
    """

    id: str = Field(..., description="The post ID.")
    url: str = Field(..., description="The URL of the post.")
    content: str = Field(..., description="The content of the post.")
    published_at: str = Field(..., description="The publication date of the post.")
    channel_id: str = Field(..., description="The channel ID.")
    channel_url: str = Field(..., description="The URL of the channel.")
    channel_name: str = Field(..., description="The name of the channel.")
    comments: str = Field(..., description="The number of comments.")
    likes: str = Field(..., description="The number of likes.")


class Short(BaseModel):
    """
    Represents a YouTube Short.
    """

    id: str = Field(..., description="The short ID.")
    url: str = Field(..., description="The URL of the short.")
    title: str = Field(..., description="The title of the short.")
    views: str = Field(..., description="The number of views.")


class YouTubeSearchResponse(BaseModel):
    """
    Represents the response from a YouTube search.
    """

    videos: list[Video] = Field(..., description="The list of videos found.")
    channels: list[Channel] = Field(..., description="The list of channels found.")
    posts: list[Post] = Field(..., description="The list of posts found.")
    shorts: list[Short] = Field(..., description="The list of shorts found.")

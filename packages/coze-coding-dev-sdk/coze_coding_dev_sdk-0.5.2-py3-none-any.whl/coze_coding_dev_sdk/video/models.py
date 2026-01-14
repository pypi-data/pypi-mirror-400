from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class VideoConfig(BaseModel):
    resolution: Optional[Literal["480p", "720p"]] = "720p"
    ratio: Optional[
        Literal["16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "adaptive"]
    ] = "16:9"
    duration: Optional[int] = Field(default=5, ge=-1, le=12)
    watermark: Optional[bool] = True
    seed: Optional[int] = None
    camerafixed: Optional[bool] = False
    generate_audio: Optional[bool] = True


class ImageURL(BaseModel):
    url: str


class ImageURLContent(BaseModel):
    type: Literal["image_url"] = "image_url"
    image_url: ImageURL
    role: Optional[Literal["first_frame", "last_frame", "reference_image"]] = None


class TextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


class VideoGenerationRequest(BaseModel):
    model: str
    content: List[Union[TextContent, ImageURLContent]]
    config: Optional[VideoConfig] = None


class VideoGenerationTask(BaseModel):
    id: str
    status: Literal["processing", "completed", "failed"]
    video_url: Optional[str] = None
    error_message: Optional[str] = None

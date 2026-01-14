"""
Data models for infinity_ml client.

Mirrors fal_client's Status types and result models.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, Union


# ─────────────────────────────────────────────────────────────────────────────
# Status Classes (fal_client style)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Status:
    """Base status class."""

    pass


@dataclass
class Queued(Status):
    """
    Indicates the request is enqueued and waiting to be processed.
    The position field indicates the relative position in the queue (0-indexed).
    """

    position: int = 0


@dataclass
class InProgress(Status):
    """
    Indicates the request is currently being processed.
    If logs were requested, they'll be included here.
    """

    logs: Optional[List[Dict[str, Any]]] = None


@dataclass
class Completed(Status):
    """
    Indicates the request has been completed.
    The logs and metrics fields may contain additional information.
    """

    logs: Optional[List[Dict[str, Any]]] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Failed(Status):
    """Indicates the request has failed."""

    error: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# File Info Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class FileInfo:
    """Information about a generated file."""

    url: str
    download_url: str
    content_type: str

    def __repr__(self):
        return f"FileInfo(download_url='{self.download_url}')"


@dataclass
class ImageInfo(FileInfo):
    """Image file with dimensions."""

    width: int = 0
    height: int = 0


@dataclass
class VideoInfo(FileInfo):
    """Video file with dimensions and duration."""

    width: int = 0
    height: int = 0
    duration: float = 0.0


@dataclass
class AudioInfo(FileInfo):
    """Audio file with duration."""

    duration: float = 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Result Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ImageResult:
    """Result of image generation."""

    images: List[ImageInfo]
    seed: int
    prompt: str
    request_id: str


@dataclass
class VideoResult:
    """Result of video generation."""

    video: VideoInfo
    seed: int
    prompt: str
    request_id: str


@dataclass
class AudioResult:
    """Result of audio generation."""

    audio: AudioInfo
    request_id: str


# Union type for all results
GenerationResult = Union[ImageResult, VideoResult, AudioResult]

# Type alias for JSON-like dicts (mirrors fal_client.AnyJSON)
AnyJSON = Dict[str, Any]


def parse_status(data: Dict[str, Any]) -> Status:
    """Parse API status response into typed Status object."""
    status_str = data.get("status", "")

    if status_str == "IN_QUEUE":
        return Queued(position=data.get("queue_position", 0))
    elif status_str == "IN_PROGRESS":
        return InProgress(logs=data.get("logs"))
    elif status_str == "COMPLETED":
        return Completed(logs=data.get("logs"), metrics=data.get("metrics", {}))
    elif status_str == "FAILED":
        return Failed(error=data.get("error", "Unknown error"))
    else:
        return Status()


def parse_result(data: Dict[str, Any], request_id: str) -> GenerationResult:
    """Parse API response into typed result."""
    if "images" in data:
        images = [
            ImageInfo(
                url=img["url"],
                download_url=img.get("download_url", img["url"]),
                content_type=img.get("content_type", "image/png"),
                width=img.get("width", 0),
                height=img.get("height", 0),
            )
            for img in data["images"]
        ]
        return ImageResult(
            images=images,
            seed=data.get("seed", 0),
            prompt=data.get("prompt", ""),
            request_id=request_id,
        )

    elif "video" in data:
        v = data["video"]
        video = VideoInfo(
            url=v["url"],
            download_url=v.get("download_url", v["url"]),
            content_type=v.get("content_type", "video/mp4"),
            width=v.get("width", 0),
            height=v.get("height", 0),
            duration=v.get("duration", 0.0),
        )
        return VideoResult(
            video=video,
            seed=data.get("seed", 0),
            prompt=data.get("prompt", ""),
            request_id=request_id,
        )

    elif "audio" in data:
        a = data["audio"]
        audio = AudioInfo(
            url=a["url"],
            download_url=a.get("download_url", a["url"]),
            content_type=a.get("content_type", "audio/wav"),
            duration=a.get("duration", 0.0),
        )
        return AudioResult(
            audio=audio,
            request_id=request_id,
        )

    else:
        raise ValueError(f"Unknown result type: {data}")

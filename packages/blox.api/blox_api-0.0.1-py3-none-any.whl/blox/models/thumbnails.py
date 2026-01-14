from enum import IntEnum
from typing import TYPE_CHECKING, Literal, Optional, Tuple
from blox.utility import DisplayNameEnum

if TYPE_CHECKING:
    from blox.api_types.web_types import v1_Thumbnail
    from blox.web import WebHandler


class ThumbnailType(IntEnum):
    """
    Represents a Roblox thumbnail target type.
    """

    GroupIcon = 0
    AvatarFull = 1
    AvatarBust = 2
    AvatarHeadshot = 3


class ThumbnailState(DisplayNameEnum):
    """
    Represents a Roblox asset thumbnail generation state.
    """

    Errored = (0, "Error")
    Ready = (1, "Completed")
    InReview = (2, "InReview")
    Pending = (3, "Pending")
    Blocked = (4, "Blocked")
    Unavailable = (5, "TemporarilyUnavailable")


class Thumbnail:
    """
    Represents a Roblox asset thumbnail.

    Parameters
    ----------
    handler
        The global/shared Blox handler.
    data
        The API response containing thumbnail data.
    """

    id: int
    size: Tuple[int, int]
    type: ThumbnailType
    circular: bool
    format: Literal["PNG", "WebP", "JPEG"]
    state: ThumbnailState
    url: Optional[str]
    version: str

    def __init__(
        self,
        handler: "WebHandler",
        data: "v1_Thumbnail",
        type: ThumbnailType,
        size: Tuple[int, int],
        circular: bool,
        format: Literal["PNG", "WebP", "JPEG"],
    ):
        self._handler = handler

        self.id = int(data["targetId"])
        self.state = ThumbnailState.parse(data["state"])
        self.version = data["version"]

        self.type = type
        self.size = size
        self.circular = circular
        self.format = format

        if image_url := data.get("imageUrl"):
            self.url = image_url

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} type={self.type.name}, id={self.id}, state={self.state}, url={self.url}>"

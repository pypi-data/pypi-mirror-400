"""

thumbnails.roblox.com

"""

from typing import TYPE_CHECKING, Literal, TypedDict
from ._shared import WebDataList


class v1_Thumbnail(TypedDict):
    targetId: int
    state: Literal[
        "Error", "Completed", "InReview", "Pending", "Blocked", "TemporarilyUnavailable"
    ]
    imageUrl: str
    version: str


# GET https://thumbnails.roblox.com/v1/groups/icons
# GET https://thumbnails.roblox.com/v1/users/avatar
# GET https://thumbnails.roblox.com/v1/users/avatar-bust
# GET https://thumbnails.roblox.com/v1/users/avatar-headshot
v1_ThumbnailResponse = dict
if TYPE_CHECKING:
    v1_ThumbnailResponse = WebDataList[v1_Thumbnail]

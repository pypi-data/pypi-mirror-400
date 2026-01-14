"""

users.roblox.com

"""

from ._shared import SearchPagination, WebDataList, WebCursorPagination
from typing import TYPE_CHECKING, Optional, TypedDict, List


class v1_MinimalUser(TypedDict):
    id: int
    name: str
    displayName: str


class v1_User(v1_MinimalUser):
    hasVerifiedBadge: bool


# GET https://users.roblox.com/v1/users/{userId}
class v1_DetailedUserResponse(v1_User):
    description: str
    created: str
    isBanned: bool
    externalAppDisplayName: None


# GET https://users.roblox.com/v1/users/{userId}/username-history
class v1_UserNameHistory(TypedDict):
    name: str


v1_UserNameHistoryResponse = dict
if TYPE_CHECKING:
    v1_UserNameHistoryResponse = WebCursorPagination[v1_UserNameHistory]


# POST https://users.roblox.com/v1/usernames/users
class v1_RequestedUserByName(v1_User):
    requestedUsername: str


v1_UsersByNameResponse = dict
if TYPE_CHECKING:
    v1_UsersByNameResponse = WebDataList[v1_RequestedUserByName]

# POST https://users.roblox.com/v1/users
v1_UsersByIdResponse = dict
if TYPE_CHECKING:
    v1_UsersByIdResponse = WebDataList[v1_User]


# GET https://users.roblox.com/v1/users/search
class v1_UserSearchResult(v1_User):
    previousUsernames: List[str]


v1_UserSearchResponse = dict
if TYPE_CHECKING:
    v1_UserSearchResponse = WebCursorPagination[v1_UserSearchResult]


# GET https://users.roblox.com/v1/users/authenticated
v1_AuthenticatedUserResponse = v1_MinimalUser


# GET https://apis.roblox.com/search-api/omni-search
class UserOmniSearchItem(TypedDict):
    username: str
    displayName: str
    previousUsernames: Optional[List[str]]
    hasVerifiedBadge: bool
    contentId: int


UserOmniSearchResponse = dict
if TYPE_CHECKING:
    UserOmniSearchResponse = SearchPagination[UserOmniSearchItem]

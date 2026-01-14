"""

groups.roblox.com

"""

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, TypedDict
from ._shared import WebDataList, WebCursorPagination


class v1_Group(TypedDict):
    id: int
    name: str


class v1_GroupUser(TypedDict):
    userId: int
    username: str
    displayName: str
    hasVerifiedBadge: bool


class v1_GroupRole(TypedDict):
    id: int
    name: str
    rank: int
    description: Optional[str]
    memberCount: Optional[int]


class v1_GroupMember(TypedDict):
    user: v1_GroupUser
    role: v1_GroupRole


class v1_GroupShout(TypedDict):
    body: str
    poster: v1_GroupUser
    created: str
    updated: str


# GET https://groups.roblox.com/v1/groups/{groupId}
class v1_GroupDetailResponse(v1_Group):
    description: str
    owner: v1_GroupUser
    shout: Optional[v1_GroupShout]
    memberCount: int
    isBuildersClubOnly: bool
    publicEntryAllowed: bool
    hasVerifiedBadge: bool
    hasSocialModules: bool
    isLocked: Optional[bool]


# GET https://groups.roblox.com/v1/groups/{groupId}/audit-log
class v1_GroupAuditLogItem(TypedDict):
    actor: v1_GroupMember
    actionType: str
    description: Dict[str, Any]
    created: str


v1_GroupAuditLogResponse = dict
if TYPE_CHECKING:
    v1_GroupAuditLogResponse = WebCursorPagination[v1_GroupAuditLogItem]


class v1_UserGroupMembership(TypedDict):
    group: v1_GroupDetailResponse
    role: v1_GroupRole
    isPrimaryGroup: Optional[Literal[True]]


# GET https://groups.roblox.com/v1/users/{userId}/groups/roles
v1_UserGroupRolesResponse = dict
if TYPE_CHECKING:
    v1_UserGroupRolesResponse = WebDataList[v1_UserGroupMembership]


# GET https://groups.roblox.com/v1/groups/{groupId}/users
v1_GroupMembersResponse = dict
if TYPE_CHECKING:
    v1_GroupMembersResponse = WebCursorPagination[v1_GroupMember]


# GET https://groups.roblox.com/v1/groups/{groupId}/join-requests/users/{userId}
class v1_GroupUserJoinRequest(TypedDict):
    requester: v1_GroupUser
    created: str


# GET https://groups.roblox.com/v1/groups/{groupId}/name-history
class v1_GroupNameHistory(TypedDict):
    name: str
    created: str


v1_GroupNameHistoryResponse = dict
if TYPE_CHECKING:
    v1_GroupNameHistoryResponse = WebCursorPagination[v1_GroupNameHistory]


# GET https://groups.roblox.com/v1/groups/{groupId}/roles
class v1_GroupRolesResponse(TypedDict):
    groupId: int
    roles: List[v1_GroupRole]


# GET https://groups.roblox.com/v1/groups/{groupId}/roles/{roleSetId}/users
v1_GroupRoleMembersResponse = dict
if TYPE_CHECKING:
    v1_GroupRoleMembersResponse = WebDataList[v1_GroupUser]

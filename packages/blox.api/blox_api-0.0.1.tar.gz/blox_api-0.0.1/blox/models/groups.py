from typing import TYPE_CHECKING, Literal, Optional, Tuple, Union
from blox.api_types.web_types.groups import v1_GroupMember
from blox.utility import SortOrder, PageIterator
from .users import MinimalUser, User
from .thumbnails import Thumbnail
from blox.exceptions import *
from datetime import datetime
import dateutil
import httpx


if TYPE_CHECKING:
    from blox.api_types.web_types import (
        v1_GroupDetailResponse,
        v1_GroupRole,
        v1_GroupShout,
        v1_GroupMember,
        v1_GroupUser,
        v1_UserGroupMembership,
    )
    from blox.web import WebHandler


class MinimalGroup:
    """
    Represents a minimal Roblox group.

    Parameters
    ----------
    handler
        The global/shared Blox handler.
    id
        The Roblox group ID.
    """

    id: int

    def __init__(self, handler: "WebHandler", id: int):
        self._handler = handler

        self.id = int(id)

    async def get_roles(self):
        """
        Get the group's roles.
        """

        return await self._handler.groups.get_roles(self.id)

    async def get_icon(
        self,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP"] = "PNG",
        size: Union[
            Tuple[Literal[150], Literal[150]],
            Tuple[Literal[420], Literal[420]],
        ] = (150, 150),
        retry_pending: bool = True,
    ) -> Optional[Thumbnail]:
        """
        Get the group's icon thumbnail.

        Parameters
        ----------
        circular
            Whether the generated thumbnail should be circular.
        format
            The thumbnail image media type.
        size
            The thumbnail image dimensions.
        retry_pending
            Whether to retry requests in case of pending thumbnail state.
        """

        return await self._handler.groups.get_icon(
            self.id,
            circular=circular,
            format=format,
            size=size,
            retry_pending=retry_pending,
        )

    def name_history(
        self,
        *,
        names_per_page: Literal[10, 25, 50, 100] = 10,
        sort_order: SortOrder = SortOrder.Ascending,
        limit: Optional[int] = None,
    ):
        """
        Iterate over the group's name history.

        Parameters
        ----------
        names_per_page
            The maximum number of names to fetch per page.
        sort_order
            The order names are sorted in (according to date of name change).
        limit
            The maximum number of names to iterate.
        """

        return self._handler.groups.name_history(
            self.id, names_per_page=names_per_page, sort_order=sort_order, limit=limit
        )

    def members(
        self,
        *,
        members_per_page: Literal[10, 25, 50, 100] = 50,
        sort_order: SortOrder = SortOrder.Ascending,
        limit: Optional[int] = None,
    ):
        """
        Iterate over the groups's members.

        Parameters
        ----------
        members_per_page
            The maximum number of members to fetch per page.
        sort_order
            The order members are sorted in (according to join date).
        limit
            The maximum number of members to iterate.
        """

        return self._handler.groups.members(
            self.id,
            members_per_page=members_per_page,
            sort_order=sort_order,
            limit=limit,
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MinimalGroup) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class Group(MinimalGroup):
    """
    Represents a Roblox group.

    Parameters
    ----------
    handler
        The global/shared Blox handler.
    data
        The API response containing group data.
    """

    name: str
    description: Optional[str] = None
    member_count: Optional[int] = None
    shout: Optional["GroupShout"] = None
    owner: Optional[User] = None
    verified: bool
    public: bool
    moderated: bool = False

    def __init__(
        self,
        handler: "WebHandler",
        data: "v1_GroupDetailResponse",
    ):
        self._handler = handler

        self.name = data["name"]
        self.verified = data["hasVerifiedBadge"]
        self.public = data["publicEntryAllowed"]

        if owner := data.get("owner"):
            self.owner = User(
                handler,
                {
                    "id": owner["userId"],
                    "name": owner["username"],
                    "displayName": owner["displayName"],
                    "hasVerifiedBadge": owner["hasVerifiedBadge"],
                },
            )

        if description := data.get("description"):
            self.description = description

        if member_count := data.get("memberCount"):
            self.member_count = int(member_count)

        if shout := data.get("shout"):
            self.shout = GroupShout(handler, shout)

        if data.get("isLocked"):
            self.moderated = True

        super().__init__(handler, data["id"])

        handler._global_cache.groups.set(self.id, self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, id={self.id}, member_count={self.member_count}>"


class GroupShout:
    """
    Represents a Roblox group shout.

    Parameters
    ----------
    handler
        The global/shared Blox handler.
    data
        The API response containing shout data.
    """

    content: Optional[str]
    poster: Union[User, MinimalUser]
    created_at: datetime
    updated_at: datetime

    def __init__(self, handler: "WebHandler", data: "v1_GroupShout"):
        self._handler = handler

        self.poster = User(handler, data["poster"])
        self.created_at = dateutil.parser.parse(data["created"])
        self.updated_at = dateutil.parser.parse(data["updated"])

        if content := data.get("body"):
            self.content = content

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} poster={self.poster}, created_at={self.created_at}, updated_at={self.updated_at}>"


class Role:
    """
    Represents a Roblox group role.

    Parameters
    ----------
    handler
        The global/shared Blox handler.
    data
        The API response containing role data.
    group_id
        The Roblox group ID the role is associated with.
    group
        The Roblox group the role is associated with.
    """

    id: int
    name: str
    rank: int
    description: Optional[str] = None
    member_count: Optional[int] = None

    def __init__(
        self,
        handler: "WebHandler",
        data: "v1_GroupRole",
        group_id: int,
        group: Optional[Group] = None,
    ):
        self._handler = handler
        self._group_id = group_id
        self.group = group

        self.id = int(data["id"])
        self.name = data["name"]
        self.rank = int(data["rank"])

        if description := data.get("description"):
            self.description = description

        if member_count := data.get("memberCount"):
            self.member_count = int(member_count)

        if self.is_guest():
            self.member_count = 0

    def is_owner(self) -> bool:
        """
        Whether the role is the group owner-only role.
        """

        return self.rank == 255

    def is_guest(self) -> bool:
        """
        Whether the role is the group guest role (for non-members).
        """

        return self.rank == 0

    def members(
        self,
        *,
        members_per_page: Literal[10, 25, 50, 100] = 50,
        sort_order: SortOrder = SortOrder.Ascending,
        limit: Optional[int] = None,
    ) -> PageIterator["Member"]:
        """
        Iterate over the role's members.

        Parameters
        ----------
        members_per_page
            The maximum number of members to fetch per page.
        sort_order
            The order members are sorted in (according to join date).
        limit
            The maximum number of members to iterate.
        """

        def page_handler(
            handler: "WebHandler",
            response: httpx.Response,
            data: "v1_GroupUser",
        ):
            return Member(handler, (data, self), self._group_id, self.group)

        return PageIterator(
            self._handler,
            "groups",
            f"/v1/groups/{self._group_id}/roles/{self.id}/users",
            sort_order,
            page_size=members_per_page,
            max_items=limit,
            page_handler=page_handler,
            exceptions={1: GroupNotFound, 2: RoleNotFound, 35: InsufficientPermissions},
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MinimalGroup) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __gt__(self, other: "Role") -> bool:
        return isinstance(other, Role) and self.rank > other.rank

    def __ge__(self, other: "Role") -> bool:
        return self.__gt__(other) or self.__eq__(other)

    def __lt__(self, other: "Role") -> bool:
        return not self.__gt__(other)

    def __le__(self, other: "Role") -> bool:
        return self.__lt__(other) or self.__eq__(other)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, id={self.id}, rank={self.rank}, group={self.group or self._group_id}>"


class Membership(MinimalUser):
    """
    Represents a Roblox group membership. A membership indicates a user's role and primary status in a group.

    Parameters
    ----------
    handler
        The global/shared Blox handler.
    user_id
        The Roblox user ID the membership is associated with.
    user
        The Roblox user the membership is associated with.
    data
        The API response containing membership data.
    """

    role: Role
    group: Group
    primary: bool = False

    def __init__(
        self,
        handler: "WebHandler",
        data: "v1_UserGroupMembership",
        user_id: int,
        user: Optional[User] = None,
    ):
        self._handler = handler
        self.user = user

        self.group = Group(handler, data=data["group"])
        self.role = Role(
            handler, data=data["role"], group_id=self.group.id, group=self.group
        )

        if data.get("isPrimaryGroup") == True:
            self.primary = True

        super().__init__(handler, user_id)

    def is_owner(self) -> bool:
        """
        Whether this member is the group owner.
        """

        return self.role.is_owner()

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} user={self.user or self.id}, role={self.role}>"
        )


class Member(User):
    """
    Represents a Roblox group member. A member is a Roblox user assigned a role in a group.

    Parameters
    ----------
    handler
        The global/shared Blox handler.
    group_id
        The Roblox group ID the member is associated with.
    group
        The Roblox group the member is associated with.
    data
        The API response containing member data.
    """

    role: Role

    def __init__(
        self,
        handler: "WebHandler",
        data: Union["v1_GroupMember", Tuple["v1_GroupUser", Role]],
        group_id: int,
        group: Optional[Group] = None,
    ):
        self._handler = handler
        self._group_id = group_id
        self.group = group

        user = None
        if isinstance(data, tuple):
            user = data[0]
            self.role = data[1]
        else:
            user = data["user"]
            self.role = Role(handler, data["role"], group_id, group)

        super().__init__(handler, user)

    def is_owner(self) -> bool:
        """
        Whether this member is the group owner.
        """

        return self.role.is_owner()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, id={self.id}, role={self.role}>"

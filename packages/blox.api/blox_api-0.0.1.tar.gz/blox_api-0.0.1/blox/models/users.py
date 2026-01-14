from typing import TYPE_CHECKING, List, Literal, Optional, Union
from blox.utility import SortOrder
from datetime import datetime
import dateutil


if TYPE_CHECKING:
    from blox.api_types.web_types import (
        v1_User,
        v1_MinimalUser,
        v1_DetailedUserResponse,
        v1_UserSearchResult,
        UserOmniSearchItem,
        v1_GroupUser,
    )
    from blox.web import (
        WebHandler,
        _AvatarFullSize,
        _AvatarBustSize,
        _AvatarHeadshotSize,
    )


class MinimalUser:
    """
    Represents a minimal Roblox user.

    Parameters
    ----------
    handler
        The global/shared Blox handler.
    id
        The Roblox user ID.
    """

    id: int

    def __init__(self, handler: "WebHandler", id: int):
        self._handler = handler

        self.id = int(id)
        self.avatar = UserAvatar(self)

    @property
    def profile_link(self) -> str:
        """
        The user's Roblox profile link/URL.
        """

        return f"https://www.roblox.com/users/{self.id}/profile"

    async def get_profile(self):
        """
        Get the user's detailed profile.
        """

        return await self._handler.users.get_profile(self.id)

    async def get_memberships(self):
        """
        Get the user's membership for each group they are in.
        """

        return await self._handler.groups.get_memberships(self.id)

    async def get_membership(self, id: int):
        """
        Get the user's membership in a group using the group ID.

        Parameters
        ----------
        id
            The Roblox group ID.
        """

        return await self._handler.groups.get_membership(self.id, group_id=id)

    async def get_primary(self):
        """
        Get the user's primary group membership.
        """

        return await self._handler.groups.get_primary(self.id)

    def name_history(
        self,
        *,
        names_per_page: Literal[10, 25, 50, 100] = 10,
        sort_order: SortOrder = SortOrder.Ascending,
        limit: Optional[int] = None,
    ):
        """
        Iterate over the user's name history.

        Parameters
        ----------
        names_per_page
            The maximum number of names to fetch per page.
        sort_order
            The order names are sorted in (according to date of name change).
        limit
            The maximum number of names to fetch.
        """

        return self._handler.users.name_history(
            self.id, names_per_page=names_per_page, sort_order=sort_order, limit=limit
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MinimalUser) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class User(MinimalUser):
    """
    Represents a Roblox user.

    Parameters
    ----------
    handler
        The global/shared Blox handler.
    data
        The API response containing user data.
    """

    name: str
    display_name: str
    verified: Optional[bool] = None
    previous_names: List[str] = []

    def __init__(
        self,
        handler: "WebHandler",
        data: Union[
            "v1_User",
            "v1_MinimalUser",
            "v1_UserSearchResult",
            "UserOmniSearchItem",
            "v1_GroupUser",
        ],
    ):
        self._handler = handler

        self.name = data.get("name", data.get("username"))
        self.display_name = data["displayName"]

        if is_verified := data.get("hasVerifiedBadge"):
            self.verified = bool(is_verified)

        if previous_names := data.get("previousUsernames"):
            self.previous_names = previous_names

        super().__init__(
            handler, data.get("id", data.get("contentId", data.get("userId")))
        )

        handler._global_cache.users.set(self.id, self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, id={self.id}, display_name={self.display_name}>"


class Profile(User):
    """
    Represents a Roblox user profile.

    Parameters
    ----------
    handler
        The global/shared Blox handler.
    data
        The API response containing user data.
    """

    description: Optional[str] = None
    banned: bool
    created_at: datetime

    def __init__(self, handler: "WebHandler", data: "v1_DetailedUserResponse"):
        self._handler = handler

        self.banned = data["isBanned"]
        self.created_at = dateutil.parser.parse(data["created"])

        if description := data.get("description"):
            self.description = description

        super().__init__(handler, data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, id={self.id}, display_name={self.display_name}, created_at={self.created_at}>"


class UserAvatar:
    def __init__(self, user: MinimalUser):
        self.handler = user._handler
        self.user = user

    async def get_full(
        self,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP", "JPEG"] = "PNG",
        size: "_AvatarFullSize" = (150, 150),
        retry_pending: bool = True,
    ):
        """
        Get the user's full avatar thumbnail.

        Parameters
        ----------
        circular
            Whether the generated thumbnail should be circular.
        format
            The thumbnail image media type.
        size
            The thumbnail image dimensions.

            | Supported |
            |-|
            |`(30, 30)`|
            |`(48, 48)`|
            |`(60, 60)`|
            |`(75, 75)`|
            |`(100, 100)`|
            |`(110, 110)`|
            |`(140, 140)`|
            |`(150, 150)`|
            |`(150, 200)`|
            |`(180, 180)`|
            |`(250, 250)`|
            |`(352, 352)`|
            |`(420, 420)`|
            |`(720, 720)`|
        retry_pending
            Whether to retry requests in case of pending thumbnail state.
        """

        return await self.handler.avatars.get_full(
            self.user.id,
            circular=circular,
            format=format,
            size=size,
            retry_pending=retry_pending,
        )

    async def get_bust(
        self,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP"] = "PNG",
        size: "_AvatarBustSize" = (150, 150),
        retry_pending: bool = True,
    ):
        """
        Get the user's avatar bust thumbnail.

        Parameters
        ----------
        circular
            Whether the generated thumbnail should be circular.
        format
            The thumbnail image media type.
        size
            The thumbnail image dimensions.

            | Supported |
            |-|
            |`(48, 48)`|
            |`(50, 50)`|
            |`(60, 60)`|
            |`(75, 75)`|
            |`(100, 100)`|
            |`(150, 150)`|
            |`(180, 180)`|
            |`(352, 352)`|
            |`(420, 420)`|
        retry_pending
            Whether to retry requests in case of pending thumbnail state.
        """

        return await self.handler.avatars.get_bust(
            self.user.id,
            circular=circular,
            format=format,
            size=size,
            retry_pending=retry_pending,
        )

    async def get_headshot(
        self,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP", "JPEG"] = "PNG",
        size: "_AvatarHeadshotSize" = (150, 150),
        retry_pending: bool = True,
    ):
        """
        Get the user's avatar headshot thumbnail.

        Parameters
        ----------
        circular
            Whether the generated thumbnail should be circular.
        format
            The thumbnail image media type.
        size
            The thumbnail image dimensions.

            | Supported |
            |-|
            |`(48, 48)`|
            |`(50, 50)`|
            |`(60, 60)`|
            |`(75, 75)`|
            |`(100, 100)`|
            |`(110, 110)`|
            |`(150, 150)`|
            |`(180, 180)`|
            |`(352, 352)`|
            |`(420, 420)`|
            |`(720, 720)`|
        retry_pending
            Whether to retry requests in case of pending thumbnail state.
        """

        return await self.handler.avatars.get_headshot(
            self.user.id,
            circular=circular,
            format=format,
            size=size,
            retry_pending=retry_pending,
        )

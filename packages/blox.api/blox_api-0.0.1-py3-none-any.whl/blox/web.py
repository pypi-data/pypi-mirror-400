from typing import (
    Callable,
    Literal,
    NoReturn,
    Optional,
    TYPE_CHECKING,
    Tuple,
    Type,
    TypeVar,
    Dict,
    Any,
    Union,
    cast,
    overload,
)

# from .utility import KeylessCache, Cache, CacheConfig, Requests
from .utility import Requests, PageIterator, SortOrder, SearchIterator
from datetime import datetime
from functools import wraps
import dateutil
import hashlib
import asyncio
import httpx
import copy
import json

from .exceptions import *
from .models import *
from .api_types import *


if TYPE_CHECKING:
    from .client import Blox

R = TypeVar("R")
M = TypeVar("M")
LOG = TypeVar("LOG")


# class WebCache:
#     """
#     Web handler long-term object caches and config. TTL in seconds, 0 to disable. (max_size, TTL)
#     """

#     def __init__(
#         self,
#         users: CacheConfig = (150, 0),
#     ):
#         self.users = Cache[int, User](*users)
#         # self.vehicles = KeylessCache[Vehicle](*vehicles)


def _refresh_handler(func):
    async def wrapper(self: "WebHandler", *args, **kwargs):
        handler = self._handler if isinstance(self, WebModule) else self
        result = await func(self, *args, **kwargs)
        if handler._web_token is not None:
            self._global_cache.web.set(handler._web_token, handler)
        return result

    return wrapper


def _ephemeral(func):
    @wraps(func)
    async def wrapper(self: "WebHandler", *args, **kwargs):
        force_fetch = kwargs.pop("fetch", False)
        try:
            args_repr = json.dumps(args, sort_keys=True, default=str)
            kwargs_repr = json.dumps(kwargs, sort_keys=True, default=str)
        except (TypeError, ValueError):
            args_repr = str(args)
            kwargs_repr = str(kwargs)

        hashed_args = hashlib.sha256(f"{args_repr}|{kwargs_repr}".encode()).hexdigest()
        cache_key = f"{func.__name__}_cache_{hashed_args}"

        if not force_fetch:
            if hasattr(self, cache_key):
                cached_result, timestamp = getattr(self, cache_key)
                if (asyncio.get_event_loop().time() - timestamp) < self._ephemeral_ttl:
                    return copy.copy(cached_result)

        result = await func(self, *args, **kwargs)

        setattr(self, cache_key, (result, asyncio.get_event_loop().time()))
        return copy.copy(result)

    return wrapper


class WebHandler:
    """
    The main class to interface with Roblox Web APIs.

    Parameters
    ----------
    client
        The global/shared Blox client.
    web_token
        The `.ROBLOSECURITY` token to authenticate requests. Defaults to `default_web_token`, if any.

        If not provided, only endpoints that do not require authentication can be used, otherwise an exception is raised.
    ephemeral_ttl
        How long, in seconds, ephemeral results (i.e, cached responses) are kept before expiring. Defaults to `3` seconds.
    cache
        An initialized web cache to use. By default, a new instance is created.
    requests
        An initialized requests class. By default, a new instance is created.
    """

    def __init__(
        self,
        client: "Blox",
        web_token: Optional[str] = None,
        ephemeral_ttl: int = 3,
        # cache: WebCache = WebCache(),
        requests: Optional[Requests] = None,
    ):
        self._client = client

        self._global_cache = client._global_cache
        # self._web_cache = cache
        self._ephemeral_ttl = ephemeral_ttl

        self._web_token = web_token
        self._requests: Requests = requests or self._refresh_requests()

        self.users = WebUsers(self)
        self.groups = WebGroups(self)
        self.avatars = WebAvatars(self)

    authenticated_user: Optional[User] = None

    def is_authenticated(self) -> bool:
        """
        Whether the handler is authenticated with a valid Roblox account (i.e, `.ROBLOSECURITY` is set and has been validated).
        """

        return True if self.authenticated_user is not None else False

    def _refresh_requests(self):
        self._requests = Requests(
            domain=self._client._domain,
            invalid_secrets=self._global_cache.invalid_secrets,
            headers={"Referer": "www.roblox.com"},
            session=self._client._session,
        )

        if self._web_token is not None:
            self._requests._session.cookies.set(".ROBLOSECURITY", self._web_token)

        return self._requests

    def _raise_web_errors(
        self,
        _content: Any,
        response: httpx.Response,
        exceptions: Optional[Dict[int, Callable[..., HTTPException]]] = None,
    ) -> NoReturn:
        if not isinstance(_content, Dict):
            raise HTTPException(
                f"Malformed response content was received: '{type(_content).__name__ if _content else 'None'}'",
                status_code=response.status_code,
            )

        content = cast(web_types.ErrorResponse, _content)
        errors = content.get("errors", [])

        if exceptions:
            for error in parse_web_errors(errors):
                if exception := exceptions.get(error.code):
                    raise exception(
                        message=f"{error.code} = {error.message}",
                        status_code=response.status_code,
                    )

        raise UnhandledWebException(errors, response.status_code)

    def _handle(
        self,
        response: httpx.Response,
        return_type: Type[R],
        *,
        exceptions: Optional[Dict[int, Callable[..., HTTPException]]] = None,
    ) -> R:
        content_type: Optional[str] = response.headers.get("Content-Type", None)
        if not content_type or not content_type.startswith("application/json"):
            raise BadContentType(response.status_code, content_type)

        if not response.is_success:
            self._raise_web_errors(response.json(), response, exceptions)
        return response.json()

    @_refresh_handler
    @_ephemeral
    async def authenticate(self) -> User:
        """
        Get the currently authenticated user. A `web_token` must be set, otherwise a `ValueError` is raised.
        """

        if self._web_token is None:
            raise ValueError("No .ROBLOSECURITY token provided but is required")

        user = User(
            self,
            data=self._handle(
                await self._requests.get("users", "/v1/users/authenticated"),
                web_types.v1_AuthenticatedUserResponse,
            ),
        )
        self.authenticated_user = user
        return user


class WebModule:
    """
    A class implemented by modules used by the main `WebHandler` class to interface with specific Roblox Web APIs.
    """

    def __init__(self, handler: WebHandler):
        self._handler = handler

        self._global_cache = handler._global_cache
        # self._web_cache = handler._web_cache
        self._ephemeral_ttl = handler._ephemeral_ttl

        self._requests = handler._requests
        self._handle = handler._handle


class WebUsers(WebModule):
    """
    Interact with Roblox User Web APIs.
    """

    def __init__(self, handler: WebHandler):
        super().__init__(handler)

    @overload
    async def get(
        self,
        id: int,
        /,
        *,
        exclude_banned: bool = True,
    ) -> Optional[User]: ...

    @overload
    async def get(
        self,
        ids: List[int],
        /,
        *,
        exclude_banned: bool = True,
    ) -> Dict[int, Optional[User]]: ...

    @overload
    async def get(
        self,
        name: str,
        /,
        *,
        exclude_banned: bool = True,
    ) -> Optional[User]: ...

    @overload
    async def get(
        self,
        names: List[str],
        /,
        *,
        exclude_banned: bool = True,
    ) -> Dict[str, Optional[User]]: ...

    @_ephemeral
    async def get(
        self,
        ids_or_names: Union[int, str, List[int], List[str]],
        /,
        *,
        exclude_banned: bool = True,
    ):
        """
        Get a single or multiple users using their user ID(s) or username(s).

        - **Single User:** Returns the user, if found.
        - **Multiple Users:** Returns a map of the requested IDs/usernames to their users, if found.

        Parameters
        ----------
        id
            The Roblox user ID.
        ids
            The Roblox user IDs.
        name
            The Roblox user name.
        names
            The Roblox user names.
        """

        single = False
        ids = names = None
        if isinstance(ids_or_names, int):
            ids = [ids_or_names]
            single = True
        elif isinstance(ids_or_names, str):
            names = [ids_or_names]
            single = True
        elif isinstance(next((v for v in ids_or_names), None), int):
            ids = [id for id in ids_or_names if isinstance(id, int)]
        else:
            names = [n for n in ids_or_names if isinstance(n, str)]

        if ids:
            ids = list(set(ids))
            users = [
                User(self._handler, u)
                for u in self._handle(
                    await self._requests.post(
                        "users",
                        "/v1/users",
                        json={
                            "userIds": ids,
                            "excludeBannedUsers": exclude_banned,
                        },
                    ),
                    web_types.v1_UsersByIdResponse,
                )["data"]
            ]

            if single:
                return next((u for u in users), None)

            map = {}
            for id in ids:
                if user := next((u for u in users if u.id == id), None):
                    map[id] = user
                else:
                    map[id] = None

            return map

        if names:
            names = list(set(names))
            users = [
                (u["requestedUsername"], User(self._handler, u))
                for u in self._handle(
                    await self._requests.post(
                        "users",
                        "/v1/usernames/users",
                        json={
                            "usernames": names,
                            "excludeBannedUsers": exclude_banned,
                        },
                    ),
                    web_types.v1_UsersByNameResponse,
                )["data"]
            ]

            if single:
                return next((u for u in users), None)

            map = {}
            for name in names:
                if user := next(
                    (u for u in users if u[0].lower() == name.lower()), None
                ):
                    map[name] = user[1]
                else:
                    map[name] = None

            return map

        return {}

    @_ephemeral
    async def get_profile(self, id: int) -> Optional[Profile]:
        """
        Get a detailed user profile using their user ID.

        Parameters
        ----------
        id
            The Roblox user ID.
        """

        try:
            return Profile(
                self._handler,
                data=self._handle(
                    await self._requests.get("users", f"/v1/users/{id}"),
                    web_types.v1_DetailedUserResponse,
                    exceptions={3: UserNotFound},
                ),
            )
        except UserNotFound:
            return None

    def name_history(
        self,
        id: int,
        *,
        names_per_page: Literal[10, 25, 50, 100] = 10,
        sort_order: SortOrder = SortOrder.Ascending,
        limit: Optional[int] = None,
    ) -> PageIterator[str]:
        """
        Iterate over a user's name history.

        Parameters
        ----------
        id
            The Roblox user ID.
        names_per_page
            The maximum number of names to fetch per page.
        sort_order
            The order names are sorted in (according to date of name change).
        limit
            The maximum number of names to iterate.
        """

        def page_handler(
            handler: WebHandler,
            response: httpx.Response,
            data: web_types.v1_UserNameHistory,
        ):
            return data["name"]

        return PageIterator(
            self._handler,
            "users",
            f"/v1/users/{id}/username-history",
            sort_order,
            page_size=names_per_page,
            max_items=limit,
            page_handler=page_handler,
            exceptions={3: UserNotFound},
        )

    def search(
        self,
        keyword: str,
        /,
        *,
        use_omni_search: bool = True,
        users_per_page: Literal[10, 25, 50, 100] = 25,
        limit: Optional[int] = None,
    ) -> Union[SearchIterator[User], PageIterator[User]]:
        """
        Search for users using a keyword.

        Parameters
        ----------
        keyword
            The keyword to query. The query matches against users' names as well as their name history. If not using `use_omni_search`, must be at least 3 characters.
        use_omni_search
            Whether to use the undocumented `omni-search` API. While it is less reliable, the limits are much more generous. If not used, this endpoint becomes nearly unusable when not using a `web_token`.
        users_per_page
            The maximum number of users to fetch per page. Ignored in `use_omni_search`.
        limit
            The maximum number of users to iterate.
        """

        def handle_omni_search_page(
            handler: WebHandler,
            response: httpx.Response,
            data: web_types.UserOmniSearchItem,
        ):
            return User(handler, data)

        def page_handler(
            handler: WebHandler,
            response: httpx.Response,
            data: web_types.v1_UserSearchResult,
        ):
            return User(handler, data)

        if use_omni_search:
            return SearchIterator(
                self._handler,
                "apis",
                "/search-api/omni-search",
                extra_params={
                    "verticalType": "user",
                    "searchQuery": keyword,
                    "sessionId": 0,
                },
                max_items=limit,
                page_handler=handle_omni_search_page,
            )

        if len(keyword) < 3:
            raise ValueError(f"Search keyword '{keyword}' is too short")

        return PageIterator(
            self._handler,
            "users",
            "/v1/users/search",
            extra_params={"keyword": keyword},
            page_size=users_per_page,
            max_items=limit,
            page_handler=page_handler,
        )


class WebGroups(WebModule):
    """
    Interact with Roblox Group Web APIs.
    """

    def __init__(self, handler: WebHandler):
        super().__init__(handler)

    @_ephemeral
    async def get(self, id: int, /) -> Optional[Group]:
        """
        Get a group using its ID.

        Parameters
        ----------
        id
            The Roblox group ID.
        """

        try:
            return Group(
                self._handler,
                data=self._handle(
                    await self._requests.get("groups", f"/v1/groups/{id}"),
                    web_types.v1_GroupDetailResponse,
                    exceptions={1: GroupNotFound},
                ),
            )
        except GroupNotFound:
            return None

    @_ephemeral
    async def get_memberships(self, id: int, /) -> Optional[List[Membership]]:
        """
        Get a user's membership for each group they are in.

        Parameters
        ----------
        id
            The Roblox user ID.
        """

        try:
            return [
                Membership(
                    self._handler,
                    data=membership,
                    user_id=id,
                    user=self._handler._global_cache.users.get(id),
                )
                for membership in self._handle(
                    await self._requests.get("groups", f"/v1/users/{id}/groups/roles"),
                    web_types.v1_UserGroupRolesResponse,
                    exceptions={3: UserNotFound},
                )["data"]
            ]
        except UserNotFound:
            return None

    @_ephemeral
    async def get_membership(
        self, id: int, /, *, group_id: int
    ) -> Optional[Membership]:
        """
        Get a user's membership in a group using the group and user IDs.

        Parameters
        ----------
        id
            The Roblox user ID.
        group_id
            The Roblox group ID.
        """

        if memberships := await self.get_memberships(id):
            return next((m for m in memberships if m.group.id == group_id), None)
        return None

    @_refresh_handler
    @_ephemeral
    async def get_primary(self, id: int, /) -> Optional[Membership]:
        """
        Get a user's primary group membership using their user ID.

        Parameters
        ----------
        id
            The Roblox user ID.
        """

        if memberships := await self.get_memberships(id):
            return next((m for m in memberships if m.primary), None)
        return None

    @_ephemeral
    async def get_roles(self, id: int, /) -> Optional[List[Role]]:
        """
        Get a group's roles.

        Parameters
        ----------
        id
            The Roblox group ID.
        """

        try:
            return [
                Role(
                    self._handler,
                    data=role,
                    group_id=id,
                    group=self._handler._global_cache.groups.get(id),
                )
                for role in self._handle(
                    await self._requests.get("groups", f"/v1/groups/{id}/roles"),
                    web_types.v1_GroupRolesResponse,
                    exceptions={1: GroupNotFound},
                )["roles"]
            ]
        except GroupNotFound:
            return None

    @overload
    async def get_role(
        self,
        id: int,
        /,
        *,
        role_id: int,
        rank: None = ...,
    ) -> Optional[Role]: ...

    @overload
    async def get_role(
        self, id: int, /, *, role_id: None = ..., rank: int
    ) -> Optional[Role]: ...

    @_ephemeral
    async def get_role(
        self, id: int, /, *, role_id: Optional[int] = None, rank: Optional[int] = None
    ):
        """
        Get a group role using the group ID and **EITHER** a role ID **OR** a role rank.

        Parameters
        ----------
        id
            The Roblox group ID.
        role_id
            The Roblox group role ID.
        rank
            The Roblox group role rank.
        """

        if roles := await self.get_roles(id):
            return next(
                (
                    r
                    for r in roles
                    if ((r.id == role_id) if role_id is not None else (r.rank == rank))
                ),
                None,
            )
        return None

    @_ephemeral
    async def get_icons(
        self,
        ids: List[int],
        /,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP"] = "PNG",
        size: Union[
            Tuple[Literal[150], Literal[150]],
            Tuple[Literal[420], Literal[420]],
        ] = (150, 150),
        retry_pending: bool = True,
        _attempt: int = 0,
    ) -> Dict[int, Optional[Thumbnail]]:
        """
        Get group icon thumbnails.

        Parameters
        ----------
        ids
            The Roblox group IDs.
        circular
            Whether the generated thumbnails should be circular.
        format
            The thumbnails' image media type.
        size
            The thumbnails' image dimensions.

            | Supported |
            |-|
            |`(150, 150)`|
            |`(420, 420)`|
        retry_pending
            Whether to retry requests in case of any pending thumbnail state.
        """

        map: Dict[int, Optional[Thumbnail]] = {id: None for id in ids}
        has_pending = False

        if data := (
            (
                self._handle(
                    await self._requests.get(
                        "thumbnails",
                        f"/v1/groups/icons",
                        params={
                            "groupIds": list(map.keys()),
                            "size": f"{size[0]}x{size[1]}",
                            "format": format,
                            "isCircular": circular,
                        },
                    ),
                    web_types.v1_ThumbnailResponse,
                )
            )["data"]
        ):
            for thumbnail_data in data:
                thumbnail = Thumbnail(
                    self._handler,
                    data=thumbnail_data,
                    type=ThumbnailType.GroupIcon,
                    circular=circular,
                    format=format,
                    size=size,
                )
                if thumbnail.state == ThumbnailState.Pending:
                    has_pending = True

                map[thumbnail.id] = thumbnail

        if not retry_pending or not has_pending:
            return map

        await asyncio.sleep(pow(_attempt, 2))
        return await self.get_icons(
            ids, circular=circular, format=format, size=size, _attempt=_attempt + 1
        )

    @_ephemeral
    async def get_icon(
        self,
        id: int,
        /,
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
        Get a group icon thumbnail.

        Parameters
        ----------
        id
            The Roblox group ID.
        circular
            Whether the generated thumbnail should be circular.
        format
            The thumbnail image media type.
        size
            The thumbnail image dimensions.

            | Supported |
            |-|
            |`(150, 150)`|
            |`(420, 420)`|
        retry_pending
            Whether to retry requests in case of pending thumbnail state.
        """

        thumbnails = await self.get_icons(
            [id],
            circular=circular,
            format=format,
            size=size,
            retry_pending=retry_pending,
        )
        return thumbnails.get(id)

    @_ephemeral
    async def get_guest_role(self, id: int):
        """
        Get a group's guest role using the group ID.

        Parameters
        ----------
        id
            The Roblox group ID.
        """

        if roles := await self.get_roles(id):
            return next((r for r in roles if r.is_guest()), None)
        return None

    def name_history(
        self,
        id: int,
        *,
        names_per_page: Literal[10, 25, 50, 100] = 10,
        sort_order: SortOrder = SortOrder.Ascending,
        limit: Optional[int] = None,
    ) -> PageIterator[Tuple[str, datetime]]:
        """
        Iterate over a group's name history.

        Parameters
        ----------
        id
            The Roblox group ID.
        names_per_page
            The maximum number of names to fetch per page.
        sort_order
            The order names are sorted in (according to date of name change).
        limit
            The maximum number of names to iterate.
        """

        def page_handler(
            handler: WebHandler,
            response: httpx.Response,
            data: web_types.v1_GroupNameHistory,
        ):
            return (data["name"], dateutil.parser.parse(data["created"]))

        return PageIterator(
            self._handler,
            "groups",
            f"/v1/groups/{id}/name-history",
            sort_order,
            page_size=names_per_page,
            max_items=limit,
            page_handler=page_handler,
            exceptions={1: GroupNotFound, 23: InsufficientPermissions},
        )

    def members(
        self,
        id: int,
        *,
        members_per_page: Literal[10, 25, 50, 100] = 50,
        sort_order: SortOrder = SortOrder.Ascending,
        limit: Optional[int] = None,
    ) -> PageIterator[Member]:
        """
        Iterate over a groups's members.

        Parameters
        ----------
        id
            The Roblox group ID.
        members_per_page
            The maximum number of members to fetch per page.
        sort_order
            The order members are sorted in (according to join date).
        limit
            The maximum number of members to iterate.
        """

        def page_handler(
            handler: WebHandler,
            response: httpx.Response,
            data: web_types.v1_GroupMember,
        ):
            return Member(
                handler, data, group_id=id, group=handler._global_cache.groups.get(id)
            )

        return PageIterator(
            self._handler,
            "groups",
            f"/v1/groups/{id}/users",
            sort_order,
            page_size=members_per_page,
            max_items=limit,
            page_handler=page_handler,
            exceptions={1: GroupNotFound, 35: InsufficientPermissions},
        )


_AvatarFullSize = Union[
    Tuple[Literal[30], Literal[30]],
    Tuple[Literal[48], Literal[48]],
    Tuple[Literal[60], Literal[60]],
    Tuple[Literal[75], Literal[75]],
    Tuple[Literal[100], Literal[100]],
    Tuple[Literal[110], Literal[110]],
    Tuple[Literal[140], Literal[140]],
    Tuple[Literal[150], Literal[150]],
    Tuple[Literal[150], Literal[200]],
    Tuple[Literal[180], Literal[180]],
    Tuple[Literal[250], Literal[250]],
    Tuple[Literal[352], Literal[352]],
    Tuple[Literal[420], Literal[420]],
    Tuple[Literal[720], Literal[720]],
]


_AvatarBustSize = Union[
    Tuple[Literal[48], Literal[48]],
    Tuple[Literal[50], Literal[50]],
    Tuple[Literal[60], Literal[60]],
    Tuple[Literal[75], Literal[75]],
    Tuple[Literal[100], Literal[100]],
    Tuple[Literal[150], Literal[150]],
    Tuple[Literal[180], Literal[180]],
    Tuple[Literal[352], Literal[352]],
    Tuple[Literal[420], Literal[420]],
]

_AvatarHeadshotSize = Union[
    Tuple[Literal[48], Literal[48]],
    Tuple[Literal[50], Literal[50]],
    Tuple[Literal[60], Literal[60]],
    Tuple[Literal[75], Literal[75]],
    Tuple[Literal[100], Literal[100]],
    Tuple[Literal[110], Literal[110]],
    Tuple[Literal[150], Literal[150]],
    Tuple[Literal[180], Literal[180]],
    Tuple[Literal[352], Literal[352]],
    Tuple[Literal[420], Literal[420]],
    Tuple[Literal[720], Literal[720]],
]


class WebAvatars(WebModule):
    """
    Interact with Roblox Avatar Web APIs.
    """

    def __init__(self, handler: WebHandler):
        super().__init__(handler)

    @overload
    async def get_full(
        self,
        id: int,
        /,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP", "JPEG"] = "PNG",
        size: _AvatarFullSize = (150, 150),
        retry_pending: bool = True,
        _attempt: int = 0,
    ) -> Optional[Thumbnail]: ...

    @overload
    async def get_full(
        self,
        ids: List[int],
        /,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP", "JPEG"] = "PNG",
        size: _AvatarFullSize = (150, 150),
        retry_pending: bool = True,
        _attempt: int = 0,
    ) -> Dict[int, Optional[Thumbnail]]: ...

    @_ephemeral
    async def get_full(
        self,
        id_or_ids: Union[int, List[int]],
        /,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP", "JPEG"] = "PNG",
        size: _AvatarFullSize = (150, 150),
        retry_pending: bool = True,
        _attempt: int = 0,
    ):
        """
        Get a single or multiple users' full avatar thumbnails using their user ID(s).

        - **Single User:** Returns the user's avatar thumbnail, if found.
        - **Multiple Users:** Returns a map of the requested IDs/usernames to their avatar thumbnails, if found.

        Parameters
        ----------
        id
            The Roblox user ID.
        ids
            The Roblox user IDs.
        circular
            Whether the generated thumbnails should be circular.
        format
            The thumbnails' image media type.
        size
            The thumbnails' image dimensions.

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
            Whether to retry requests in case of any pending thumbnail state.
        """

        single = isinstance(id_or_ids, int)
        ids = [id_or_ids] if single else id_or_ids

        map: Dict[int, Optional[Thumbnail]] = {id: None for id in ids}
        has_pending = False

        if data := (
            (
                self._handle(
                    await self._requests.get(
                        "thumbnails",
                        f"/v1/users/avatar",
                        params={
                            "userIds": list(map.keys()),
                            "size": f"{size[0]}x{size[1]}",
                            "format": format,
                            "isCircular": circular,
                        },
                    ),
                    web_types.v1_ThumbnailResponse,
                )
            )["data"]
        ):
            for thumbnail_data in data:
                thumbnail = Thumbnail(
                    self._handler,
                    data=thumbnail_data,
                    type=ThumbnailType.AvatarFull,
                    circular=circular,
                    format=format,
                    size=size,
                )
                if thumbnail.state == ThumbnailState.Pending:
                    has_pending = True

                map[thumbnail.id] = thumbnail

        if retry_pending and has_pending:
            await asyncio.sleep(pow(_attempt, 2))
            return await self.get_full(
                ids,
                circular=circular,
                format=format,
                size=size,
                retry_pending=retry_pending,
                _attempt=_attempt + 1,
            )

        return map[ids[0]] if single else map

    @overload
    async def get_bust(
        self,
        id: int,
        /,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP"] = "PNG",
        size: _AvatarBustSize = (150, 150),
        retry_pending: bool = True,
        _attempt: int = 0,
    ) -> Optional[Thumbnail]: ...

    @overload
    async def get_bust(
        self,
        ids: List[int],
        /,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP"] = "PNG",
        size: _AvatarBustSize = (150, 150),
        retry_pending: bool = True,
        _attempt: int = 0,
    ) -> Dict[int, Optional[Thumbnail]]: ...

    @_ephemeral
    async def get_bust(
        self,
        id_or_ids: Union[int, List[int]],
        /,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP"] = "PNG",
        size: _AvatarBustSize = (150, 150),
        retry_pending: bool = True,
        _attempt: int = 0,
    ):
        """
        Get a single or multiple users' avatar bust thumbnails using their user ID(s).

        - **Single User:** Returns the user's avatar thumbnail, if found.
        - **Multiple Users:** Returns a map of the requested IDs/usernames to their avatar thumbnails, if found.

        Parameters
        ----------
        id
            The Roblox user ID.
        ids
            The Roblox user IDs.
        circular
            Whether the generated thumbnails should be circular.
        format
            The thumbnails' image media type.
        size
            The thumbnails' image dimensions.

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
            Whether to retry requests in case of any pending thumbnail state.
        """

        single = isinstance(id_or_ids, int)
        ids = [id_or_ids] if single else id_or_ids

        map: Dict[int, Optional[Thumbnail]] = {id: None for id in ids}
        has_pending = False

        if data := (
            (
                self._handle(
                    await self._requests.get(
                        "thumbnails",
                        f"/v1/users/avatar-bust",
                        params={
                            "userIds": list(map.keys()),
                            "size": f"{size[0]}x{size[1]}",
                            "format": format,
                            "isCircular": circular,
                        },
                    ),
                    web_types.v1_ThumbnailResponse,
                )
            )["data"]
        ):
            for thumbnail_data in data:
                thumbnail = Thumbnail(
                    self._handler,
                    data=thumbnail_data,
                    type=ThumbnailType.AvatarBust,
                    circular=circular,
                    format=format,
                    size=size,
                )
                if thumbnail.state == ThumbnailState.Pending:
                    has_pending = True

                map[thumbnail.id] = thumbnail

        if retry_pending and has_pending:
            await asyncio.sleep(pow(_attempt, 2))
            return await self.get_bust(
                ids,
                circular=circular,
                format=format,
                size=size,
                retry_pending=retry_pending,
                _attempt=_attempt + 1,
            )

        return map[ids[0]] if single else map

    @overload
    async def get_headshot(
        self,
        id: int,
        /,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP", "JPEG"] = "PNG",
        size: _AvatarHeadshotSize = (150, 150),
        retry_pending: bool = True,
        _attempt: int = 0,
    ) -> Optional[Thumbnail]: ...

    @overload
    async def get_headshot(
        self,
        ids: List[int],
        /,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP", "JPEG"] = "PNG",
        size: _AvatarHeadshotSize = (150, 150),
        retry_pending: bool = True,
        _attempt: int = 0,
    ) -> Dict[int, Optional[Thumbnail]]: ...

    @_ephemeral
    async def get_headshot(
        self,
        id_or_ids: Union[int, List[int]],
        /,
        *,
        circular: bool = False,
        format: Literal["PNG", "WebP", "JPEG"] = "PNG",
        size: _AvatarHeadshotSize = (150, 150),
        retry_pending: bool = True,
        _attempt: int = 0,
    ):
        """
        Get a single or multiple users' avatar headshot thumbnails using their user ID(s).

        - **Single User:** Returns the user's avatar thumbnail, if found.
        - **Multiple Users:** Returns a map of the requested IDs/usernames to their avatar thumbnails, if found.

        Parameters
        ----------
        id
            The Roblox user ID.
        ids
            The Roblox user IDs.
        circular
            Whether the generated thumbnails should be circular.
        format
            The thumbnails' image media type.
        size
            The thumbnails' image dimensions.

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
            Whether to retry requests in case of any pending thumbnail state.
        """

        single = isinstance(id_or_ids, int)
        ids = [id_or_ids] if single else id_or_ids

        map: Dict[int, Optional[Thumbnail]] = {id: None for id in ids}
        has_pending = False

        if data := (
            (
                self._handle(
                    await self._requests.get(
                        "thumbnails",
                        f"/v1/users/avatar-headshot",
                        params={
                            "userIds": list(map.keys()),
                            "size": f"{size[0]}x{size[1]}",
                            "format": format,
                            "isCircular": circular,
                        },
                    ),
                    web_types.v1_ThumbnailResponse,
                )
            )["data"]
        ):
            for thumbnail_data in data:
                thumbnail = Thumbnail(
                    self._handler,
                    data=thumbnail_data,
                    type=ThumbnailType.AvatarHeadshot,
                    circular=circular,
                    format=format,
                    size=size,
                )
                if thumbnail.state == ThumbnailState.Pending:
                    has_pending = True

                map[thumbnail.id] = thumbnail

        if retry_pending and has_pending:
            await asyncio.sleep(pow(_attempt, 2))
            return await self.get_headshot(
                ids,
                circular=circular,
                format=format,
                size=size,
                retry_pending=retry_pending,
                _attempt=_attempt + 1,
            )

        return map[ids[0]] if single else map

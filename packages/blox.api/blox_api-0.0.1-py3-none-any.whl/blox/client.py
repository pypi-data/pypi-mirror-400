"""

The main blox.api client.

"""

from .utility import KeylessCache, Cache, CacheConfig
from .utility.requests import CleanAsyncClient
from typing import TYPE_CHECKING, Optional
from .web import WebHandler

if TYPE_CHECKING:
    from .models import User, Group


class GlobalCache:
    """
    Global object caches and config. TTL in seconds, 0 to disable. (max_size, TTL)
    """

    def __init__(
        self,
        web: CacheConfig = (2, 0),
        cloud: CacheConfig = (2, 0),
        invalid_secrets: CacheConfig = (25, 0),
        users: CacheConfig = (150, 0),
        groups: CacheConfig = (50, 0),
    ):
        self.web = Cache[str, WebHandler](*web)
        # self.cloud = Cache[str, Server](*cloud)
        self.invalid_secrets = KeylessCache[str](*invalid_secrets)

        self.users = Cache[int, "User"](*users)
        self.groups = Cache[int, "Group"](*groups)


class Blox:
    """
    The main Blox API client.

    Parameters
    ----------
    domain
        The domain to construct URLs from. Custom subdomain support has not yet been implemented.
    default_web_token
        The default `.ROBLOSECURITY` token to use. This will allow you to use `use_web` without needing to pass a key.
    default_cloud_key
        The default Open Cloud key to use. This will allow you to use `use_cloud` without needing to pass a key.
    """

    def __init__(
        self,
        domain: str = "roblox.com",
        default_web_token: Optional[str] = None,
        default_cloud_key: Optional[str] = None,
        _cache: Optional[GlobalCache] = None,
    ):
        self._default_web_token = default_web_token
        self._default_cloud_key = default_cloud_key
        self._domain = domain
        self._global_cache = _cache if _cache is not None else GlobalCache()
        self._session = CleanAsyncClient()

    def use_web(self, web_token: Optional[str] = None) -> WebHandler:
        """
        Get a web handler using a web token.

        Parameters
        ----------
        web_token
            The `.ROBLOSECURITY` token to authenticate requests. Defaults to `default_web_token`, if any.

            If not provided, only endpoints that do not require authentication can be used, otherwise an exception is raised.
        """

        if web_token is None:
            web_token = self._default_web_token

        if web_token is None:
            return WebHandler(self)

        existing_handler = self._global_cache.web.get(web_token)
        if existing_handler:
            if existing_handler._web_token != web_token:
                existing_handler._web_token = web_token
                existing_handler._refresh_requests()

                return self._global_cache.web.set(web_token, existing_handler)
            else:
                return existing_handler
        else:
            return self._global_cache.web.set(
                web_token, WebHandler(client=self, web_token=web_token)
            )

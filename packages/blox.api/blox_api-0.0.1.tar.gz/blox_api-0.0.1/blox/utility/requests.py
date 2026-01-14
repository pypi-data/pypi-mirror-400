from ..exceptions import HTTPException, BloxException, RequestTimeout
from typing import Dict, List, Optional, Tuple, Union
from .cache import Cache, KeylessCache
from time import time
import asyncio
import httpx


class CleanAsyncClient(httpx.AsyncClient):
    def __init__(self):
        super().__init__()

    def __del__(self):
        try:
            asyncio.get_event_loop().create_task(self.aclose())
        except RuntimeError:
            pass


class Bucket:
    def __init__(
        self,
        url: str,
        limit: int,
        remaining: int,
        reset_at: float,
        window: Optional[int],
    ):
        self.url = url
        self.limit = limit
        self.remaining = remaining
        self.reset_at = reset_at
        self.window = window


def parse_ratelimit_header(value: str) -> List[Tuple[int, Union[int, None]]]:
    limits = []

    for part in value.split(","):
        part = part.strip()

        if ";w=" in part:
            limit, window = part.split(";w=")
            limits.append((int(limit), int(window)))
        else:
            limits.append((int(part), None))

    return limits


class RateLimiter:
    def __init__(self):
        self.buckets = Cache[str, Bucket](max_size=50)

    def save_bucket(self, url: str, headers: httpx.Headers) -> None:
        limit_header = headers.get("x-ratelimit-limit")
        remaining = int(headers.get("x-ratelimit-remaining", 0))
        reset_seconds = float(headers.get("x-ratelimit-reset", 0))

        if not limit_header:
            return

        limits = parse_ratelimit_header(limit_header)

        limit, window = next(
            ((l, w) for l, w in limits if w is not None),
            limits[0],
        )

        reset_at = time() + reset_seconds

        self.buckets.set(
            url,
            Bucket(
                url=url,
                limit=limit,
                remaining=remaining,
                reset_at=reset_at,
                window=window,
            ),
        )

    def get_bucket(self, url: str) -> Optional[Bucket]:
        return self.buckets.get(url)

    async def avoid_limit(self, url: str, max_retry_after: float) -> None:
        bucket = self.get_bucket(url)
        if not bucket:
            return

        if bucket.remaining > 0:
            return

        sleep_for = bucket.reset_at - time()

        if sleep_for <= 0:
            self.buckets.delete(url)
            return

        if sleep_for > max_retry_after:
            raise HTTPException(
                f"Rate limit exceeded max threshold ({sleep_for:.2f}s > {max_retry_after}s).",
                status_code=429,
            )

        await asyncio.sleep(sleep_for)

    async def wait_to_retry(
        self, headers: httpx.Headers, max_retry_after: float
    ) -> bool:
        value = headers.get_list("retry-after")
        retry_after = float(next((v for v in value), 0))

        if retry_after <= 0:
            return False

        if retry_after > max_retry_after:
            return False

        await asyncio.sleep(retry_after)
        return True


class Requests:
    """
    Handles outgoing API requests while respecting rate limits.
    """

    def __init__(
        self,
        domain: str,
        invalid_secrets: KeylessCache[str],
        headers: Optional[Dict[str, str]] = None,
        session: Optional[CleanAsyncClient] = None,
        max_retries: int = 3,
        max_retry_after: float = 20.0,
        timeout: float = 5.0,
    ):
        self._rate_limiter = RateLimiter()
        self._session = session if session is not None else CleanAsyncClient()

        self._domain = domain
        self._default_headers = headers if headers is not None else {}
        self._max_retries = max_retries
        self._max_retry_after = max_retry_after
        self._timeout = timeout

        self._invalid_secrets = invalid_secrets

    def _can_retry(self, status_code: int = 500, retry: int = 0):
        return (status_code == 429 or status_code >= 500) and retry < self._max_retries

    def _check_default_headers(self):
        for header, value in self._default_headers.items():
            if value in self._invalid_secrets:
                raise BloxException(
                    f"Cannot reuse an invalid secret from default header: '{header}'"
                )

    async def _make_request(
        self, method: str, subdomain: str, route: str, retry: int = 0, **kwargs
    ) -> httpx.Response:
        self._check_default_headers()

        url = f"https://{subdomain}.{self._domain}{route}"
        headers = {**self._default_headers, **kwargs.pop("headers", {})}

        await self._rate_limiter.avoid_limit(url, self._max_retry_after)

        async def resend():
            return await self._make_request(
                method, subdomain, route, retry + 1, **kwargs, headers=headers
            )

        try:
            response = await self._session.request(
                method,
                url,
                headers=headers,
                timeout=httpx.Timeout(self._timeout),
                **kwargs,
            )
        except httpx.ReadTimeout:
            if self._can_retry(retry=retry):
                await asyncio.sleep(retry * 1.5)
                return await resend()
            else:
                raise RequestTimeout(retry, self._max_retries, self._timeout)

        self._rate_limiter.save_bucket(url, response.headers)

        if self._can_retry(response.status_code, retry):
            if await self._rate_limiter.wait_to_retry(
                response.headers, self._max_retry_after
            ):
                return await resend()
            else:
                await asyncio.sleep(retry * 1.5)
                return await resend()

        return response

    async def get(self, subdomain: str, route: str, **kwargs):
        return await self._make_request("GET", subdomain, route, **kwargs)

    async def post(self, subdomain: str, route: str, **kwargs):
        return await self._make_request("POST", subdomain, route, **kwargs)

    async def _close(self):
        await self._session.aclose()

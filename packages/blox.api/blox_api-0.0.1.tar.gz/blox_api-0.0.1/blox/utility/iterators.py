from __future__ import annotations

from enum import Enum
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Optional,
    AsyncIterator,
    Generic,
    TypeVar,
    List,
)

from blox.api_types import *

from ..exceptions import NoMoreItems, HTTPException

if TYPE_CHECKING:
    from ..web import WebHandler

# Original iterators (slightly modified below) are courtesy of ro.py
# see: https://github.com/ro-py/ro.py/blob/main/roblox/utilities/iterators.py

T = TypeVar("T")


class SortOrder(Enum):
    """
    Order in which page data should load in.
    """

    Ascending = "Asc"
    Descending = "Desc"


class BloxIterator(Generic[T]):
    """
    Represents a basic iterator that all iterators implement.
    """

    def __init__(self, max_items: Optional[int] = None):
        self.max_items: Optional[int] = max_items

    async def next(self) -> List[T]:
        """
        Moves to the next page and returns that page's data.
        """

        raise NotImplementedError

    async def flatten(self, max_items: Optional[int] = None) -> List[T]:
        """
        Flattens the data into a list.
        """

        if max_items is None:
            max_items = self.max_items

        items: List[T] = []

        while True:
            try:
                new_items = await self.next()
                items.extend(new_items)
            except NoMoreItems:
                break

            if max_items is not None and len(items) >= max_items:
                break

        return items[:max_items]

    def __aiter__(self) -> AsyncIterator[T]:
        return IteratorItems(self, max_items=self.max_items)

    def items(self, max_items: Optional[int] = None) -> AsyncIterator[T]:
        """
        Returns an AsyncIterable containing each iterator item.
        """

        if max_items is None:
            max_items = self.max_items
        return IteratorItems(self, max_items=max_items)

    def pages(self) -> AsyncIterator[List[T]]:
        """
        Returns an AsyncIterable containing each iterator page. Each page is a list of items.
        """

        return IteratorPages(self)


class IteratorItems(AsyncIterator[T], Generic[T]):
    """
    Represents the items inside of an iterator.
    """

    def __init__(self, iterator: BloxIterator[T], max_items: Optional[int] = None):
        self._iterator = iterator
        self._position: int = 0
        self._global_position: int = 0
        self._items: List[T] = []
        self._max_items = max_items

    def __aiter__(self) -> IteratorItems[T]:
        self._position = 0
        self._items = []
        return self

    async def __anext__(self) -> T:
        if self._position == len(self._items):
            self._position = 0
            try:
                self._items = await self._iterator.next()
            except NoMoreItems:
                self._position = 0
                self._global_position = 0
                self._items = []
                raise StopAsyncIteration

        if self._max_items is not None and self._global_position >= self._max_items:
            raise StopAsyncIteration

        try:
            item = self._items[self._position]
        except IndexError:
            raise StopAsyncIteration

        self._position += 1
        self._global_position += 1
        return item


class IteratorPages(AsyncIterator[List[T]], Generic[T]):
    """
    Represents the pages inside of an iterator.
    """

    def __init__(self, iterator: BloxIterator[T]):
        self._iterator = iterator

    def __aiter__(self) -> IteratorPages[T]:
        return self

    async def __anext__(self) -> List[T]:
        try:
            return await self._iterator.next()
        except NoMoreItems:
            raise StopAsyncIteration


class PageIterator(BloxIterator[T]):
    """
    Represents a cursor-based pagination iterator.
    """

    _next_cursor: Optional[str] = None
    _previous_cursor: Optional[str] = None

    def __init__(
        self,
        handler: "WebHandler",
        subdomain: str,
        route: str,
        sort_order: SortOrder = SortOrder.Ascending,
        page_size: int = 10,
        max_items: Optional[int] = None,
        exceptions: Optional[Dict[int, Callable[..., HTTPException]]] = None,
        extra_params: Optional[Dict] = None,
        page_handler: Optional[Callable[..., T]] = None,
        page_handler_kwargs: Optional[Dict] = None,
    ):
        super().__init__(max_items=max_items)

        self._handler = handler

        self._subdomain = subdomain
        self._route = route

        self._sort_order = sort_order
        self._page_size = page_size

        self._exceptions = exceptions
        self._extra_params = extra_params or {}
        self._page_handler = page_handler
        self._page_handler_kwargs = page_handler_kwargs or {}

        self._iterator_items: List[T] = []
        self._iterator_position: int = 0
        self._next_started: bool = False

    async def next(self) -> List[T]:
        """
        Advances the iterator to the next page.
        """

        if self._next_started and not self._next_cursor:
            raise NoMoreItems("No more items.")

        if not self._next_started:
            self._next_started = True

        response = await self._handler._requests.get(
            subdomain=self._subdomain,
            route=self._route,
            params={
                "cursor": self._next_cursor,
                "limit": self._page_size,
                "sortOrder": self._sort_order.value,
                **self._extra_params,
            },
        )
        page = self._handler._handle(
            response, web_types.WebCursorPagination, exceptions=self._exceptions
        )

        self._next_cursor = page["nextPageCursor"]
        self._previous_cursor = page["previousPageCursor"]

        if self._page_handler:
            return [
                self._page_handler(
                    handler=self._handler,
                    response=response,
                    data=item_data,
                    **self._page_handler_kwargs,
                )
                for item_data in page["data"]
            ]

        return list(page["data"])


class SearchIterator(BloxIterator[T]):
    """
    Represents a cursor-based pagination iterator. Supports one content group only.
    """

    _next_page_token: Optional[str] = None

    def __init__(
        self,
        handler: "WebHandler",
        subdomain: str,
        route: str,
        max_items: Optional[int] = None,
        exceptions: Optional[Dict[int, Callable[..., HTTPException]]] = None,
        extra_params: Optional[Dict] = None,
        page_handler: Optional[Callable[..., T]] = None,
        page_handler_kwargs: Optional[Dict] = None,
    ):
        super().__init__(max_items=max_items)

        self._handler = handler

        self._subdomain = subdomain
        self._route = route

        self._exceptions = exceptions
        self._extra_params = extra_params or {}
        self._page_handler = page_handler
        self._page_handler_kwargs = page_handler_kwargs or {}

        self._iterator_items: List[T] = []
        self._iterator_position: int = 0
        self._next_started: bool = False

    async def next(self) -> List[T]:
        """
        Advances the iterator to the next page.
        """

        if self._next_started and not self._next_page_token:
            raise NoMoreItems("No more items.")

        if not self._next_started:
            self._next_started = True

        response = await self._handler._requests.get(
            subdomain=self._subdomain,
            route=self._route,
            params={
                "pageToken": self._next_page_token,
                **self._extra_params,
            },
        )
        page = self._handler._handle(
            response, web_types.SearchPagination, exceptions=self._exceptions
        )
        content = next((r["contents"] for r in page["searchResults"]), [])

        self._next_page_token = page["nextPageToken"]

        if self._page_handler:
            return [
                self._page_handler(
                    handler=self._handler,
                    response=response,
                    data=item_data,
                    **self._page_handler_kwargs,
                )
                for item_data in content
            ]

        return list(content)

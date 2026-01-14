from typing import TYPE_CHECKING, Generic, TypedDict, List, Optional, TypeVar

D = TypeVar("D")


class WebDataList(TypedDict, Generic[D]):
    data: List[D]


if TYPE_CHECKING:

    class WebCursorPagination(WebDataList[D]):
        previousPageCursor: Optional[str]
        nextPageCursor: Optional[str]

else:
    WebCursorPagination = TypedDict


class SearchPaginationResult(TypedDict, Generic[D]):
    contentGroupType: str
    contents: List[D]
    topicId: str


if TYPE_CHECKING:

    class SearchPagination(TypedDict, Generic[D]):
        searchResults: List[SearchPaginationResult[D]]
        nextPageToken: str

else:
    SearchPagination = TypedDict


class ErrorItem(TypedDict):
    code: int
    message: str


class ErrorResponse(TypedDict):
    errors: List[ErrorItem]

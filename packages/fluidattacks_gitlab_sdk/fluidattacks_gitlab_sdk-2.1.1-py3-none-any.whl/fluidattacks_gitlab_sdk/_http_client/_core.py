from __future__ import (
    annotations,
)

import logging
from collections.abc import Callable
from dataclasses import (
    dataclass,
    field,
)

from fa_purity import (
    Cmd,
    Coproduct,
    FrozenList,
    Result,
    ResultE,
    UnitType,
)
from fa_purity.json import (
    JsonObj,
)
from pure_requests.retry import (
    MaxRetriesReached,
)
from requests.exceptions import (
    ChunkedEncodingError as RawChunkedEncodingError,
)
from requests.exceptions import (
    ConnectionError as RawConnectionError,
)
from requests.exceptions import (
    HTTPError as RawHTTPError,
)
from requests.exceptions import (
    JSONDecodeError as RawJSONDecodeError,
)
from requests.exceptions import (
    RequestException as RawRequestException,
)

LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class Credentials:
    api_key: str

    def __repr__(self) -> str:
        return "Credentials([masked])"

    def __str__(self) -> str:
        return "Credentials([masked])"


@dataclass(frozen=True)
class _Private:
    pass


@dataclass(frozen=True)
class HTTPError:
    raw: RawHTTPError


@dataclass(frozen=True)
class JSONDecodeError:
    raw: RawJSONDecodeError


@dataclass(frozen=True)
class ChunkedEncodingError:
    _private: _Private = field(repr=False, hash=False, compare=False)
    raw: RawChunkedEncodingError


@dataclass(frozen=True)
class RequestsConnectionError:
    _private: _Private = field(repr=False, hash=False, compare=False)
    raw: RawConnectionError


@dataclass(frozen=True)
class RequestException:
    raw: RawRequestException

    def to_chunk_error(self) -> ResultE[ChunkedEncodingError]:
        if isinstance(self.raw, RawChunkedEncodingError):
            return Result.success(ChunkedEncodingError(_Private(), self.raw))
        return Result.failure(ValueError("Not a ChunkedEncodingError"))

    def to_connection_error(self) -> ResultE[RequestsConnectionError]:
        if isinstance(self.raw, RawConnectionError):
            return Result.success(RequestsConnectionError(_Private(), self.raw))
        return Result.failure(ValueError("Not a RequestsConnectionError"))


@dataclass(frozen=True)
class UnhandledErrors:
    error: Coproduct[JSONDecodeError, Coproduct[HTTPError, RequestException]]


@dataclass(frozen=True)
class HandledErrors:
    error: Coproduct[
        HTTPError,
        Coproduct[ChunkedEncodingError, RequestsConnectionError],
    ]


@dataclass(frozen=True)
class RelativeEndpoint:
    paths: FrozenList[str]

    @staticmethod
    def new(*args: str) -> RelativeEndpoint:
        return RelativeEndpoint(tuple(args))


@dataclass(frozen=True)
class HttpJsonClient:
    get: Callable[
        [RelativeEndpoint, JsonObj],
        Cmd[
            Result[
                Coproduct[JsonObj, FrozenList[JsonObj]],
                Coproduct[UnhandledErrors, MaxRetriesReached],
            ]
        ],
    ]
    post: Callable[
        [RelativeEndpoint],
        Cmd[Result[UnitType, Coproduct[UnhandledErrors, MaxRetriesReached]]],
    ]


@dataclass(frozen=True)
class Page:
    @dataclass(frozen=True)
    class _Private:
        pass

    private: Page._Private = field(repr=False, hash=False, compare=False)
    page_num: int
    per_page: int

    @staticmethod
    def new_page(page_num: int, per_page: int) -> ResultE[Page]:
        if page_num > 0 and per_page in range(1, 101):
            pag = Page(Page._Private(), page_num, per_page)
            return Result.success(pag)
        return Result.failure(ValueError("Invalid page"))

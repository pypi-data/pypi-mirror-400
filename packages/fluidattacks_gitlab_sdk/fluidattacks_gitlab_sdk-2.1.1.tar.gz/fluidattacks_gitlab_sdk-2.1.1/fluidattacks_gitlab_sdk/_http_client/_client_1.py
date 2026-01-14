from __future__ import (
    annotations,
)

import logging
from dataclasses import (
    dataclass,
)
from typing import (
    TypeVar,
)

from fa_purity import (
    Cmd,
    Coproduct,
    FrozenDict,
    FrozenList,
    Result,
    UnitType,
    unit,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveFactory,
    JsonUnfolder,
    JsonValue,
)
from fluidattacks_etl_utils.smash import bind_chain
from pure_requests import (
    response,
)
from pure_requests import (
    retry as _retry,
)
from pure_requests.basic import (
    Data,
    Endpoint,
    HttpClientFactory,
    Params,
)
from pure_requests.retry import (
    HandledError,
    MaxRetriesReached,
)

from ._core import (
    Credentials,
    HandledErrors,
    HTTPError,
    HttpJsonClient,
    JSONDecodeError,
    RelativeEndpoint,
    RequestException,
    UnhandledErrors,
)

LOG = logging.getLogger(__name__)


_S = TypeVar("_S")
_F = TypeVar("_F")


def _retry_cmd(retry: int, item: Result[_S, _F]) -> Cmd[Result[_S, _F]]:
    log = Cmd.wrap_impure(lambda: LOG.info("retry #%2s waiting...", retry))
    return _retry.cmd_if_fail(item, log + _retry.sleep_cmd(retry**2))


def _http_error_handler(
    error: HTTPError,
) -> HandledError[HandledErrors, UnhandledErrors]:
    err_code: int = error.raw.response.status_code  # type: ignore[misc]
    handled = (
        409,
        429,
    )
    if err_code in range(500, 600) or err_code in handled:
        return HandledError.handled(HandledErrors(Coproduct.inl(error)))
    return HandledError.unhandled(UnhandledErrors(Coproduct.inr(Coproduct.inl(error))))


def _handled_request_exception(
    error: RequestException,
) -> HandledError[HandledErrors, UnhandledErrors]:
    return (
        error.to_chunk_error()
        .map(lambda e: HandledError.handled(HandledErrors(Coproduct.inr(Coproduct.inl(e)))))
        .lash(
            lambda _: error.to_connection_error().map(
                lambda e: HandledError.handled(HandledErrors(Coproduct.inr(Coproduct.inr(e)))),
            ),
        )
        .value_or(HandledError.unhandled(UnhandledErrors(Coproduct.inr(Coproduct.inr(error)))))
    )


def _handled_errors(
    error: Coproduct[JSONDecodeError, Coproduct[HTTPError, RequestException]],
) -> HandledError[HandledErrors, UnhandledErrors]:
    """Classify errors."""
    return error.map(
        lambda _: HandledError.unhandled(UnhandledErrors(error)),
        lambda c: c.map(
            _http_error_handler,
            _handled_request_exception,
        ),
    )


def _adjust_unhandled(
    error: UnhandledErrors | MaxRetriesReached,
) -> Coproduct[UnhandledErrors, MaxRetriesReached]:
    return Coproduct.inr(error) if isinstance(error, MaxRetriesReached) else Coproduct.inl(error)


@dataclass(frozen=True)
class Client1:
    _creds: Credentials
    _max_retries: int

    def _full_endpoint(self, endpoint: RelativeEndpoint) -> Endpoint:
        return Endpoint("/".join(("https://gitlab.com/api/v4", *endpoint.paths)))

    @staticmethod
    def new(creds: Credentials) -> Client1:
        return Client1(
            creds,
            150,
        )

    @property
    def _headers(self) -> JsonObj:
        return FrozenDict(
            {
                "Private-Token": JsonValue.from_primitive(
                    JsonPrimitiveFactory.from_raw(self._creds.api_key),
                ),
            },
        )

    def get(
        self,
        endpoint: RelativeEndpoint,
        params: JsonObj,
    ) -> Cmd[
        Result[
            Coproduct[JsonObj, FrozenList[JsonObj]],
            Coproduct[UnhandledErrors, MaxRetriesReached],
        ]
    ]:
        _full = self._full_endpoint(endpoint)
        log = Cmd.wrap_impure(
            lambda: LOG.debug(
                "[API] get: %s\nparams = %s",
                _full,
                JsonUnfolder.dumps(params),
            ),
        )
        client = HttpClientFactory.new_client(None, self._headers, False)
        handled = log + client.get(_full, Params(params)).map(
            lambda r: r.alt(RequestException),
        ).map(
            lambda r: bind_chain(r, lambda i: response.handle_status(i).alt(HTTPError)),
        ).map(
            lambda r: bind_chain(r, lambda i: response.json_decode(i).alt(JSONDecodeError)).alt(
                _handled_errors,
            ),
        )
        return _retry.retry_cmd(
            handled,
            _retry_cmd,
            self._max_retries,
        ).map(lambda r: r.alt(_adjust_unhandled))

    def post(
        self,
        endpoint: RelativeEndpoint,
    ) -> Cmd[Result[UnitType, Coproduct[UnhandledErrors, MaxRetriesReached]]]:
        _full = self._full_endpoint(endpoint)
        log = Cmd.wrap_impure(lambda: LOG.info("API call (post): %s", _full))
        client = HttpClientFactory.new_client(None, self._headers, False)
        handled = log + client.post(
            self._full_endpoint(endpoint),
            Params(FrozenDict({})),
            Data(FrozenDict({})),
        ).map(lambda r: r.alt(RequestException)).map(
            lambda r: bind_chain(r, lambda i: response.handle_status(i).alt(HTTPError)).alt(
                lambda e: _handled_errors(Coproduct.inr(e)),
            ),
        )
        return _retry.retry_cmd(
            handled,
            _retry_cmd,
            self._max_retries,
        ).map(
            lambda r: r.map(
                lambda _: unit,
            ).alt(_adjust_unhandled),
        )

    @property
    def client(self) -> HttpJsonClient:
        return HttpJsonClient(
            self.get,
            self.post,
        )

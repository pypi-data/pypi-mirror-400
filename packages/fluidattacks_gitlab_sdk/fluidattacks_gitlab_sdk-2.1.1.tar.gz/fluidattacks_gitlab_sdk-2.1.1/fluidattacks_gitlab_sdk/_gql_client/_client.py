from __future__ import (
    annotations,
)

import inspect
from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
    FrozenDict,
    Result,
    ResultE,
)
from fa_purity.json import (
    JsonObj,
    JsonValueFactory,
    Unfolder,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.retry import (
    cmd_if_fail,
    retry_cmd,
    sleep_cmd,
)
from fluidattacks_etl_utils.typing import (
    Dict,
    TypeVar,
)
from gql import (
    Client,
    gql,
)
from gql.transport.requests import (
    RequestsHTTPTransport,
)

from . import _handlers
from ._error import (
    ApiError,
)

API_ENDPOINT = "https://gitlab.com/api/graphql"
_T = TypeVar("_T")


def error_handler(cmd: Cmd[_T]) -> Cmd[ResultE[_T]]:
    return _handlers.too_many_requests_handler(
        _handlers.server_error_handler(_handlers.connection_error_handler(cmd)),
    ).map(lambda a: a.bind(lambda b: b.bind(lambda c: c)))


@dataclass(frozen=True)
class _GraphQlAsmClient:
    client: Client


@dataclass(frozen=True)
class GraphQlGitlabClient:
    _inner: _GraphQlAsmClient

    @staticmethod
    def new(token: str) -> Cmd[GraphQlGitlabClient]:
        def _new() -> GraphQlGitlabClient:
            headers: Dict[str, str] = {"Authorization": f"Bearer {token}"}
            transport = RequestsHTTPTransport(API_ENDPOINT, headers)
            client = Client(transport=transport, fetch_schema_from_transport=False)
            return GraphQlGitlabClient(_GraphQlAsmClient(client))

        return Cmd.wrap_impure(_new)

    def _get(self, query: str, values: FrozenDict[str, str]) -> Cmd[JsonObj]:
        def _action() -> JsonObj:
            return Bug.assume_success(
                "gql_decode_get_response",
                inspect.currentframe(),
                (query, str(values)),
                JsonValueFactory.from_any(
                    self._inner.client.execute(gql(query), dict(values)),  # type: ignore[misc]
                ).bind(Unfolder.to_json),
            )

        return Cmd.wrap_impure(_action)

    def get(self, query: str, values: FrozenDict[str, str]) -> Cmd[Result[JsonObj, ApiError]]:
        result = retry_cmd(
            error_handler(self._get(query, values)),
            lambda i, r: cmd_if_fail(r, sleep_cmd(i**2)),
            10,
        ).map(
            lambda r: Bug.assume_success(
                "gql_get_response",
                inspect.currentframe(),
                (query, str(values)),
                r,
            ),
        )
        return _handlers.api_error_handler(result)

import inspect

from fa_purity import (
    Cmd,
    CmdUnwrapper,
    Result,
    ResultE,
    ResultFactory,
)
from fa_purity.json import (
    JsonValueFactory,
    Unfolder,
)
from fluidattacks_etl_utils.bug import (
    Bug,
)
from fluidattacks_etl_utils.typing import (
    Callable,
    TypeVar,
)
from gql.transport.exceptions import (
    TransportQueryError,
    TransportServerError,
)
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
)

from ._error import (
    ApiError,
)

_T = TypeVar("_T")


def http_status_handler(is_handled: Callable[[int], bool], cmd: Cmd[_T]) -> Cmd[ResultE[_T]]:
    factory: ResultFactory[_T, Exception] = ResultFactory()

    def _action(unwrapper: CmdUnwrapper) -> ResultE[_T]:
        try:
            return factory.success(unwrapper.act(cmd))
        except TransportServerError as err:
            if err.code is not None and is_handled(err.code):
                return factory.failure(err)
            raise

    return Cmd.new_cmd(_action)


def api_error_handler(cmd: Cmd[_T]) -> Cmd[Result[_T, ApiError]]:
    factory: ResultFactory[_T, ApiError] = ResultFactory()

    def _action(unwrapper: CmdUnwrapper) -> Result[_T, ApiError]:
        try:
            return factory.success(unwrapper.act(cmd))
        except TransportQueryError as err:  # type: ignore[misc]
            _errors = JsonValueFactory.from_any(err.errors).bind(  # type: ignore[misc]
                lambda x: Unfolder.to_list(x),
            )
            errors = Bug.assume_success(
                "decode_errors",
                inspect.currentframe(),
                (str(_errors),),
                _errors,
            )
            return factory.failure(ApiError(errors))

    return Cmd.new_cmd(_action)


def too_many_requests_handler(cmd: Cmd[_T]) -> Cmd[ResultE[_T]]:
    too_many_requests_num = 429
    return http_status_handler(lambda c: c == too_many_requests_num, cmd)


def server_error_handler(cmd: Cmd[_T]) -> Cmd[ResultE[_T]]:
    return http_status_handler(lambda c: c in range(500, 600), cmd)


def connection_error_handler(cmd: Cmd[_T]) -> Cmd[ResultE[_T]]:
    def _action(unwrapper: CmdUnwrapper) -> ResultE[_T]:
        try:
            return Result.success(unwrapper.act(cmd))
        except RequestsConnectionError as err:
            return Result.failure(Exception(err))

    return Cmd.new_cmd(_action)

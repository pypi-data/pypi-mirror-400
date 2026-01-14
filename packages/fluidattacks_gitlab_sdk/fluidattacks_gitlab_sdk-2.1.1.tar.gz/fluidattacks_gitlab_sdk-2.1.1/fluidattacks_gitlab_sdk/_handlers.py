from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from fa_purity import Coproduct, Result, ResultE, cast_exception

from fluidattacks_gitlab_sdk._http_client import HTTPError, UnhandledErrors

_T = TypeVar("_T")


@dataclass
class NotFound(Exception):
    parent: Exception | None


def handle_value_error(value: Callable[[], _T]) -> ResultE[_T]:
    try:
        return Result.success(value())
    except ValueError as error:
        return Result.failure(error)


def _handle_not_found(error: HTTPError) -> Coproduct[NotFound, Exception]:
    not_found_code = 404
    err_code: int = error.raw.response.status_code  # type: ignore[misc]

    if err_code == not_found_code:
        return Coproduct.inl(NotFound(error.raw))
    return Coproduct.inr(error.raw)


def handle_not_found(error: UnhandledErrors) -> Coproduct[NotFound, Exception]:
    return error.error.map(
        lambda e: Coproduct.inr(cast_exception(e.raw)),
        lambda c: c.map(
            _handle_not_found,
            lambda e: Coproduct.inr(cast_exception(e.raw)),
        ),
    )

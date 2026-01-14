from dataclasses import (
    dataclass,
)

from fa_purity import (
    FrozenList,
    Result,
)
from fa_purity.json import (
    JsonValue,
)
from fluidattacks_etl_utils.typing import (
    TypeVar,
)

_T = TypeVar("_T")


@dataclass
class ApiError(Exception):
    errors: FrozenList[JsonValue]


ApiResult = Result[_T, ApiError]  # type: ignore[misc]

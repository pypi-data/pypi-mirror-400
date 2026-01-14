from arch_lint.dag import (
    DagMap,
)
from arch_lint.graph import (
    FullPathModule,
)
from fluidattacks_etl_utils.typing import (
    Dict,
    FrozenSet,
    NoReturn,
    TypeVar,
)

_T = TypeVar("_T")


def raise_or_return(item: _T | Exception) -> _T | NoReturn:
    if isinstance(item, Exception):
        raise item
    return item


def _module(path: str) -> FullPathModule | NoReturn:
    return raise_or_return(FullPathModule.from_raw(path))


_dag: Dict[str, tuple[tuple[str, ...] | str, ...]] = {
    "fluidattacks_gitlab_sdk": (
        ("merge_requests", "members", "issues", "milestones", "mr_approvals", "jobs"),
        "users",
        "_handlers",
        ("_http_client", "_gql_client", "_decoders"),
        "ids",
        "_logger",
    ),
    "fluidattacks_gitlab_sdk._http_client": (
        "_client_1",
        "_core",
    ),
    "fluidattacks_gitlab_sdk._gql_client": (
        "_client",
        "_handlers",
        "_error",
    ),
    "fluidattacks_gitlab_sdk.merge_requests": (
        "_client",
        "_decode",
        "core",
    ),
    "fluidattacks_gitlab_sdk.issues": (
        "_client",
        "core",
    ),
    "fluidattacks_gitlab_sdk.issues._client": (
        ("_get_issue", "_most_recent", "_updated_by"),
        "_decode",
    ),
    "fluidattacks_gitlab_sdk.members": (
        "_client",
        "_decode",
        "core",
    ),
    "fluidattacks_gitlab_sdk.users": (
        "decode",
        "core",
    ),
    "fluidattacks_gitlab_sdk.milestones": (
        "_client",
        "_decode",
        "core",
    ),
    "fluidattacks_gitlab_sdk.mr_approvals": (
        "_client",
        "_decode",
        "core",
    ),
    "fluidattacks_gitlab_sdk.jobs": ("_client", "_decode", "core"),
}


def project_dag() -> DagMap:
    return raise_or_return(DagMap.new(_dag))


def forbidden_allowlist() -> Dict[FullPathModule, FrozenSet[FullPathModule]]:
    _raw: Dict[str, FrozenSet[str]] = {}
    return {_module(k): frozenset(_module(i) for i in v) for k, v in _raw.items()}

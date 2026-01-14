from __future__ import (
    annotations,
)

import inspect
from dataclasses import (
    dataclass,
)
from datetime import datetime

from fa_purity import (
    Cmd,
    FrozenDict,
    FrozenList,
    Maybe,
    NewFrozenList,
    Result,
    ResultE,
    Stream,
    cast_exception,
)
from fa_purity._core.utils import raise_exception
from fa_purity.date_time import DatetimeUTC
from fa_purity.json import Primitive, UnfoldedFactory
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import int_to_str
from fluidattacks_etl_utils.paginate import (
    cursor_pagination,
)

from fluidattacks_gitlab_sdk._decoders import assert_multiple, assert_single, decode_maybe_single
from fluidattacks_gitlab_sdk._http_client import (
    ClientFactory,
    Credentials,
    HttpJsonClient,
    RelativeEndpoint,
)
from fluidattacks_gitlab_sdk.ids import MrFullId, MrInternalId, ProjectId

from ._decode import decode_batch_mrs, decode_mr_and_id
from .core import MergeRequest, MrsClient, PerPage


def get_mr(
    client: HttpJsonClient,
    project: ProjectId,
    mr_id: MrInternalId,
) -> Cmd[ResultE[tuple[MrFullId, MergeRequest]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.value),
        "merge_requests",
        int_to_str(mr_id.internal.value),
    )
    return client.get(
        endpoint,
        FrozenDict({}),
    ).map(
        lambda r: r.alt(
            lambda e: cast_exception(
                Bug.new(
                    "_get_mr",
                    inspect.currentframe(),
                    e,
                    (),
                ),
            ),
        )
        .bind(assert_single)
        .bind(decode_mr_and_id),
    )


def most_recent_mr_until(
    client: HttpJsonClient,
    project: ProjectId,
    date_created_before: DatetimeUTC,
) -> Cmd[ResultE[Maybe[tuple[MrFullId, MergeRequest]]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.value),
        "merge_requests",
    )
    params: dict[str, Primitive] = {
        "created_before": date_created_before.date_time.isoformat(),
        "order_by": "created_at",
        "sort": "desc",
        "per_page": 1,
    }
    empty: Maybe[tuple[MrFullId, MergeRequest]] = Maybe.empty()
    return client.get(
        endpoint,
        UnfoldedFactory.from_dict(params),
    ).map(
        lambda r: r.alt(
            lambda e: cast_exception(
                Bug.new(
                    "most_recent_mr",
                    inspect.currentframe(),
                    e,
                    (),
                ),
            ),
        )
        .bind(assert_multiple)
        .map(NewFrozenList)
        .map(decode_maybe_single)
        .bind(
            lambda m: m.to_coproduct().map(
                lambda r: decode_mr_and_id(r).map(Maybe.some),
                lambda _: Result.success(empty),
            ),
        ),
    )


def most_recent_mr(
    client: HttpJsonClient,
    project: ProjectId,
) -> Cmd[ResultE[Maybe[tuple[MrFullId, MergeRequest]]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.value),
        "merge_requests",
    )
    params: dict[str, Primitive] = {
        "order_by": "created_at",
        "sort": "desc",
        "per_page": 1,
    }
    empty: Maybe[tuple[MrFullId, MergeRequest]] = Maybe.empty()
    return client.get(
        endpoint,
        UnfoldedFactory.from_dict(params),
    ).map(
        lambda r: r.alt(
            lambda e: cast_exception(
                Bug.new(
                    "most_recent_mr",
                    inspect.currentframe(),
                    e,
                    (),
                ),
            ),
        )
        .bind(assert_multiple)
        .map(NewFrozenList)
        .map(decode_maybe_single)
        .bind(
            lambda m: m.to_coproduct().map(
                lambda r: decode_mr_and_id(r).map(Maybe.some),
                lambda _: Result.success(empty),
            ),
        ),
    )


def validate_next_page(
    page: int,
    items: FrozenList[tuple[MrFullId, MergeRequest]],
) -> ResultE[tuple[FrozenList[tuple[MrFullId, MergeRequest]], Maybe[int]]]:
    return Result.success((items, Maybe.some(page + 1) if len(items) > 0 else Maybe.empty()))


def get_updated_mrs(  # noqa: PLR0913
    client: HttpJsonClient,
    project: ProjectId,
    date_update_after: datetime,
    date_updated_before: datetime,
    page: Maybe[int],
    per_page: PerPage,
) -> Cmd[ResultE[tuple[FrozenList[tuple[MrFullId, MergeRequest]], Maybe[int]]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.value),
        "merge_requests",
    )
    current_page: int = page.value_or(1)
    params: dict[str, Primitive] = {
        "updated_after": date_update_after.isoformat(),
        "updated_before": date_updated_before.isoformat(),
        "labels": "Any",
        "order_by": "updated_at",
        "sort": "desc",
        "page": int_to_str(current_page),
        "per_page": per_page,
    }
    return client.get(
        endpoint,
        UnfoldedFactory.from_dict(params),
    ).map(
        lambda r: r.alt(
            lambda e: cast_exception(
                Bug.new(
                    "mr_updates",
                    inspect.currentframe(),
                    e,
                    (),
                ),
            ),
        )
        .bind(assert_multiple)
        .bind(decode_batch_mrs)
        .bind(lambda items: validate_next_page(current_page, items)),
    )


def get_page(  # noqa: PLR0913
    client: HttpJsonClient,
    project: ProjectId,
    date_update_after: datetime,
    date_updated_before: datetime,
    page: Maybe[int],
    per_page: PerPage,
) -> Cmd[tuple[FrozenList[tuple[MrFullId, MergeRequest]], Maybe[int]]]:
    return get_updated_mrs(
        client,
        project,
        date_update_after,
        date_updated_before,
        page,
        per_page,
    ).map(lambda r: r.alt(raise_exception).to_union())


def get_all_updated_mrs(
    client: HttpJsonClient,
    project: ProjectId,
    date_update_after: datetime,
    date_updated_before: datetime,
    per_page: PerPage,
) -> Cmd[Stream[FrozenList[tuple[MrFullId, MergeRequest]]]]:
    stream = cursor_pagination(
        lambda maybe_page: get_page(
            client,
            project,
            date_update_after,
            date_updated_before,
            maybe_page,
            per_page,
        ),
    )
    return Cmd.wrap_value(stream)


def _from_client(client: HttpJsonClient) -> MrsClient:
    return MrsClient(
        lambda p, i: get_mr(client, p, i),
        lambda p: most_recent_mr(client, p),
        lambda p, d: most_recent_mr_until(client, p, d),
        lambda p, a, b, v: get_all_updated_mrs(
            client,
            p,
            a,
            b,
            v,
        ),
    )


@dataclass(frozen=True)
class MrClientFactory:
    @staticmethod
    def new(creds: Credentials) -> MrsClient:
        return _from_client(ClientFactory.new(creds))

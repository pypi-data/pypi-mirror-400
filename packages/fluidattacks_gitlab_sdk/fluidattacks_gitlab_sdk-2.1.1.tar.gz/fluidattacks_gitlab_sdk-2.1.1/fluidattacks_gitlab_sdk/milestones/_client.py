from __future__ import (
    annotations,
)

import inspect
import logging
from dataclasses import (
    dataclass,
)

from fa_purity import (
    Cmd,
    Coproduct,
    CoproductFactory,
    FrozenDict,
    FrozenList,
    Maybe,
    NewFrozenList,
    Result,
    ResultE,
    cast_exception,
)
from fa_purity.json import JsonObj, Primitive, UnfoldedFactory
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import int_to_str

from fluidattacks_gitlab_sdk._decoders import assert_multiple, decode_maybe_single
from fluidattacks_gitlab_sdk._handlers import NotFound, handle_not_found
from fluidattacks_gitlab_sdk._http_client import (
    ClientFactory,
    Credentials,
    HttpJsonClient,
    RelativeEndpoint,
)
from fluidattacks_gitlab_sdk.ids import MilestoneFullId, MilestoneInternalId, ProjectId

from ._decode import decode_milestone_and_id
from .core import Milestone, MilestoneClient

LOG = logging.getLogger(__name__)


def handler_empty(
    item: Maybe[tuple[MilestoneFullId, Milestone]],
) -> Result[tuple[MilestoneFullId, Milestone], Coproduct[NotFound, Exception]]:
    return item.to_coproduct().map(
        Result.success,
        lambda _: Result.failure(Coproduct.inl(NotFound(ValueError("Milestone Not Found")))),
    )


def handler_empty_two(
    item: ResultE[Maybe[tuple[MilestoneFullId, Milestone]]],
) -> Result[tuple[MilestoneFullId, Milestone], Coproduct[NotFound, Exception]]:
    factory: CoproductFactory[NotFound, Exception] = CoproductFactory()
    return item.alt(lambda i: factory.inr(i)).bind(handler_empty)


def get_milestone(
    client: HttpJsonClient,
    project: ProjectId,
    milestone_id: MilestoneInternalId,
) -> Cmd[Result[tuple[MilestoneFullId, Milestone], Coproduct[NotFound, Exception]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.value),
        f"milestones?iids[]={int_to_str(milestone_id.internal.value)}",  # cspell:ignore iids
    )
    msg = Cmd.wrap_impure(lambda: LOG.info("[API] get_milestone(%s, %s)", project, milestone_id))
    return msg + client.get(
        endpoint,
        FrozenDict({}),
    ).map(
        lambda r: r.alt(
            lambda e: e.map(handle_not_found, lambda e: Coproduct.inr(cast_exception(e))),
        )
        .bind(lambda v: assert_multiple(v).alt(Coproduct.inr))
        .bind(lambda v: handler_empty_two(decode_milestone_and_id(v)))
        .alt(
            lambda c: c.map(
                Coproduct.inl,
                lambda e: Coproduct.inr(
                    Bug.new(
                        "_get_milestone",
                        inspect.currentframe(),
                        e,
                        (),
                    ),
                ),
            ),
        ),
    )


def most_recent_milestone(
    client: HttpJsonClient,
    project: ProjectId,
) -> Cmd[ResultE[Maybe[tuple[MilestoneFullId, Milestone]]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.value),
        "milestones",
    )
    params: dict[str, Primitive] = {
        "order_by": "created_at",
        "sort": "desc",
        "per_page": 1,
    }
    empty: Maybe[tuple[MilestoneFullId, Milestone]] = Maybe.empty()
    return client.get(
        endpoint,
        UnfoldedFactory.from_dict(params),
    ).map(
        lambda r: r.alt(
            lambda e: cast_exception(
                Bug.new(
                    "most_recent_milestone",
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
                lambda r: decode_milestone_and_id(FrozenList[JsonObj]((r,))),
                lambda _: Result.success(empty),
            ),
        ),
    )


def _from_client(client: HttpJsonClient) -> MilestoneClient:
    return MilestoneClient(
        lambda p, i: get_milestone(client, p, i),
        lambda p: most_recent_milestone(client, p),
    )


@dataclass(frozen=True)
class MilestoneFactory:
    @staticmethod
    def new(creds: Credentials) -> MilestoneClient:
        return _from_client(ClientFactory.new(creds))

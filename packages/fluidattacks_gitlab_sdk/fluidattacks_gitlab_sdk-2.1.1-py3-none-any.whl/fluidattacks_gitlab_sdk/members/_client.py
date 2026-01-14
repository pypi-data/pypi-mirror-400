import inspect

from fa_purity import (
    Cmd,
    FrozenList,
    ResultE,
    cast_exception,
)
from fa_purity.json import Primitive, UnfoldedFactory
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import int_to_str

from fluidattacks_gitlab_sdk._decoders import assert_multiple
from fluidattacks_gitlab_sdk._http_client import HttpJsonClient, RelativeEndpoint
from fluidattacks_gitlab_sdk.ids import MemberId, ProjectId

from ._decode import decode_members
from .core import Member


def get_members(
    client: HttpJsonClient,
    project: ProjectId,
) -> Cmd[ResultE[FrozenList[tuple[MemberId, Member]]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.value),
        "members",
    )

    params: dict[str, Primitive] = {
        "page": 1,
        "per_page": 100,
    }

    return client.get(
        endpoint,
        UnfoldedFactory.from_dict(params),
    ).map(
        lambda result: (
            result.alt(
                lambda e: cast_exception(
                    Bug.new("_get_members", inspect.currentframe(), e, ()),
                ),
            )
            .bind(assert_multiple)
            .bind(lambda members: decode_members(members, project))
        ),
    )

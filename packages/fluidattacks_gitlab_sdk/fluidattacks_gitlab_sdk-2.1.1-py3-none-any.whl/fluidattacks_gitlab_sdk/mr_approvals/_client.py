from __future__ import (
    annotations,
)

import inspect
from dataclasses import dataclass

from fa_purity import (
    Cmd,
    FrozenDict,
    ResultE,
    cast_exception,
)
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import int_to_str

from fluidattacks_gitlab_sdk._decoders import assert_single
from fluidattacks_gitlab_sdk._http_client import (
    ClientFactory,
    Credentials,
    HttpJsonClient,
    RelativeEndpoint,
)
from fluidattacks_gitlab_sdk.ids import MrFullId, MrInternalId, ProjectId
from fluidattacks_gitlab_sdk.mr_approvals.core import ApprovalsClient, MrApprovals

from ._decode import decode_id_and_mr_approvals


def _get_mr_approvals(
    client: HttpJsonClient,
    project: ProjectId,
    mr_internal: MrInternalId,
) -> Cmd[ResultE[tuple[MrFullId, MrApprovals]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.value),
        "merge_requests",
        int_to_str(mr_internal.internal.value),
        "approvals",
    )
    return client.get(
        endpoint,
        FrozenDict({}),
    ).map(
        lambda r: r.alt(
            lambda e: cast_exception(
                Bug.new(
                    "get_mr_approvals",
                    inspect.currentframe(),
                    e,
                    (),
                ),
            ),
        )
        .bind(assert_single)
        .bind(decode_id_and_mr_approvals),
    )


def _from_client(client: HttpJsonClient) -> ApprovalsClient:
    return ApprovalsClient(lambda p, i: _get_mr_approvals(client, p, i))


@dataclass(frozen=True)
class MrApprovalsFactory:
    @staticmethod
    def new(creds: Credentials) -> ApprovalsClient:
        return _from_client(ClientFactory.new(creds))

import inspect
import logging

from fa_purity import (
    Cmd,
    CmdTransform,
    Coproduct,
    FrozenDict,
    Maybe,
    Result,
    cast_exception,
)
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import int_to_str
from fluidattacks_etl_utils.smash import merge_coproduct, right_map

from fluidattacks_gitlab_sdk._decoders import assert_single
from fluidattacks_gitlab_sdk._gql_client import GraphQlGitlabClient
from fluidattacks_gitlab_sdk._handlers import NotFound, handle_not_found
from fluidattacks_gitlab_sdk._http_client import HttpJsonClient, RelativeEndpoint
from fluidattacks_gitlab_sdk.ids import IssueFullId, IssueInternalId, ProjectId
from fluidattacks_gitlab_sdk.issues._client._updated_by import get_updated_by
from fluidattacks_gitlab_sdk.issues.core import Issue, ProjectIdObj
from fluidattacks_gitlab_sdk.users.core import UserObj

from ._decode import decode_issue_and_id

LOG = logging.getLogger(__name__)


def _get_issue(
    client: HttpJsonClient,
    project: ProjectId,
    updated_by: Maybe[UserObj],
    issue_id: IssueInternalId,
) -> Cmd[Result[tuple[IssueFullId, Issue], Coproduct[NotFound, Exception]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.value),
        "issues",
        int_to_str(issue_id.internal_id.value),
    )
    msg = Cmd.wrap_impure(lambda: LOG.info("[API] get_issue(%s, %s)", project, issue_id))
    return msg + client.get(
        endpoint,
        FrozenDict({}),
    ).map(
        lambda r: r.alt(
            lambda e: e.map(handle_not_found, lambda e: Coproduct.inr(cast_exception(e))),
        )
        .bind(lambda i: assert_single(i).alt(Coproduct.inr))
        .bind(lambda i: decode_issue_and_id(updated_by, i).alt(Coproduct.inr))
        .alt(
            lambda c: right_map(
                c,
                lambda e: cast_exception(
                    Bug.new(
                        "_get_issue",
                        inspect.currentframe(),
                        e,
                        (),
                    ),
                ),
            ),
        ),
    )


def get_issue(
    client: HttpJsonClient,
    gql_client: GraphQlGitlabClient,
    project: ProjectIdObj,
    issue_id: IssueInternalId,
) -> Cmd[Result[tuple[IssueFullId, Issue], Coproduct[NotFound, Exception]]]:
    updated_by = get_updated_by(gql_client, project.project_path, issue_id)
    return CmdTransform.chain_cmd_result(
        updated_by,
        lambda u: _get_issue(client, project.project_id, u, issue_id),
    ).map(lambda r: r.alt(merge_coproduct))

import inspect
import logging

from fa_purity import (
    Cmd,
    Maybe,
    NewFrozenList,
    Result,
    ResultE,
    cast_exception,
)
from fa_purity.json import JsonObj, JsonUnfolder, Primitive, UnfoldedFactory
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import int_to_str

from fluidattacks_gitlab_sdk._decoders import (
    assert_multiple,
    decode_issue_internal_id,
    decode_maybe_single,
)
from fluidattacks_gitlab_sdk._gql_client import GraphQlGitlabClient
from fluidattacks_gitlab_sdk._http_client import HttpJsonClient, RelativeEndpoint
from fluidattacks_gitlab_sdk.ids import IssueFullId, ProjectPath
from fluidattacks_gitlab_sdk.issues._client._updated_by import get_updated_by
from fluidattacks_gitlab_sdk.issues.core import Issue, ProjectIdObj
from fluidattacks_gitlab_sdk.users.core import UserObj

from ._decode import decode_issue_and_id

LOG = logging.getLogger(__name__)


def _most_recent_issue(
    gql_client: GraphQlGitlabClient,
    raw: JsonObj,
    project: ProjectPath,
) -> Cmd[ResultE[tuple[IssueFullId, Issue]]]:
    """
    Completes the raw issue obj by getting the updated by field.

    This function should be called always after getting the raw issue.
    It can fail when:
    - decode fails
    - raw issue id not exist and/or is fake
    """
    _updated_by: Cmd[ResultE[Maybe[UserObj]]] = (
        decode_issue_internal_id(raw)
        .to_coproduct()
        .map(
            lambda i: get_updated_by(gql_client, project, i.internal_id).map(
                lambda r: r.alt(
                    lambda c: c.map(
                        lambda e: Bug.new(
                            "most_recent_issue: race condition",
                            inspect.currentframe(),
                            e,
                            (str(project), JsonUnfolder.dumps(raw)),
                        ),  # this should be not possible, the issue was retrieved before
                        lambda e: e,
                    ),
                ),
            ),
            lambda e: Cmd.wrap_value(Result.failure(e)),
        )
    )
    return _updated_by.map(
        lambda r: r.bind(
            lambda u: decode_issue_and_id(u, raw),
        ),
    )


def most_recent_issue(
    client: HttpJsonClient,
    gql_client: GraphQlGitlabClient,
    project: ProjectIdObj,
) -> Cmd[ResultE[Maybe[tuple[IssueFullId, Issue]]]]:
    endpoint = RelativeEndpoint.new(
        "projects",
        int_to_str(project.project_id.project_id.value),
        "issues",
    )
    params: dict[str, Primitive] = {
        "order_by": "created_at",
        "sort": "desc",
        "per_page": 1,
    }
    empty: Maybe[tuple[IssueFullId, Issue]] = Maybe.empty()
    msg: Cmd[None] = Cmd.wrap_impure(lambda: LOG.info("[API] most_recent_issue(%s)", project))
    get_maybe_single = client.get(
        endpoint,
        UnfoldedFactory.from_dict(params),
    ).map(
        lambda r: r.alt(
            lambda e: cast_exception(
                Bug.new(
                    "most_recent_issue",
                    inspect.currentframe(),
                    e,
                    (),
                ),
            ),
        )
        .bind(assert_multiple)
        .map(NewFrozenList)
        .map(decode_maybe_single),
    )
    get_issue: Cmd[ResultE[Maybe[tuple[IssueFullId, Issue]]]] = get_maybe_single.bind(
        lambda r: r.to_coproduct().map(
            lambda m: m.to_coproduct().map(
                lambda raw: _most_recent_issue(gql_client, raw, project.project_path).map(
                    lambda r: r.map(Maybe.some),
                ),
                lambda _: Cmd.wrap_value(Result.success(empty)),
            ),
            lambda e: Cmd.wrap_value(Result.failure(e)),
        ),
    )
    return msg + get_issue

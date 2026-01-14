import inspect
import logging
from collections.abc import Callable
from typing import TypeVar

from fa_purity import (
    Cmd,
    Coproduct,
    FrozenList,
    FrozenTools,
    Maybe,
    Result,
    ResultE,
)
from fa_purity.json import JsonObj, JsonUnfolder, JsonValue, Unfolder
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import DecodeUtils, int_to_str, str_to_int
from fluidattacks_etl_utils.natural import Natural
from fluidattacks_etl_utils.smash import right_map

from fluidattacks_gitlab_sdk._gql_client import GraphQlGitlabClient
from fluidattacks_gitlab_sdk._handlers import NotFound
from fluidattacks_gitlab_sdk.ids import IssueInternalId, ProjectPath, UserId
from fluidattacks_gitlab_sdk.users.core import User, UserName, UserObj

LOG = logging.getLogger(__name__)
_T = TypeVar("_T")


def _nested_key(raw: JsonObj, first_key: str, next_keys: FrozenList[str]) -> ResultE[JsonValue]:
    if next_keys:
        return JsonUnfolder.require(
            raw,
            first_key,
            lambda v: Unfolder.to_json(v).bind(
                lambda v: _nested_key(v, next_keys[0], next_keys[1:]),
            ),
        )
    return JsonUnfolder.require(raw, first_key, lambda v: Result.success(v))


def _decode_gid(raw: str) -> ResultE[UserId]:
    return str_to_int(raw.removeprefix("gid://gitlab/User/")).bind(Natural.from_int).map(UserId)


def decode_user_obj(raw: JsonObj) -> ResultE[UserObj]:
    return (
        JsonUnfolder.require(raw, "id", DecodeUtils.to_str)
        .bind(_decode_gid)
        .bind(
            lambda user_id: JsonUnfolder.require(raw, "username", DecodeUtils.to_str)
            .map(User)
            .bind(
                lambda user: JsonUnfolder.require(raw, "name", DecodeUtils.to_str)
                .map(UserName)
                .map(
                    lambda name: UserObj(user_id, user, name),
                ),
            ),
        )
    )


def decode_updated_by(raw: JsonObj) -> ResultE[Maybe[UserObj]]:
    return JsonUnfolder.require(
        raw,
        "updatedBy",
        lambda v: DecodeUtils.to_maybe(v, lambda v: Unfolder.to_json(v).bind(decode_user_obj)),
    )


def _set_not_found_if_empty(
    value: JsonValue,
    transform: Callable[[JsonValue], ResultE[_T]],
) -> Result[_T, Coproduct[NotFound, Exception]]:
    return (
        DecodeUtils.to_maybe(value, transform)
        .alt(Coproduct[NotFound, Exception].inr)
        .bind(
            lambda m: m.to_coproduct().map(
                lambda m: Result.success(m),
                lambda _: Result.failure(Coproduct.inl(NotFound(ValueError("Issue not found")))),
            ),
        )
    )


def _decode(raw: JsonObj) -> Result[Maybe[UserObj], Coproduct[NotFound, Exception]]:
    return (
        _nested_key(raw, "project", ("issue",))
        .alt(Coproduct[NotFound, Exception].inr)
        .bind(
            lambda v: _set_not_found_if_empty(
                v,
                lambda v: Unfolder.to_json(v).bind(decode_updated_by),
            ),
        )
        .alt(
            lambda c: c.map(
                Coproduct.inl,
                lambda e: Coproduct.inr(
                    Bug.new(
                        "decode_updated_by",
                        inspect.currentframe(),
                        e,
                        (JsonUnfolder.dumps(raw),),
                    ),
                ),
            ),
        )
    )


def get_updated_by(
    client: GraphQlGitlabClient,
    project: ProjectPath,
    issue_id: IssueInternalId,
) -> Cmd[Result[Maybe[UserObj], Coproduct[NotFound, Exception]]]:
    """
    Get the updatedBy field of an issue.

    To avoid failure ensure:
    - The issue exist
    - The credentials are correct
    """
    query = """
    query getIssueUpdatedBy($project: ID!, $issue_iid: String!){
        project(fullPath: $project) {
            issue(iid: $issue_iid) {
                updatedBy {
                    id
                    name
                    username
                }
            }
        }
    }
    """
    values: dict[str, str] = {
        "project": project.path,
        "issue_iid": int_to_str(issue_id.internal_id.value),
    }
    return client.get(query, FrozenTools.freeze(values)).map(
        lambda r: r.alt(Coproduct[NotFound, Exception].inr)
        .bind(_decode)
        .alt(
            lambda c: right_map(
                c,
                lambda e: Bug.new(
                    "get_updated_by",
                    inspect.currentframe(),
                    e,
                    (str(project), str(issue_id)),
                ),
            ),
        ),
    )

import pytest
from fa_purity import Cmd, Coproduct, Result, Unsafe
from fluidattacks_etl_utils.natural import NaturalOperations

from fluidattacks_gitlab_sdk._handlers import NotFound
from fluidattacks_gitlab_sdk.ids import IssueFullId, IssueInternalId
from fluidattacks_gitlab_sdk.issues._client import IssueClientFactory
from fluidattacks_gitlab_sdk.issues.core import Issue
from tests_fx._utils import get_creds_from_env, get_project_id_obj_from_env


def _check_not_found(
    result: Result[tuple[IssueFullId, Issue], Coproduct[NotFound, Exception]],
) -> None:
    assert result.to_coproduct().map(
        lambda _: False,
        lambda c: c.map(
            lambda _: True,
            lambda _: False,
        ),
    )


def _check_data(result: Result[tuple[IssueFullId, Issue], Coproduct[NotFound, Exception]]) -> None:
    assert result.to_coproduct().map(
        lambda _: True,
        lambda c: c.map(
            lambda _: False,
            lambda _: False,
        ),
    )


def test_issue_not_found() -> None:
    get_creds = get_creds_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    get_project = get_project_id_obj_from_env().map(
        lambda r: r.alt(Unsafe.raise_exception).to_union(),
    )

    action: Cmd[None] = (
        get_creds.map(IssueClientFactory.new)
        .bind(
            lambda c: get_project.bind(
                lambda project: c.get_issue(
                    project,
                    IssueInternalId(NaturalOperations.absolute(3018)),
                ),
            ),
        )
        .map(_check_not_found)
    )

    with pytest.raises(SystemExit):
        action.compute()


def test_issue() -> None:
    get_creds = get_creds_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    get_project = get_project_id_obj_from_env().map(
        lambda r: r.alt(Unsafe.raise_exception).to_union(),
    )

    action: Cmd[None] = (
        get_creds.map(IssueClientFactory.new)
        .bind(
            lambda c: get_project.bind(
                lambda project: c.get_issue(
                    project,
                    IssueInternalId(NaturalOperations.absolute(15000)),
                ),
            ),
        )
        .map(_check_data)
    )

    with pytest.raises(SystemExit):
        action.compute()

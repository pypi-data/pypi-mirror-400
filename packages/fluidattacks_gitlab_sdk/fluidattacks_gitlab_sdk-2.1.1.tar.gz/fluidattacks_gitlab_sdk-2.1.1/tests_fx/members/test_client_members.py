import pytest
from fa_purity import Cmd, FrozenList, Unsafe
from fluidattacks_etl_utils.natural import NaturalOperations

from fluidattacks_gitlab_sdk.ids import MemberId, ProjectId
from fluidattacks_gitlab_sdk.members import MembersClientFactory
from fluidattacks_gitlab_sdk.members.core import Member
from tests_fx._utils import get_creds_from_env, get_project_from_env


def _check_data(data: FrozenList[tuple[MemberId, Member]]) -> None:
    project_id = ProjectId(NaturalOperations.absolute(20741933))
    expected = (
        (
            MemberId(NaturalOperations.absolute(4312474)),
            Member(
                "slizcanoatfluid",
                "Sebastian Lizcano",
                project_id,
            ),
        ),
        (
            MemberId(NaturalOperations.absolute(4319452)),
            Member(
                "drestrepoatfluid",
                "Diego Restrepo",
                project_id,
            ),
        ),
    )

    assert data == expected


def test_members() -> None:
    """
    Client member validation.

    This test does not verify all possible members in a project.
    For simplicity reason, the client was temporarily modified to
    limit the number of members returned by the API (e.g., using `per_page=2`).
    This makes it feasible to run assertions on a small, controlled dataset instead
    of processing a large number of users.

    To run this test correctly, ensure the client is configured to return only 2 members,
    as assertions are only made on those.
    """
    get_creds = get_creds_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    get_project = get_project_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())

    action: Cmd[None] = (
        get_creds.map(MembersClientFactory.new)
        .bind(
            lambda c: get_project.bind(lambda project: c.get_members(project)),
        )
        .map(lambda r: r.alt(Unsafe.raise_exception).to_union())
        .map(_check_data)
    )

    with pytest.raises(SystemExit):
        action.compute()

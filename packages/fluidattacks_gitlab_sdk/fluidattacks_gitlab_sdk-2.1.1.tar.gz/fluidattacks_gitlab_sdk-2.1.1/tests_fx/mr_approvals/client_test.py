import pytest
from fa_purity import Cmd, Unsafe
from fluidattacks_etl_utils.natural import NaturalOperations

from fluidattacks_gitlab_sdk.ids import MrFullId, MrInternalId
from fluidattacks_gitlab_sdk.mr_approvals import MrApprovalsFactory
from fluidattacks_gitlab_sdk.mr_approvals.core import MrApprovals
from tests_fx._utils import get_creds_from_env, get_project_from_env


def _check_data(data: tuple[MrFullId, MrApprovals]) -> None:
    assert data


def test_mr_approvals() -> None:
    get_creds = get_creds_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    get_project = get_project_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())

    action: Cmd[None] = (
        get_creds.map(MrApprovalsFactory.new)
        .bind(
            lambda v: get_project.bind(
                lambda project: v.get_approvals(
                    project,
                    MrInternalId(NaturalOperations.absolute(78237)),
                ),
            ),
        )
        .map(lambda r: r.alt(Unsafe.raise_exception).to_union())
        .map(_check_data)
    )
    with pytest.raises(SystemExit):
        action.compute()

import inspect

import pytest
from fa_purity import Cmd, Maybe, Unsafe
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.natural import NaturalOperations

from fluidattacks_gitlab_sdk.ids import MilestoneFullId, MilestoneInternalId
from fluidattacks_gitlab_sdk.milestones import MilestoneFactory
from fluidattacks_gitlab_sdk.milestones.core import Milestone
from tests_fx._utils import get_creds_from_env, get_project_from_env


def _check_data(data: Maybe[tuple[MilestoneFullId, Milestone]]) -> None:
    assert data.value_or(None)


def test_milestone() -> None:
    get_creds = get_creds_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    get_project = get_project_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    action: Cmd[None] = (
        get_creds.map(MilestoneFactory.new)
        .bind(
            lambda v: get_project.bind(
                lambda project: v.get_milestone(
                    project,
                    MilestoneInternalId(NaturalOperations.absolute(14)),
                ),
            ),
        )
        .map(
            lambda r: r.to_coproduct().map(
                Maybe.some,
                lambda c: c.map(
                    lambda _: Maybe.empty(),
                    lambda e: Bug.new(
                        "get_issue",
                        inspect.currentframe(),
                        e,
                        ("project", "i"),
                    ).explode(),
                ),
            ),
        )
        .map(_check_data)
    )
    with pytest.raises(SystemExit):
        action.compute()

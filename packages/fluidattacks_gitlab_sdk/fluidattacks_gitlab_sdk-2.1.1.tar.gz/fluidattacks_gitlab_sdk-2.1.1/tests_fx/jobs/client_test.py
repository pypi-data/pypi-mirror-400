import pytest
from fa_purity import Cmd, Coproduct, Result, Unsafe
from fluidattacks_etl_utils.natural import NaturalOperations

from fluidattacks_gitlab_sdk._handlers import NotFound
from fluidattacks_gitlab_sdk.ids import JobId
from fluidattacks_gitlab_sdk.jobs import JobClientFactory
from fluidattacks_gitlab_sdk.jobs.core import JobObj
from tests_fx._utils import get_creds_from_env, get_project_from_env


def _check_data(result: Result[JobObj, Coproduct[NotFound, Exception]]) -> None:
    assert result.to_coproduct().map(
        lambda _: True,
        lambda c: c.map(
            lambda _: False,
            lambda _: False,
        ),
    )


def _check_not_found(
    result: Result[JobObj, Coproduct[NotFound, Exception]],
) -> None:
    assert result.to_coproduct().map(
        lambda _: False,
        lambda c: c.map(
            lambda _: True,
            lambda _: False,
        ),
    )


def test_job() -> None:
    get_creds = get_creds_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    get_project = get_project_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    action: Cmd[None] = (
        get_creds.map(JobClientFactory.new)
        .bind(
            lambda c: get_project.bind(
                lambda project: c.get_job(
                    project,
                    JobId(NaturalOperations.absolute(12634660510)),
                ),
            ),
        )
        .map(_check_data)
    )
    with pytest.raises(SystemExit):
        action.compute()

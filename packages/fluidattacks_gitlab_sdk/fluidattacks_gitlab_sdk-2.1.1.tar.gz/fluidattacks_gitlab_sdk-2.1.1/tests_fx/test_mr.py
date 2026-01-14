from datetime import UTC, datetime

import pytest
from fa_purity import Cmd, Stream, Unsafe
from fa_purity._core.frozen import FrozenList
from fluidattacks_etl_utils.natural import NaturalOperations

from fluidattacks_gitlab_sdk.ids import MrFullId, MrInternalId
from fluidattacks_gitlab_sdk.merge_requests import MrClientFactory
from fluidattacks_gitlab_sdk.merge_requests.core import MergeRequest, PerPage
from tests_fx._utils import get_creds_from_env, get_project_from_env


def _check_data(data: tuple[MrFullId, MergeRequest]) -> None:
    assert data


def _check_batch_data(items: Stream[FrozenList[tuple[MrFullId, MergeRequest]]] | None) -> None:
    assert items


def test_mr() -> None:
    get_creds = get_creds_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    get_project = get_project_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    action: Cmd[None] = (
        get_creds.map(MrClientFactory.new)
        .bind(
            lambda c: get_project.bind(
                lambda project: c.get_mr(
                    project,
                    MrInternalId(NaturalOperations.absolute(3)),
                ),
            ),
        )
        .map(lambda r: r.alt(Unsafe.raise_exception).to_union())
        .map(_check_data)
    )

    with pytest.raises(SystemExit):
        action.compute()


def test_streams_mrs_updates() -> None:
    get_creds = get_creds_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    get_project = get_project_from_env().map(lambda r: r.alt(Unsafe.raise_exception).to_union())
    action: Cmd[None] = (
        get_creds.map(MrClientFactory.new)
        .bind(
            lambda c: get_project.bind(
                lambda project: c.get_mr_updated(
                    project,
                    datetime(2025, 9, 1, 0, 0, 0, tzinfo=UTC),
                    datetime(2025, 9, 1, 0, 1, 0, tzinfo=UTC),
                    PerPage(50),
                ),
            ),
        )
        .map(_check_batch_data)
    )
    with pytest.raises(SystemExit):
        action.compute()

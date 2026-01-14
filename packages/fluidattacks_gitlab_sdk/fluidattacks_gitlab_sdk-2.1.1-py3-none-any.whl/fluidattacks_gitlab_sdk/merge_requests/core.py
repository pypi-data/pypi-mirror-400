from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType

from fa_purity import (
    Cmd,
    FrozenList,
    Maybe,
    Result,
    ResultE,
    Stream,
    cast_exception,
)
from fa_purity.date_time import DatetimeUTC

from fluidattacks_gitlab_sdk.ids import (
    MilestoneFullId,
    MrFullId,
    MrInternalId,
    ProjectId,
)
from fluidattacks_gitlab_sdk.users.core import UserObj

PerPage = NewType("PerPage", int)


class MergeRequestState(Enum):
    # locked: transitional state while a merge is happening
    OPENED = "opened"
    CLOSED = "closed"
    LOCKED = "locked"
    MERGED = "merged"

    @staticmethod
    def from_raw(raw: str) -> ResultE[MergeRequestState]:
        try:
            return Result.success(MergeRequestState(raw))
        except ValueError as err:
            return Result.failure(cast_exception(err))


@dataclass(frozen=True)
class MergeRequestSha:
    sha: Maybe[str]
    merge_commit_sha: Maybe[str]
    squash_commit_sha: Maybe[str]


@dataclass(frozen=True)
class MergeRequestDates:
    created_at: DatetimeUTC
    prepared_at: Maybe[DatetimeUTC]
    updated_at: Maybe[DatetimeUTC]
    merged_at: Maybe[DatetimeUTC]
    closed_at: Maybe[DatetimeUTC]


@dataclass(frozen=True)
class MergeRequestPeople:
    author: UserObj
    merge_user: Maybe[UserObj]
    closed_by: Maybe[UserObj]
    assignees: FrozenList[UserObj]
    reviewers: FrozenList[UserObj]


@dataclass(frozen=True)
class MergeRequestFullState:
    state: MergeRequestState
    detailed_merge_status: str
    has_conflicts: bool
    user_notes_count: int
    merge_error: Maybe[str]


@dataclass(frozen=True)
class MergeRequestProperties:
    title: str
    description: Maybe[str]
    draft: bool
    squash: bool
    imported: bool
    imported_from: str
    first_contribution: bool
    labels: FrozenList[str]
    merge_after: Maybe[DatetimeUTC]
    web_url: str


@dataclass(frozen=True)
class MergeRequestOrigins:
    source_project_id: ProjectId
    source_branch: str
    target_project_id: ProjectId
    target_branch: str


@dataclass(frozen=True)
class TaskCompletion:
    count: int
    completed_count: int


@dataclass(frozen=True)
class MergeRequest:
    shas: MergeRequestSha
    dates: MergeRequestDates
    people: MergeRequestPeople
    full_state: MergeRequestFullState
    properties: MergeRequestProperties
    origins: MergeRequestOrigins
    milestone: Maybe[MilestoneFullId]
    task_completion: TaskCompletion


@dataclass(frozen=True)
class MrsClient:
    get_mr: Callable[
        [ProjectId, MrInternalId],
        Cmd[ResultE[tuple[MrFullId, MergeRequest]]],
    ]
    most_recent_mr: Callable[
        [ProjectId],
        Cmd[ResultE[Maybe[tuple[MrFullId, MergeRequest]]]],
    ]
    most_recent_mr_until: Callable[
        [ProjectId, DatetimeUTC],
        Cmd[ResultE[Maybe[tuple[MrFullId, MergeRequest]]]],
    ]
    get_mr_updated: Callable[
        [ProjectId, datetime, datetime, PerPage],
        Cmd[Stream[FrozenList[tuple[MrFullId, MergeRequest]]]],
    ]

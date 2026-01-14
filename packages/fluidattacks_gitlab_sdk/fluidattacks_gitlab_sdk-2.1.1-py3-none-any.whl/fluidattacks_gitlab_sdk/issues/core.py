from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from enum import (
    Enum,
)

from fa_purity import Cmd, Coproduct, FrozenList, Maybe, Result, ResultE
from fa_purity.date_time import DatetimeUTC

from fluidattacks_gitlab_sdk._handlers import NotFound
from fluidattacks_gitlab_sdk.ids import (
    EpicFullId,
    IssueFullId,
    IssueInternalId,
    MilestoneFullId,
    ProjectId,
    ProjectPath,
)
from fluidattacks_gitlab_sdk.users.core import UserObj


class IssueType(Enum):
    ISSUE = "issue"
    INCIDENT = "incident"
    TASK = "task"
    TEST_CASE = "test_case"
    REQUIREMENT = "requirement"


@dataclass(frozen=True)
class IssueCounts:
    up_votes: int
    down_votes: int
    merge_requests_count: int


@dataclass(frozen=True)
class IssueDates:
    created_at: DatetimeUTC
    updated_at: Maybe[DatetimeUTC]
    closed_at: Maybe[DatetimeUTC]
    due_date: Maybe[date]


@dataclass(frozen=True)
class IssueOtherProperties:
    confidential: bool
    discussion_locked: Maybe[bool]
    labels: FrozenList[str]
    health_status: Maybe[str]
    weight: Maybe[int]


@dataclass(frozen=True)
class IssueReferences:
    author: UserObj
    milestone: Maybe[MilestoneFullId]
    epic: Maybe[EpicFullId]
    closed_by: Maybe[UserObj]
    assignees: FrozenList[UserObj]
    updated_by: Maybe[UserObj]


@dataclass(frozen=True)
class IssueDef:
    title: str
    state: str
    issue_type: IssueType
    description: Maybe[str]


@dataclass(frozen=True)
class Issue:
    definition: IssueDef
    references: IssueReferences
    properties: IssueOtherProperties
    dates: IssueDates
    stats: IssueCounts


@dataclass(frozen=True)
class ProjectIdObj:
    project_id: ProjectId
    project_path: ProjectPath


@dataclass(frozen=True)
class IssueClient:
    get_issue: Callable[
        [ProjectIdObj, IssueInternalId],
        Cmd[Result[tuple[IssueFullId, Issue], Coproduct[NotFound, Exception]]],
    ]
    most_recent_issue: Callable[
        [ProjectIdObj],
        Cmd[ResultE[Maybe[tuple[IssueFullId, Issue]]]],
    ]

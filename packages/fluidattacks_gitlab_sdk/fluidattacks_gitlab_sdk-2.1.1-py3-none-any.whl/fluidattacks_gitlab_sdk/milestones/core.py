from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from fa_purity import Cmd, Coproduct, Maybe, Result, ResultE
from fa_purity.date_time import DatetimeUTC

from fluidattacks_gitlab_sdk._handlers import NotFound
from fluidattacks_gitlab_sdk.ids import MilestoneFullId, MilestoneInternalId, ProjectId


@dataclass(frozen=True)
class Milestone:
    title: str
    description: str
    state: str
    expired: bool
    dates: MilestoneDates


@dataclass(frozen=True)
class MilestoneDates:
    create_at: DatetimeUTC
    update_at: Maybe[DatetimeUTC]
    due_date: Maybe[date]
    start_date: Maybe[date]


@dataclass(frozen=True)
class MilestoneClient:
    get_milestone: Callable[
        [ProjectId, MilestoneInternalId],
        Cmd[Result[tuple[MilestoneFullId, Milestone], Coproduct[NotFound, Exception]]],
    ]
    most_recent_milestone: Callable[
        [ProjectId],
        Cmd[ResultE[Maybe[tuple[MilestoneFullId, Milestone]]]],
    ]

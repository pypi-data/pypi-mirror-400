from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from fa_purity import Cmd, Coproduct, FrozenList, Maybe, Result, ResultE
from fa_purity.date_time import DatetimeUTC

from fluidattacks_gitlab_sdk._handlers import NotFound
from fluidattacks_gitlab_sdk.ids import JobId, ProjectId, RunnerId, UserId


@dataclass(frozen=True)
class CommitHash:
    hash_str: str


@dataclass(frozen=True)
class Commit:
    sha_commit: Maybe[CommitHash]
    title_commit: Maybe[str]


@dataclass(frozen=True)
class JobDates:
    created_at: DatetimeUTC
    started_at: Maybe[DatetimeUTC]
    finished_at: Maybe[DatetimeUTC]


@dataclass(frozen=True)
class JobConf:
    allow_failure: bool
    tag_list: FrozenList[str]
    ref_branch: str
    stage: str


class JobStatus(Enum):
    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    SUCCESS = "success"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    WAITING_FOR_RESOURCE = "waiting_for_resource"
    MANUAL = "manual"

    @staticmethod
    def from_raw(raw: str) -> ResultE[JobStatus]:
        try:
            return Result.success(JobStatus(raw))
        except ValueError as err:
            return Result.failure(Exception(err))


@dataclass(frozen=True)
class JobResultStatus:
    status: str
    failure_reason: Maybe[str]
    duration: Maybe[Decimal]
    queued_duration: Maybe[Decimal]


@dataclass(frozen=True)
class Job:
    name: str
    user_id: Maybe[UserId]
    runner_id: Maybe[RunnerId]
    coverage: Maybe[float]
    commit: Commit
    dates: JobDates
    conf: JobConf
    result: JobResultStatus


@dataclass(frozen=True)
class JobObj:
    job_id: JobId
    obj: Job


@dataclass(frozen=True)
class JobClient:
    get_job: Callable[[ProjectId, JobId], Cmd[Result[JobObj, Coproduct[NotFound, Exception]]]]


__all__ = [
    "JobId",
]

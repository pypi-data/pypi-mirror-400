from __future__ import annotations

from dataclasses import dataclass

from fa_purity import Coproduct
from fluidattacks_etl_utils.natural import Natural


@dataclass(frozen=True)
class ProjectId:
    """Represents a global project id."""

    project_id: Natural


@dataclass(frozen=True)
class ProjectPath:
    """Represents a project path."""

    path: str


@dataclass(frozen=True)
class GroupId:
    """Represents a global group id."""

    group_id: Natural


@dataclass(frozen=True)
class UserId:
    """Represents an user id."""

    user_id: Natural


@dataclass(frozen=True)
class MilestoneGlobalId:
    """Represents an milestone global id."""

    global_id: Natural


@dataclass(frozen=True)
class MilestoneInternalId:
    """Represents an milestone internal id."""

    internal: Natural


@dataclass(frozen=True)
class MilestoneFullInternalId:
    parent: Coproduct[ProjectId, GroupId]
    internal: MilestoneInternalId


@dataclass(frozen=True)
class MilestoneFullId:
    global_id: MilestoneGlobalId
    internal_id: MilestoneFullInternalId


@dataclass(frozen=True)
class MrGlobalId:
    """Represents an MR global id."""

    global_id: Natural


@dataclass(frozen=True)
class MrInternalId:
    """Represents an MR internal id."""

    internal: Natural


@dataclass(frozen=True)
class MrFullInternalId:
    project: ProjectId
    internal: MrInternalId


@dataclass(frozen=True)
class MrFullId:
    global_id: MrGlobalId
    internal_id: MrFullInternalId


@dataclass(frozen=True)
class MemberId:
    member_id: Natural


@dataclass(frozen=True)
class EpicGlobalId:
    global_id: Natural


@dataclass(frozen=True)
class EpicInternalId:
    internal_id: Natural


@dataclass(frozen=True)
class EpicFullInternalId:
    group: GroupId
    internal_id: EpicInternalId


@dataclass(frozen=True)
class EpicFullId:
    global_id: EpicGlobalId
    internal_id: EpicFullInternalId


@dataclass(frozen=True)
class IssueGlobalId:
    global_id: Natural


@dataclass(frozen=True)
class IssueInternalId:
    internal_id: Natural


@dataclass(frozen=True)
class IssueFullInternalId:
    project: ProjectId
    internal_id: IssueInternalId


@dataclass(frozen=True)
class IssueFullId:
    global_id: IssueGlobalId
    internal_id: IssueFullInternalId


@dataclass(frozen=True)
class JobId:
    job_id: Natural


@dataclass(frozen=True)
class RunnerId:
    runner_id: Natural

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from fa_purity import Cmd, FrozenList, ResultE

from fluidattacks_gitlab_sdk.ids import MemberId, ProjectId


@dataclass(frozen=True)
class Member:
    member_user_name: str
    member_name: str
    id_project: ProjectId


@dataclass(frozen=True)
class MemberClient:
    get_members: Callable[
        [ProjectId],
        Cmd[ResultE[FrozenList[tuple[MemberId, Member]]]],
    ]

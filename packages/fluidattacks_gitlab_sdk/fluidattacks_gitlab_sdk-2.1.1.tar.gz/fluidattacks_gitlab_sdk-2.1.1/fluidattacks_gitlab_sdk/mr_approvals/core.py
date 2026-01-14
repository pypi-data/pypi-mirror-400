from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from fa_purity import Cmd, FrozenList, ResultE

from fluidattacks_gitlab_sdk.ids import MrFullId, MrInternalId, ProjectId
from fluidattacks_gitlab_sdk.users import UserObj


@dataclass(frozen=True)
class Approver:
    user: UserObj


@dataclass(frozen=True)
class MrApprovals:
    approved: bool
    approved_by: FrozenList[Approver]


@dataclass
class ApprovalsClient:
    get_approvals: Callable[[ProjectId, MrInternalId], Cmd[ResultE[tuple[MrFullId, MrApprovals]]]]

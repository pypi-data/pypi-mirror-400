from pathlib import Path

from fa_purity import FrozenList, Unsafe
from fa_purity.json import JsonValueFactory, Unfolder
from fluidattacks_etl_utils.natural import NaturalOperations

from fluidattacks_gitlab_sdk.ids import (
    MrFullId,
    MrFullInternalId,
    MrGlobalId,
    MrInternalId,
    ProjectId,
    UserId,
)
from fluidattacks_gitlab_sdk.mr_approvals._decode import decode_id_and_mr_approvals
from fluidattacks_gitlab_sdk.mr_approvals.core import Approver, MrApprovals
from fluidattacks_gitlab_sdk.users.core import User, UserName, UserObj


def test_decode() -> None:
    mr_ids = MrFullId(
        MrGlobalId(NaturalOperations.absolute(345678912)),
        MrFullInternalId(
            ProjectId(NaturalOperations.absolute(20742211)),
            MrInternalId(NaturalOperations.absolute(78456)),
        ),
    )
    users_approver: FrozenList[Approver] = (
        Approver(
            UserObj(
                UserId(NaturalOperations.absolute(26904760)),
                User("useratfluid"),
                UserName("User Fluid"),
            ),
        ),
        Approver(
            UserObj(
                UserId(NaturalOperations.absolute(34547217)),
                User("project_20741933_bot_7328383692d798602683c341e690"),
                UserName("****"),
            ),
        ),
    )
    mr_approvers = MrApprovals(
        True,
        users_approver,
    )
    expected = (
        mr_ids,
        mr_approvers,
    )

    raw_data_path = Path(__file__).parent / "data.json"
    raw_data = (
        JsonValueFactory.load(raw_data_path.open(encoding="utf-8"))
        .bind(Unfolder.to_json)
        .alt(Unsafe.raise_exception)
        .to_union()
    )
    decoded_mr_approvals = (
        decode_id_and_mr_approvals(raw_data).alt(Unsafe.raise_exception).to_union()
    )
    assert decoded_mr_approvals == expected

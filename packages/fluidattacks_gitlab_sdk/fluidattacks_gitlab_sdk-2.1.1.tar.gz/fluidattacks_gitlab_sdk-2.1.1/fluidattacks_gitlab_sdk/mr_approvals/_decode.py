from fa_purity import ResultE
from fa_purity.json import JsonObj, JsonUnfolder, Unfolder
from fluidattacks_etl_utils import smash
from fluidattacks_etl_utils.decode import DecodeUtils

from fluidattacks_gitlab_sdk._decoders import decode_mr_full_id
from fluidattacks_gitlab_sdk.ids import MrFullId
from fluidattacks_gitlab_sdk.mr_approvals.core import Approver, MrApprovals
from fluidattacks_gitlab_sdk.users.decode import decode_user_obj


def decode_mr_approvals(raw: JsonObj) -> ResultE[MrApprovals]:
    return smash.smash_result_2(
        JsonUnfolder.require(raw, "approved", DecodeUtils.to_bool),
        JsonUnfolder.require(
            raw,
            "approved_by",
            lambda v: Unfolder.to_list_of(
                v,
                lambda x: Unfolder.to_json(x)
                .bind(lambda user_obj: JsonUnfolder.require(user_obj, "user", Unfolder.to_json))
                .bind(decode_user_obj)
                .map(lambda u: Approver(u)),
            ).map(lambda approvers: tuple(approvers)),
        ),
    ).map(lambda v: MrApprovals(v[0], v[1]))


def decode_id_and_mr_approvals(raw: JsonObj) -> ResultE[tuple[MrFullId, MrApprovals]]:
    return smash.smash_result_2(decode_mr_full_id(raw), decode_mr_approvals(raw))

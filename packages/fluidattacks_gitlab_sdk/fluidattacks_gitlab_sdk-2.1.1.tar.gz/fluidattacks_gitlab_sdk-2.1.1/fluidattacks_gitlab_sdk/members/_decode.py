import logging

from fa_purity import FrozenList, PureIterFactory, Result, ResultE, ResultTransform
from fa_purity.json import JsonObj, JsonUnfolder
from fluidattacks_etl_utils import smash
from fluidattacks_etl_utils.decode import DecodeUtils
from fluidattacks_etl_utils.natural import Natural

from fluidattacks_gitlab_sdk.ids import MemberId, ProjectId
from fluidattacks_gitlab_sdk.members.core import Member

LOG = logging.getLogger(__name__)


def decode_member(raw: JsonObj, id_project: ProjectId) -> ResultE[Member]:
    return smash.smash_result_2(
        JsonUnfolder.require(raw, "username", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "name", DecodeUtils.to_str),
    ).map(lambda m: Member(m[0], m[1], id_project))


def decode_member_and_id(raw: JsonObj, id_project: ProjectId) -> ResultE[tuple[MemberId, Member]]:
    return smash.smash_result_2(
        JsonUnfolder.require(raw, "id", DecodeUtils.to_int).bind(Natural.from_int).map(MemberId),
        decode_member(raw, id_project),
    )


def decode_members(
    members: FrozenList[JsonObj],
    id_project: ProjectId,
) -> ResultE[FrozenList[tuple[MemberId, Member]]]:
    if not members:
        return Result.failure(ValueError("Expected a list of members"))

    return ResultTransform.all_ok(
        PureIterFactory.from_list(members)
        .map(lambda c: decode_member_and_id(c, id_project))
        .to_list(),
    )

import inspect
import logging

from fa_purity import FrozenList, Maybe, Result, ResultE
from fa_purity.json import JsonObj, JsonUnfolder
from fluidattacks_etl_utils import smash
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import DecodeUtils

from fluidattacks_gitlab_sdk._decoders import (
    decode_date,
    decode_milestone_full_id,
)
from fluidattacks_gitlab_sdk.ids import MilestoneFullId
from fluidattacks_gitlab_sdk.milestones.core import Milestone, MilestoneDates

LOG = logging.getLogger(__name__)


def decode_milestone_dates(raw: JsonObj) -> ResultE[MilestoneDates]:
    return smash.smash_result_4(
        JsonUnfolder.require(raw, "created_at", DecodeUtils.to_date_time),
        JsonUnfolder.optional(raw, "updated_at", DecodeUtils.to_opt_date_time).map(
            lambda v: v.bind(lambda j: j),
        ),
        JsonUnfolder.optional(
            raw,
            "due_date",
            lambda v: DecodeUtils.to_maybe(v, lambda i: DecodeUtils.to_str(i).bind(decode_date)),
        ).map(lambda m: m.bind(lambda x: x)),
        JsonUnfolder.optional(
            raw,
            "start_date",
            lambda v: DecodeUtils.to_maybe(v, lambda i: DecodeUtils.to_str(i).bind(decode_date)),
        ).map(lambda m: m.bind(lambda x: x)),
    ).map(lambda v: MilestoneDates(*v))


def decode_milestone(raw: JsonObj) -> ResultE[Milestone]:
    dates = decode_milestone_dates(raw)
    group = smash.smash_result_4(
        JsonUnfolder.require(raw, "title", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "description", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "state", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "expired", DecodeUtils.to_bool),
    )
    return (
        smash.smash_result_2(
            group,
            dates,
        )
        .map(
            lambda v: Milestone(
                *v[0],
                v[1],
            ),
        )
        .alt(
            lambda e: Bug.new(
                "decode_mr",
                inspect.currentframe(),
                e,
                (JsonUnfolder.dumps(raw),),
            ),
        )
    )


def decode_milestone_and_id(
    raw: FrozenList[JsonObj],
) -> ResultE[Maybe[tuple[MilestoneFullId, Milestone]]]:
    if not raw:
        return Result.success(Maybe.empty())

    return smash.smash_result_2(
        decode_milestone_full_id(raw[0]),
        decode_milestone(raw[0]),
    ).map(Maybe.some)

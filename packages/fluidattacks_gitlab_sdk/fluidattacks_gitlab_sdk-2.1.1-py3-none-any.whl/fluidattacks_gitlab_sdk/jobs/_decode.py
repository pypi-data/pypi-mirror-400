import logging
from datetime import datetime
from decimal import Decimal

from dateutil.parser import (
    isoparse,
)
from fa_purity import (
    FrozenDict,
    FrozenList,
    Maybe,
    Result,
    ResultE,
    ResultSmash,
)
from fa_purity.json import JsonObj, JsonPrimitiveUnfolder, JsonUnfolder, JsonValue, Unfolder
from fluidattacks_etl_utils import smash
from fluidattacks_etl_utils.decode import DecodeUtils
from fluidattacks_etl_utils.natural import Natural, NaturalOperations

from fluidattacks_gitlab_sdk.ids import JobId, RunnerId, UserId

from .core import Commit, CommitHash, Job, JobConf, JobDates, JobObj, JobResultStatus

LOG = logging.getLogger(__name__)


def _decoder_require_list(item: JsonValue) -> ResultE[FrozenList[str]]:
    return Unfolder.to_list_of(
        item,
        lambda v: Unfolder.to_primitive(v).bind(
            lambda p: JsonPrimitiveUnfolder.to_str(p),
        ),
    )


def get_float(number: JsonValue) -> ResultE[float]:
    return Unfolder.to_primitive(number).bind(lambda v: JsonPrimitiveUnfolder.to_float(v))


def str_to_datetime(raw: str) -> ResultE[datetime]:
    try:
        return Result.success(isoparse(raw))
    except ValueError as err:
        return Result.failure(Exception(err))


def decode_str(value: JsonValue) -> ResultE[str]:
    return Unfolder.to_primitive(value).bind(lambda p: JsonPrimitiveUnfolder.to_str(p))


def decode_datetime(value: JsonValue) -> ResultE[datetime]:
    return decode_str(value).bind(str_to_datetime)


def decode_job_id(raw: JsonObj) -> ResultE[JobId]:
    return JsonUnfolder.require(raw, "id", DecodeUtils.to_int).bind(Natural.from_int).map(JobId)


def decode_user_id(raw: JsonObj) -> ResultE[Maybe[UserId]]:
    def decode_maybe_id(raw: JsonObj) -> ResultE[Maybe[UserId]]:
        return JsonUnfolder.optional(
            raw,
            "id",
            lambda v: Unfolder.to_primitive(v)
            .bind(JsonPrimitiveUnfolder.to_int)
            .map(lambda j: UserId(NaturalOperations.absolute(j))),
        )

    maybe_user_obj = JsonUnfolder.optional(raw, "user", lambda v: Unfolder.to_json(v))
    return maybe_user_obj.bind(lambda v: decode_maybe_id(v.value_or(FrozenDict({}))))


def decode_runner_id(raw: JsonObj) -> ResultE[Maybe[RunnerId]]:
    def decode_maybe_id(raw: JsonObj) -> ResultE[Maybe[RunnerId]]:
        return JsonUnfolder.optional(
            raw,
            "id",
            lambda v: Unfolder.to_primitive(v)
            .bind(JsonPrimitiveUnfolder.to_int)
            .map(lambda j: RunnerId(NaturalOperations.absolute(j))),
        )

    maybe_runner_obj = JsonUnfolder.optional(raw, "runner", lambda v: Unfolder.to_json(v))
    return maybe_runner_obj.bind(lambda v: decode_maybe_id(v.value_or(FrozenDict({}))))


def decode_commit_properties(raw: JsonObj) -> ResultE[Commit]:
    sha_commit = JsonUnfolder.optional(raw, "id", DecodeUtils.to_opt_str).map(
        lambda v: v.bind(lambda j: j.map(lambda p: CommitHash(p))),
    )
    title = JsonUnfolder.optional(raw, "title", DecodeUtils.to_opt_str).map(
        lambda v: v.bind(lambda j: j),
    )
    return ResultSmash.smash_result_2(sha_commit, title).map(lambda v: Commit(*v))


def decode_commit(raw: JsonObj) -> ResultE[Commit]:
    maybe_commit_obj = JsonUnfolder.optional(raw, "commit", lambda v: Unfolder.to_json(v))
    return maybe_commit_obj.bind(lambda v: decode_commit_properties(v.value_or(FrozenDict({}))))


def decode_job_dates(raw: JsonObj) -> ResultE[JobDates]:
    created_at = JsonUnfolder.require(raw, "created_at", DecodeUtils.to_date_time)
    started_at = JsonUnfolder.optional(raw, "started_at", DecodeUtils.to_opt_date_time).map(
        lambda m: m.bind(lambda x: x),
    )
    finished_at = JsonUnfolder.optional(raw, "finished_at", DecodeUtils.to_opt_date_time).map(
        lambda m: m.bind(lambda x: x),
    )
    return ResultSmash.smash_result_3(created_at, started_at, finished_at).map(
        lambda t: JobDates(*t),
    )


def decode_job_conf(raw: JsonObj) -> ResultE[JobConf]:
    return smash.smash_result_4(
        JsonUnfolder.require(raw, "allow_failure", DecodeUtils.to_bool),
        JsonUnfolder.require(raw, "tag_list", _decoder_require_list),
        JsonUnfolder.require(raw, "ref", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "stage", DecodeUtils.to_str),
    ).map(lambda v: JobConf(*v))


def decode_job_result(raw: JsonObj) -> ResultE[JobResultStatus]:
    return smash.smash_result_4(
        JsonUnfolder.require(raw, "status", DecodeUtils.to_str),
        JsonUnfolder.optional(raw, "failure_reason", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda j: j),
        ),
        JsonUnfolder.optional(raw, "duration", lambda v: get_float(v).map(Decimal)),
        JsonUnfolder.optional(raw, "queued_duration", lambda v: get_float(v).map(Decimal)),
    ).map(lambda v: JobResultStatus(*v))


def decode_job(raw: JsonObj) -> ResultE[Job]:
    first = smash.smash_result_5(
        JsonUnfolder.require(raw, "name", DecodeUtils.to_str),
        decode_user_id(raw),
        decode_runner_id(raw),
        JsonUnfolder.optional(raw, "coverage", get_float),
        decode_commit(raw),
    )
    second = smash.smash_result_3(
        decode_job_dates(raw),
        decode_job_conf(raw),
        decode_job_result(raw),
    )

    return smash.smash_result_2(first, second).map(lambda v: Job(*v[0], *v[1]))


def decode_job_obj(raw: JsonObj) -> ResultE[JobObj]:
    id_job = JsonUnfolder.require(raw, "id", DecodeUtils.to_int).map(
        lambda v: JobId(NaturalOperations.absolute(v)),
    )
    return smash.smash_result_2(id_job, decode_job(raw)).map(lambda v: JobObj(*v))

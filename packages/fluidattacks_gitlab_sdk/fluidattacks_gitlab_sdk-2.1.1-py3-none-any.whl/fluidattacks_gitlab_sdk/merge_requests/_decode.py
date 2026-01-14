import inspect

from fa_purity import Maybe, PureIterFactory, Result, ResultE, ResultTransform
from fa_purity._core.frozen import FrozenList
from fa_purity.json import JsonObj, JsonUnfolder, Unfolder
from fluidattacks_etl_utils import smash
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import DecodeUtils
from fluidattacks_etl_utils.natural import Natural

from fluidattacks_gitlab_sdk._decoders import (
    decode_milestone_full_id,
    decode_mr_full_id,
)
from fluidattacks_gitlab_sdk.ids import (
    MrFullId,
    ProjectId,
    UserId,
)
from fluidattacks_gitlab_sdk.merge_requests.core import (
    MergeRequest,
    MergeRequestDates,
    MergeRequestFullState,
    MergeRequestOrigins,
    MergeRequestPeople,
    MergeRequestProperties,
    MergeRequestSha,
    MergeRequestState,
    TaskCompletion,
)
from fluidattacks_gitlab_sdk.users.decode import decode_user_obj


def decode_sha(raw: JsonObj) -> ResultE[MergeRequestSha]:
    return smash.smash_result_3(
        JsonUnfolder.require(raw, "sha", DecodeUtils.to_opt_str),
        JsonUnfolder.optional(raw, "merge_commit_sha", DecodeUtils.to_opt_str).map(
            lambda m: m.bind(lambda x: x),
        ),
        JsonUnfolder.optional(raw, "squash_commit_sha", DecodeUtils.to_opt_str).map(
            lambda m: m.bind(lambda x: x),
        ),
    ).map(lambda t: MergeRequestSha(*t))


def decode_dates(raw: JsonObj) -> ResultE[MergeRequestDates]:
    return smash.smash_result_5(
        JsonUnfolder.require(raw, "created_at", DecodeUtils.to_date_time),
        JsonUnfolder.optional(raw, "prepared_at", DecodeUtils.to_opt_date_time).map(
            lambda m: m.bind(lambda x: x),
        ),
        JsonUnfolder.optional(raw, "updated_at", DecodeUtils.to_opt_date_time).map(
            lambda m: m.bind(lambda x: x),
        ),
        JsonUnfolder.optional(raw, "merged_at", DecodeUtils.to_opt_date_time).map(
            lambda m: m.bind(lambda x: x),
        ),
        JsonUnfolder.optional(raw, "closed_at", DecodeUtils.to_opt_date_time).map(
            lambda m: m.bind(lambda x: x),
        ),
    ).map(lambda t: MergeRequestDates(*t))


def decode_user_id(raw: JsonObj) -> ResultE[UserId]:
    return JsonUnfolder.require(raw, "id", DecodeUtils.to_int).bind(Natural.from_int).map(UserId)


def decode_people(raw: JsonObj) -> ResultE[MergeRequestPeople]:
    return smash.smash_result_5(
        JsonUnfolder.require(
            raw,
            "author",
            lambda v: Unfolder.to_json(v).bind(decode_user_obj),
        ),
        JsonUnfolder.optional(
            raw,
            "merge_user",
            lambda v: Unfolder.to_optional(
                v,
                lambda v: Unfolder.to_json(v).bind(decode_user_obj),
            ),
        ).map(lambda m: m.bind(lambda x: Maybe.from_optional(x))),
        JsonUnfolder.optional(
            raw,
            "closed_by",
            lambda v: Unfolder.to_optional(
                v,
                lambda v: Unfolder.to_json(v).bind(decode_user_obj),
            ),
        ).map(lambda m: m.bind(lambda x: Maybe.from_optional(x))),
        JsonUnfolder.require(
            raw,
            "assignees",
            lambda v: Unfolder.to_list_of(
                v,
                lambda v: Unfolder.to_json(v).bind(decode_user_obj),
            ),
        ),
        JsonUnfolder.require(
            raw,
            "reviewers",
            lambda v: Unfolder.to_list_of(
                v,
                lambda v: Unfolder.to_json(v).bind(decode_user_obj),
            ),
        ),
    ).map(lambda t: MergeRequestPeople(*t))


def decode_state(raw: JsonObj) -> ResultE[MergeRequestFullState]:
    return smash.smash_result_5(
        JsonUnfolder.require(raw, "state", DecodeUtils.to_str).bind(
            MergeRequestState.from_raw,
        ),
        JsonUnfolder.require(raw, "detailed_merge_status", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "has_conflicts", DecodeUtils.to_bool),
        JsonUnfolder.require(raw, "user_notes_count", DecodeUtils.to_int),
        JsonUnfolder.optional(raw, "merge_error", DecodeUtils.to_opt_str).map(
            lambda m: m.bind(lambda x: x),
        ),
    ).map(lambda t: MergeRequestFullState(*t))


def decode_properties(raw: JsonObj) -> ResultE[MergeRequestProperties]:
    group_1 = smash.smash_result_5(
        JsonUnfolder.require(raw, "title", DecodeUtils.to_str),
        JsonUnfolder.optional(raw, "description", DecodeUtils.to_opt_str).map(
            lambda m: m.bind(lambda x: x),
        ),
        JsonUnfolder.require(raw, "draft", DecodeUtils.to_bool),
        JsonUnfolder.require(raw, "squash", DecodeUtils.to_bool),
        JsonUnfolder.require(raw, "imported", DecodeUtils.to_bool),
    )
    group_2 = smash.smash_result_5(
        JsonUnfolder.require(raw, "imported_from", DecodeUtils.to_str),
        JsonUnfolder.optional(raw, "first_contribution", DecodeUtils.to_bool).map(
            lambda m: m.value_or(False),
        ),
        JsonUnfolder.require(
            raw,
            "labels",
            lambda v: Unfolder.to_list_of(v, DecodeUtils.to_str),
        ),
        JsonUnfolder.optional(raw, "merge_after", DecodeUtils.to_opt_date_time).map(
            lambda m: m.bind(lambda x: x),
        ),
        JsonUnfolder.require(raw, "web_url", DecodeUtils.to_str),
    )
    return smash.smash_result_2(group_1, group_2).map(
        lambda g: MergeRequestProperties(*g[0], *g[1]),
    )


def decode_origins(raw: JsonObj) -> ResultE[MergeRequestOrigins]:
    return smash.smash_result_4(
        JsonUnfolder.require(raw, "source_project_id", DecodeUtils.to_int)
        .bind(Natural.from_int)
        .map(
            ProjectId,
        ),
        JsonUnfolder.require(raw, "source_branch", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "target_project_id", DecodeUtils.to_int)
        .bind(Natural.from_int)
        .map(
            ProjectId,
        ),
        JsonUnfolder.require(raw, "target_branch", DecodeUtils.to_str),
    ).map(lambda t: MergeRequestOrigins(*t))


def decode_completion(raw: JsonObj) -> ResultE[TaskCompletion]:
    return JsonUnfolder.require(
        raw,
        "task_completion_status",
        lambda v: Unfolder.to_json(v).bind(
            lambda raw: smash.smash_result_2(
                JsonUnfolder.require(raw, "count", DecodeUtils.to_int),
                JsonUnfolder.require(raw, "completed_count", DecodeUtils.to_int),
            ).map(lambda t: TaskCompletion(*t)),
        ),
    )


def decode_mr(raw: JsonObj) -> ResultE[MergeRequest]:
    group_1 = smash.smash_result_5(
        decode_sha(raw),
        decode_dates(raw),
        decode_people(raw),
        decode_state(raw),
        decode_properties(raw),
    )
    group_2 = smash.smash_result_3(
        decode_origins(raw),
        JsonUnfolder.require(
            raw,
            "milestone",
            lambda v: DecodeUtils.to_maybe(
                v,
                lambda v: Unfolder.to_json(v).bind(decode_milestone_full_id),
            ),
        ),
        decode_completion(raw),
    )
    return (
        smash.smash_result_2(group_1, group_2)
        .map(
            lambda g: MergeRequest(*g[0], *g[1]),
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


def decode_mr_and_id(raw: JsonObj) -> ResultE[tuple[MrFullId, MergeRequest]]:
    return smash.smash_result_2(
        decode_mr_full_id(raw),
        decode_mr(raw),
    )


def decode_batch_mrs(
    mrs: FrozenList[JsonObj],
) -> ResultE[FrozenList[tuple[MrFullId, MergeRequest]]]:
    if not mrs:
        return Result.success(FrozenList[tuple[MrFullId, MergeRequest]]([]), Exception)
    return ResultTransform.all_ok(
        PureIterFactory.from_list(mrs).map(lambda v: decode_mr_and_id(v)).to_list(),
    )

import inspect

from fa_purity import Maybe, ResultE
from fa_purity.json import JsonObj, JsonPrimitiveUnfolder, JsonUnfolder, JsonValue, Unfolder
from fluidattacks_etl_utils import smash
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import DecodeUtils

from fluidattacks_gitlab_sdk import _handlers
from fluidattacks_gitlab_sdk._decoders import (
    decode_date,
    decode_epic_full_id,
    decode_issue_full_id,
    decode_milestone_full_id,
)
from fluidattacks_gitlab_sdk.ids import (
    IssueFullId,
)
from fluidattacks_gitlab_sdk.issues.core import (
    Issue,
    IssueCounts,
    IssueDates,
    IssueDef,
    IssueOtherProperties,
    IssueReferences,
    IssueType,
)
from fluidattacks_gitlab_sdk.users.core import UserObj
from fluidattacks_gitlab_sdk.users.decode import decode_user_obj


def decode_type(raw: JsonValue) -> ResultE[IssueType]:
    return Unfolder.to_primitive(raw).bind(
        lambda p: JsonPrimitiveUnfolder.to_str(p).bind(
            lambda r: _handlers.handle_value_error(lambda: IssueType(r)),
        ),
    )


def _decode_stats(raw: JsonObj) -> ResultE[IssueCounts]:
    return smash.smash_result_3(
        JsonUnfolder.require(raw, "upvotes", DecodeUtils.to_int),
        JsonUnfolder.require(raw, "downvotes", DecodeUtils.to_int),
        JsonUnfolder.require(raw, "merge_requests_count", DecodeUtils.to_int),
    ).map(lambda t: IssueCounts(*t))


def _decode_properties(raw: JsonObj) -> ResultE[IssueOtherProperties]:
    return smash.smash_result_5(
        JsonUnfolder.require(raw, "confidential", DecodeUtils.to_bool),
        JsonUnfolder.require(
            raw,
            "discussion_locked",
            lambda v: DecodeUtils.to_maybe(v, DecodeUtils.to_bool),
        ),
        JsonUnfolder.require(raw, "labels", lambda v: Unfolder.to_list_of(v, DecodeUtils.to_str)),
        JsonUnfolder.optional(
            raw,
            "health_status",
            lambda v: DecodeUtils.to_maybe(v, DecodeUtils.to_str),
        ).map(lambda m: m.bind(lambda x: x)),
        JsonUnfolder.optional(
            raw,
            "weight",
            lambda v: DecodeUtils.to_maybe(v, DecodeUtils.to_int),
        ).map(lambda m: m.bind(lambda x: x)),
    ).map(lambda t: IssueOtherProperties(*t))


def _decode_refs(updated_by: Maybe[UserObj], raw: JsonObj) -> ResultE[IssueReferences]:
    return smash.smash_result_5(
        JsonUnfolder.require(raw, "author", lambda v: Unfolder.to_json(v).bind(decode_user_obj)),
        JsonUnfolder.require(
            raw,
            "milestone",
            lambda v: DecodeUtils.to_maybe(
                v,
                lambda v: Unfolder.to_json(v).bind(decode_milestone_full_id),
            ),
        ),
        JsonUnfolder.optional(
            raw,
            "epic",
            lambda v: DecodeUtils.to_maybe(
                v,
                lambda v: Unfolder.to_json(v).bind(decode_epic_full_id),
            ),
        ).map(lambda m: m.bind(lambda x: x)),
        JsonUnfolder.require(
            raw,
            "closed_by",
            lambda v: DecodeUtils.to_maybe(v, lambda v: Unfolder.to_json(v).bind(decode_user_obj)),
        ),
        JsonUnfolder.require(
            raw,
            "assignees",
            lambda v: Unfolder.to_list_of(v, lambda v: Unfolder.to_json(v).bind(decode_user_obj)),
        ),
    ).map(lambda t: IssueReferences(*t, updated_by))


def _decode_def(raw: JsonObj) -> ResultE[IssueDef]:
    return smash.smash_result_4(
        JsonUnfolder.require(raw, "title", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "state", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "issue_type", decode_type),
        JsonUnfolder.require(
            raw,
            "description",
            lambda v: DecodeUtils.to_maybe(v, DecodeUtils.to_str),
        ),
    ).map(lambda t: IssueDef(*t))


def _decode_dates(raw: JsonObj) -> ResultE[IssueDates]:
    return smash.smash_result_4(
        JsonUnfolder.require(raw, "created_at", DecodeUtils.to_date_time),
        JsonUnfolder.require(
            raw,
            "updated_at",
            lambda v: DecodeUtils.to_maybe(v, DecodeUtils.to_date_time),
        ),
        JsonUnfolder.require(
            raw,
            "closed_at",
            lambda v: DecodeUtils.to_maybe(v, DecodeUtils.to_date_time),
        ),
        JsonUnfolder.optional(
            raw,
            "due_date",
            lambda v: DecodeUtils.to_maybe(v, lambda i: DecodeUtils.to_str(i).bind(decode_date)),
        ).map(lambda m: m.bind(lambda x: x)),
    ).map(lambda t: IssueDates(*t))


def decode_issue(updated_by: Maybe[UserObj], raw: JsonObj) -> ResultE[Issue]:
    return (
        smash.smash_result_5(
            _decode_def(raw),
            _decode_refs(updated_by, raw),
            _decode_properties(raw),
            _decode_dates(raw),
            _decode_stats(raw),
        )
        .map(lambda t: Issue(*t))
        .alt(
            lambda e: Bug.new(
                "decode_issue",
                inspect.currentframe(),
                e,
                (JsonUnfolder.dumps(raw),),
            ),
        )
    )


def decode_issue_and_id(
    updated_by: Maybe[UserObj],
    raw: JsonObj,
) -> ResultE[tuple[IssueFullId, Issue]]:
    _id = decode_issue_full_id(raw)
    return smash.smash_result_2(
        _id,
        decode_issue(updated_by, raw),
    )

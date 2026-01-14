from collections.abc import Callable
from datetime import date
from typing import TypeVar

from fa_purity import (
    Bool,
    Coproduct,
    CoproductFactory,
    FrozenList,
    Maybe,
    NewFrozenList,
    Result,
    ResultE,
    ResultSmash,
    ResultTransform,
)
from fa_purity.json import JsonObj, JsonUnfolder
from fluidattacks_etl_utils import smash
from fluidattacks_etl_utils.decode import DecodeUtils
from fluidattacks_etl_utils.natural import Natural

from fluidattacks_gitlab_sdk._handlers import handle_value_error
from fluidattacks_gitlab_sdk.ids import (
    EpicFullId,
    EpicFullInternalId,
    EpicGlobalId,
    EpicInternalId,
    GroupId,
    IssueFullId,
    IssueFullInternalId,
    IssueGlobalId,
    IssueInternalId,
    MilestoneFullId,
    MilestoneFullInternalId,
    MilestoneGlobalId,
    MilestoneInternalId,
    MrFullId,
    MrFullInternalId,
    MrGlobalId,
    MrInternalId,
    ProjectId,
)

_T = TypeVar("_T")


def decode_maybe_single(items: NewFrozenList[_T]) -> Maybe[_T]:
    return Bool.from_primitive(len(items.items) <= 1).map(
        lambda _: ResultTransform.get_index(items, 0).map(Maybe.some).value_or(Maybe.empty()),
        lambda _: Maybe.empty(),
    )


def _decode_internal_id(
    raw: JsonObj,
    iid_transform: Callable[[Natural], _T],
) -> ResultE[tuple[ProjectId, _T]]:
    _project = (
        JsonUnfolder.require(raw, "project_id", DecodeUtils.to_int)
        .bind(Natural.from_int)
        .map(ProjectId)
    )
    return smash.smash_result_2(
        _project,
        JsonUnfolder.require(raw, "iid", DecodeUtils.to_int)
        .bind(Natural.from_int)
        .map(iid_transform),
    )


def _decode_id(
    raw: JsonObj,
) -> ResultE[Natural]:
    return JsonUnfolder.require(raw, "id", DecodeUtils.to_int).bind(Natural.from_int)


def decode_milestone_internal_id(raw: JsonObj) -> ResultE[MilestoneFullInternalId]:
    _decode_project = (
        JsonUnfolder.require(raw, "project_id", DecodeUtils.to_int)
        .bind(Natural.from_int)
        .map(ProjectId)
    )
    _decode_group = (
        JsonUnfolder.require(raw, "group_id", DecodeUtils.to_int)
        .bind(Natural.from_int)
        .map(GroupId)
    )
    _decode_iid = (
        JsonUnfolder.require(raw, "iid", DecodeUtils.to_int)
        .bind(Natural.from_int)
        .map(MilestoneInternalId)
    )
    _union: CoproductFactory[ProjectId, GroupId] = CoproductFactory()
    _project_or_group = _decode_project.map(_union.inl).lash(
        lambda _: _decode_group.map(_union.inr),
    )
    return ResultSmash.smash_result_2(
        _project_or_group,
        _decode_iid,
    ).map(lambda t: MilestoneFullInternalId(*t))


def decode_milestone_full_id(raw: JsonObj) -> ResultE[MilestoneFullId]:
    return smash.smash_result_2(
        _decode_id(raw).map(MilestoneGlobalId),
        decode_milestone_internal_id(raw),
    ).map(lambda t: MilestoneFullId(*t))


def decode_epic_internal_id(raw: JsonObj) -> ResultE[EpicFullInternalId]:
    _decode_group = (
        JsonUnfolder.require(raw, "group_id", DecodeUtils.to_int)
        .bind(Natural.from_int)
        .map(GroupId)
    )
    _decode_iid = (
        JsonUnfolder.require(raw, "iid", DecodeUtils.to_int)
        .bind(Natural.from_int)
        .map(EpicInternalId)
    )
    return ResultSmash.smash_result_2(
        _decode_group,
        _decode_iid,
    ).map(lambda t: EpicFullInternalId(*t))


def decode_epic_full_id(raw: JsonObj) -> ResultE[EpicFullId]:
    return smash.smash_result_2(
        _decode_id(raw).map(EpicGlobalId),
        decode_epic_internal_id(raw),
    ).map(lambda t: EpicFullId(*t))


def decode_mr_internal_id(raw: JsonObj) -> ResultE[MrFullInternalId]:
    return _decode_internal_id(raw, MrInternalId).map(lambda t: MrFullInternalId(*t))


def decode_mr_full_id(raw: JsonObj) -> ResultE[MrFullId]:
    return smash.smash_result_2(_decode_id(raw).map(MrGlobalId), decode_mr_internal_id(raw)).map(
        lambda t: MrFullId(*t),
    )


def decode_issue_internal_id(raw: JsonObj) -> ResultE[IssueFullInternalId]:
    return _decode_internal_id(raw, IssueInternalId).map(lambda t: IssueFullInternalId(*t))


def decode_issue_full_id(raw: JsonObj) -> ResultE[IssueFullId]:
    return smash.smash_result_2(
        _decode_id(raw).map(IssueGlobalId),
        decode_issue_internal_id(raw),
    ).map(lambda t: IssueFullId(*t))


def decode_date(raw: str) -> ResultE[date]:
    return handle_value_error(lambda: date.fromisoformat(raw))


def assert_single(item: Coproduct[JsonObj, FrozenList[JsonObj]]) -> ResultE[JsonObj]:
    return item.map(
        Result.success,
        lambda _: Result.failure(ValueError("Expected a json not a list")),
    )


def assert_multiple(item: Coproduct[JsonObj, FrozenList[JsonObj]]) -> ResultE[FrozenList[JsonObj]]:
    return item.map(
        lambda _: Result.failure(ValueError("Expected a json list not a single json")),
        Result.success,
    )

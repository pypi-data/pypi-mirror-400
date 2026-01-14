from datetime import UTC, datetime
from pathlib import Path

from fa_purity import FrozenList, Maybe, Unsafe
from fa_purity.date_time import DatetimeUTC
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
from fluidattacks_gitlab_sdk.merge_requests._decode import decode_batch_mrs, decode_mr_and_id
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
from fluidattacks_gitlab_sdk.users.core import User, UserName, UserObj


def _assert_utc(date_time: datetime) -> DatetimeUTC:
    return DatetimeUTC.assert_utc(date_time).alt(Unsafe.raise_exception).to_union()


def test_decode() -> None:
    author = UserObj(
        UserId(NaturalOperations.absolute(987654321)),
        User("the_author"),
        UserName("The Author"),
    )
    merger = UserObj(
        UserId(NaturalOperations.absolute(1234567)),
        User("the_merger"),
        UserName("The merger"),
    )
    project = ProjectId(NaturalOperations.absolute(123456789))
    expected = (
        MrFullId(
            MrGlobalId(NaturalOperations.absolute(99887766)),
            MrFullInternalId(project, MrInternalId(NaturalOperations.absolute(333))),
        ),
        MergeRequest(
            MergeRequestSha(
                Maybe.some("a" * 40),
                Maybe.some("b" * 40),
                Maybe.empty(),
            ),
            MergeRequestDates(
                _assert_utc(datetime(2025, 2, 18, 1, 22, 33, tzinfo=UTC)),
                Maybe.some(_assert_utc(datetime(2025, 2, 19, 1, 22, 32, tzinfo=UTC))),
                Maybe.some(_assert_utc(datetime(2025, 2, 19, 1, 22, 33, tzinfo=UTC))),
                Maybe.some(_assert_utc(datetime(2025, 2, 20, 1, 22, 33, tzinfo=UTC))),
                Maybe.empty(),
            ),
            MergeRequestPeople(
                author,
                Maybe.some(merger),
                Maybe.empty(),
                (author,),
                (merger,),
            ),
            MergeRequestFullState(
                MergeRequestState.MERGED,
                "not_open",
                False,
                0,
                Maybe.empty(),
            ),
            MergeRequestProperties(
                "the_commit_title",
                Maybe.some("- Do something\\n- Update something links\\n- Other item"),
                True,
                False,
                True,
                "none",
                False,
                (),
                Maybe.empty(),
                "https://gitlab.com/foo/test-project/-/merge_requests/333",
            ),
            MergeRequestOrigins(
                ProjectId(NaturalOperations.absolute(123456789)),
                "source_branch",
                ProjectId(NaturalOperations.absolute(777)),
                "master",
            ),
            Maybe.empty(),
            TaskCompletion(1, 0),
        ),
    )
    raw_data_path = Path(__file__).parent / "data.json"
    raw_data = (
        JsonValueFactory.load(raw_data_path.open(encoding="utf-8"))
        .bind(Unfolder.to_json)
        .alt(Unsafe.raise_exception)
        .to_union()
    )
    decoded_mr = decode_mr_and_id(raw_data).alt(Unsafe.raise_exception).to_union()
    assert decoded_mr == expected


def test_decode_mrs_updated() -> None:
    author = UserObj(
        UserId(NaturalOperations.absolute(987654321)),
        User("the_author"),
        UserName("The Author"),
    )
    merger = UserObj(
        UserId(NaturalOperations.absolute(1234567)),
        User("the_merger"),
        UserName("The merger"),
    )
    project = ProjectId(NaturalOperations.absolute(123456789))
    expected_mrs = (
        (
            MrFullId(
                MrGlobalId(NaturalOperations.absolute(99887766)),
                MrFullInternalId(project, MrInternalId(NaturalOperations.absolute(333))),
            ),
            MergeRequest(
                MergeRequestSha(
                    Maybe.some("a" * 40),
                    Maybe.some("b" * 40),
                    Maybe.empty(),
                ),
                MergeRequestDates(
                    _assert_utc(datetime(2025, 9, 1, 1, 23, 33, tzinfo=UTC)),
                    Maybe.some(_assert_utc(datetime(2025, 9, 1, 1, 22, 32, tzinfo=UTC))),
                    Maybe.some(_assert_utc(datetime(2025, 9, 1, 1, 24, 33, tzinfo=UTC))),
                    Maybe.some(_assert_utc(datetime(2025, 9, 1, 1, 27, 33, tzinfo=UTC))),
                    Maybe.empty(),
                ),
                MergeRequestPeople(
                    author,
                    Maybe.some(merger),
                    Maybe.empty(),
                    (author,),
                    (merger,),
                ),
                MergeRequestFullState(
                    MergeRequestState.MERGED,
                    "not_open",
                    False,
                    0,
                    Maybe.empty(),
                ),
                MergeRequestProperties(
                    "the_commit_title",
                    Maybe.some("- Do something\\n- Update something links\\n- Other item"),
                    True,
                    False,
                    True,
                    "none",
                    False,
                    (),
                    Maybe.empty(),
                    "https://gitlab.com/foo/test-project/-/merge_requests/333",
                ),
                MergeRequestOrigins(
                    ProjectId(NaturalOperations.absolute(123456789)),
                    "source_branch",
                    ProjectId(NaturalOperations.absolute(777)),
                    "master",
                ),
                Maybe.empty(),
                TaskCompletion(1, 0),
            ),
        ),
        (
            MrFullId(
                MrGlobalId(NaturalOperations.absolute(99887767)),
                MrFullInternalId(project, MrInternalId(NaturalOperations.absolute(444))),
            ),
            MergeRequest(
                MergeRequestSha(
                    Maybe.some("c" * 40),
                    Maybe.some("b" * 40),
                    Maybe.empty(),
                ),
                MergeRequestDates(
                    _assert_utc(datetime(2025, 9, 2, 1, 22, 33, tzinfo=UTC)),
                    Maybe.some(_assert_utc(datetime(2025, 9, 2, 1, 22, 32, tzinfo=UTC))),
                    Maybe.some(_assert_utc(datetime(2025, 9, 2, 1, 22, 33, tzinfo=UTC))),
                    Maybe.some(_assert_utc(datetime(2025, 9, 2, 1, 22, 33, tzinfo=UTC))),
                    Maybe.empty(),
                ),
                MergeRequestPeople(
                    author,
                    Maybe.some(merger),
                    Maybe.empty(),
                    (author,),
                    (merger,),
                ),
                MergeRequestFullState(
                    MergeRequestState.MERGED,
                    "not_open",
                    False,
                    0,
                    Maybe.empty(),
                ),
                MergeRequestProperties(
                    "the_commit_title",
                    Maybe.some("- Do something\\n- Update something links\\n- Other item"),
                    True,
                    False,
                    True,
                    "none",
                    False,
                    (),
                    Maybe.empty(),
                    "https://gitlab.com/foo/test-project/-/merge_requests/333",
                ),
                MergeRequestOrigins(
                    ProjectId(NaturalOperations.absolute(123456789)),
                    "source_branch",
                    ProjectId(NaturalOperations.absolute(777)),
                    "master",
                ),
                Maybe.empty(),
                TaskCompletion(1, 0),
            ),
        ),
    )
    raw_data_path = Path(__file__).parent / "data_mr_updates.json"
    json_value = JsonValueFactory.load(raw_data_path.open(encoding="utf-8"))
    list_objs_mr = (
        json_value.bind(lambda v: Unfolder.to_list_of(v, Unfolder.to_json))
        .alt(Unsafe.raise_exception)
        .to_union()
    )
    decoded_mrs: FrozenList[tuple[MrFullId, MergeRequest]] = (
        decode_batch_mrs(list_objs_mr).alt(Unsafe.raise_exception).to_union()
    )
    assert decoded_mrs == expected_mrs

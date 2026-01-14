from datetime import UTC, datetime
from pathlib import Path

from fa_purity import Coproduct, Maybe, Unsafe
from fa_purity.date_time import DatetimeUTC
from fa_purity.json import JsonValueFactory, Unfolder
from fluidattacks_etl_utils.natural import NaturalOperations

from fluidattacks_gitlab_sdk.ids import (
    IssueFullId,
    IssueFullInternalId,
    IssueGlobalId,
    IssueInternalId,
    MilestoneFullId,
    MilestoneFullInternalId,
    MilestoneGlobalId,
    MilestoneInternalId,
    ProjectId,
    UserId,
)
from fluidattacks_gitlab_sdk.issues._client._decode import decode_issue_and_id
from fluidattacks_gitlab_sdk.issues.core import (
    Issue,
    IssueCounts,
    IssueDates,
    IssueDef,
    IssueOtherProperties,
    IssueReferences,
    IssueType,
)
from fluidattacks_gitlab_sdk.users.core import User, UserName, UserObj


def test_decode() -> None:
    author = UserObj(UserId(NaturalOperations.absolute(1)), User("ghost1"), UserName("Ghost User"))
    assignee = UserObj(
        UserId(NaturalOperations.absolute(333)),
        User("the_user"),
        UserName("The User"),
    )
    closed_by = assignee
    issue_def = IssueDef("The title", "closed", IssueType.ISSUE, Maybe.some(""))
    milestone_id = MilestoneFullId(
        MilestoneGlobalId(NaturalOperations.absolute(5)),
        MilestoneFullInternalId(
            Coproduct.inl(ProjectId(NaturalOperations.absolute(222))),
            MilestoneInternalId(NaturalOperations.absolute(103)),
        ),
    )
    references = IssueReferences(
        author,
        Maybe.some(milestone_id),
        Maybe.empty(),
        Maybe.some(closed_by),
        (assignee,),
        Maybe.some(author),
    )
    properties = IssueOtherProperties(
        False,
        Maybe.empty(),
        ("some_tag",),
        Maybe.empty(),
        Maybe.some(1),
    )
    dates = IssueDates(
        DatetimeUTC.assert_utc(datetime(2025, 3, 17, 0, 0, 0, 0, tzinfo=UTC))
        .alt(Unsafe.raise_exception)
        .to_union(),
        Maybe.some(
            DatetimeUTC.assert_utc(datetime(2025, 3, 28, 0, 0, 0, tzinfo=UTC))
            .alt(Unsafe.raise_exception)
            .to_union(),
        ),
        Maybe.some(
            DatetimeUTC.assert_utc(datetime(2025, 3, 28, 0, 0, 0, tzinfo=UTC))
            .alt(Unsafe.raise_exception)
            .to_union(),
        ),
        Maybe.empty(),
    )
    stats = IssueCounts(0, 0, 0)
    issue = Issue(issue_def, references, properties, dates, stats)
    issue_id = IssueFullId(
        IssueGlobalId(NaturalOperations.absolute(111222333)),
        IssueFullInternalId(
            ProjectId(NaturalOperations.absolute(222)),
            IssueInternalId(NaturalOperations.absolute(111)),
        ),
    )
    expected = (
        issue_id,
        issue,
    )

    raw_data_path = Path(__file__).parent / "data.json"
    raw_data = (
        JsonValueFactory.load(raw_data_path.open(encoding="utf-8"))
        .bind(Unfolder.to_json)
        .alt(Unsafe.raise_exception)
        .to_union()
    )
    decoded_issue_obj = (
        decode_issue_and_id(Maybe.some(author), raw_data).alt(Unsafe.raise_exception).to_union()
    )
    assert decoded_issue_obj == expected

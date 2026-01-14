from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from fa_purity import Maybe, Unsafe
from fa_purity.date_time import DatetimeUTC
from fa_purity.json import JsonValueFactory, Unfolder
from fluidattacks_etl_utils.natural import NaturalOperations

from fluidattacks_gitlab_sdk.ids import JobId, RunnerId, UserId
from fluidattacks_gitlab_sdk.jobs._decode import decode_job_obj
from fluidattacks_gitlab_sdk.jobs.core import (
    Commit,
    CommitHash,
    Job,
    JobConf,
    JobDates,
    JobObj,
    JobResultStatus,
)


def _assert_utc(date_time: datetime) -> DatetimeUTC:
    return DatetimeUTC.assert_utc(date_time).alt(Unsafe.raise_exception).to_union()


def test_decode() -> None:
    architectures = ("aarch64",)
    expected_job = JobObj(
        JobId(NaturalOperations.absolute(10891419293)),
        Job(
            "integrates-back-test",
            Maybe.some(UserId(NaturalOperations.absolute(4312487))),
            Maybe.some(RunnerId(NaturalOperations.absolute(46453645))),  # int
            Maybe.empty(),
            Commit(
                Maybe.some(CommitHash("82717b572300d92cd8dab2d7b9fff6f0090c69f7")),
                Maybe.some("integrates/refac(back) test"),
            ),
            JobDates(
                _assert_utc(datetime(2025, 8, 1, 23, 49, 19, tzinfo=UTC)),
                Maybe.some(_assert_utc(datetime(2025, 8, 1, 23, 49, 22, tzinfo=UTC))),
                Maybe.some(_assert_utc(datetime(2025, 8, 2, 0, 9, 5, tzinfo=UTC))),
            ),
            JobConf(False, architectures, "developeratfluid", "test"),
            JobResultStatus(
                "success",
                Maybe.empty(),
                Maybe.some(Decimal(1183.281855)),  # noqa: RUF032
                Maybe.some(Decimal(3.151458)),  # noqa: RUF032
            ),
        ),
    )

    raw_path = Path(__file__).parent / "data.json"
    raw_data = (
        JsonValueFactory.load(raw_path.open(encoding="utf-8"))
        .bind(Unfolder.to_json)
        .alt(Unsafe.raise_exception)
        .to_union()
    )

    decode_obj = decode_job_obj(raw_data).alt(Unsafe.raise_exception).to_union()
    assert decode_obj == expected_job

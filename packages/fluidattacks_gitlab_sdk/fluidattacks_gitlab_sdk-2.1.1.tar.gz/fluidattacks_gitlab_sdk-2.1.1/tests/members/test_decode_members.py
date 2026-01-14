from pathlib import Path

from fa_purity import (
    FrozenList,
    Unsafe,
)
from fa_purity.json import JsonValueFactory, Unfolder
from fluidattacks_etl_utils.natural import NaturalOperations

from fluidattacks_gitlab_sdk.ids import MemberId, ProjectId
from fluidattacks_gitlab_sdk.members._decode import decode_members
from fluidattacks_gitlab_sdk.members.core import Member


def test_decode() -> None:
    id_project_universe = ProjectId(NaturalOperations.absolute(1234567))
    expected_list = (
        (
            MemberId(NaturalOperations.absolute(1234567)),
            Member("useratfluid", "User Fluid", id_project_universe),
        ),
        (
            MemberId(NaturalOperations.absolute(7654321)),
            Member("usertwoatfluid", "User Two", id_project_universe),
        ),
        (
            MemberId(NaturalOperations.absolute(7561990)),
            Member("userThreeatfluid", "User Three", id_project_universe),
        ),
    )

    raw_data_path = Path(__file__).parent / "data.json"

    json_value = JsonValueFactory.load(raw_data_path.open(encoding="utf-8"))
    list_objs_memeber = (
        json_value.bind(lambda v: Unfolder.to_list_of(v, Unfolder.to_json))
        .alt(Unsafe.raise_exception)
        .to_union()
    )

    decoded_members: FrozenList[tuple[MemberId, Member]] = (
        decode_members(list_objs_memeber, id_project_universe)
        .alt(Unsafe.raise_exception)
        .to_union()
    )
    assert decoded_members == expected_list

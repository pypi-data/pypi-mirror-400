from fa_purity import ResultE
from fa_purity.json import JsonObj, JsonUnfolder
from fluidattacks_etl_utils.decode import DecodeUtils
from fluidattacks_etl_utils.natural import Natural

from fluidattacks_gitlab_sdk.ids import UserId
from fluidattacks_gitlab_sdk.users.core import User, UserName, UserObj


def decode_user_obj(raw: JsonObj) -> ResultE[UserObj]:
    return JsonUnfolder.require(raw, "id", DecodeUtils.to_int).bind(
        lambda uid: Natural.from_int(uid)
        .map(UserId)
        .bind(
            lambda user_id: JsonUnfolder.require(raw, "username", DecodeUtils.to_str)
            .map(User)
            .bind(
                lambda user: JsonUnfolder.require(raw, "name", DecodeUtils.to_str)
                .map(UserName)
                .map(
                    lambda name: UserObj(user_id, user, name),
                ),
            ),
        ),
    )

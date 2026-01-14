import os

from fa_purity import Cmd, CmdTransform, Maybe, Result, ResultE
from fluidattacks_etl_utils.natural import Natural
from fluidattacks_etl_utils.smash import merge_coproduct

from fluidattacks_gitlab_sdk._http_client import Credentials
from fluidattacks_gitlab_sdk.ids import ProjectId, ProjectPath
from fluidattacks_gitlab_sdk.issues.core import ProjectIdObj


def get_env_var(var: str) -> Cmd[Maybe[str]]:
    return Cmd.wrap_impure(lambda: Maybe.from_optional(os.environ.get(var)))


def require_env_var(var: str) -> Cmd[ResultE[str]]:
    return get_env_var(var).map(lambda m: m.to_result().alt(lambda _: KeyError(var)))


def get_creds_from_env() -> Cmd[ResultE[Credentials]]:
    return require_env_var("GITLAB_TOKEN").map(lambda r: r.map(Credentials))


def _str_to_int(value: str) -> ResultE[int]:
    try:
        return Result.success(int(value))
    except ValueError as error:
        return Result.failure(error)


def get_project_from_env() -> Cmd[ResultE[ProjectId]]:
    return require_env_var("GITLAB_PROJECT").map(
        lambda r: r.bind(_str_to_int).bind(Natural.from_int).map(ProjectId),
    )


def get_project_path_from_env() -> Cmd[ResultE[ProjectPath]]:
    return require_env_var("GITLAB_PROJECT_PATH").map(
        lambda r: r.map(ProjectPath),
    )


def get_project_id_obj_from_env() -> Cmd[ResultE[ProjectIdObj]]:
    return CmdTransform.chain_cmd_result(
        get_project_from_env(),
        lambda project: get_project_path_from_env().map(
            lambda r: r.map(lambda p: ProjectIdObj(project, p)),
        ),
    ).map(lambda r: r.alt(merge_coproduct))

from fa_purity import (
    Cmd,
)
from fluidattacks_utils_logger import (
    set_main_log,
)
from fluidattacks_utils_logger.env import (
    current_app_env,
    notifier_key,
    observes_debug,
)
from fluidattacks_utils_logger.handlers import (
    LoggingConf,
)


def set_logger(root_name: str, version: str) -> Cmd[None]:
    n_key = notifier_key()
    app_env = current_app_env()
    debug = observes_debug()
    conf = n_key.bind(
        lambda key: app_env.map(
            lambda env: LoggingConf(
                "sdk",
                version,
                "./observes/sdk/fluidattacks_gitlab_sdk",
                False,
                key,
                env,
                "observes",
            ),
        ),
    )
    return debug.bind(lambda d: conf.bind(lambda c: set_main_log(root_name, c, d)))

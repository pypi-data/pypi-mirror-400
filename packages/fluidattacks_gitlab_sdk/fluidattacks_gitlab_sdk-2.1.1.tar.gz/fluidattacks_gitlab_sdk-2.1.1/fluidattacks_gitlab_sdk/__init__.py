import logging

from fa_purity import (
    Unsafe,
)

from fluidattacks_gitlab_sdk._http_client import Credentials

from ._handlers import NotFound
from ._logger import (
    set_logger,
)

__version__ = "2.1.1"

Unsafe.compute(set_logger(__name__, __version__))
LOG = logging.getLogger(__name__)

__all__ = [
    "Credentials",
    "NotFound",
]

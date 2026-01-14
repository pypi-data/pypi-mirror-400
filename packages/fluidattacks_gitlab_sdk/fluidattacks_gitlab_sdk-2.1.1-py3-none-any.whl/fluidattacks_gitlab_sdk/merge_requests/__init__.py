"""Main documentation at https://docs.gitlab.com/ee/api/merge_requests.html ."""

from ._client import MrClientFactory
from .core import MrsClient

__all__ = [
    "MrClientFactory",
    "MrsClient",
]

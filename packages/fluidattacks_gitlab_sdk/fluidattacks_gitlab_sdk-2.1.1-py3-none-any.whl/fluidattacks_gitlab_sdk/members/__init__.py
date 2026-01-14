from dataclasses import dataclass

from fluidattacks_gitlab_sdk._http_client import ClientFactory, Credentials, HttpJsonClient
from fluidattacks_gitlab_sdk.members.core import Member, MemberClient

from . import _client


def _from_client(client: HttpJsonClient) -> MemberClient:
    return MemberClient(
        lambda p: _client.get_members(client, p),
    )


@dataclass(frozen=True)
class MembersClientFactory:
    @staticmethod
    def new(creds: Credentials) -> MemberClient:
        return _from_client(ClientFactory.new(creds))


__all__ = [
    "Member",
    "MemberClient",
]

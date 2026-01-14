from __future__ import (
    annotations,
)

from dataclasses import dataclass

from fa_purity import Cmd

from fluidattacks_gitlab_sdk._gql_client import GraphQlGitlabClient
from fluidattacks_gitlab_sdk._http_client import ClientFactory, Credentials, HttpJsonClient
from fluidattacks_gitlab_sdk.issues.core import IssueClient

from ._get_issue import get_issue
from ._most_recent import most_recent_issue


def _from_client(client: HttpJsonClient, new_gql_client: Cmd[GraphQlGitlabClient]) -> IssueClient:
    return IssueClient(
        lambda p, i: new_gql_client.bind(lambda c: get_issue(client, c, p, i)),
        lambda p: new_gql_client.bind(lambda c: most_recent_issue(client, c, p)),
    )


@dataclass(frozen=True)
class IssueClientFactory:
    @staticmethod
    def new(creds: Credentials) -> IssueClient:
        return _from_client(ClientFactory.new(creds), GraphQlGitlabClient.new(creds.api_key))

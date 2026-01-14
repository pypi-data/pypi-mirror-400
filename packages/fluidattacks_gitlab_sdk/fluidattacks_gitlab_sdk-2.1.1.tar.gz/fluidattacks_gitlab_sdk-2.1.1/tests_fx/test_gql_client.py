import pytest
from fa_purity import Cmd, FrozenDict, PureIterFactory, Unsafe
from fluidattacks_etl_utils.parallel import ThreadPool
from gql.transport.exceptions import TransportAlreadyConnected

from fluidattacks_gitlab_sdk._gql_client._client import GraphQlGitlabClient


def test_gql_client() -> None:
    query = """
    query {
        __typename
    }
    """
    get_data = (
        GraphQlGitlabClient.new("").bind(lambda c: c.get(query, FrozenDict({}))).map(lambda _: None)
    )
    common_client: Cmd[None] = GraphQlGitlabClient.new("").bind(
        lambda c: ThreadPool.new(10).bind(
            lambda p: p.in_threads_none(
                PureIterFactory.from_range(range(5)).map(
                    lambda _: c.get(query, FrozenDict({})).map(lambda _: None),
                ),
            ),
        ),
    )
    isolated_client: Cmd[None] = ThreadPool.new(10).bind(
        lambda p: p.in_threads_none(PureIterFactory.from_range(range(5)).map(lambda _: get_data)),
    )
    with pytest.raises(TransportAlreadyConnected):
        Unsafe.compute(common_client)
    assert Unsafe.compute(isolated_client)

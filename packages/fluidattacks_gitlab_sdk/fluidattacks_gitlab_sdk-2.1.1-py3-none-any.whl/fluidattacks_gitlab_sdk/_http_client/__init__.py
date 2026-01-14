from dataclasses import dataclass

from fluidattacks_gitlab_sdk._http_client._client_1 import Client1
from fluidattacks_gitlab_sdk._http_client._core import (
    Credentials,
    HTTPError,
    HttpJsonClient,
    Page,
    RelativeEndpoint,
    UnhandledErrors,
)


@dataclass(frozen=True)
class ClientFactory:
    @staticmethod
    def new(creds: Credentials) -> HttpJsonClient:
        return Client1.new(creds).client


__all__ = [
    "Credentials",
    "HTTPError",
    "HttpJsonClient",
    "Page",
    "RelativeEndpoint",
    "UnhandledErrors",
]

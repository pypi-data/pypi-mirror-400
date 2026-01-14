from __future__ import annotations

from dataclasses import dataclass

from fluidattacks_gitlab_sdk.ids import UserId


@dataclass(frozen=True)
class User:
    """The name of the user in the system."""

    value: str


@dataclass(frozen=True)
class UserName:
    """The real name of the user."""

    value: str


@dataclass(frozen=True)
class UserObj:
    user_id: UserId
    user: User
    name: UserName

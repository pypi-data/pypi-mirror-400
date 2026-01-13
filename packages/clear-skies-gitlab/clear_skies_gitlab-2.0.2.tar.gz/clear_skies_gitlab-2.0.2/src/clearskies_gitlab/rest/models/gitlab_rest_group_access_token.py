from __future__ import annotations

from typing import Self

from clearskies import Model
from clearskies.columns import Boolean, Datetime, Integer, Json, String

from clearskies_gitlab.rest.backends import GitlabRestBackend


class GitlabRestGroupAccessToken(
    Model,
):
    """Model for groups access tokens."""

    id_column_name = "id"
    backend = GitlabRestBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "groups/:group_id/access_tokens"

    group_id = String()
    id = Integer()
    user_id = Integer()
    name = String()
    created_at = Datetime()
    expires_at = Datetime(date_format="%Y-%m-%d")
    active = Boolean()
    revoked = Boolean()
    access_level = Integer()
    token = String()
    scopes = Json()

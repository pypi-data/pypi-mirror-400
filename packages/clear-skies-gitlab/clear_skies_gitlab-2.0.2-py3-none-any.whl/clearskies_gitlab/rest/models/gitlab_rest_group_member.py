from __future__ import annotations

from typing import Self

from clearskies.columns import Boolean, Json, String

from clearskies_gitlab.rest import gitlab_member
from clearskies_gitlab.rest.backends import GitlabRestBackend


class GitlabRestGroupMember(
    gitlab_member.GitlabMember,
):
    """Model for group members."""

    id_column_name = "id"
    backend = GitlabRestBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "groups/:group_id/members"

    group_id = String()
    query = String()
    user_ids = Json()
    skip_users = Json()
    show_seat_info = Boolean()
    all = Boolean()

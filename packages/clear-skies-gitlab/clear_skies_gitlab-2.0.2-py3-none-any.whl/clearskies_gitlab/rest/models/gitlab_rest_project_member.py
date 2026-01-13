from __future__ import annotations

from typing import Self

from clearskies.columns import Boolean, Json, String

from clearskies_gitlab.rest import gitlab_member
from clearskies_gitlab.rest.backends import GitlabRestBackend


class GitlabRestProjectMember(
    gitlab_member.GitlabMember,
):
    """Model for project members."""

    backend = GitlabRestBackend()
    id_column_name = "id"

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/members"

    project_id = String()
    query = String()
    user_ids = Json()
    skip_users = Json()
    show_seat_info = Boolean()
    all = Boolean()

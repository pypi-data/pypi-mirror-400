from __future__ import annotations

from clearskies import Model

from clearskies_gitlab.graphql.backends import GitlabGraphqlBackend


class GitlabGroup(Model):
    """Model for gitlab projects via GQL."""

    gitlab_id_pattern: str = "gid://gitlab/Group/[ID]"

    id_column_name: str = "id"
    backend = GitlabGraphqlBackend(
        root_field="groups",
        id_argument_is_array=True,
        id_format_pattern="gid://gitlab/Project/{id}",
        id_argument_name="ids",
    )

    @classmethod
    def destination_name(cls) -> str:
        """Return the slug of the api endpoint for this model."""
        return "group"

from __future__ import annotations

from typing import Self

from clearskies.columns import String

from clearskies_gitlab.rest import gitlab_cicd_variable
from clearskies_gitlab.rest.backends import GitlabRestBackend


class GitlabRestGroupVariable(
    gitlab_cicd_variable.GitlabCICDVariable,
):
    """Model for gitlab group variables."""

    id_column_name = "id"
    backend = GitlabRestBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "groups/:group_id/variables"

    group_id = String()

from __future__ import annotations

from typing import Self

from clearskies.columns import BelongsToId, BelongsToModel

from clearskies_gitlab.rest import gitlab_cicd_variable
from clearskies_gitlab.rest.backends import GitlabRestBackend
from clearskies_gitlab.rest.models import gitlab_rest_project_reference


class GitlabRestProjectVariable(
    gitlab_cicd_variable.GitlabCICDVariable,
):
    """Model for gitlab group variables."""

    backend = GitlabRestBackend()
    id_column_name = "key"

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/variables"

    project_id = BelongsToId(gitlab_rest_project_reference.GitlabRestProjectReference)
    project = BelongsToModel("project_id")

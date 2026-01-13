from __future__ import annotations

from typing import Self

from clearskies import Model
from clearskies.columns import BelongsToId, BelongsToModel, Boolean, Integer, Json, String

from clearskies_gitlab.rest.backends import GitlabRestBackend
from clearskies_gitlab.rest.models import gitlab_rest_project_reference


class GitlabRestProjectProtectedBranch(
    Model,
):
    """Model for gitlab project protected branches."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/protected_branches"

    id_column_name = "id"

    backend = GitlabRestBackend()

    id = Integer()
    name = String()
    allow_force_push = Boolean()
    code_owner_approval_required = Boolean()
    merge_access_levels = Json()
    push_access_levels = Json()
    unprotect_access_levels = Json()

    project_id = BelongsToId(gitlab_rest_project_reference.GitlabRestProjectReference)
    project = BelongsToModel("project_id")

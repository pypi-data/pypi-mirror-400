from __future__ import annotations

from typing import Self

from clearskies import Model
from clearskies.columns import BelongsToId, BelongsToModel, Boolean

from clearskies_gitlab.rest.backends import GitlabRestBackend
from clearskies_gitlab.rest.models import gitlab_rest_project_reference


class GitlabRestProjectApprovalConfig(
    Model,
):
    """Model for gitlab project protected branches."""

    backend = GitlabRestBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/approvals"

    project_id = BelongsToId(gitlab_rest_project_reference.GitlabRestProjectReference)
    project = BelongsToModel("project_id")

    id_column_name = "project_id"

    reset_approvals_on_push = Boolean()
    require_user_password_for_approval = Boolean()
    disable_overriding_approvers_per_merge_request = Boolean()
    merge_requests_author_approval = Boolean()
    merge_requests_disable_committers_approval = Boolean()
    require_reauthentication_to_approve = Boolean()

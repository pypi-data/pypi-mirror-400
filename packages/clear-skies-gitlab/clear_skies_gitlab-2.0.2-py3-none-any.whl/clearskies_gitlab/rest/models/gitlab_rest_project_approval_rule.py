from __future__ import annotations

from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from builtins import type as builtins_type

from clearskies import Model
from clearskies.columns import BelongsToId, BelongsToModel, Boolean, Integer, Json, Select, String

from clearskies_gitlab.rest.backends import GitlabRestBackend
from clearskies_gitlab.rest.models import gitlab_rest_project_reference


class GitlabRestProjectApprovalRule(
    Model,
):
    """Model for gitlab project protected branches."""

    backend = GitlabRestBackend()

    @classmethod
    def destination_name(cls: builtins_type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/approval_rules"

    id_column_name = "id"

    name = String()
    id = Integer()
    type = Select(allowed_values=["regular", "code_owner", "report_approver"])
    approvals_required = Integer()
    applies_to_all_protected_branches = Boolean()

    project_id = BelongsToId(gitlab_rest_project_reference.GitlabRestProjectReference)
    project = BelongsToModel("project_id")

    eligible_approvers = Json()
    users = Json()
    groups = Json()
    protected_branches = Json()
    contains_hidden_groups = Boolean()

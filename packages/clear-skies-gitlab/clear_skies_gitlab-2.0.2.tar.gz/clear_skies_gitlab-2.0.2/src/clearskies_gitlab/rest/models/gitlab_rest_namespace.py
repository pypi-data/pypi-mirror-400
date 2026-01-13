from __future__ import annotations

from typing import Self

from clearskies import Model
from clearskies.columns import (
    BelongsToModel,
    BelongsToSelf,
    Boolean,
    Datetime,
    HasMany,
    Integer,
    Json,
    Select,
    String,
)

from clearskies_gitlab.rest.backends import GitlabRestBackend
from clearskies_gitlab.rest.models import (
    gitlab_rest_group_access_token,
    gitlab_rest_group_subgroup_reference,
    gitlab_rest_group_variable,
    gitlab_rest_project_reference,
)


class GitlabRestNamespace(Model):
    """Model for namespaces."""

    backend = GitlabRestBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "namespaces"

    id_column_name = "id"

    id = String()
    name = String()
    path = String()
    kind = Select(allowed_values=["group", "user"])
    full_path = String()
    avatar_url = String()
    web_url = String()
    billable_members_count = Integer()
    plan = Select(allowed_values=["free", "premium", "ultimate", "bronze", "silver", "gold"])
    end_date = Datetime()
    trial_ends_on = Datetime()
    trial = Boolean()
    root_repository_size = Integer()
    projects_count = Integer()
    max_seats_used = Integer()
    max_seats_used_changed_at = Datetime()
    seats_in_use = Integer()
    members_counts_with_descendants = Integer()

    projects = HasMany(
        gitlab_rest_project_reference.GitlabRestProjectReference,
        foreign_column_name="group_id",
    )
    access_tokens = HasMany(
        gitlab_rest_group_access_token.GitlabRestGroupAccessToken,
        foreign_column_name="group_id",
    )
    variables = HasMany(
        gitlab_rest_group_variable.GitlabRestGroupVariable,
        foreign_column_name="group_id",
    )
    subgroups = HasMany(
        gitlab_rest_group_subgroup_reference.GitlabRestGroupSubgroupReference,
        foreign_column_name="group_id",
    )
    parent_id = BelongsToSelf()
    parent = BelongsToModel("parent_id")
    ### Search params
    skip_groups = Json()
    all_available = Boolean()
    search = String()
    order_by = String()
    sort = String()
    visibility = Select(allowed_values=["public", "internal", "private"])
    with_custom_attributes = Boolean()
    owned = Boolean()
    min_access_level = Integer()
    top_level_only = Boolean()
    repository_storage = String()
    marked_for_deletion_on = Datetime(date_format="%Y-%m-%d")

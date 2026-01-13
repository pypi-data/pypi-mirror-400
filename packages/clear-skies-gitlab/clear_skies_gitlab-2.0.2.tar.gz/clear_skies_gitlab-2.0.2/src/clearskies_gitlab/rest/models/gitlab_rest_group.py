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
    gitlab_rest_group_member_reference,
    gitlab_rest_group_project_reference,
    gitlab_rest_group_subgroup_reference,
    gitlab_rest_group_variable,
)


class GitlabRestGroup(
    Model,
):
    """Model for groups."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "groups"

    id_column_name = "id"

    backend = GitlabRestBackend()

    id = String()
    web_url = String()
    name = String()
    path = String()
    description = String()
    visibility = String()
    share_with_group_lock = Boolean()
    require_two_factor_authentication = Boolean()
    two_factor_grace_period = Integer()
    project_creation_level = String()
    auto_devops_enabled = Boolean()
    subgroup_creation_level = String()
    emails_disabled = Boolean()
    emails_enabled = Boolean()
    mentions_disabled = String()
    lfs_enabled = String()
    math_rendering_limits_enabled = Boolean()
    lock_math_rendering_limits_enabled = Boolean()
    default_branch = String()
    default_branch_protection = String()
    default_branch_protection_defaults = String()
    avatar_url = String()
    request_access_enabled = Boolean()
    full_name = String()
    full_path = String()
    created_at = Datetime()
    parent_id = String()
    organization_id = String()
    shared_runners_setting = String()
    custom_attributes = Json()
    statistics = Json()
    ldap_cn = String()
    ldap_access = String()
    ldap_group_links = Json()
    saml_group_links = Json()
    file_template_project_id = String()
    marked_for_deletion_on = Datetime()
    wiki_access_level = String()
    repository_storage = String()
    duo_features_enabled = Boolean()
    lock_duo_features_enabled = Boolean()
    shared_with_groups = Json()
    runners_token = String()
    enabled_git_access_protocol = String()
    prevent_sharing_groups_outside_hierarchy = Boolean()
    shared_runners_minutes_limit = Integer()
    extra_shared_runners_minutes_limit = Integer()
    prevent_forking_outside_group = Boolean()
    service_access_tokens_expiration_enforced = Boolean()
    membership_lock = Boolean()
    ip_restriction_ranges = Json()
    unique_project_download_limit = String()
    unique_project_download_limit_interval_in_seconds = Integer()
    unique_project_download_limit_alertlist = Json()
    auto_ban_user_on_excessive_projects_download = Boolean()

    projects = HasMany(
        gitlab_rest_group_project_reference.GitlabRestGroupProjectReference,
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
    members = HasMany(
        gitlab_rest_group_member_reference.GitlabRestGroupMemberReference,
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

from __future__ import annotations

from typing import Self

from clearskies import Model
from clearskies.columns import (
    BelongsToId,
    BelongsToModel,
    Boolean,
    Datetime,
    HasMany,
    HasOne,
    Integer,
    Json,
    Select,
    String,
)

from clearskies_gitlab.rest.backends import GitlabRestBackend
from clearskies_gitlab.rest.models import (
    gitlab_rest_group_reference,
    gitlab_rest_namespace,
    gitlab_rest_project_approval_config_reference,
    gitlab_rest_project_approval_rule_reference,
    gitlab_rest_project_protected_branch_reference,
    gitlab_rest_project_variable_reference,
)


class GitlabRestProject(Model):
    """Model for projects."""

    id_column_name: str = "id"

    backend = GitlabRestBackend(
        api_to_model_map={
            "namespace.id": ["namespace_id", "group_id"],
        }
    )

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects"

    id = String()

    description = String()
    description_html = String()
    visibility = String()
    ssh_url_to_repo = String()
    http_url_to_repo = String()
    web_url = String()
    topics = Json()
    name = String()
    path = String()
    issues_enabled = Boolean()
    open_issues_count = Integer()
    merge_requests_enabled = Boolean()
    jobs_enabled = Boolean()
    wiki_enabled = Boolean()
    snippets_enabled = Boolean()
    created_at = Datetime()
    updated_at = Datetime()
    last_activity_at = Datetime()
    import_status = String()
    archived = Boolean()
    avatar_url = String()
    shared_runners_enabled = Boolean()
    forks_count = Integer()
    star_count = Integer()

    group_id = BelongsToId(gitlab_rest_group_reference.GitlabRestGroupReference)
    group = BelongsToModel("group_id")

    namespace_id = BelongsToId(gitlab_rest_namespace.GitlabRestNamespace)
    namespace = BelongsToModel("namespace_id")

    allow_pipeline_trigger_approve_deployment = Boolean()

    # REST-specific fields not available in GraphQL
    default_branch = String()
    creator_id = Integer()
    readme_url = String()
    owner = Json()
    resolve_outdated_diff_discussions = Boolean()
    import_url = String()
    import_type = String()
    import_error = String()
    license_url = String()
    license = Json()
    group_runners_enabled = Boolean()
    container_registry_access_level = Select(allowed_values=["disabled", "private", "enabled"])
    container_security_and_compliance_access_level = Select(allowed_values=["disabled", "private", "enabled"])
    container_expiration_policy = Json()
    runners_token = String()
    ci_forward_deployment_enabled = Boolean()
    ci_forward_deployment_rollback_allowed = Boolean()
    ci_separated_caches = Boolean()
    ci_restrict_pipeline_cancellation_role = Select(allowed_values=["maintainer", "developer", "no_one"])
    ci_pipeline_variables_minimum_override_role = Select(
        allowed_values=["owner", "developer", "maintainer", "no_one_allowed"]
    )
    ci_push_repository_for_job_token_allowed = Boolean()
    public_jobs = Boolean()
    shared_with_groups = Json()
    repository_storage = String()
    only_allow_merge_if_pipeline_succeeds = Boolean()
    allow_merge_on_skipped_pipeline = Boolean()
    restrict_user_defined_variables = Boolean()
    only_allow_merge_if_all_discussions_are_resolved = Boolean()
    remove_source_branch_after_merge = Boolean()
    printing_merge_requests_link_enabled = Boolean()
    request_access_enabled = Boolean()
    merge_method = Select(allowed_values=["merge", "rebase_merge", "ff"])
    squash_option = Select(allowed_values=["never", "always", "default_on", "default_off"])
    mirror = Boolean()
    mirror_user_id = Integer()
    mirror_trigger_builds = Boolean()
    only_mirror_protected_branches = Boolean()
    mirror_overwrites_diverged_branches = Boolean()
    external_authorization_classification_label = String()
    packages_enabled = Boolean()
    service_desk_enabled = Boolean()
    service_desk_address = String()
    autoclose_referenced_issues = Boolean()
    suggestion_commit_message = String()
    enforce_auth_checks_on_uploads = Boolean()
    merge_commit_template = String()
    squash_commit_template = String()
    issue_branch_template = String()
    compliance_frameworks = Json()
    statistics = Json()
    container_registry_image_prefix = String()

    can_create_merge_request_in = Boolean()
    auto_devops_enabled = Boolean()
    auto_devops_deploy_strategy = Select(allowed_values=["continuous", "manual", "timed_incremental"])
    ci_allow_fork_pipelines_to_run_in_parent_project = Boolean()
    ci_default_git_depth = Integer()
    name_with_namespace = String()
    path_with_namespace = String()
    permissions = Json()

    variables = HasMany(
        gitlab_rest_project_variable_reference.GitlabRestProjectVariableReference,
        foreign_column_name="project_id",
    )

    protected_branches = HasMany(
        gitlab_rest_project_protected_branch_reference.GitlabRestProjectProtectedBranchReference,
        foreign_column_name="project_id",
    )

    approval_config = HasOne(
        gitlab_rest_project_approval_config_reference.GitlabRestProjectApprovalConfigReference,
        foreign_column_name="project_id",
    )

    approval_rules = HasMany(
        gitlab_rest_project_approval_rule_reference.GitlabRestProjectApprovalRuleReference,
        foreign_column_name="project_id",
    )

    # contributors = HasMany(
    ### Search params
    include_hidden = Boolean()
    include_pending_delete = Boolean()
    last_activity_after = Datetime()
    last_activity_before = Datetime()
    membership = Boolean()
    min_access_level = Integer()
    order_by = Select(
        allowed_values=[
            "id",
            "name",
            "path",
            "created_at",
            "updated_at",
            "star_count",
            "last_activity_at",
            "similarity",
        ]
    )
    owned = Boolean()
    repository_checksum_failed = Boolean()
    repository_storage = String()
    search_namespaces = Boolean()
    search = String()
    simple = Boolean()
    sort = String()
    starred = Boolean()
    topic_id = Integer()
    topic = String()
    updated_after = Datetime()
    updated_before = Datetime()
    visibility = Select(allowed_values=["public", "internal", "private"])
    wiki_checksum_failed = Boolean()
    with_custom_attributes = Boolean()
    with_issues_enabled = Boolean()
    with_merge_requests_enabled = Boolean()
    with_programming_language = String()
    marked_for_deletion_on = Datetime(date_format="%Y-%m-%d")

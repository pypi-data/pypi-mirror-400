from __future__ import annotations

from clearskies import Model
from clearskies.columns import Boolean, Datetime, Integer, Json, String


class GitlabBranchRule(Model):
    """Model for GitLab branch rules."""

    id = Integer()
    name = String()
    protected = Boolean()
    developers_can_push = Boolean()
    developers_can_merge = Boolean()
    can_push = Boolean()
    default = Boolean()
    created_at = Datetime()
    updated_at = Datetime()
    code_owner_approval_required = Boolean()
    unprotect_access_levels = Json()
    push_access_levels = Json()

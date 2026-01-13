from __future__ import annotations

from clearskies import Model
from clearskies.columns import Boolean, String


class GitlabCICDVariable(Model):
    """Base model for groups ci/cd variables."""

    id_column_name = "key"

    key = String()
    value = String()
    description = String()
    environment_scope = String()
    variable_type = String()
    masked = Boolean()
    protected = Boolean()
    hidden = Boolean()
    raw = Boolean()

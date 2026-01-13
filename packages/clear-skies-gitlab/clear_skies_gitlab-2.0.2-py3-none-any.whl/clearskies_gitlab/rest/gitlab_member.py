from __future__ import annotations

from clearskies import Model
from clearskies.columns import Datetime, Email, Integer, Json, String


class GitlabMember(Model):
    """Base model for group or project members."""

    id_column_name = "id"

    id = Integer()
    username = String()
    name = String()
    state = String()
    avatar_url = String()
    access_level = Integer()
    created_at = Datetime()
    created_by = Json()
    email = Email()
    group_saml_identity = Json()

from __future__ import annotations

from typing import Self

from clearskies import Model
from clearskies.columns import Boolean, Json, Select, String

from clearskies_gitlab.rest.backends import GitlabRestBackend


class GitlabRestAdvancedSearch(Model):
    """Model for advanced search."""

    backend = GitlabRestBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "search"

    scope = Select(
        allowed_values=[
            "projects",
            "issues",
            "merge_requests",
            "milestones",
            "snippet_titles",
            "users",
            "wiki_blobs",
            "commits",
            "blobs",
            "notes",
        ]
    )
    search = String()
    confidential = Boolean()
    state = String()
    fields = Json()

from __future__ import annotations

from typing import Self

from clearskies.columns import Integer

from clearskies_gitlab.rest.models import gitlab_rest_advanced_search


class GitlabRestGroupSearch(
    gitlab_rest_advanced_search.GitlabRestAdvancedSearch,
):
    """Model for groups access tokens."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "groups/:group_id/search"

    group_id = Integer()

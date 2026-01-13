from __future__ import annotations

from clearskies_gitlab.rest.models import (
    gitlab_rest_advanced_search_blob,
    gitlab_rest_group_search,
)


class GitlabRestGroupSearchBlob(
    gitlab_rest_group_search.GitlabRestGroupSearch,
    gitlab_rest_advanced_search_blob.GitlabRestAdvancedSearchBlob,
):
    """Model for advanced searching blobs."""

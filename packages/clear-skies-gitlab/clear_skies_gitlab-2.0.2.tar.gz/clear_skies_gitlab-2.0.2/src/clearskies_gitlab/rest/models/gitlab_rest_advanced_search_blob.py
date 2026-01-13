from __future__ import annotations

from clearskies.columns import BelongsToId, BelongsToModel, Integer, String

from clearskies_gitlab.rest.models import gitlab_rest_advanced_search, gitlab_rest_project


class GitlabRestAdvancedSearchBlob(
    gitlab_rest_advanced_search.GitlabRestAdvancedSearch,
):
    """Model for advanced searching blobs."""

    basename = String()
    data = String()
    path = String()
    filename = String()
    id = Integer()
    ref = String()
    startline = Integer()
    project_id = BelongsToId(
        gitlab_rest_project.GitlabRestProject,
    )
    project = BelongsToModel("project_id")

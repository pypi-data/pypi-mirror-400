from __future__ import annotations

from typing import Self

from clearskies import Model
from clearskies.columns import BelongsToId, BelongsToModel, Boolean, Integer, String

from clearskies_gitlab.rest.backends import GitlabRestBackend
from clearskies_gitlab.rest.models import gitlab_rest_project_reference


class GitlabRestProjectRepositoryFile(
    Model,
):
    """Model for projects repository commits diff."""

    id_column_name = "file_path"

    backend = GitlabRestBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/repository/files/:file_path"

    project_id = BelongsToId(gitlab_rest_project_reference.GitlabRestProjectReference)
    project = BelongsToModel("project_id")

    file_path = String()
    ref = String(default="HEAD")
    blob_id = String()
    commit_id = String()
    content = String()
    content_sha256 = String()
    encoding = String()
    execute_filemode = Boolean()
    file_name = String()
    last_commit_id = String()
    size = Integer()

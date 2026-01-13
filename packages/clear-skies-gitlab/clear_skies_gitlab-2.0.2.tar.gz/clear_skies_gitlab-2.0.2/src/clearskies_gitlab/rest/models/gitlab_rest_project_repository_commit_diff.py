from __future__ import annotations

from typing import Self

from clearskies import Model
from clearskies.columns import Boolean, Integer, String

from clearskies_gitlab.rest.backends import GitlabRestBackend


class GitlabRestProjectRepositoryCommitDiff(
    Model,
):
    """Model for projects repository commits diff."""

    id_column_name = "commit_id"

    backend = GitlabRestBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/repository/commits/:commit_id/diff"

    diff = String()
    new_path = String()
    old_path = String()
    a_mode = Integer()
    b_mode = Integer()
    new_file = Boolean()
    renamed_file = Boolean()
    deleted_file = Boolean()
    # search params
    project_id = Integer()
    commit_id = String()
    unidiff = Boolean()

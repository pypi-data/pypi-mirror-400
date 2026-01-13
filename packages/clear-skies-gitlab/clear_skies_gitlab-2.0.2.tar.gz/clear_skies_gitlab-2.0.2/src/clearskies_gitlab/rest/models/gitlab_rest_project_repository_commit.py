from __future__ import annotations

from typing import Self

from clearskies import Model
from clearskies.columns import Boolean, Datetime, Email, HasOne, Integer, Json, String

from clearskies_gitlab.rest.backends import GitlabRestBackend
from clearskies_gitlab.rest.models import gitlab_rest_project_repository_commit_diff


class GitlabRestProjectRepositoryCommit(
    Model,
):
    """Model for projects repository commits."""

    backend = GitlabRestBackend()
    id_column_name = "id"

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "projects/:project_id/repository/commits"

    diff = HasOne(
        gitlab_rest_project_repository_commit_diff.GitlabRestProjectRepositoryCommitDiff,
        foreign_column_name="commit_id",
        where=lambda model, parent: model.where(f"gitlab_project_id={parent.id}"),
    )

    id = String()
    short_id = String()
    title = String()
    author_name = String()
    author_email = Email()
    authored_date = Datetime()
    committer_name = String()
    committer_email = Email()
    committed_date = Datetime()
    created_at = Datetime()
    messsage = String()
    parent_ids = Json()
    web_url = String()
    extended_trailers = Json()
    # search params
    project_id = Integer()
    ref_name = String()
    since = Datetime()
    until = Datetime()
    path = String()
    all = Boolean()
    with_stats = Boolean()
    first_parent = Boolean()
    trailers = Boolean()

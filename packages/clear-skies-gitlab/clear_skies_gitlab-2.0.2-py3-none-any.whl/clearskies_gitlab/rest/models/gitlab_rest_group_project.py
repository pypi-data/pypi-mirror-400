from __future__ import annotations

from typing import Self

from clearskies_gitlab.rest.models import gitlab_rest_project


class GitlabRestGroupProject(
    gitlab_rest_project.GitlabRestProject,
):
    """Model for groups projects."""

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "groups/:group_id/projects"

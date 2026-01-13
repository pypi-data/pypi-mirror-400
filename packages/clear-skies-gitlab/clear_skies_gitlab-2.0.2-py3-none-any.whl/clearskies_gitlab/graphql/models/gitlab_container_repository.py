from clearskies import Model
from clearskies.columns import BelongsToId, BelongsToModel, Datetime, HasMany, String

from clearskies_gitlab.graphql.backends import GitlabGraphqlBackend
from clearskies_gitlab.graphql.models import gitlab_container_repository_tag_reference, gitlab_project_reference


class GitlabContainerRepository(Model):
    """Model for gitlab container repositories via GQL."""

    id_column_name: str = "id"

    backend = GitlabGraphqlBackend(
        root_field="containerRepositories",
        id_argument_is_array=True,
        id_format_pattern="gid://gitlab/ContainerRepository/{id}",
        id_argument_name="ids",
    )

    @classmethod
    def destination_name(cls) -> str:
        """Return the slug of the api endpoint for this model."""
        return "containerRepository"

    name = String()
    location = String()
    path = String()
    created_at = Datetime()
    project_id = BelongsToId(gitlab_project_reference.GitlabProjectReference)
    project = BelongsToModel("project_id")
    tags = HasMany(
        gitlab_container_repository_tag_reference.GitlabContainerRepositoryTagReference,
        foreign_column_name="containerRepositoryId",
    )

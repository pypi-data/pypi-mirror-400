from clearskies import Model
from clearskies.columns import BelongsToId, BelongsToModel, Datetime, String

from clearskies_gitlab.graphql.backends import GitlabGraphqlBackend
from clearskies_gitlab.graphql.models import gitlab_container_repository_reference


class GitlabContainerRepositoryTag(Model):
    """Model for gitlab container repositories via GQL."""

    id_column_name: str = "name"

    backend = GitlabGraphqlBackend(
        root_field="containerRepositories",
        id_argument_is_array=True,
        id_format_pattern="gid://gitlab/ContainerRepository/{id}",
        id_argument_name="ids",
    )

    @classmethod
    def destination_name(cls) -> str:
        """Return the slug of the api endpoint for this model."""
        return "tag"

    name = String()
    digest = String()
    location = String()
    path = String()
    created_at = Datetime()
    published_at = Datetime()
    container_repository_id = BelongsToId(gitlab_container_repository_reference.GitlabContainerRepositoryReference)
    container_repository = BelongsToModel("container_repository_id")

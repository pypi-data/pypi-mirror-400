class GitlabContainerRepositoryReference:
    """Reference to GitlabContainerRepository model."""

    def get_model_class(self) -> type:
        """Return the model class this reference points to."""
        from clearskies_gitlab.graphql.models import gitlab_container_repository

        return gitlab_container_repository.GitlabContainerRepository

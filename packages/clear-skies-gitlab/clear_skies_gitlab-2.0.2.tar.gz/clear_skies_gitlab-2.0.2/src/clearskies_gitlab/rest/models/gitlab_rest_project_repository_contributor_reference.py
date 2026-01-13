class GitlabRestProjectRepositoryContributorReference:
    """Reference to GitlabRestProjectRepositoryContributor model."""

    def get_model_class(self) -> type:
        """Return the model class this reference points to."""
        from clearskies_gitlab.rest.models import gitlab_rest_project_repository_contributor

        return gitlab_rest_project_repository_contributor.GitlabRestProjectRepositoryContributor

class GitlabRestProjectRepositoryFileReference:
    """Reference to GitlabRestProjectRepositoryFile model."""

    def get_model_class(self) -> type:
        """Return the model class this reference points to."""
        from clearskies_gitlab.rest.models import gitlab_rest_project_repository_file

        return gitlab_rest_project_repository_file.GitlabRestProjectRepositoryFile

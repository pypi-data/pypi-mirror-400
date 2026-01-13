class GitlabProjectReference:
    """Reference to GitlabProject model."""

    def get_model_class(self) -> type:
        """Return the model class this reference points to."""
        from clearskies_gitlab.graphql.models import gitlab_project

        return gitlab_project.GitlabProject

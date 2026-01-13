class GitlabGroupReference:
    """Reference to GitlabGroup model."""

    def get_model_class(self) -> type:
        """Return the model class this reference points to."""
        from clearskies_gitlab.graphql.models import gitlab_group

        return gitlab_group.GitlabGroup

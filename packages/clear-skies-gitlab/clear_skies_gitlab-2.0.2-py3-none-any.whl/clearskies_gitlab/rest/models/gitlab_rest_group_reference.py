from clearskies_gitlab.rest.models import gitlab_rest_group


class GitlabRestGroupReference:
    """Reference to GitlabRestGroup model."""

    def get_model_class(self) -> type:
        """Return the model class this reference points to."""
        return gitlab_rest_group.GitlabRestGroup

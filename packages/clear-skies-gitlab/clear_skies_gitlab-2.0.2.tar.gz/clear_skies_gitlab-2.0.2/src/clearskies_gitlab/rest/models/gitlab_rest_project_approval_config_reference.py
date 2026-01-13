class GitlabRestProjectApprovalConfigReference:
    """Reference to GitlabRestProjectApprovalConfig model."""

    def get_model_class(self) -> type:
        """Return the model class this reference points to."""
        from clearskies_gitlab.rest.models import gitlab_rest_project_approval_config

        return gitlab_rest_project_approval_config.GitlabRestProjectApprovalConfig

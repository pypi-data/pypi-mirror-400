class GitlabRestProjectMemberReference:
    """Reference to GitlabRestProjectMember model."""

    def get_model_class(self) -> type:
        """Return the model class this reference points to."""
        from clearskies_gitlab.rest.models import gitlab_rest_project_member

        return gitlab_rest_project_member.GitlabRestProjectMember

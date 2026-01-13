class GitlabRestGroupMemberReference:
    """Reference to GitlabRestGroupMember model."""

    def get_model_class(self) -> type:
        """Return the model class this reference points to."""
        from clearskies_gitlab.rest.models import gitlab_rest_group_member

        return gitlab_rest_group_member.GitlabRestGroupMember

class GitlabRestGroupSubgroupReference:
    """Reference to GitlabRestGroupSubgroup model."""

    def get_model_class(self) -> type:
        """Return the model class this reference points to."""
        from clearskies_gitlab.rest.models import gitlab_rest_group_subgroup

        return gitlab_rest_group_subgroup.GitlabRestGroupSubgroup

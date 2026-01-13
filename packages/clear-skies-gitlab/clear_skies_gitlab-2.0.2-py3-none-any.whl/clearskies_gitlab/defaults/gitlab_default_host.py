import clearskies


class GitlabDefaultHost(clearskies.di.AdditionalConfigAutoImport):
    """Provide default GitLab Host from environment."""

    def provide_gitlab_host(self, environment: clearskies.Environment):
        """Provide the GitLab host from environment or default."""
        gitlab_host = environment.get("GITLAB_HOST", True)
        return gitlab_host if gitlab_host else "https://gitlab.com/"

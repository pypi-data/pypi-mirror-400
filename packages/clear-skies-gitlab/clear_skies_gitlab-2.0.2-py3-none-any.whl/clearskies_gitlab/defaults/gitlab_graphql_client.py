import clearskies


class GitlabDefaultGraphqlClient(clearskies.di.AdditionalConfigAutoImport):
    """Provide default Gitlab authentication from environment."""

    def provide_gitlab_graphql_client(
        self,
        gitlab_auth: clearskies.authentication.Authentication,
        gitlab_host: str,
        environment: clearskies.Environment,
    ):
        """Provide the Gitlab authentication from environment."""
        return clearskies.clients.GraphqlClient(
            endpoint=f"{gitlab_host.rstrip('/')}/api/graphql",
            authentication=gitlab_auth,
            timeout=30,
        )

from __future__ import annotations

from clearskies import configs, decorators
from clearskies.backends import GraphqlBackend
from clearskies.clients.graphql_client import GraphqlClient
from clearskies.di import inject


class GitlabGraphqlBackend(GraphqlBackend):
    """Backend to gitlab using graphql."""

    graphql_client_name = configs.String(default="gitlab_graphql_client")

    api_to_model_map = configs.AnyDict(default={})
    pagination_parameter_name = configs.String(default="page")
    api_casing = configs.String(default="camelCase")
    model_casing = configs.String(default="snake_case")

    di = inject.Di()

    @decorators.parameters_to_properties
    def __init__(
        self,
        graphql_client: GraphqlClient | None = None,
        graphql_client_name: str = "gitlab_graphql_client",
        root_field: str = "",
        pagination_style: str = "cursor",
        api_case: str = "camelCase",
        model_case: str = "snake_case",
        is_collection: bool | None = None,
        max_relationship_depth: int = 2,
        relationship_limit: int = 10,
        use_connection_for_relationships: bool = True,
        id_argument_name: str | None = None,
        id_argument_is_array: bool = False,
        id_format_pattern: str = "",
    ):
        self.finalize_and_validate_configuration()

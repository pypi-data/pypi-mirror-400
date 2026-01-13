from __future__ import annotations

import urllib
from typing import TYPE_CHECKING, Any

from clearskies import configs
from clearskies.backends import ApiBackend
from clearskies.decorators import parameters_to_properties
from clearskies.di import inject
from clearskies.query import Query
from requests.structures import CaseInsensitiveDict

if TYPE_CHECKING:
    from clearskies.authentication import Authentication
    from clearskies.query import Query


class GitlabRestBackend(ApiBackend):
    """Backend for Gitlab.com."""

    gitlab_host = inject.ByName("gitlab_host", cache=True)  # type: ignore[assignment]
    authentication = inject.ByName("gitlab_auth", cache=False)  # type: ignore[assignment]
    requests = inject.Requests()
    _auth_headers: dict[str, str] = {}

    api_to_model_map = configs.AnyDict(default={})
    pagination_parameter_name = configs.String(default="page")

    @parameters_to_properties
    def __init__(
        self,
        base_url: str | None = None,
        authentication: Authentication | None = None,
        model_casing: str = "snake_case",
        api_casing: str = "snake_case",
        api_to_model_map: dict[str, str | list[str]] = {},
        pagination_parameter_name: str = "page",
        pagination_parameter_type: str = "str",
        limit_parameter_name: str = "per_page",
    ):
        self.finalize_and_validate_configuration()

    @property
    def base_url(self) -> str:
        """
        Docstring for base_url.

        :param self: Description
        :return: Description
        :rtype: str
        """
        return f"{self.gitlab_host.rstrip('/')}/api/v4"

    def count_method(self, query: Query) -> str:
        """Return the request method to use when making a request for a record count."""
        return "HEAD"

    def count(self, query: Query) -> int:
        """Return the count of records matching the query."""
        self.check_query(query)
        (url, method, body, headers) = self.build_records_request(query)
        response = self.execute_request(url, self.count_method(query), json=body, headers=headers)
        return self._map_count_response(response.headers)

    def _map_count_response(self, headers: CaseInsensitiveDict[str]) -> int:
        return int(headers.get("x-total", 0))

    # def map_records_response(
    #     self, response_data: Any, query: Query, query_data: dict[str, Any] | None = None
    # ) -> list[dict[str, Any]]:
    #     """Map the response data to model records with support for nested fields."""
    #     if query_data is None:
    #         query_data = {}

    #     columns = query.model_class.get_columns()
    #     result = []

    #     # Handle list response
    #     if isinstance(response_data, list):
    #         for item in response_data:
    #             if not isinstance(item, dict):
    #                 continue
    #             mapped = self.check_dict_and_map_to_model(item, columns, query_data)
    #             if mapped:
    #                 result.append(mapped)
    #     # Handle single object response
    #     elif isinstance(response_data, dict):
    #         mapped = self.check_dict_and_map_to_model(response_data, columns, query_data)
    #         if mapped:
    #             result.append(mapped)

    #     return result

    def conditions_to_request_parameters(
        self, query: Query, used_routing_parameters: list[str]
    ) -> tuple[str, dict[str, str], dict[str, Any]]:
        """Convert query conditions to request parameters."""
        route_id = ""

        url_parameters = {}
        for condition in query.conditions:
            if condition.column_name in used_routing_parameters:
                continue
            if condition.operator != "=":
                raise ValueError(
                    f"I'm not very smart and only know how to search with the equals operator, but I received a condition of {condition.parsed}.  If you need to support this, you'll have to extend the ApiBackend and overwrite the build_records_request method."
                )
            if condition.column_name == query.model_class.id_column_name:
                route_id = urllib.parse.quote_plus(condition.values[0]).replace("+", "%20")
                continue
            url_parameters[condition.column_name] = condition.values[0]

        return (route_id, url_parameters, {})

    # def set_next_page_data_from_response(
    #     self,
    #     next_page_data: dict[str, Any],
    #     query: Query,
    #     response: requests.Response,
    # ) -> None:
    #     """
    #     Update the next_page_data dictionary with the appropriate data needed to fetch the next page of records.

    #     This method has a very important job, which is to inform clearskies about how to make another API call to fetch the next
    #     page of records.  The way this happens is by updating the `next_page_data` dictionary in place with whatever pagination
    #     information is necessary.  Note that this relies on next_page_data being passed by reference, hence the need to update
    #     it in place.  That means that you can do this:

    #     ```python
    #     next_page_data["some_key"] = "some_value"
    #     ```

    #     but if you do this:

    #     ```python
    #     next_page_data = {"some_key": "some_value"}
    #     ```

    #     Then things simply won't work.
    #     """
    #     # Different APIs generally have completely different ways of communicating pagination data, but one somewhat common
    #     # approach is to use a link header, so let's support that in the base class.
    #     if "link" not in response.headers:
    #         return
    #     next_link = [rel for rel in response.headers["link"].split(",") if 'rel="next"' in rel]
    #     if not next_link:
    #         return
    #     parsed_next_link = urllib.parse.urlparse(next_link[0].split(";")[0].strip(" <>"))
    #     query_parameters = urllib.parse.parse_qs(parsed_next_link.query)
    #     if self.pagination_parameter_name not in query_parameters:
    #         raise ValueError(
    #             f"Configuration error with {self.__class__.__name__}!  I am configured to expect a pagination key of '{self.pagination_parameter_name}.  However, when I was parsing the next link from a response to get the next pagination details, I could not find the designated pagination key.  This likely means that backend.pagination_parameter_name is set to the wrong value.  The link in question was "
    #             + parsed_next_link.geturl()
    #         )
    #     next_page_data[self.pagination_parameter_name] = query_parameters[self.pagination_parameter_name][0]

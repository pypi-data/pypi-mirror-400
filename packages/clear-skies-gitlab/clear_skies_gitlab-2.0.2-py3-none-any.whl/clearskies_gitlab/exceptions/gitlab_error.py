from clearskies.exceptions import ClientError


class CredentialError(ClientError):
    """Throw exception if something goes wrong for fetching the credentials from Akeyless."""

    def __init__(self, key_name: str) -> None:
        """Create specific message for Credential Issue."""
        super().__init__(f"Could not retrieve {key_name}")


class InvalidCredentialError(ClientError):
    """Throw exception if the token isn't valid anymore."""

    def __init__(self) -> None:
        """Create specific message for InvalidCredentialError Issue."""
        super().__init__("Gitlab token for was not valid - please contact Cimpress security and privacy")


class MethodNotImplementedError(NotImplementedError):
    """Error if Method is not implemented in the Gitlab api for endpoint."""

    def __init__(self, method: str, endpoint: str, version: str = "v1") -> None:
        """Create error with method and endpoint on version."""
        super().__init__(f"Method: {method} is not implemented for {endpoint} in {version}.")


class GitlabResourceError(ValueError):
    """Error if resource could be found."""

    def __init__(self, endpoint: str, resource_name: str) -> None:
        """Create error if resource name is not specified for endpoint."""
        super().__init__(
            f"The Gitlab API for endpoint {endpoint} requires searching by a column named {resource_name}, but it was missing in the query"
        )


class GitlabResponseError(ValueError):
    """Error if response of Gitlab is wrong."""

    def __init__(self, status_code: int, message: bytes) -> None:
        """Create error with request info."""
        super().__init__(f"Failed request.  Status code: {status_code}, message: {message.decode()}")


class GitlabParamMissingError(ValueError):
    """Error if param is missing."""

    def __init__(self, param_name: str, table_name: str) -> None:
        """Create error with param and table name."""
        super().__init__(f"Must provide the {param_name} to add the member to when updating a {table_name}")

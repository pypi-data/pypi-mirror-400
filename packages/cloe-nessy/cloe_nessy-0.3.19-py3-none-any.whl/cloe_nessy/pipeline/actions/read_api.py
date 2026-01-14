from collections.abc import Mapping
from typing import Any, cast

from pydantic import ConfigDict, validate_call
from requests.auth import AuthBase, HTTPBasicAuth

from ...clients.api_client import PaginationConfig, PaginationConfigData
from ...clients.api_client.auth import AzureCredentialAuth, ChainedAuth, EnvVariableAuth, SecretScopeAuth
from ...integration.reader import APIReader, RequestSet
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


def process_auth(
    auth: Mapping[str, str | Mapping[str, str] | list[Mapping[str, str]]] | AuthBase | None,
) -> AuthBase | None:
    """Processes the auth parameter to create an AuthBase object."""
    result: AuthBase | None = None

    if isinstance(auth, list):
        auths = [process_auth(sub_auth) for sub_auth in auth]
        result = ChainedAuth(*auths)
    elif isinstance(auth, dict):
        match auth.get("type"):
            case "basic":
                result = HTTPBasicAuth(auth["username"], auth["password"])
            case "secret_scope":
                result = SecretScopeAuth(auth["header_template"], auth["secret_scope"])
            case "env":
                result = EnvVariableAuth(auth["header_template"])
            case "azure_oauth":
                result = AzureCredentialAuth(
                    scope=auth["scope"],
                    client_id=auth["client_id"],
                    client_secret=auth["client_secret"],
                    tenant_id=auth["tenant_id"],
                )
            case _:
                raise ValueError(
                    "Invalid auth type specified. Supported types are: basic, secret_scope, env, azure_oauth"
                )
    else:
        if isinstance(auth, AuthBase):
            result = auth  # Assume it's already an AuthBase instance

    return result


class ReadAPIAction(PipelineAction):
    """Reads data from an API and loads it into a Spark DataFrame.

    This action executes HTTP requests (optionally paginated) in parallel using the
    [`APIReader`][cloe_nessy.integration.reader.api_reader] and returns a DataFrame
    containing the response payloads plus request/response metadata. No intermediate
    files are written.

    Example:
        === "Basic Usage"
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: my/endpoint/
            ```

        === "Usage with Parameters and Headers"
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: my/endpoint/
                    method: GET
                    timeout: 90
                    headers:
                        Accept: application/json
                        X-Request: foo
                    params:
                        q: widget
                        include: details
            ```

        === "Usage with Authentication (can be chained)"
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: my/endpoint/
                    auth:
                        - type: basic
                          username: my_username
                          password: my_password
                        - type: env
                          header_template:
                            "X-API-Key": "<ENV_VAR_NAME>"
                        - type: secret_scope
                          secret_scope: my_secret_scope
                          header_template:
                            "X-ORG-Token": "<SECRET_NAME>"
                        - type: azure_oauth
                          client_id: my_client_id
                          client_secret: my_client_secret
                          tenant_id: my_tenant_id
                          scope: <entra-id-client-id>
            ```
            The above will combine credentials (via `ChainedAuth`) so that headers from `env`/`secret_scope`
            are merged and auth flows like Basic / Azure OAuth are applied to each request.

        === "Extracting a Nested Field (key)"
            If the API returns a large JSON object but you only want a nested list (e.g. `data.items`):
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: reports/
                    key: data.items
            ```

        === "Pagination (Supported: page_based, limit_offset)"
            Only `page_based` and `limit_offset` strategies are currently supported. You may also
            supply the shared/advanced options `check_field`, `next_page_field`, `max_page`,
            `pages_per_array_limit`, and `preliminary_probe`.

            **1) Page-Based Pagination**
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: items/
                    params:
                        page: 1              # starting page (optional; defaults to 1)
                        per_page: 100
                    pagination:
                        strategy: page_based
                        page_field: page     # required
                        # Shared/advanced (optional):
                        check_field: results           # e.g. list to check for emptiness
                        next_page_field: info.has_next # boolean flag; if present it is trusted
                        max_page: -1                   # -1 = all pages
                        pages_per_array_limit: 2       # chunk output rows every 2 pages
                        preliminary_probe: false       # set true to pre-scan/build all page params
            ```
            This issues requests like:
            ```
            GET .../items/?page=1&per_page=100
            GET .../items/?page=2&per_page=100
            ...
            ```

            **2) Limit/Offset Pagination**
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: products/
                    params:
                        limit: 50
                        offset: 0
                    pagination:
                        strategy: limit_offset
                        limit_field: limit       # required
                        offset_field: offset     # required
                        # Shared/advanced (optional):
                        check_field: data.items
                        next_page_field: page_info.has_next
                        max_page: -1
                        pages_per_array_limit: -1
                        preliminary_probe: false
            ```
            This issues requests like:
            ```
            GET .../products/?limit=50&offset=0
            GET .../products/?limit=50&offset=50
            GET .../products/?limit=50&offset=100
            ...
            ```

            **Using `preliminary_probe` to pre-compute all pages**
            If `preliminary_probe: true` is set, the reader will first probe the API to determine
            the final page (using `check_field` and/or `next_page_field`) and then fan out one request
            per page/offset—useful when driving fully parallel execution:
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://api.example.com/
                    endpoint: orders/
                    params:
                        limit: 100
                        offset: 0
                    pagination:
                        strategy: limit_offset
                        limit_field: limit
                        offset_field: offset
                        check_field: data
                        preliminary_probe: true
                    max_concurrent_requests: 16
            ```

        === "Retries and Concurrency"
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: heavy/endpoint/
                    max_retries: 3           # network/5xx retry count
                    backoff_factor: 2        # exponential backoff multiplier
                    max_concurrent_requests: 16
                    timeout: 60
            ```

        === "Default Headers on All Requests"
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: v1/resources
                    default_headers:
                        X-Client: my-pipeline
                        Accept: application/json
                    headers:
                        X-Request: custom
            ```

        === "Deriving Requests from Context (multiple dynamic requests)"
            When `requests_from_context: true`, distinct rows from the upstream `context.data`
            are converted into individual requests (enabling heterogeneous endpoints/params).
            The DataFrame must have columns: `endpoint`, `params`, `headers`, `data`, `json_body`.

            ```yaml
            # Upstream step produces rows like:
            # | endpoint        | params                  | headers | data | json_body |
            # | "u/123/profile" | {"verbose": "true"}     |  null   | null |   null    |
            # | "u/456/profile" | {"verbose": "false"}    |  null   | null |   null    |

            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    requests_from_context: true
                    method: GET
                    timeout: 45
            ```

    Output:
        The action returns a Spark DataFrame with one column `json_response` (ArrayType).
        Each element contains:
        ```json
        {
          "response": "<json string of the API payload (optionally reduced by 'key')>",
          "__metadata": {
            "timestamp": "YYYY-MM-DD HH:MM:SS.ssssss",
            "base_url": "https://some_url.com/api/",
            "url": "https://some_url.com/api/my/endpoint/?q=...",
            "status_code": 200,
            "reason": "OK",
            "elapsed": 0.123,
            "endpoint": "my/endpoint/",
            "query_parameters": { "q": "..." }
          }
        }
        ```
        When pagination is enabled and `pages_per_array_limit` > 0, responses are chunked
        into arrays of that many pages; otherwise all pages for a request are grouped together.

    Validation & Errors:
        - `base_url` must be provided.
        - Either `endpoint` must be provided **or** `requests_from_context` must be `true`.
        - If `requests_from_context` is `true`, `context.data` must be present and non-empty.
        - Pagination config:
            - `strategy` must be `page_based` or `limit_offset` (other strategies are not yet supported).
            - For `page_based`, `page_field` is required.
            - For `limit_offset`, both `limit_field` and `offset_field` are required.

    !!! warning "Secret information"
        Don't write sensitive information like passwords or tokens directly in the pipeline configuration.
        Use secret scopes or environment variables instead.
    """

    name: str = "READ_API"

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def run(
        self,
        context: PipelineContext,
        *,
        base_url: str | None = None,
        auth: Mapping[str, str | Mapping[str, str] | list[Mapping[str, str]]] | None = None,
        endpoint: str | None = None,
        default_headers: dict[str, Any] | None = None,
        method: str = "GET",
        key: str | None = None,
        timeout: int = 30,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        pagination: PaginationConfigData | None = None,
        max_retries: int = 0,
        backoff_factor: int = 0,
        max_concurrent_requests: int = 8,
        requests_from_context: bool = False,
        **_: Any,
    ) -> PipelineContext:
        """Executes API requests in parallel by using mapInPandas.

        We do NOT write intermediate files; instead we directly return the responses
        as rows in a Spark DataFrame.


        Args:
            context: The pipeline context used to carry data between actions.
            base_url: The base URL for all API requests.
            auth: Authentication configuration, which may be a simple header map,
                a nested map for different auth scopes, or a list thereof.
            endpoint: The specific path to append to the base URL for this call.
            default_headers: Headers to include on every request.
            method: HTTP method to use.
            key: JSON field name to extract from each response.
            timeout: Request timeout in seconds.
            params: Query parameters to append to the URL.
            headers: Additional request-specific headers.
            data: Form-encoded body to send.
            json_body: JSON-encoded body to send.
            pagination: Configuration for paginated endpoints.
            max_retries: Number of times to retry on failure.
            backoff_factor: Multiplier for retry backoff delays.
            max_concurrent_requests: Maximum number of parallel API calls.
            requests_from_context: Whether to derive request parameters from context data.

        Returns:
            The updated context, with the read data as a DataFrame.

        Raises:
            ValueError: If no base URL is provided.
            ValueError: If neither an endpoint nor context-derived requests are specified.
            ValueError: If context-derived requests are enabled but no data is present in context.
        """
        deserialized_auth = process_auth(auth)
        pagination_config = PaginationConfig(**pagination) if pagination is not None else None

        if base_url is None:
            raise ValueError("A value for base_url must to be supplied")

        if endpoint is None and not requests_from_context:
            raise ValueError("A value for endpoint must to be supplied")

        api_reader = APIReader(
            base_url=base_url,
            auth=deserialized_auth,
            default_headers=default_headers,
            max_concurrent_requests=max_concurrent_requests,
        )

        dynamic_requests: list[RequestSet] | None = None

        if requests_from_context:
            if not context.data:
                raise ValueError("Cannot generate requests from the context without a DataFrame in the context.")

            dynamic_requests = [
                cast(RequestSet, row.asDict())
                for row in context.data.select(
                    "endpoint",
                    "params",
                    "headers",
                    "data",
                    "json_body",
                )
                .distinct()
                .collect()
            ]

        df = api_reader.read(
            endpoint=endpoint,
            method=method,
            key=key,
            timeout=timeout,
            params=params,
            headers=headers,
            data=data,
            json_body=json_body,
            pagination_config=pagination_config,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            dynamic_requests=dynamic_requests,
        )

        row_count = df.count()
        self._console_logger.info(f"API requests completed. Final row count = {row_count}.")

        return context.from_existing(data=df)

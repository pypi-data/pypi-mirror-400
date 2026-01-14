import json
from collections.abc import Generator
from datetime import datetime
from typing import Any, cast

import pandas as pd
from pyspark.sql import types as T
from requests.auth import AuthBase
from typing_extensions import TypedDict

from cloe_nessy.session import DataFrame

from ...clients.api_client import APIClient, APIResponse, PaginationConfig, PaginationStrategy, PaginationStrategyType
from ...clients.api_client.exceptions import (
    APIClientConnectionError,
    APIClientError,
    APIClientHTTPError,
    APIClientTimeoutError,
)
from .reader import BaseReader


class RequestSet(TypedDict):
    """The format for dynamic requests."""

    endpoint: str
    params: dict[str, Any]
    headers: dict[str, Any] | None
    data: dict[str, Any] | None
    json_body: dict[str, Any] | None


class MetadataEntry(TypedDict):
    """An entry for metadata."""

    timestamp: str
    base_url: str
    url: str
    status_code: int
    reason: str
    elapsed: float
    endpoint: str
    query_parameters: dict[str, str]


class ResponseMetadata(TypedDict):
    """The metadata response."""

    __metadata: MetadataEntry


class ResponseData(TypedDict):
    """The response."""

    response: str
    __metadata: MetadataEntry


class APIReader(BaseReader):
    """Utility class for reading an API into a DataFrame with pagination support.

    This class uses an APIClient to fetch paginated data from an API and load it into a Spark DataFrame.

    Attributes:
        api_client: The client for making API requests.
    """

    OUTPUT_SCHEMA = T.StructType(
        [
            T.StructField(
                "json_response",
                T.ArrayType(
                    T.StructType(
                        [
                            T.StructField("response", T.StringType(), True),
                            T.StructField(
                                "__metadata",
                                T.StructType(
                                    [
                                        T.StructField("base_url", T.StringType(), True),
                                        T.StructField("elapsed", T.DoubleType(), True),
                                        T.StructField("reason", T.StringType(), True),
                                        T.StructField("status_code", T.LongType(), True),
                                        T.StructField("timestamp", T.StringType(), True),
                                        T.StructField("url", T.StringType(), True),
                                        T.StructField("endpoint", T.StringType(), True),
                                        T.StructField(
                                            "query_parameters",
                                            T.MapType(T.StringType(), T.StringType(), True),
                                            True,
                                        ),
                                    ]
                                ),
                                True,
                            ),
                        ]
                    )
                ),
                True,
            )
        ]
    )

    def __init__(
        self,
        base_url: str,
        auth: AuthBase | None = None,
        default_headers: dict[str, str] | None = None,
        max_concurrent_requests: int = 8,
    ):
        """Initializes the APIReader object.

        Args:
            base_url: The base URL for the API.
            auth: The authentication method for the API.
            default_headers: Default headers to include in requests.
            max_concurrent_requests: The maximum concurrent requests. Defaults to 8.
        """
        super().__init__()
        self.base_url = base_url
        self.auth = auth
        self.default_headers = default_headers
        self.max_concurrent_requests = max_concurrent_requests

    @staticmethod
    def _get_pagination_strategy(config: PaginationConfig | dict[str, str]) -> PaginationStrategy:
        """Return the appropriate pagination strategy."""
        if isinstance(config, PaginationConfig):
            config = config.model_dump()  # PaginationStrategy expects a dict

        pagination_strategy: PaginationStrategy = PaginationStrategyType[config["strategy"]].value(config)
        return pagination_strategy

    @staticmethod
    def _get_metadata(
        response: APIResponse, base_url: str, endpoint: str, params: dict[str, Any] | None = None
    ) -> ResponseMetadata:
        """Creates a dictionary with metadata from an APIResponse.

        Creates a dictionary containing metadata related to an API response. The metadata includes the current timestamp,
        the base URL of the API, the URL of the request, the HTTP status code, the reason phrase,
        and the elapsed time of the request in seconds.

        Args:
            response: The API response object containing the metadata to be added.
            base_url: The base url.
            endpoint: The endpoint.
            params: The parameters to be passed to the query.

        Returns:
            The dictionary containing metadata of API response.
        """
        params = params or {}
        metadata: ResponseMetadata = {
            "__metadata": {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "base_url": base_url,
                "url": response.url,
                "status_code": response.status_code,
                "reason": response.reason,
                "elapsed": response.elapsed.total_seconds(),
                "endpoint": endpoint,
                "query_parameters": params.copy(),
            }
        }
        return metadata

    @staticmethod
    def _paginate(
        api_client: APIClient,
        endpoint: str,
        method: str,
        key: str | None,
        params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        timeout: int,
        max_retries: int,
        backoff_factor: int,
        pagination_config: PaginationConfig,
    ) -> Generator[ResponseData]:
        """Paginates through an API endpoint based on the given pagination strategy."""
        strategy = APIReader._get_pagination_strategy(pagination_config)

        query_parameters = params
        current_page = 1

        while True:
            if pagination_config.max_page != -1 and current_page > pagination_config.max_page:
                break

            response = api_client.request(
                method=method,
                endpoint=endpoint,
                params=query_parameters,
                headers=headers,
                data=data,
                json=json_body,
                timeout=timeout,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
                raise_for_status=False,
            )

            response_data = {"response": json.dumps(response.to_dict(key))} | APIReader._get_metadata(
                response, api_client.base_url, endpoint, query_parameters
            )

            yield cast(ResponseData, response_data)

            if not strategy.has_more_data(response):
                break

            query_parameters = strategy.get_next_params(query_parameters)
            current_page += 1

    @staticmethod
    def _read_from_api(
        api_client: APIClient,
        endpoint: str,
        method: str,
        key: str | None,
        timeout: int,
        params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        max_retries: int,
        backoff_factor: int,
    ) -> list[list[ResponseData]]:
        try:
            response = api_client.request(
                method=method,
                endpoint=endpoint,
                timeout=timeout,
                params=params,
                headers=headers,
                data=data,
                json=json_body,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
            )
            response_data = [
                [
                    cast(
                        ResponseData,
                        {"response": json.dumps(response.to_dict(key))}
                        | APIReader._get_metadata(response, api_client.base_url, endpoint, params),
                    )
                ]
            ]
            return response_data

        except (APIClientHTTPError, APIClientConnectionError, APIClientTimeoutError) as e:
            raise RuntimeError(f"API request failed: {e}") from e
        except APIClientError as e:
            raise RuntimeError(f"An error occurred while reading the API data: {e}") from e
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}") from e

    @staticmethod
    def _read_from_api_with_pagination(
        api_client: APIClient,
        endpoint: str,
        method: str,
        key: str | None,
        timeout: int,
        params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        pagination_config: PaginationConfig,
        max_retries: int,
        backoff_factor: int,
    ) -> list[list[ResponseData]]:
        all_data: list[list[ResponseData]] = []
        all_data_temp: list[ResponseData] = []

        try:
            for response_data in APIReader._paginate(
                api_client=api_client,
                method=method,
                endpoint=endpoint,
                key=key,
                timeout=timeout,
                params=params,
                headers=headers,
                data=data,
                json_body=json_body,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
                pagination_config=pagination_config,
            ):
                all_data_temp.append(response_data)
                if (
                    len(all_data_temp) >= pagination_config.pages_per_array_limit
                    and pagination_config.pages_per_array_limit != -1
                ):
                    all_data.append(all_data_temp)
                    all_data_temp = []

            if all_data_temp:
                all_data.append(all_data_temp)

            return all_data

        except (APIClientHTTPError, APIClientConnectionError, APIClientTimeoutError) as e:
            raise RuntimeError(f"API request failed: {e}") from e
        except APIClientError as e:
            raise RuntimeError(f"An error occurred while reading the API data: {e}") from e
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}") from e

    def read(
        self,
        *,
        endpoint: str | None = None,
        method: str = "GET",
        key: str | None = None,
        timeout: int = 30,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        pagination_config: PaginationConfig | None = None,
        max_retries: int = 0,
        backoff_factor: int = 1,
        dynamic_requests: list[RequestSet] | None = None,
        **_: Any,
    ) -> DataFrame:
        """Reads data from an API endpoint and returns it as a DataFrame.

        Args:
            endpoint: The endpoint to send the request to.
            method: The HTTP method to use for the request.
            key: The key to extract from the JSON response.
            timeout: The timeout for the request in seconds.
            params: The query parameters for the request.
            headers: The headers to include in the request.
            data: The form data to include in the request.
            json_body: The JSON data to include in the request.
            pagination_config: Configuration for pagination.
            max_retries: The maximum number of retries for the request.
            backoff_factor: Factor for exponential backoff between retries.
            options: Additional options for the createDataFrame function.
            dynamic_requests: .

        Returns:
            DataFrame: The Spark DataFrame containing the read data in the json_object column.

        Raises:
            RuntimeError: If there is an error with the API request or reading the data.
        """
        api_client = APIClient(
            base_url=self.base_url,
            auth=self.auth,
            default_headers=self.default_headers,
            pool_maxsize=self.max_concurrent_requests,
        )

        if dynamic_requests or getattr(pagination_config, "preliminary_probe", False):
            if not dynamic_requests:
                if not endpoint:
                    raise ValueError("endpoint parameter must be provided.")
                dynamic_requests = [
                    {
                        "endpoint": endpoint,
                        "params": params or {},
                        "headers": headers,
                        "data": data,
                        "json_body": json_body,
                    }
                ]

            return self._read_dynamic(
                api_client=api_client,
                dynamic_requests=dynamic_requests,
                method=method,
                key=key,
                timeout=timeout,
                pagination_config=pagination_config,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
            )

        params = params if params is not None else {}

        if not endpoint:
            raise ValueError("endpoint parameter must be provided.")

        if pagination_config is not None:
            response_data = self._read_from_api_with_pagination(
                api_client=api_client,
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
            )

        else:
            response_data = self._read_from_api(
                api_client=api_client,
                endpoint=endpoint,
                method=method,
                key=key,
                timeout=timeout,
                params=params,
                headers=headers,
                data=data,
                json_body=json_body,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
            )

        return self._spark.createDataFrame(data=[(response,) for response in response_data], schema=self.OUTPUT_SCHEMA)

    def _read_dynamic(
        self,
        api_client: APIClient,
        dynamic_requests: list[RequestSet],
        method: str,
        key: str | None,
        timeout: int,
        pagination_config: PaginationConfig | None,
        max_retries: int,
        backoff_factor: int,
    ) -> DataFrame:
        def _process_partition(pdf_iter):
            for pdf in pdf_iter:
                for _, row in pdf.iterrows():
                    endpoint = row["endpoint"]
                    params = row["params"] or {}
                    headers = row["headers"] or {}
                    data = row["data"] or {}
                    json_body = row["json_body"] or {}

                    if any([pagination_config is None, getattr(pagination_config, "preliminary_probe", False)]):
                        response_data = APIReader._read_from_api(
                            api_client=api_client,
                            endpoint=endpoint,
                            method=method,
                            key=key,
                            timeout=timeout,
                            params=params,
                            headers=headers,
                            data=data,
                            json_body=json_body,
                            max_retries=max_retries,
                            backoff_factor=backoff_factor,
                        )
                    else:
                        response_data = APIReader._read_from_api_with_pagination(
                            api_client=api_client,
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
                        )

                    yield pd.DataFrame(data=[(response,) for response in response_data])

        if pagination_config is not None and getattr(pagination_config, "preliminary_probe", False):
            pagination_strategy = APIReader._get_pagination_strategy(pagination_config)

            def make_request(
                endpoint: str,
                params: dict[str, Any],
                headers: dict[str, Any] | None,
                data: dict[str, Any] | None,
                json_body: dict[str, Any] | None,
            ) -> APIResponse:
                return api_client.request(
                    method=method,
                    endpoint=endpoint,
                    params=params,
                    headers=headers,
                    data=data,
                    json=json_body,
                    timeout=timeout,
                    max_retries=max_retries,
                    backoff_factor=backoff_factor,
                    raise_for_status=False,
                )

            extended_dynamic_requests: list[RequestSet] = []
            for request in dynamic_requests:
                probed_params_items = pagination_strategy.probe_max_page(
                    **request,
                    make_request=make_request,
                )
                for probed_params_item in probed_params_items:
                    extended_dynamic_requests.append(
                        {
                            "endpoint": request["endpoint"],
                            "params": probed_params_item,
                            "headers": request["headers"],
                            "data": request["data"],
                            "json_body": request["json_body"],
                        }
                    )

            dynamic_requests = extended_dynamic_requests

        df_requests = self._spark.createDataFrame(
            cast(dict, dynamic_requests),
            schema="endpoint string, params map<string, string>, headers map<string, string>, data map<string, string>, json_body map<string, string>",
        )

        self._console_logger.info(
            f"Repartitioning requests to achieve [ '{self.max_concurrent_requests}' ] concurrent requests ..."
        )
        df_requests = df_requests.repartition(self.max_concurrent_requests)
        total_requests = df_requests.count()

        self._console_logger.info(f"Preparing to perform [ '{total_requests}' ] API requests in parallel ...")

        df_response = df_requests.mapInPandas(_process_partition, schema=self.OUTPUT_SCHEMA)

        return df_response

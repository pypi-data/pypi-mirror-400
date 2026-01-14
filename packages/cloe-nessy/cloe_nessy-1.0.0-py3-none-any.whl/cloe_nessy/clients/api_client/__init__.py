from enum import Enum

from .api_client import APIClient
from .api_response import APIResponse
from .pagination_config import PaginationConfig, PaginationConfigData
from .pagination_strategy import PaginationStrategy

pagination_strategies = {cls.name: cls for cls in PaginationStrategy.__subclasses__()}
PaginationStrategyType = Enum("PaginationStrategyType", pagination_strategies)  # type: ignore[misc]


__all__ = ["APIClient", "APIResponse", "PaginationStrategyType", "PaginationConfig", "PaginationConfigData"]

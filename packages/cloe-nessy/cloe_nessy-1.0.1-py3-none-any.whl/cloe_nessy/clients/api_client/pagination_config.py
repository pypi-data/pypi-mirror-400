from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import TypedDict


class PaginationStrategyConfigData(TypedDict, total=False):
    """Shared config across all strategies."""

    check_field: str | None  # e.g. "results" or "data.items"
    next_page_field: str | None  # e.g. "info.next_page"
    max_page: int  # hard cap (reader also enforces)
    pages_per_array_limit: int  # chunking behavior for output arrays
    preliminary_probe: bool  # enable probe_max_page pre-scan


class LimitOffsetPaginationConfigData(PaginationStrategyConfigData, total=False):
    """Config for limit-offset pagination."""

    limit_field: str  # e.g. "limit" or "page_size"
    offset_field: str  # e.g. "offset" or "cursor"


class PageBasedPaginationConfigData(PaginationStrategyConfigData, total=False):
    """Config for page-based pagination."""

    page_field: str  # e.g. "page"


class PaginationConfigData(TypedDict, total=False):
    """Top-level config (what your Pydantic model or dict can accept)."""

    strategy: str  # "limit_offset" | "page_based" | ...
    # strategy-specific fields:
    limit_field: str
    offset_field: str
    page_field: str
    # shared/advanced fields:
    check_field: str | None
    next_page_field: str | None
    max_page: int
    pages_per_array_limit: int
    preliminary_probe: bool


class PaginationConfig(BaseModel):
    """Configuration model for pagination options."""

    strategy: str = Field(..., description="Pagination strategy (limit_offset, page_based, cursor_based, etc.)")
    check_field: str | None = Field(None, description="Field to check for emptiness of response.")
    next_page_field: str | None = Field(None, description="Field that indicates there is a next page.")
    limit_field: str | None = Field(
        None, description="Name of the limit parameter field for items per page or request."
    )
    offset_field: str | None = Field(
        None, description="Name of the offset parameter field for items per page or request."
    )
    page_field: str | None = Field(None, description="Name of the page parameter field.")
    max_page: int = Field(-1, description="Amount of pages to fetch. If not set, will fetch all available data.")
    pages_per_array_limit: int = Field(-1, description="Maximum number of pages per array.")
    preliminary_probe: bool = Field(
        False, description="Whether to perform a preliminary probe to determine the total number of pages."
    )

    @field_validator("strategy", mode="before")
    @classmethod
    def _validate_strategy(cls, v: str) -> str:
        """Validates the pagination strategy."""
        supported_strategies = ["limit_offset", "page_based", "cursor_based", "time_based"]
        if v not in supported_strategies:
            if v in ["cursor_based", "time_based"]:
                raise NotImplementedError("cursor_based and time_based are not yet supported.")
            supported_str = ", ".join(supported_strategies)
            raise ValueError(f"Unsupported pagination strategy: {v}. Supported strategies: {supported_str}")
        return v

    @model_validator(mode="after")
    def _validate_strategy_config(self) -> Self:
        """Validates the configuration of the pagination strategy."""
        if self.strategy == "limit_offset" and any(field is None for field in [self.limit_field, self.offset_field]):
            raise ValueError(f"Both <limit_field> and <offset_field> must be set for strategy '{self.strategy}'")
        if self.strategy == "page_based" and self.page_field is None:
            raise ValueError(f"<page_field> must be set for strategy '{self.strategy}'")
        return self

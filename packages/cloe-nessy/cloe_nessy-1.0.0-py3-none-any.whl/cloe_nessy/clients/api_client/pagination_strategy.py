from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from .api_response import APIResponse
from .pagination_config import (
    LimitOffsetPaginationConfigData,
    PageBasedPaginationConfigData,
    PaginationStrategyConfigData,
)


class PaginationStrategy(ABC):
    """Abstract base class for implementing pagination strategies."""

    name = ""

    def __init__(self, config: PaginationStrategyConfigData):
        """Initialize the strategy with a concrete pagination configuration."""
        self._config: PaginationStrategyConfigData = config

    @staticmethod
    def _resolve_path(data: Any, path: str | None) -> Any:
        """Resolve a dotted path (e.g., 'info.next_page') inside a dict, returning None if any segment is missing."""
        if not path:
            return data
        cur = data
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur

    def has_any_data(self, response: APIResponse) -> bool:
        """Return True if the current page contains data.

        If 'check_field' is configured, truthiness of that field is used;
        otherwise, truthiness of the entire response payload is used.
        """
        payload = response.to_dict()
        check_field = self._config.get("check_field")
        if check_field:
            value = self._resolve_path(payload, check_field)
            return bool(value)
        return bool(payload)

    def has_more_pages(self, response: APIResponse) -> bool | None:
        """Return True/False if 'next_page_field' is configured; return None if not configured."""
        next_field = self._config.get("next_page_field")
        if not next_field:
            return None
        payload = response.to_dict()
        value = self._resolve_path(payload, next_field)
        return bool(value)

    def has_more_data(self, response: APIResponse) -> bool:
        """Return True if there is more data to fetch.

        Prefers explicit next-pointer semantics via 'next_page_field'. If not configured,
        falls back to presence of current-page data.
        """
        has_next = self.has_more_pages(response)
        if has_next is not None:
            return has_next
        return self.has_any_data(response)

    @abstractmethod
    def get_next_params(self, current_params: Any) -> Any:
        """Generate the next set of parameters for the API request."""
        pass

    @abstractmethod
    def probe_max_page(
        self,
        endpoint: str,
        params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        make_request: Callable[
            [str, dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None], APIResponse
        ],
    ) -> list[dict[str, Any]]:
        """Find and return the list of parameter maps for all available pages."""
        pass


class LimitOffsetStrategy(PaginationStrategy):
    """Implementation of the limit-offset pagination strategy."""

    name = "limit_offset"

    def __init__(self, config: LimitOffsetPaginationConfigData):
        """Initialize the limit/offset strategy with its configuration."""
        super().__init__(config)
        self._config: LimitOffsetPaginationConfigData = config

    def get_next_params(self, current_params: dict[str, Any]) -> dict[str, Any]:
        """Return parameters for the next page by advancing 'offset' by 'limit'."""
        limit_field = self._config["limit_field"]
        offset_field = self._config["offset_field"]

        limit = int(current_params[limit_field])
        offset = int(current_params[offset_field])

        current_params[offset_field] = offset + limit
        return current_params

    def _aligned_double(self, current_offset: int, limit_val: int) -> int:
        """Return a next offset that roughly doubles progress while remaining aligned to 'limit'."""
        if current_offset == 0:
            return limit_val
        return ((current_offset // limit_val) + 1) * limit_val * 2

    def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        make_request: Callable[
            [str, dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None], APIResponse
        ],
    ) -> APIResponse:
        """Invoke the provided request callable with the given arguments."""
        return make_request(endpoint, params, headers, data, json_body)

    def _expansion_phase(
        self,
        endpoint: str,
        base_params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        make_request: Callable[
            [str, dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None], APIResponse
        ],
        initial_offset: int,
        limit_val: int,
        offset_field: str,
        limit_field: str,
        max_steps: int = 64,
    ) -> tuple[bool, int | None, int, bool]:
        """Perform exponential probing to locate a valid range of offsets.

        Returns:
            seen_valid: whether any page contained data
            low_offset: last offset known to be valid (None if none)
            current_offset: offset at which probing ended
            broke_on_no_more: True if an explicit 'no more pages' signal ended probing
        """
        seen_valid = False
        low_offset: int | None = None
        current_offset = initial_offset
        broke_on_no_more = False

        for _ in range(max_steps):
            new_params = base_params.copy()
            new_params[offset_field] = current_offset
            new_params[limit_field] = limit_val

            resp = self._request(endpoint, new_params, headers, data, json_body, make_request)
            valid_now = self.has_any_data(resp)
            has_next = self.has_more_pages(resp)

            if not valid_now:
                break

            seen_valid = True
            low_offset = current_offset

            if has_next is False:
                broke_on_no_more = True
                break

            current_offset = self._aligned_double(current_offset, limit_val)

        return seen_valid, low_offset, current_offset, broke_on_no_more

    def _binary_search_last_valid_offset(
        self,
        endpoint: str,
        base_params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        make_request: Callable[
            [str, dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None], APIResponse
        ],
        low_valid_offset: int,
        high_invalid_offset: int,
        limit_val: int,
        offset_field: str,
        limit_field: str,
        max_steps: int = 64,
    ) -> int:
        """Binary search for the last valid offset between a known-valid low bound and an invalid/safety high bound."""
        low = low_valid_offset
        high = max(high_invalid_offset, low + limit_val)

        for _ in range(max_steps):
            if low + limit_val >= high:
                break

            mid = ((low + high) // 2 // limit_val) * limit_val
            if mid <= low:
                mid = low + limit_val
            if mid >= high:
                break

            p = base_params.copy()
            p[offset_field] = mid
            p[limit_field] = limit_val
            resp = self._request(endpoint, p, headers, data, json_body, make_request)

            if self.has_any_data(resp):
                low = mid
            else:
                high = mid

        return low

    def _build_offset_pages(
        self,
        base_params: dict[str, Any],
        initial_offset: int,
        last_valid_offset: int,
        limit_val: int,
        offset_field: str,
        limit_field: str,
    ) -> list[dict[str, Any]]:
        """Build and return the list of parameter maps for all offsets from the initial offset to the last valid offset."""
        if last_valid_offset < initial_offset:
            return []
        page_count = ((last_valid_offset - initial_offset) // limit_val) + 1
        if page_count <= 0:
            return []

        out: list[dict[str, Any]] = []
        for i in range(page_count):
            p = base_params.copy()
            p[offset_field] = initial_offset + i * limit_val
            p[limit_field] = limit_val
            out.append(p)
        return out

    def probe_max_page(
        self,
        endpoint: str,
        params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        make_request: Callable[
            [str, dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None], APIResponse
        ],
    ) -> list[dict[str, Any]]:
        """Find the maximum page available.

        Works with either:
        - a data list field (via config['check_field']), or
        - an explicit next-page pointer (via config['next_page_field']).

        If both are present, a page is considered valid if it has data, and probing
        stops after the last valid page when 'next_page_field' indicates no more.
        """
        offset_field = self._config["offset_field"]
        limit_field = self._config["limit_field"]

        initial_offset = max(0, int(params.get(offset_field, 0)))
        limit_val = int(params[limit_field])

        if limit_val <= 0:
            p = params.copy()
            p[offset_field] = initial_offset
            p[limit_field] = limit_val
            return [p]

        seen_valid, low_offset, current_offset, broke_on_no_more = self._expansion_phase(
            endpoint,
            params,
            headers,
            data,
            json_body,
            make_request,
            initial_offset,
            limit_val,
            offset_field,
            limit_field,
        )

        if not seen_valid or low_offset is None:
            return []

        if broke_on_no_more:
            high_offset = low_offset + limit_val
        else:
            high_offset = max(current_offset, low_offset + limit_val)

        last_valid_offset = self._binary_search_last_valid_offset(
            endpoint,
            params,
            headers,
            data,
            json_body,
            make_request,
            low_offset,
            high_offset,
            limit_val,
            offset_field,
            limit_field,
        )

        return self._build_offset_pages(params, initial_offset, last_valid_offset, limit_val, offset_field, limit_field)


class PageBasedStrategy(PaginationStrategy):
    """Implementation of page-based pagination strategy."""

    name = "page_based"

    def __init__(self, config: PageBasedPaginationConfigData):
        """Initialize the page-based strategy with its configuration."""
        super().__init__(config)
        self._config: PageBasedPaginationConfigData = config

    def get_next_params(self, current_params: dict[str, Any]) -> dict[str, Any]:
        """Return parameters for the next page by incrementing 'page_field' by 1."""
        page_field = self._config["page_field"]
        current_page = int(current_params[page_field])
        current_params[page_field] = current_page + 1
        return current_params

    def _page_request(
        self,
        endpoint: str,
        base_params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        make_request: Callable[
            [str, dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None], APIResponse
        ],
        page_field: str,
        page_value: int,
    ) -> APIResponse:
        """Send a request for a specific page value."""
        p = base_params.copy()
        p[page_field] = page_value
        return make_request(endpoint, p, headers, data, json_body)

    def _expansion_phase(
        self,
        endpoint: str,
        base_params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        make_request: Callable[
            [str, dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None], APIResponse
        ],
        start_page: int,
        page_field: str,
        max_steps: int = 64,
    ) -> tuple[int, bool, int]:
        """Perform exponential probing to locate a valid range of page numbers.

        Returns:
            last_valid: last page number known to be valid (0 if none)
            broke_on_no_more: True if an explicit 'no more pages' signal ended probing
            current: page number at which probing ended
        """
        last_valid = 0
        current = start_page
        broke_on_no_more = False

        for _ in range(max_steps):
            resp = self._page_request(
                endpoint, base_params, headers, data, json_body, make_request, page_field, current
            )
            valid_now = self.has_any_data(resp)
            has_next = self.has_more_pages(resp)

            if not valid_now:
                break

            last_valid = current

            if has_next is False:
                broke_on_no_more = True
                break

            current = current * 2 if current > 0 else 1

        return last_valid, broke_on_no_more, current

    def _binary_search_last_valid_page(
        self,
        endpoint: str,
        base_params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        make_request: Callable[
            [str, dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None], APIResponse
        ],
        low_valid: int,
        high_invalid_or_safety: int,
        page_field: str,
        max_steps: int = 64,
    ) -> int:
        """Binary search for the last valid page number between a known-valid low bound and an invalid/safety high bound."""
        low = low_valid
        high = max(high_invalid_or_safety, low + 1)

        for _ in range(max_steps):
            if low + 1 >= high:
                break

            mid = (low + high) // 2
            resp = self._page_request(endpoint, base_params, headers, data, json_body, make_request, page_field, mid)

            if self.has_any_data(resp):
                low = mid
            else:
                high = mid

        candidate = low

        if candidate + 1 < high:
            resp = self._page_request(
                endpoint, base_params, headers, data, json_body, make_request, page_field, candidate + 1
            )
            if self.has_any_data(resp):
                candidate += 1

        return candidate

    def _build_page_list(
        self,
        base_params: dict[str, Any],
        start_page: int,
        max_page: int,
        page_field: str,
    ) -> list[dict[str, Any]]:
        """Build and return the list of parameter maps for all pages from start_page to max_page inclusive."""
        if max_page < start_page:
            return []
        out: list[dict[str, Any]] = []
        for page in range(start_page, max_page + 1):
            p = base_params.copy()
            p[page_field] = page
            out.append(p)
        return out

    def probe_max_page(
        self,
        endpoint: str,
        params: dict[str, Any],
        headers: dict[str, Any] | None,
        data: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        make_request: Callable[
            [str, dict[str, Any], dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None], APIResponse
        ],
    ) -> list[dict[str, Any]]:
        """Find the maximum page available.

        Honors both 'check_field' (data-present) and 'next_page_field' (explicit next pointer).
        If probing stops because 'next_page_field' is False, no forward-check beyond that point is performed.
        """
        page_field = self._config["page_field"]

        start_page = max(1, int(params.get(page_field, 1)))

        last_valid, broke_on_no_more, current = self._expansion_phase(
            endpoint, params, headers, data, json_body, make_request, start_page, page_field
        )

        if last_valid == 0:
            return []

        if broke_on_no_more:
            max_page = last_valid
            return self._build_page_list(params, start_page, max_page, page_field)

        max_page = self._binary_search_last_valid_page(
            endpoint,
            params,
            headers,
            data,
            json_body,
            make_request,
            low_valid=last_valid,
            high_invalid_or_safety=max(current, last_valid + 1),
            page_field=page_field,
        )
        return self._build_page_list(params, start_page, max_page, page_field)

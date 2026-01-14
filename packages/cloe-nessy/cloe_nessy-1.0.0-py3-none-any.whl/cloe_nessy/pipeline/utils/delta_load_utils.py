"""Utilities for managing delta load information in pipeline runtime context."""

from typing import Any


def set_delta_load_info(
    table_identifier: str,
    delta_load_options: dict[str, Any],
    runtime_info: dict[str, Any],
) -> dict[str, Any]:
    """Update the runtime information dictionary with delta load options for a specific table.

    If delta load options are provided, this function marks the runtime as a delta load and
    stores the options under the given table identifier within the 'delta_load_options' key
    of the runtime_info dictionary.

    The method uses `setdefault("delta_load_options", {})` to ensure that the 'delta_load_options'
    key exists in the runtime_info dictionary. If the key is not present, it initializes it with
    an empty dictionary. This prevents overwriting existing delta load options and allows
    multiple tables' options to be stored without losing previous entries.

    Args:
        table_identifier: The identifier for the table (can be table name or file path).
        delta_load_options: Options specific to the delta load for the table.
        runtime_info: The runtime information dictionary to update.

    Returns:
        The updated runtime information dictionary with delta load details.
    """
    if not delta_load_options:
        return runtime_info

    runtime_info["is_delta_load"] = True
    runtime_info.setdefault("delta_load_options", {})[table_identifier] = delta_load_options

    return runtime_info

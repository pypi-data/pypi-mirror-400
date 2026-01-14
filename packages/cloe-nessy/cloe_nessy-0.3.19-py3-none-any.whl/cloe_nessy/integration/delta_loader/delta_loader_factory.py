from typing import Any

from .delta_load_options import DeltaLoadOptions
from .delta_loader import DeltaLoader
from .strategies import DeltaCDFConfig, DeltaCDFLoader, DeltaTimestampConfig, DeltaTimestampLoader


def consume_delta_load(
    runtime_info: dict[str, Any],
    delta_load_identifier: str | None = None,
) -> None:
    """Consumes a delta load by updating the metadata table.

    Args:
        runtime_info: Runtime information.
        delta_load_identifier: If set, the ConsumeDeltaLoadAction action
            will only consume DeltaLoader transaction for the given
            delta_load_identifier.
    """
    for table_name, value in runtime_info["delta_load_options"].items():
        if delta_load_identifier is None or delta_load_identifier == value.get("delta_load_identifier"):
            delta_loader: DeltaLoader = DeltaLoaderFactory.create_loader(
                table_identifier=table_name,
                options=DeltaLoadOptions(
                    **value,
                ),
            )
            delta_loader.consume_data()


class DeltaLoaderFactory:
    """Factory to create a DeltaLoader instance based on the DeltaLoadOptions."""

    @staticmethod
    def create_loader(table_identifier: str, options: DeltaLoadOptions) -> DeltaLoader:
        """Creates an instance of DeltaLoader, choosing the desired strategy."""
        if options.strategy.upper() == "CDF":
            cdf_config = DeltaCDFConfig(**options.strategy_options)
            return DeltaCDFLoader(
                table_identifier=table_identifier,
                delta_load_identifier=options.delta_load_identifier,
                config=cdf_config,
                metadata_table_identifier=options.metadata_table_identifier,
            )
        if options.strategy.upper() == "TIMESTAMP":
            timestamp_config = DeltaTimestampConfig(**options.strategy_options)
            return DeltaTimestampLoader(
                table_identifier=table_identifier,
                delta_load_identifier=options.delta_load_identifier,
                config=timestamp_config,
                metadata_table_identifier=options.metadata_table_identifier,
            )
        raise ValueError(f"Unknown strategy: {options.strategy}")

from typing import Any

from ...integration.delta_loader import DeltaLoadOptions
from ...integration.reader import CatalogReader
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext
from ..utils import set_delta_load_info


class ReadCatalogTableAction(PipelineAction):
    """Reads a table from Unity Catalog using a specified table identifier and optional reader configurations.

    This function retrieves data from a catalog table using the
    [`CatalogReader`][cloe_nessy.integration.reader.catalog_reader] identified
    by either the `table_identifier` parameter or the `table_metadata` from the
    provided `PipelineContext` of a previous step. The retrieved data is loaded
    into a DataFrame and returned as part of an updated `PipelineContext`.

    Example:
        ```yaml
        Read Sales Table:
            action: READ_CATALOG_TABLE
            options:
                table_identifier: my_catalog.business_schema.sales_table
                options: <options for the CatalogReader read method>
                delta_load_options:
                    strategy: CDF
                    delta_load_identifier: my_delta_load_id
                    strategy_options:
                        deduplication_columns: ["id"]
                        enable_full_load: true
        ```
        === "Batch Read"
            ```yaml
            Read Sales Table:
                action: READ_CATALOG_TABLE
                options:
                    table_identifier: my_catalog.business_schema.sales_table
                    options: <options for the CatalogReader read method>
            ```
        === "Streaming Read"
            ```yaml
            Read Sales Table Stream:
                action: READ_CATALOG_TABLE
                options:
                    table_identifier: my_catalog.business_schema.sales_table
                    stream: true
                    options: <options for the CatalogReader read_stream method>
            ```
        === "Delta Load Read"
            ```yaml
            Read Sales Table:
                action: READ_CATALOG_TABLE
                options:
                    table_identifier: my_catalog.business_schema.sales_table
                    options: <options for the CatalogReader read method>
                delta_load_options:
                    strategy: CDF
                    delta_load_identifier: my_delta_load_id
                    strategy_options:
                        deduplication_columns: ["id"]
                        enable_full_load: true
            ```
    """

    name: str = "READ_CATALOG_TABLE"

    @staticmethod
    def run(
        context: PipelineContext,
        *,
        table_identifier: str | None = None,
        options: dict[str, str] | None = None,
        delta_load_options: dict[Any, Any] | DeltaLoadOptions | None = None,
        stream: bool = False,
        **_: Any,  # define kwargs to match the base class signature
    ) -> PipelineContext:
        """Reads a table from Unity Catalog using a specified table identifier and optional reader configurations.

        Args:
            context: The pipeline's context, which contains
                metadata and configuration for the action.
            table_identifier: The identifier of the catalog table to
                read. If not provided, the function will attempt to use the table
                identifier from the `table_metadata` in the `context`.
            options: A dictionary of options for customizing
                the [`CatalogReader`][cloe_nessy.integration.reader.catalog_reader]
                behavior, such as filters or reading modes. Defaults to None.
            delta_load_options: Options for delta loading, if applicable.
                Configures the [`DeltaLoader`][cloe_nessy.integration.delta_loader].
                behavior, such as filters or reading modes.
            stream: If True, the action will read the table as a stream.
            checkpoint_location: The location for storing
                checkpoints if streaming is enabled.
            trigger_dict: A dictionary specifying the trigger
                configuration for the streaming query, such as processing time or
                continuous processing.
                behavior, such as filters or reading modes. Defaults to None.
            delta_load_options: Options for delta loading, if applicable.
                Configures the [`DeltaLoader`][cloe_nessy.integration.delta_loader].

        Raises:
            ValueError: If neither `table_identifier` nor `table_metadata.identifier` in the `context` is provided.

        Returns:
        An updated pipeline context containing the data read from the catalog table as a DataFrame.
        """
        if not options:
            options = {}

        if not delta_load_options:
            delta_load_options = {}

        if (table_metadata := context.table_metadata) and table_identifier is None:
            table_identifier = table_metadata.identifier
        if table_identifier is None:
            raise ValueError("Table name must be specified or a valid Table object with identifier must be set.")

        if isinstance(delta_load_options, dict):
            delta_options_dict = delta_load_options
            if delta_load_options:
                delta_load_options = DeltaLoadOptions(**delta_load_options)
            else:
                delta_load_options = None
        else:
            delta_options_dict = delta_load_options.model_dump() if delta_load_options else {}

        runtime_info = set_delta_load_info(
            table_identifier=table_identifier,
            delta_load_options=delta_options_dict,
            runtime_info=context.runtime_info or {},
        )

        if isinstance(delta_load_options, dict):
            delta_options_dict = delta_load_options
            if delta_load_options:
                delta_load_options = DeltaLoadOptions(**delta_load_options)
            else:
                delta_load_options = None
        else:
            delta_options_dict = delta_load_options.model_dump() if delta_load_options else {}

        runtime_info = set_delta_load_info(
            table_identifier=table_identifier,
            delta_load_options=delta_options_dict,
            runtime_info=context.runtime_info or {},
        )

        table_reader = CatalogReader()

        if stream:
            context.runtime_info = (context.runtime_info or {}) | {"streaming": True}
            df = table_reader.read_stream(table_identifier=table_identifier, options=options)
        else:
            df = table_reader.read(
                table_identifier=table_identifier,
                options=options,
                delta_load_options=delta_load_options,
            )

        return context.from_existing(data=df, runtime_info=runtime_info)

from typing import Any

from ...integration.delta_loader import DeltaLoadOptions
from ...integration.reader import FileReader
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext
from ..utils import set_delta_load_info


class ReadFilesAction(PipelineAction):
    """Reads files from a specified location.

    If an extension is provided, all files with the given extension will be read
    using the [`FileReader`][cloe_nessy.integration.reader.file_reader]. If no
    extension is provided, the `spark_format` must be set, and all files in the
    location will be read using a DataFrameReader with the specified format.

    Example:
        === "Read files specified by spark_format"
            ```yaml
            Read Files:
                action: READ_FILES
                options:
                    location: json_file_folder/
                    search_subdirs: True
                    spark_format: JSON
            ```
            !!! note "Define Spark Format"
                Use the `spark_format` option to specify the format with which
                to read the files. Supported formats are e.g., `CSV`, `JSON`,
                `PARQUET`, `TEXT`, and `XML`.

        === "Read files specified by extension"
            ```yaml
            Read Files:
                action: READ_FILES
                options:
                    location: csv_file_folder/
                    search_subdirs: True
                    extension: csv
            ```
            !!! note "Define Extension"
                Use the `extension` option to specify the extension of the files
                to read. If not specified, the `spark_format` will be derived from
                the extension.

        === "Read files with a specified spark_format AND extension"
            ```yaml
            Read Files:
                action: READ_FILES
                options:
                    location: file_folder/
                    extension: abc_custom_extension  # specifies the files to read
                    spark_format: CSV  # specifies the format to read the files with
            ```
            !!! note "Define both Extension & Spark Format"
                Use the `extension` option to specify the extension of the files
                to read. Additionally, use the `spark_format` option to specify
                the format with which to read the files.

        === "Read Delta Lake table with delta loading"
            ```yaml
            Read Delta Files:
                action: READ_FILES
                options:
                    location: /path/to/delta/table
                    spark_format: delta
                delta_load_options:
                    strategy: CDF
                    delta_load_identifier: my_delta_files_load
                    strategy_options:
                        deduplication_columns: ["id"]
                        enable_full_load: false
            ```
            !!! note "Delta Loading for Files"
                Use `delta_load_options` when reading Delta Lake tables to enable
                incremental loading. This works with both CDF and timestamp strategies.
    """

    name: str = "READ_FILES"

    @staticmethod
    def run(
        context: PipelineContext,
        *,
        location: str | None = None,
        search_subdirs: bool = False,
        extension: str | None = None,
        spark_format: str | None = None,
        schema: str | None = None,
        add_metadata_column: bool = True,
        options: dict[str, str] | None = None,
        delta_load_options: dict[Any, Any] | DeltaLoadOptions | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Reads files from a specified location.

        Args:
            context: The context in which this Action is executed.
            location: The location from which to read files.
            search_subdirs: Recursively search subdirectories for files
                if an extension is provided.
            extension: The file extension to filter files by.
            spark_format: The format to use for reading the files. If not provided,
                it will be deferred from the file extension.
            schema: The schema of the data. If None, schema is obtained from
                the context metadata.
            add_metadata_column: Whether to include the `__metadata` column with
                file metadata in the DataFrame.
            options: Additional options passed to the reader.
            delta_load_options: Options for delta loading, if applicable. When provided
                for Delta format files, enables incremental loading using delta loader strategies.

        Raises:
            ValueError: If neither `extension` nor `spark_format` are provided, or if
                no location is specified.

        Returns:
            The context after the Action has been executed, containing the read data as a DataFrame.
        """
        if not location:
            raise ValueError("No location provided. Please specify location to read files from.")
        if not options:
            options = dict()
        if not spark_format and not extension:
            raise ValueError("Either spark_format or extension must be provided.")

        if (metadata := context.table_metadata) and schema is None:
            schema = metadata.schema

        # Convert dict to DeltaLoadOptions if needed
        if isinstance(delta_load_options, dict):
            delta_load_options = DeltaLoadOptions(**delta_load_options)

        # Set up runtime info for delta loading
        runtime_info = context.runtime_info or {}
        if delta_load_options:
            # Convert DeltaLoadOptions to dict for runtime info storage
            delta_options_dict = (
                delta_load_options.model_dump()
                if isinstance(delta_load_options, DeltaLoadOptions)
                else delta_load_options
            )
            runtime_info = set_delta_load_info(
                table_identifier=location,  # Use location as identifier for file-based delta loading
                delta_load_options=delta_options_dict,
                runtime_info=runtime_info,
            )

        file_reader = FileReader()
        df = file_reader.read(
            location=location,
            schema=schema,
            extension=extension,
            spark_format=spark_format,
            search_subdirs=search_subdirs,
            options=options,
            add_metadata_column=add_metadata_column,
            delta_load_options=delta_load_options,
        )

        # Only process metadata column if it exists and wasn't using delta loading
        if add_metadata_column and "__metadata" in df.columns:
            read_files_list = [x.file_path for x in df.select("__metadata.file_path").drop_duplicates().collect()]
            if runtime_info is None:
                runtime_info = {"read_files": read_files_list}
            else:
                try:
                    runtime_info["read_files"] = list(set(runtime_info["read_files"] + read_files_list))
                except KeyError:
                    runtime_info["read_files"] = read_files_list

        return context.from_existing(data=df, runtime_info=runtime_info)

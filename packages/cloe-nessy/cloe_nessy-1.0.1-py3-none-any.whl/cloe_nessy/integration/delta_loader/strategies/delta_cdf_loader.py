from pydantic import BaseModel, Field
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from ....models import Column
from ....utils.column_names import generate_unique_column_name
from ..delta_loader import DeltaLoader


class DeltaCDFConfig(BaseModel):
    """This class holds the config for the DeltaCDFLoader.

    Args:
        deduplication_columns: A list of columns used for deduplication.
        from_commit_version: The starting commit version. If None, it starts from the first viable version.
        to_commit_version: The ending commit version. If None, it goes up to the latest version.
        enable_full_load: Enables an initial full load of the target table. If
            no valid delta load history for the table exists, the delta loader
            will do a full load of the target table and set the metadata to the
            newest commit version. This might be useful if the change data feed
            history is incomplete, either because the table was vacuumed or the
            change data feed was enabled later in the lifecycle of the table.
            Otherwise the table will initially be loaded from the first valid
            commit version. When True, `from_commit_version` and
            `to_commit_version` will be ignored on the initial load. Defaults to
            False.
    """

    deduplication_columns: list[str | Column] | None = Field(default=None)
    from_commit_version: int | None = Field(default=None)
    to_commit_version: int | None = Field(default=None)
    enable_full_load: bool = Field(default=False)


class DeltaCDFLoader(DeltaLoader):
    """Implementation of the DeltaLoader interface using CDF strategy.

    Args:
        config: Configuration for the DeltaCDFLoader.
        table_identifier: Identifier for the table to be loaded.
        delta_load_identifier: Identifier for the delta load.
        metadata_table_identifier: Identifier for the metadata table. Defaults to None.
    """

    def __init__(
        self,
        config: DeltaCDFConfig,
        table_identifier: str,
        delta_load_identifier: str,
        metadata_table_identifier: str | None = None,
    ):
        super().__init__(
            table_identifier,
            delta_load_identifier,
            metadata_table_identifier,
        )
        self.config = config
        self.table_reader = self._spark.read

    def _check_cdf_enabled(self, table_identifier: str) -> bool:
        """Checks if Change Data Feed is enabled for the table."""
        try:
            # Try catalog table approach first (for table names like catalog.schema.table)
            if table_identifier.count(".") == 2 and not table_identifier.startswith("/"):
                table_properties = self._query(f"SHOW TBLPROPERTIES {table_identifier}").collect()
                properties_dict = {row["key"]: row["value"] for row in table_properties}
                value = properties_dict.get("delta.enableChangeDataFeed", "false")
                return str(value).lower() == "true"
            # For file paths, use Delta Table API directly
            from delta import DeltaTable  # type: ignore[import-untyped]

            delta_table = DeltaTable.forPath(self._spark, table_identifier)
            properties = delta_table.detail().select("properties").collect()[0]["properties"]
            value = properties.get("delta.enableChangeDataFeed", "false") if properties else "false"
            return str(value).lower() == "true"
        except Exception:
            # If we can't determine CDF status, assume it's not enabled
            return False

    def _has_valid_metadata(self) -> bool:
        """Checks if valid (i.e. non-stale) metadata exists for the delta load."""
        try:
            df = self._spark.sql(f"""
                SELECT * FROM {self.metadata_table_identifier}
                WHERE source_table_identifier = '{self.table_identifier}'
                AND delta_load_identifier = '{self.delta_load_identifier}'
                AND is_processed = true
                AND is_stale = false
            """)
            return not df.isEmpty()
        except Exception as e:
            self._console_logger.warning(f"Error accessing metadata table: {e}")
            return False

    def _get_commit_versions(self) -> tuple[int, int]:
        """Retrieves the starting and ending commit versions for CDF data."""

        def _get_metadata_df() -> DataFrame:
            df = self.table_reader.table(self.metadata_table_identifier)
            return df.filter(
                (F.col("source_table_identifier") == self.table_identifier)
                & (F.col("delta_load_identifier") == self.delta_load_identifier)
                & F.col("is_processed")
                & ~F.col("is_stale"),
            )

        def _get_commit_version(query: DataFrame, version_filter: str | None = None) -> int | None:
            if version_filter is not None:
                query = query.filter(version_filter)
            row = query.selectExpr("max(version)").first()
            if row is None or row[0] is None:
                return None
            # Add type validation before casting
            version_value = row[0]
            if not isinstance(version_value, (int | float)) or isinstance(version_value, bool):
                raise TypeError(f"Expected numeric version, got {type(version_value)}: {version_value}")
            return int(version_value)

        metadata_df = _get_metadata_df()
        self._console_logger.info("Querying table history to find minimum version.")
        min_version_filter = None
        if self.config.from_commit_version is not None:
            min_version_filter = f"version >= {self.config.from_commit_version}"
        # Handle history queries for both catalog tables and file paths
        if self.table_identifier.count(".") == 2 and not self.table_identifier.startswith("/"):
            # Catalog table
            history_query = f"DESCRIBE HISTORY {self.table_identifier}"
        else:
            # File path - need to use delta.`path` format
            history_query = f"DESCRIBE HISTORY delta.`{self.table_identifier}`"

        min_commit_version = _get_commit_version(
            self._query(history_query).filter(
                "operation like 'CREATE%' OR operation = 'TRUNCATE' OR operationParameters.properties like '%delta.enableChangeDataFeed%' "
            ),
            min_version_filter,
        )
        if min_commit_version is None:
            min_commit_version = 0

        max_version_filter = None
        if self.config.to_commit_version is not None:
            max_version_filter = f"version <= {self.config.to_commit_version}"
        max_commit_version = _get_commit_version(
            self._query(history_query),
            max_version_filter,
        )
        if min_commit_version is None or max_commit_version is None:
            raise RuntimeError(f"No valid versions found for Table [ '{self.table_identifier}' ].")

        # Handle cases based on metadata
        if metadata_df.isEmpty():
            # Case 1: No metadata found, read all versions (first delta load)
            self._console_logger.info("No CDF History for this identifier, reading all versions.")
            commit_tuple = (min_commit_version, max_commit_version)
            self._console_logger.info(f"Reading Versions: {commit_tuple}")
            return commit_tuple

        start_commit_row = metadata_df.agg(F.max("end_commit_version")).first()
        start_commit_version = start_commit_row[0] if start_commit_row is not None else None
        if start_commit_version is None:
            # Case 2: No processed version found in metadata, treat as no metadata
            self._console_logger.info("No processed version found in metadata, reading all versions.")
            commit_tuple = (min_commit_version, max_commit_version)
            self._console_logger.info(f"Reading Versions: {commit_tuple}")
            return commit_tuple

        if start_commit_version > max_commit_version:
            # Case 3: Last processed version in metadata is greater than last version in table history
            # This can happen if the table is recreated after the last processed version
            raise RuntimeError(
                f"Table ['{self.table_identifier}'] history and CDF metadata are incompatible. "
                "Either reset the CDF metadata and recreate the target table from scratch,"
                "or repair CDF metadata."
            )

        if min_commit_version > start_commit_version:
            # Case 4: First version in table history is greater than last processed version in metadata
            # This can happen if the table is truncated after the last processed version
            self._console_logger.info("The first version in Table history is greater than the last processed version.")
            commit_tuple = (min_commit_version, max_commit_version)
            self._console_logger.info(f"Reading Versions: {commit_tuple}")
            return commit_tuple

        # Case 5: Normal case, read from last processed version to last available version
        self._console_logger.info("Reading from the last processed version to the last available version.")
        commit_tuple = (start_commit_version, max_commit_version)
        self._console_logger.info(f"Reading Versions: {commit_tuple}")
        return commit_tuple

    def verify(self) -> None:
        """Verify that the source table has the Change Data Feed enabled."""
        self._console_logger.info("Verifying table is enabled for Change Data Feed.")
        if not self._check_cdf_enabled(self.table_identifier):
            raise RuntimeError(f"Table {self.table_identifier} is not enabled for Change Data Feed.")

    def _full_load(self, options: dict[str, str]) -> DataFrame:
        self._console_logger.info(f"Performing full load from source table: {self.table_identifier}")

        # Handle history queries for both catalog tables and file paths
        if self.table_identifier.count(".") == 2 and not self.table_identifier.startswith("/"):
            # Catalog table
            history_query = f"DESCRIBE HISTORY {self.table_identifier}"
        else:
            # File path - need to use delta.`path` format
            history_query = f"DESCRIBE HISTORY delta.`{self.table_identifier}`"

        max_version_query = self._query(history_query).selectExpr("max(version)").first()
        if not max_version_query or max_version_query[0] is None:
            raise RuntimeError(f"No valid versions found for Table [ '{self.table_identifier}' ].")

        # Add type validation before casting
        version_value = max_version_query[0]
        if not isinstance(version_value, (int | float)) or isinstance(version_value, bool):
            raise TypeError(f"Expected numeric version, got {type(version_value)}: {version_value}")

        start_version = 0
        end_version = int(version_value)
        start_commit_timestamp = None
        end_commit_timestamp = None

        self.table_reader.options(**options)

        # Handle table reading for both catalog tables and file paths
        if self.table_identifier.count(".") == 2 and not self.table_identifier.startswith("/"):
            # Catalog table
            df = self.table_reader.table(self.table_identifier)
        else:
            # File path - use load method
            df = self.table_reader.load(self.table_identifier)

        # Cache the DataFrame since it will be used for both counting and returning
        df.cache()
        row_count = df.count()

        self._create_metadata_entry(
            rows=row_count,
            last_read_timestamp=end_commit_timestamp,
            start_version=start_version,
            end_version=end_version,
            start_commit_timestamp=start_commit_timestamp,
            end_commit_timestamp=end_commit_timestamp,
        )

        # Note: We keep the DataFrame cached since it's returned to the caller
        # The caller is responsible for unpersisting when done
        return df

    def _delta_load(self, options: dict[str, str]) -> DataFrame:
        self._console_logger.info(f"Performing delta load from source table: {self.table_identifier}")
        start_version, end_version = self._get_commit_versions()

        self._invalidate_versions()

        if start_version != end_version:
            # Increment version by one to avoid reading the same version twice
            read_start_version = str(start_version + 1)
        else:
            read_start_version = str(start_version)

        self._console_logger.info(f"Reading commit versions: (from: {read_start_version}, to: {str(end_version)})")
        # Set CDF-specific options
        self.table_reader.option("readChangeFeed", "true")
        self.table_reader.option("startingVersion", read_start_version)
        self.table_reader.option("endingVersion", str(end_version))

        # Set additional options
        for key, value in options.items():
            self.table_reader.option(key, str(value))

        # Handle table reading for both catalog tables and file paths
        if self.table_identifier.count(".") == 2 and not self.table_identifier.startswith("/"):
            # Catalog table
            df = self.table_reader.table(self.table_identifier)
        else:
            # File path - use load method
            df = self.table_reader.load(self.table_identifier)

        df = df.filter("_change_type <> 'update_preimage'")

        # Cache the DataFrame as it will be used multiple times
        df.cache()

        # Optimize timestamp extraction by combining operations
        start_commit_timestamp = None
        end_commit_timestamp = None

        if start_version != end_version:
            # Combine both timestamp extractions into a single operation
            timestamp_df = (
                df.filter(F.col("_commit_version").isin([start_version, end_version]))
                .select("_commit_version", "_commit_timestamp")
                .collect()
            )

            timestamp_map = {row["_commit_version"]: row["_commit_timestamp"] for row in timestamp_df}
            start_commit_timestamp = timestamp_map.get(start_version)
            end_commit_timestamp = timestamp_map.get(end_version)

        # Handle case where start_version == end_version
        if start_version == end_version:
            df = df.limit(0)
            row_count = 0
        else:
            row_count = df.count()

        self._create_metadata_entry(
            rows=row_count,
            last_read_timestamp=end_commit_timestamp,
            start_version=start_version,
            end_version=end_version,
            start_commit_timestamp=start_commit_timestamp,
            end_commit_timestamp=end_commit_timestamp,
        )
        # Remove duplicates introduced by CDF. This happens if a row is changed
        # in multiple read versions. We are only interested in the latest
        # change.
        if self.config.deduplication_columns:
            key_columns = self.config.deduplication_columns
            key_column_names = [col.name if isinstance(col, Column) else col for col in key_columns]
            self._console_logger.info(f"Deduplicating with columns: {key_column_names}")
            window_spec = (
                Window.partitionBy(*key_column_names)
                .orderBy(F.desc("_commit_version"))
                .rowsBetween(Window.unboundedPreceding, Window.currentRow)
            )

            row_number_col_name = generate_unique_column_name(existing_columns=set(df.columns), prefix="row_num")

            df = (
                df.withColumn(row_number_col_name, F.row_number().over(window_spec))
                .filter(F.col(row_number_col_name) == 1)
                .drop(row_number_col_name)
            )

        # Strip CDF metadata columns and unpersist the intermediate cache
        result_df = df.drop("_commit_version", "_commit_timestamp")

        # Unpersist the cached DataFrame to free memory
        df.unpersist()

        return result_df

    def read_data(
        self,
        options: dict[str, str] | None = None,
    ) -> DataFrame:
        """Reads data using the CDF strategy.

        Args:
            options: Additional DataFrameReader options.
        """
        self.verify()
        options = options or {}
        do_full_load = self.config.enable_full_load and not self._has_valid_metadata()

        if do_full_load:
            return self._full_load(options)

        return self._delta_load(options)

from datetime import UTC, datetime
from typing import cast

from pydantic import BaseModel, Field, field_validator, model_validator
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from ....integration.writer import CatalogWriter
from ....models import Column
from ..delta_loader import DeltaLoader


class DeltaTimestampConfig(BaseModel):
    """This class holds the config for the DeltaTimestampLoader.

    Args:
        timestamp_filter_cols: A list of columns used for timestamp filtering.
        from_timestamp: The starting timestamp. If None, it starts from the beginning.
        to_timestamp: The ending timestamp. If None, it goes up to the latest timestamp.
        filter_method: The method used for filtering when multiple timestamp
            columns are used. Allowed values are '||', '&&', 'OR', 'AND'. Defaults
            to None.
    """

    timestamp_filter_cols: list[str | Column]
    from_timestamp: datetime | None = Field(default=None)
    to_timestamp: datetime | None = Field(default=None)
    filter_method: str | None = Field(default=None)

    @field_validator("from_timestamp", "to_timestamp", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        """Parses datetime input.

        If a string is parsed, it is expected to be in ISO 8601 format.
        """
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

    @field_validator("filter_method", mode="before")
    @classmethod
    def parse_filter_method(cls, value):
        """Parses and validates filter_method input."""
        value = value.upper()
        match value:
            case "OR":
                value = "||"
            case "AND":
                value = "&&"
            case "||" | "&&":
                # Valid filter methods, do nothing
                pass
            case _:
                raise ValueError("Invalid filter method. Allowed values are '||', '&&', 'OR', 'AND'.")
        return value

    @model_validator(mode="after")
    def check_filter_method(self):
        """Validates that a filter method is set, when more than one timestamp col is used."""
        if len(self.timestamp_filter_cols) > 1 and self.filter_method is None:
            raise ValueError("filter_method must be set when more than one timestamp_filter_cols is used.")
        return self


class DeltaTimestampLoader(DeltaLoader):
    """Implementation of the DeltaLoader interface using timestamp strategy.

    Args:
        config: Configuration for the DeltaTimestampLoader.
        table_identifier: Identifier for the table to be loaded.
        delta_load_identifier: Identifier for the delta load.
        metadata_table_identifier: Identifier for the metadata table. Defaults to None.
    """

    def __init__(
        self,
        config: DeltaTimestampConfig,
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
        self.catalog_writer = CatalogWriter()

    def _get_last_timestamp(self) -> datetime:
        """Retrieves last read timestamp for delta load."""
        self._console_logger.info(f"Fetchin last read timestamp for table [ '{self.table_identifier}' ].")
        df = self.table_reader.table(self.metadata_table_identifier)
        row = (
            df.filter(
                (F.col("source_table_identifier") == self.table_identifier)
                & (F.col("delta_load_identifier") == self.delta_load_identifier)
                & F.col("is_processed")
                & ~F.col("is_stale"),
            )
            .agg(F.max("last_read_timestamp"))
            .first()
        )
        last_timestamp = row[0] if row is not None else None
        if last_timestamp is None:
            return datetime.fromtimestamp(0)
        return cast(datetime, last_timestamp)

    def verify(self) -> None:
        """Verify that the source table has the Change Data Feed enabled."""
        self._console_logger.info("Verifying that table has all configured timestamp columns.")
        df = self._spark.read.table(self.table_identifier)
        missing_columns = [col for col in self.config.timestamp_filter_cols if col not in df.columns]
        if missing_columns:
            raise RuntimeError(
                f"Timestamp filter Columns not found in Table {self.table_identifier} : {', '.join(str(col) for col in missing_columns)}.",
            )

    def read_data(
        self,
        options: dict[str, str] | None = None,
    ) -> DataFrame:
        """Reads data using the Timestamp strategy.

        Args:
            options: Additional DataFrameReader options.
        """
        if options is None:
            options = {}

        last_read_timestamp = self.config.to_timestamp or datetime.now(UTC)

        from_timestamp = self._get_last_timestamp()
        if self.config.from_timestamp and self.config.from_timestamp > from_timestamp:
            from_timestamp = self.config.from_timestamp
        self._invalidate_versions()

        self.table_reader.options(**options)
        df = self.table_reader.table(self.table_identifier)
        if from_timestamp != datetime.fromtimestamp(0):
            df = df.filter(
                f" {self.config.filter_method} ".join(
                    [f"{col} >= '{from_timestamp.isoformat()}'" for col in self.config.timestamp_filter_cols],
                ),
            )
        if last_read_timestamp == from_timestamp:
            # to avoid reading multiple times
            df = df.limit(0)
        else:
            df = df.filter(
                f" {self.config.filter_method} ".join(
                    [f"{col} < '{last_read_timestamp.isoformat()}'" for col in self.config.timestamp_filter_cols],
                ),
            )

        self._create_metadata_entry(
            rows=df.count(),
            last_read_timestamp=last_read_timestamp,
        )

        return df

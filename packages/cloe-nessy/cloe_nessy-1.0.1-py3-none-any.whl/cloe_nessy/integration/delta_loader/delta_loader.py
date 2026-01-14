from abc import ABC, abstractmethod
from datetime import datetime
from functools import partial

from delta import DeltaTable  # type: ignore[import-untyped]
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from ...integration.writer import CatalogWriter
from ...logging import LoggerMixin
from ...object_manager import TableManager
from ...session import SessionManager
from .delta_loader_metadata_table import DeltaLoaderMetadataTable


class DeltaLoader(ABC, LoggerMixin):
    """Base class for delta load operations.

    Args:
        table_identifier: Identifier for the table to be loaded.
        delta_load_identifier: Identifier for the delta load.
        metadata_table_identifier: Identifier for the metadata table. If None,
            the metadata_table_identifier will be derived from the table identifier:
            `<table_catalog>.<table_schema>.metadata_delta_load`.
    """

    def __init__(
        self,
        table_identifier: str,
        delta_load_identifier: str,
        metadata_table_identifier: str | None = None,
    ):
        self._spark = SessionManager.get_spark_session()
        self._console_logger = self.get_console_logger()
        self.table_identifier = table_identifier
        self.delta_load_identifier = delta_load_identifier
        self.metadata_table_identifier = (
            metadata_table_identifier
            or f"{self.table_identifier.split('.')[0]}.{self.table_identifier.split('.')[1]}.metadata_delta_load"
        )
        table_manager = TableManager()
        table_manager.create_table(table=DeltaLoaderMetadataTable(identifier=self.metadata_table_identifier))

    @abstractmethod
    def read_data(
        self,
        options: dict[str, str] | None = None,
    ) -> DataFrame:
        """Reads data incrementally using a strategy.

        Args:
            options: Additional DataFrameReader options.
        """
        pass

    @abstractmethod
    def verify(self) -> None:
        """Verify that the source table qualifies for the delta load strategy."""
        pass

    def _query(self, query: str) -> DataFrame:
        df = self._spark.sql(query)
        return df

    def _create_metadata_entry(
        self,
        *,
        rows: int,
        last_read_timestamp: datetime | None = None,
        start_version: int | None = None,
        end_version: int | None = None,
        start_commit_timestamp: datetime | None = None,
        end_commit_timestamp: datetime | None = None,
    ) -> None:
        """Creates an entry in the metadata table for the delta load."""
        self._console_logger.info(
            f"Creating metadata entry for table: [ {self.table_identifier} ] with Delta Load Identifier: [ {self.delta_load_identifier} ]",
        )
        metadata_df = self._spark.range(1)
        metadata_df = metadata_df.select(
            F.lit(rows).alias("rows").cast("bigint"),
            F.lit(False).alias("is_processed"),
            F.lit(False).alias("is_stale"),
            F.lit(self.table_identifier).alias("source_table_identifier"),
            F.lit(self.delta_load_identifier).alias("delta_load_identifier"),
            F.lit(start_version).alias("start_commit_version"),
            F.lit(end_version).alias("end_commit_version"),
            F.lit(start_commit_timestamp).alias("start_commit_timestamp_utc"),
            F.lit(end_commit_timestamp).alias("end_commit_timestamp_utc"),
            F.lit(last_read_timestamp).alias("last_read_timestamp"),
            F.current_timestamp().alias("__DCR"),
            F.current_timestamp().alias("__DMR"),
        ).withColumn(
            "BK",
            F.md5(
                F.concat_ws(
                    "-",
                    F.col("source_table_identifier"),
                    F.col("delta_load_identifier"),
                    F.current_timestamp(),
                ),
            ),
        )
        catalog_writer = CatalogWriter()
        catalog_writer.write(
            df=metadata_df,
            table_identifier=self.metadata_table_identifier,
            mode="append",
        )

    def _invalidate_versions(self) -> None:
        """Invalidate any pending changes in the metadata for the delta load."""
        self._console_logger.info(
            f"Invalidating unprocessed delta load metadata for table: [ {self.table_identifier} ] with Delta Load Identifier: [ {self.delta_load_identifier} ]",
        )
        delta_table = DeltaTable.forName(self._spark, self.metadata_table_identifier)
        delta_table.update(
            condition=(F.col("source_table_identifier") == self.table_identifier)
            & (F.col("delta_load_identifier") == self.delta_load_identifier)
            & ~F.col("is_processed")
            & ~F.col("is_stale"),
            set={"is_stale": F.lit(True), "__DMR": F.current_timestamp()},
        )

    def reset_cdf(self) -> None:
        """Invalidates all changes in the metadata for the delta load."""
        delta_table = DeltaTable.forName(self._spark, self.metadata_table_identifier)
        self._console_logger.info(
            f"Resetting delta load metadata for table: [ {self.table_identifier} ] with Delta Load Identifier: [ {self.delta_load_identifier} ]",
        )
        delta_table.update(
            condition=(F.col("source_table_identifier") == self.table_identifier)
            & (F.col("delta_load_identifier") == self.delta_load_identifier)
            & ~F.col("is_stale"),
            set={"is_stale": F.lit(True), "__DMR": F.current_timestamp()},
        )

    def consume_data(self) -> None:
        """Marks data as consumed in the metadata for the delta load."""
        df = self._spark.table(self.metadata_table_identifier)
        df = df.filter(
            (F.col("source_table_identifier") == self.table_identifier)
            & (F.col("delta_load_identifier") == self.delta_load_identifier)
            & ~F.col("is_processed")
            & ~F.col("is_stale"),
        )
        df = df.groupBy("BK", "delta_load_identifier").agg(F.max("__DCR")).limit(1)
        self._console_logger.info(
            f"Mark metadata for table as processed: [ {self.table_identifier} ] with Delta Load Identifier: [ {self.delta_load_identifier} ].",
        )
        delta_table = DeltaTable.forName(self._spark, self.metadata_table_identifier)
        delta_table.alias("target").merge(df.alias("source"), "target.BK = source.BK").whenMatchedUpdate(
            set={
                "is_processed": F.lit(True),
                "__DMR": F.current_timestamp(),
            },
        ).execute()

    def write_data(self, write_callable: partial):
        """Wrapper to write and consume a delta load."""
        try:
            write_callable()
        except Exception as e:
            raise RuntimeError("Error while writing...") from e
        self.consume_data()

from typing import Any

from pyspark.errors.exceptions.connect import IllegalArgumentException
from pyspark.sql import functions as F
from pyspark.sql.utils import AnalysisException

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformConvertTimestampAction(PipelineAction):
    """This action performs timestamp based conversions.

    Example:
        ```yaml
        Convert Timestamp:
            action: TRANSFORM_CONVERT_TIMESTAMP
            options:
                columns:
                    - date
                    - creation_timestamp
                    - current_ts
                source_format: unixtime_ms
                target_format: timestamp
        ```
    """

    name: str = "TRANSFORM_CONVERT_TIMESTAMP"

    def run(
        self,
        context: PipelineContext,
        *,
        columns: list[str] | str | None = None,
        source_format: str = "",
        target_format: str = "",
        **_: Any,
    ) -> PipelineContext:
        """Converts column(s) from a given source format to a new format.

        Args:
            context: Context in which this Action is executed.
            columns: A column name or a list of column names that should be converted.
            source_format: Initial format type of the column.
            target_format: Desired format type of the column.
                This also supports passing a format string like `yyyy-MM-dd HH:mm:ss`.

        Raises:
            ValueError: If no column, source_format or target_format are provided.
            ValueError: If source_format or target_format are not supported.

        Returns:
            PipelineContext: Context after the execution of this Action.
        """
        if not columns:
            raise ValueError("No column names provided.")
        if not source_format:
            raise ValueError("No source_format provided.")
        if not target_format:
            raise ValueError("No target_format provided.")
        if context.data is None:
            raise ValueError("Context DataFrame is required.")
        df = context.data

        columns = [columns] if isinstance(columns, str) else columns

        match source_format:
            # convert always to timestamp first
            case "string" | "date" | "unixtime":
                for column in columns:
                    df = df.withColumn(column, F.to_timestamp(F.col(column)))
            case "unixtime_ms":
                for column in columns:
                    df = df.withColumn(column, F.to_timestamp(F.col(column) / 1000))
            case "timestamp":
                pass
            case _:
                raise ValueError(f"Unknown source_format {source_format}")

        match target_format:
            # convert from timestamp to desired output type and format
            case "timestamp":
                pass
            case "unixtime":
                for column in columns:
                    df = df.withColumn(column, F.to_unix_timestamp(F.col(column)))
            case "date":
                for column in columns:
                    df = df.withColumn(column, F.to_date(F.col(column)))
            case _:
                try:
                    for column in columns:
                        df = df.withColumn(column, F.date_format(F.col(column), target_format))
                except (IllegalArgumentException, AnalysisException) as e:
                    raise ValueError(f"Invalid target_format {target_format}") from e

        return context.from_existing(data=df)

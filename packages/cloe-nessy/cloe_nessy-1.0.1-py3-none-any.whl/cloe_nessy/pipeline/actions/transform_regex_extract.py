import re
from typing import Any

import pyspark.sql.functions as F

from cloe_nessy.pipeline.pipeline_action import PipelineAction
from cloe_nessy.pipeline.pipeline_context import PipelineContext


class TransformRegexExtract(PipelineAction):
    r"""Extract values from a specified column in a DataFrame using regex patterns.

    This action extracts values from a column based on a regex pattern and stores
    the result in a new column. Optionally, you can replace the matched pattern in
    the original column with a different string, remove the original column, or add
    a boolean column indicating which rows matched the pattern.

    Example:
        ```yaml
        Extract Action:
            action: TRANSFORM_REGEX_EXTRACT
            options:
                source_column_name: Email
                extract_column_name: org_domain
                pattern: (?<=@)([A-Za-z0-9-]+)
                replace_by: exampledomain.org
        ```

    This action also supports processing multiple columns simultaneously. To use this
    functionality, structure the configuration as a dictionary mapping each source
    column name to its extraction parameters.

    Example:
        ```yaml
        Extract Action:
            action: TRANSFORM_REGEX_EXTRACT
            options:
                extract_columns:
                    Name:
                        pattern: (?<=\w+) (\w+)
                        replace_by: ''
                        extract_column_name: last_name
                        match_info_column_name: has_last_name
                    Email:
                        pattern: @\w+\.\w+
                        extract_column_name: domain
                        keep_original_column: False
        ```

    """

    name: str = "TRANSFORM_REGEX_EXTRACT"

    def run(
        self,
        context: PipelineContext,
        source_column_name: str = "",
        extract_column_name: str = "",
        pattern: str = "",
        keep_original_column: bool = True,
        replace_by: str = "",
        match_info_column_name: str = "",
        extract_columns: dict | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Performs a regex extract (and replace) on a specified column in a DataFrame.

        This function performs a regex extract (and optionally a replace) on one or more columns.

        Args:
            context: The context in which this action is executed.
            source_column_name: Column name to perform the regex replace on.
            pattern: Regex pattern to match.
            replace_by: String that should replace the extracted pattern in the source column.
            extract_column_name: Column name to store the extract, default: <source_column_name>_extract
            keep_original_column: Whether to keep the original column, default: True
            match_info_column_name: Column name to store a boolean column whether a match was found, default: None
            extract_columns: Dictionary of column names and their corresponding 1-column-case.

        Raises:
            ValueError: If any of the required arguments are not provided.
            ValueError: If the regex pattern is invalid.

        Returns:
            PipelineContext: Transformed context with the modified DataFrame.
        """
        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")
        if not extract_columns and not source_column_name:
            raise ValueError("Either extract_columns or source_column_name must be provided.")

        df = context.data

        if source_column_name:
            self._console_logger.info(f"Extracting from column '{source_column_name}' using pattern: {pattern}")
            df = self._process_one_column(
                df,
                source_column_name,
                pattern,
                extract_column_name,
                replace_by,
                keep_original_column,
                match_info_column_name,
            )

        elif isinstance(extract_columns, dict):
            self._console_logger.info(f"Extracting from {len(extract_columns)} columns")
            for one_source_column_name in extract_columns:
                parameter_dict = self._get_default_dict() | extract_columns[one_source_column_name]
                df = self._process_one_column(df, one_source_column_name, **parameter_dict)

        else:
            raise ValueError("extract_columns must be a dictionary. See documentation for proper format.")

        return context.from_existing(data=df)

    def _process_one_column(
        self,
        df,
        source_column_name,
        pattern,
        extract_column_name,
        replace_by,
        keep_original_column,
        match_info_column_name,
    ):
        # Extract the first captured group (group 0 is the entire match)
        matched_group_id = 0

        if not extract_column_name:
            extract_column_name = f"{source_column_name}_extracted"

        if not pattern:
            raise ValueError(f"The regex pattern (pattern) for column {source_column_name} must be provided.")

        # Validate regex pattern
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}' for column {source_column_name}: {e}") from e

        df = df.withColumn(extract_column_name, F.regexp_extract(source_column_name, pattern, matched_group_id))

        if replace_by:
            df = df.withColumn(source_column_name, F.regexp_replace(source_column_name, pattern, replace_by))

        if match_info_column_name:
            # Check if extraction is null or empty string
            df = df.withColumn(
                match_info_column_name,
                F.when((F.col(extract_column_name).isNull()) | (F.col(extract_column_name) == ""), False).otherwise(
                    True
                ),
            )

        if not keep_original_column:
            df = df.drop(source_column_name)

        return df

    def _get_default_dict(self) -> dict[str, Any]:
        """Return default parameters for single column extraction."""
        return {
            "pattern": "",
            "extract_column_name": "",
            "replace_by": "",
            "keep_original_column": True,
            "match_info_column_name": "",
        }

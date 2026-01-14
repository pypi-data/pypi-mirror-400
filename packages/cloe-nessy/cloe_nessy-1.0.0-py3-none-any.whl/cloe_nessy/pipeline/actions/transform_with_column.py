"""Transform action to add or update a column using a SQL expression."""

from typing import Any

from pyspark.sql import functions as F

from cloe_nessy.pipeline.pipeline_action import PipelineAction
from cloe_nessy.pipeline.pipeline_context import PipelineContext


class TransformWithColumnAction(PipelineAction):
    """Add or update a column in the DataFrame using a SQL expression.

    This action uses PySpark's expr() function to evaluate SQL expressions and
    create or update columns in the DataFrame.

    Examples:
        === "Create new column"
            ```yaml
            Create Full Name:
                action: TRANSFORM_WITH_COLUMN
                options:
                    column_name: full_name
                    expression: concat(first_name, ' ', last_name)
            ```

        === "Update existing column"
            ```yaml
            Lowercase Email:
                action: TRANSFORM_WITH_COLUMN
                options:
                    column_name: email
                    expression: lower(email)
            ```

        === "Calculated column"
            ```yaml
            Calculate Total:
                action: TRANSFORM_WITH_COLUMN
                options:
                    column_name: total_price
                    expression: price * quantity * (1 + tax_rate)
            ```

        === "Extract date parts"
            ```yaml
            Extract Year:
                action: TRANSFORM_WITH_COLUMN
                options:
                    column_name: year
                    expression: year(order_date)
            ```
    """

    name: str = "TRANSFORM_WITH_COLUMN"

    def run(
        self,
        context: PipelineContext,
        *,
        column_name: str = "",
        expression: str = "",
        **_: Any,
    ) -> PipelineContext:
        """Add or update a column using a SQL expression.

        Args:
            context: The pipeline context containing the DataFrame
            column_name: Name of the column to create or update
            expression: SQL expression to evaluate for the column value
            **_: Additional unused keyword arguments

        Returns:
            PipelineContext: Updated context with the modified DataFrame

        Raises:
            ValueError: If column_name is not provided
            ValueError: If expression is not provided
            ValueError: If context.data is None
            Exception: If the SQL expression is invalid
        """
        if not column_name:
            raise ValueError("No column_name provided.")

        if not expression:
            raise ValueError("No expression provided.")

        if context.data is None:
            raise ValueError("Data from context is required for transform_with_column")

        self._console_logger.info(f"Adding/updating column '{column_name}' with expression: {expression}")

        df = context.data

        try:
            # Use F.expr() to evaluate the SQL expression
            df = df.withColumn(column_name, F.expr(expression))
        except Exception as e:
            self._console_logger.error(f"Failed to evaluate expression '{expression}' for column '{column_name}': {e}")
            raise

        self._console_logger.info(f"Successfully added/updated column '{column_name}'")

        return context.from_existing(data=df)

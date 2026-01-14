from typing import TYPE_CHECKING

from pyspark.sql.utils import is_remote

if TYPE_CHECKING:
    from pyspark.sql import Column, DataFrame, SparkSession
else:
    # Real runtime imports
    if is_remote():
        from pyspark.sql.connect.dataframe import DataFrame
        from pyspark.sql.connect.session import SparkSession
    else:
        from pyspark.sql import DataFrame, SparkSession

__all__ = ["SparkSession", "DataFrame", "Column"]

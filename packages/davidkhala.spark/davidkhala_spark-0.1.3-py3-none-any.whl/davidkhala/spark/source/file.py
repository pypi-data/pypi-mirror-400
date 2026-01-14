from pyspark.sql.connect.dataframe import DataFrame
from pyspark.sql.connect.session import SparkSession


def read(spark: SparkSession, _path: str) -> DataFrame | None:
    if _path.endswith(".csv"):
        return spark.read.option("header", True).csv(_path)
    elif _path.endswith(".json"):
        return spark.read.json(_path)
    elif _path.endswith(".parquet"):
        return spark.read.parquet(_path)
    return None

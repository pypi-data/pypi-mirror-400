from pyspark.sql.connect.dataframe import DataFrame
from pyspark.sql.connect.session import SparkSession


def sample(spark: SparkSession, density=1) -> DataFrame:
    return spark.readStream.format('rate').option("rowsPerSecond", density).load()

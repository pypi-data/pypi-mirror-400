from pyspark.sql.connect.dataframe import DataFrame
from pyspark.sql.connect.readwriter import DataFrameWriter
from pyspark.sql.connect.session import SparkSession


class Write:
    def __init__(self, df: DataFrame):
        assert not df.isStreaming
        self.batch: DataFrameWriter = df.write

    @property
    def spark(self) -> SparkSession:
        return self.batch._spark

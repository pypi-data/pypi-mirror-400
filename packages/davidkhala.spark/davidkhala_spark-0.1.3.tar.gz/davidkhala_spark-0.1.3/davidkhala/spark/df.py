from pyspark.sql.connect.dataframe import DataFrame as SparkDataFrame
from pyspark.sql.connect.functions import lit


class DataFrame:
    def __init__(self, df: SparkDataFrame):
        self.df = df

    def setColumn(self, column: str, const: str):
        return self.df.withColumn(column, lit(const))

    def profile(self):
        return self.df.describe()
    def __getattr__(self, name):
        return getattr(self.df, name)

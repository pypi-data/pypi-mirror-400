from enum import Enum
from typing import Union

from pyspark.sql.connect.dataframe import DataFrame

from davidkhala.spark.sink import Write


class Mode(Enum):
    append = "append"
    overwrite = "overwrite"
    ignore = "ignore"
    error = "errorifexists"  # default. Throw an exception if data already exists.


class SQLServer(Write):

    def __init__(self, df: DataFrame, *,
                 server: str, database: str, table: str, user: str, password: str,
                 mode: Union[Mode,str] = Mode.error
                 ):
        super().__init__(df)
        self.url = f"jdbc:sqlserver://{server};databaseName={database}"
        self.table = table
        self.mode = mode.value if isinstance(mode,Mode) else Mode(mode).value
        self.properties = {
            "user": user,
            "password": password,
            "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
        }

    def start(self):
        self.batch.jdbc(
            self.url, self.table, self.mode, self.properties
        )

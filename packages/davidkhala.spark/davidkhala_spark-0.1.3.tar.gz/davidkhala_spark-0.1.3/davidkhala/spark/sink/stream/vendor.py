import os

from pyspark import Row
from pyspark.sql.connect.dataframe import DataFrame

from davidkhala.spark.sink.stream import ForeachBatchWriter


class NewRelic(ForeachBatchWriter):
    def __init__(self, license_key=None):
        self.license_key = license_key or os.environ.get('NEW_RELIC_LICENSE_KEY')

    @property
    def on_batch(self):
        s = self.license_key  # cloned string for spark serialize

        def func(df: DataFrame, batch_id: int):
            from davidkhala.newrelic.log import Ingestion
            i = Ingestion(s)
            data = {
                'data': df.toPandas().to_dict(),
                'batch_id': batch_id
            }

            i.send(str(data))

        return func

    @property
    def on_row(self):
        s = self.license_key  # cloned string for spark serialize

        def func(row: Row):
            from davidkhala.newrelic.log import Ingestion
            i = Ingestion(s)
            data = row.asDict(),
            i.send(str(data))

        return func

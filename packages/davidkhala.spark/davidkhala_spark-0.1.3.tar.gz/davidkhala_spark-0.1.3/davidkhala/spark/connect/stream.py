from davidkhala.spark.sink.stream import ForeachBatchWriter
from pyspark.sql.connect.session import SparkSession
from pyspark.sql.connect.dataframe import DataFrame
from pyspark.sql.connect.streaming import StreamingQuery, DataStreamWriter


def startAny(df: DataFrame, writer: ForeachBatchWriter) -> StreamingQuery:
    assert df.isStreaming

    return df.writeStream.foreachBatch(writer.on_batch).start()


class Write:
    def __init__(self, df: DataFrame):
        assert df.isStreaming
        self.stream: DataStreamWriter = df.writeStream

    @property
    def spark(self) -> SparkSession:
        return self.stream._session

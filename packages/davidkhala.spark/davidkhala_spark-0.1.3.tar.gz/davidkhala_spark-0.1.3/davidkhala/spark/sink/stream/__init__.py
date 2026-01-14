from abc import abstractmethod, ABC
from typing import Callable, Protocol

from pyspark.sql.connect.dataframe import DataFrame
from pyspark.sql.types import Row


class ForeachWriter(ABC):
    """
    object class used in DataStreamWriter.foreach(...)
    """

    def open(self, partition_id: int, epoch_id: int) -> bool: pass

    @abstractmethod
    def process(self, row: Row) -> None: ...

    def close(self, error: Exception | None) -> None: pass


class ForeachBatchWriter(Protocol):
    @property
    def on_batch(self) -> Callable[[DataFrame, int], None]: ...

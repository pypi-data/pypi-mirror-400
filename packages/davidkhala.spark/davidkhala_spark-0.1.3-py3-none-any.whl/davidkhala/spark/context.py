from datetime import datetime

from pyspark import SparkContext, SparkConf


class Wrapper(SparkContext):
    sc: SparkContext

    def __init__(self, sc: SparkContext):
        self.sc = sc

    def __getattr__(self, name):
        # Delegate unknown attributes/methods to the wrapped instance
        return getattr(self.sc, name)

    def disconnect(self):
        self.sc.stop()

    @property
    def startTime(self):
        return datetime.fromtimestamp(self.sc.startTime / 1000)

    @property
    def appTime(self) -> int:
        """
        assume local spark app, not YARN
        :return: nanoseconds since unix epoch
        """
        assert self.sc.applicationId.startswith('local-')
        epoch_nano = int(self.sc.applicationId[6:])
        assert epoch_nano > self.sc.startTime
        return epoch_nano

    @staticmethod
    def from_config(conf: SparkConf = SparkConf()):
        return Wrapper(SparkContext.getOrCreate(conf))

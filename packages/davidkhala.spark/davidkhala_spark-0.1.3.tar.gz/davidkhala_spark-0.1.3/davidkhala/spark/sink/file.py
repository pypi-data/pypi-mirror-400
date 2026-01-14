from davidkhala.spark.sink import Write


class Save(Write):
    def parquet(self, *args, **kwargs):
        self.batch.parquet(*args, **kwargs)
    def avro(self, *args, **kwargs):
        self.batch.format('avro').save(*args, **kwargs)
    def orc(self, *args, **kwargs):
        self.batch.orc(*args, **kwargs)

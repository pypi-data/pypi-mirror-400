from pyspark import SparkConf
from pyspark.errors import IllegalArgumentException
from pyspark.sql import SparkSession as JavaSparkSession
from pyspark.sql.connect.session import SparkSession


class Wrapper:
    spark: SparkSession | JavaSparkSession

    def __init__(self, spark):
        self.spark = spark

    def disconnect(self):
        if not self.spark.is_stopped:
            self.spark.stop()

    @property
    def schema(self) -> str:
        """
        :return: current schema full name
        """
        return self.spark.catalog.currentCatalog() + '.' + self.spark.catalog.currentDatabase()

    def __getattr__(self, name):
        # Delegate unknown attributes/methods to the wrapped instance
        return getattr(self.spark, name)


class ServerMore(Wrapper):
    @property
    def appName(self):
        try:
            return self.spark.conf.get("spark.app.name")
        except IllegalArgumentException as e:
            if str(e).splitlines()[0] == "The value of property spark.app.name must not be null":
                return
            else:
                raise e

    @property
    def clusterId(self):
        """almost abstract method"""
        ...


def regular(*, name: str = None, conf: SparkConf = SparkConf()) -> JavaSparkSession:
    """
    Visit https://spark.apache.org/docs/latest/sql-getting-started.html#starting-point-sparksession for creating regular Spark Session
    """
    _ = JavaSparkSession.builder.config(conf=conf)
    if name: _.appName(name)

    return _.getOrCreate()


class Databricks(ServerMore):
    spark: SparkSession
    cluster_id: str

    def __init__(self, workspace_instance_name: str, token: str, cluster_id: str):
        from getpass import getuser
        user_id = getuser()  # can be any
        connection_string = f"sc://{workspace_instance_name}:443/;token={token};x-databricks-cluster-id={cluster_id};user_id={user_id}"
        session = SparkSession.builder.remote(connection_string).getOrCreate()
        super().__init__(session)
        self.cluster_id = cluster_id
        self.user_id = user_id

    @property
    def clusterId(self):
        return self.cluster_id

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json, struct
from pyspark.sql.types import StringType, IntegerType, StructField, StructType,ArrayType,DoubleType
from pathlib import Path
import sys

src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from env.env import KAFKA_BOOTSTRAP_SERVERS, NEWSTOPIC3, NEWSTOPIC4, NEWS4_CHECKPOINT

features_schema = StructType([
    StructField("type", IntegerType(), True),
    StructField("size", IntegerType(), True),
    StructField("indices", ArrayType(IntegerType()), True),
    StructField("values", ArrayType(DoubleType()), True)
])

processed_news_schema = StructType([
    StructField("id", StringType(), True),
    StructField("title", StringType(), True),
    StructField("description", StringType(), True),
    StructField("source_name", StringType(), True),
    StructField("url", StringType(), True),
    StructField("img_url", StringType(), True),
    StructField("publication_date", IntegerType(), True),
    StructField("lang", StringType(), True),
    StructField("author", StringType(), True),
    StructField("prediction", DoubleType(), True),
    StructField("sentiment_label", IntegerType(), True),
    StructField("sentiment_score", DoubleType(), True),
    StructField("category", StringType(), True),

])
print('****************')

spark = SparkSession.builder \
    .appName("ProcessedNewsForwardingApp") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
    .getOrCreate()

def forward_news():
    
    
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", NEWSTOPIC3) \
        .option("startingOffsets", "earliest") \
        .load()   
     
    news_df = kafka_df.selectExpr("CAST(value AS STRING) as json") \
        .select(from_json(col("json"), processed_news_schema).alias("data")) \
        .select("data.*")
    
    news_df=news_df.selectExpr("to_json(struct(*)) AS value")
    
    recommended_news_query = news_df.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("topic", NEWSTOPIC4) \
        .option("checkpointLocation", NEWS4_CHECKPOINT) \
        .trigger(once=True) \
        .start()
    
    recommended_news_query.awaitTermination()

if __name__ == "__main__":
    forward_news()

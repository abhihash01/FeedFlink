from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StringType, StructType, StructField, IntegerType,DoubleType, StringType, DoubleType, ArrayType
from pymongo import MongoClient
from similarity import look_for_similarity
from pathlib import Path
import sys


src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))
from src.db.interaction_db import InteractionDB
from env.env import MONGO_DB_URI,DB_NAME,KAFKA_BOOTSTRAP_SERVERS,NEWSTOPIC3

from src.db.user_db import UserDB


spark = SparkSession.builder \
    .appName("AvailableNewsRecommendationApp") \
    .getOrCreate()

features_schema = StructType([
    StructField("type", IntegerType(), True),
    StructField("size", IntegerType(), True),
    StructField("indices", ArrayType(IntegerType()), True),
    StructField("values", ArrayType(DoubleType()), True)
])


schema = StructType([
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
    StructField("features", features_schema, True),

])
interaction_db=InteractionDB()

def get_seen_and_liked_news(seen_news):
    if seen_news is None:
        seen_news=[]
    print('**********',seen_news)
    news_ids = []
    for news in seen_news:
        for news_id, value in news.items():
            if value == 0 or value == 1:
                news_ids.append(news_id)
    return news_ids


kafka_df = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe",NEWSTOPIC3) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .option("kafka.group.id", "available_news_recommender_group")\
    .load()

processed_news_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")



processed_news_df = processed_news_df.orderBy(col("publication_date").desc())

client = MongoClient(MONGO_DB_URI)
db = client[DB_NAME]
user_preferences_collection = db["users"]


user_db = UserDB()
users = user_db.retrieve_user_preferences()


for user in users:
    user_id = user.id
    categories = user.categories
    sentiments = user.sentiments
    ansa=user.ansa

    seen_and_liked_news_ids = get_seen_and_liked_news(user.seen_news)
 
    filtered_interactions = interaction_db.retrieve_all_interactions(seen_and_liked_news_ids)
    filtered_interactions=[interaction.to_dict()['features'] for interaction in filtered_interactions]






    if not ansa:
        filtered_news_df = filtered_news_df.filter(
            (col('source_name').isNotNull()) &
              (col('source_name') != "")
        )

    

    filtered_news_df = processed_news_df.filter(
        (col('prediction').isin(categories)) 
        &
        (col('sentiment_label').isin(sentiments))


    )

    filtered_news_df.show()


    filtered_news = filtered_news_df.collect()

    recommendations = []

    if not filtered_interactions:
        recommended_news_ids=[news["id"] for news in filtered_news]
    else:
      

        for news in filtered_news:
            news_id = news["id"]
            news_features = news["features"]

            similarity = look_for_similarity(news_features.asDict(), 
                                            filtered_interactions)
            print('similarity=',similarity)
            
            recommendations.append((news_id, similarity))

        recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)
        recommended_news_ids = [values[0] for values in recommendations]

        print('%%%%%%%%%%The recommendations are: ',recommendations)
        
    print('Recommended News ids for:',user.email,':',recommended_news_ids)


    user.recommended_news = recommended_news_ids


    user_preferences_collection.update_one(
        {'_id': user_id},
        {'$set': {'recommended_news': recommended_news_ids}}
    )


spark.stop()

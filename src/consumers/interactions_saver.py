from kafka import KafkaConsumer
import json
from pathlib import Path
import sys
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, DoubleType
from pyspark.sql.functions import struct, collect_list, col
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, udf
from pyspark.sql.types import StructType, StructField, IntegerType


src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from src.models.interaction import Interaction
from src.db.interaction_db import InteractionDB
from src.db.user_db import UserDB
from src.models.interaction import Interaction
from env.env import KAFKA_BOOTSTRAP_SERVERS, NEWSTOPIC5, NEWSTOPIC3,GROUP_TIME_OUT



def store_interactions():
   
    interaction_consumer = KafkaConsumer(
        NEWSTOPIC5,  
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',  
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=GROUP_TIME_OUT,
        group_id="interactions_saver_group",
        enable_auto_commit=False 
    )


    interactions_list = []
    news_features_list = []

 




    for message in interaction_consumer:
        interaction_data = message.value
        print(f"Received interaction message: {interaction_data}")
        interactions_list.append(interaction_data)

    interaction_consumer.commit()


    print(f"Retrieved {len(interactions_list)} interaction messages")

    if len(interactions_list)==0:
        print('No interaction registred in the last 24 hours')
        return

    print('The interactions list is',interactions_list)



    news_consumer = KafkaConsumer(
        NEWSTOPIC3,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=GROUP_TIME_OUT,
        group_id='processed_news_consumer_group',
        enable_auto_commit=False  
    )

    print("Kafka Consumer Initialized")

 
    interaction_db = InteractionDB()

    print("Connected to MongoDB")



    for  message in news_consumer:
        news_data = message.value
        print(f"Received news message : {news_data}")
        news_features_list.append(news_data)

    news_consumer.commit()

    print(f"Processed {len(news_features_list)} news messages")


    user_ids = UserDB().retrieve_user_ids()
    print('User IDs are:', user_ids)

    

    feature_schema = StructType([
        StructField("size", IntegerType(), True),
        StructField("indices", ArrayType(IntegerType()), True),
        StructField("values", ArrayType(DoubleType()), True)
    ])


    interaction_schema = StructType([
        StructField("user_id", StringType(), True),
        StructField("news_id", StringType(), True),
        StructField("action", IntegerType(), True),
        StructField("date", IntegerType(), True),
        StructField("features", feature_schema, True),
    ])


    news_schema = StructType([
        StructField("id", StringType(), True),
        StructField("features", feature_schema, True),
    ])


    interaction_data_list = [(interaction['user_id'], interaction['news_id'], interaction['action'], interaction['date'], interaction.get('features')) for interaction in interactions_list]


    news_data_list = [(news['id'], news['features']) for news in news_features_list]


    interactions_df = spark.createDataFrame(interaction_data_list, schema=interaction_schema)
    news_df = spark.createDataFrame(news_data_list, schema=news_schema)

    news_df = news_df.withColumnRenamed('id', 'news_id').withColumnRenamed('features', 'news_features')

    combined_df = interactions_df.join(news_df, on='news_id', how='left')

    combined_df = combined_df.drop('features').withColumnRenamed('news_features', 'features')
    print('Combined df is',combined_df)
    print('Combined df schema:')
    combined_df.printSchema()
    print('Combined df data:')
    combined_df.show(truncate=False)

    interaction_df=combined_df.select(['news_id','features','date']).dropDuplicates(subset=['news_id']).orderBy('date', ascending=True)


    print('Interaction df schema:')
    interaction_df.printSchema()
    print('Interaction df data:')
    interaction_df.show(truncate=False)

    for row in interaction_df.collect():
        interaction = Interaction(
            news_id=row['news_id'],
            features=row['features'],
            date=row['date']
        )
        interaction_id = interaction_db.insert_interaction(interaction)
        print(f"Inserted interaction with ID: {interaction_id}")


    grouped_df = combined_df.groupBy("user_id", "news_id").agg(
        collect_list(struct("action", "date")).alias("actions")
    )

    print('The grouped df is')
    grouped_df.show(truncate=False)

    def deduplicate(actions):
        actions.sort(key=lambda x: x.date) 
        non_neutral_actions = [action for action in actions if action.action != 0]
        if non_neutral_actions:
            return non_neutral_actions[-1] 
        return actions[-1]  

    def deduplicate(actions):
        actions.sort(key=lambda x: x.date)  
        non_neutral_actions = [action for action in actions if action.action != 0]
        if non_neutral_actions:
            return non_neutral_actions[-1] 
        return actions[-1]

   
    deduplicate_udf = udf(deduplicate, StructType([
        StructField("action", IntegerType(), True),
        StructField("date", IntegerType(), True)
        
    ]))

    deduplicated_df = grouped_df.withColumn("deduplicated", deduplicate_udf(col("actions"))).select("user_id", "news_id", "deduplicated.*")

    final_df = deduplicated_df.join(news_df, on='news_id', how='left')

    final_grouped_df = deduplicated_df.groupBy("user_id").agg(
        collect_list(struct("news_id", "action", "date")).alias("interactions")
    )

    print('The final grouped df is')
    final_grouped_df.printSchema()
    final_grouped_df.show(truncate=False)

    final_grouped_rows = final_grouped_df.collect()


    user_db = UserDB()


    for row in final_grouped_rows:
        print('(((((((((((((((((((((((())))))))))))))))))))))))')
        user_id = row['user_id']
        interactions = row['interactions']
        news_actions = {interaction['news_id']: interaction['action'] for interaction in interactions}
        print('News actions:',news_actions)
        user_db.add_seen_news(user_id, news_actions)

    print('***********')
    print('But why')

    


if __name__=="__main__":
    spark = SparkSession.builder.appName("InteractionsStorageApp").getOrCreate()
    store_interactions()
    spark.stop()
    print('Spark session stopped')
    
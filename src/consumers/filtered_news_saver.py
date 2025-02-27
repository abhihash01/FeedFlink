from kafka import KafkaConsumer
import json
from pathlib import Path
import sys


src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from src.models.filtered_news import FilteredNews
from src.db.filtered_news_db import FilteredNewsDB
from env.env import KAFKA_BOOTSTRAP_SERVERS,NEWSTOPIC2,TIME_OUT


def persist_filtered_news():
     

    consumer = KafkaConsumer(
        NEWSTOPIC2, 
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest', 
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5*TIME_OUT,
        group_id="filtered_news_saver_group",
        enable_auto_commit=False  

        
    )

    print("Kafka Consumer Initialized")

    

    filtered_news_list=[]

    
  
  
    for message in consumer:
        print('******')
        filtered_news_data = message.value
        print(f"Received message : {filtered_news_data}")

      
        filtered_news_data['_id'] = filtered_news_data.pop('id')
        filtered_news = FilteredNews.from_dict_persist(filtered_news_data)

        filtered_news_list.append(filtered_news)

    consumer.commit()

    n= len(filtered_news_list)

    if n ==0:
        print('No filtered news registred in the last 24h')

    elif FilteredNewsDB().create_many_filtered_news(filtered_news_list):
        print(f"{n} filtered news saved to MongoDB")
 
    else:
        print('Not able to reach MongoDB')

if __name__=="__main__":
    persist_filtered_news()
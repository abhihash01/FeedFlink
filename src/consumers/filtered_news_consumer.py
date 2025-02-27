from kafka import KafkaConsumer
import json
from pathlib import Path
import sys


src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from env.env import KAFKA_BOOTSTRAP_SERVERS,NEWSTOPIC2


def persist_filtered_news(topics=[NEWSTOPIC2] ,
       servers=KAFKA_BOOTSTRAP_SERVERS):
     
            

    consumer = KafkaConsumer(
        *topics, 
        bootstrap_servers=servers,
        auto_offset_reset='earliest',  
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        
    )

    print("Kafka Consumer Initialized")

   


    

    for n, message in enumerate(consumer):
        print('******')
        filtered_news_data = message.value
        print(f"Received message {n + 1} from topic {NEWSTOPIC2}: {filtered_news_data}")

        

if __name__=="__main__":
    persist_filtered_news()
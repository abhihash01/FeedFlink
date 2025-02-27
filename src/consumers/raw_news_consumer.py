from kafka import KafkaConsumer
import json
import sys
from pathlib import Path


    
src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from env.env import KAFKA_BOOTSTRAP_SERVERS, NEWSTOPIC1

topics = [NEWSTOPIC1]
          

consumer = KafkaConsumer(
    *topics,  
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest', 
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    
)

print(consumer)


n=0


for message in consumer:
    print(f"Received message from topic {message.topic}: {message.value}")
    n+=1
    print(n)


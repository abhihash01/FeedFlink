from kafka import KafkaConsumer
import json
from pathlib import Path
import sys
from pathlib import Path
import sys


src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))
from src.models.interaction import Interaction
from env.env import KAFKA_BOOTSTRAP_SERVERS,NEWSTOPIC5,TIME_OUT


consumer = KafkaConsumer(
    NEWSTOPIC5, 
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',  
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
)

print("Kafka Consumer Initialized")

n=0

for message in consumer:
    interaction_data = message.value
    print(f"Received message {n + 1} from {NEWSTOPIC5}: {interaction_data}")


    interaction = Interaction.from_dict(interaction_data)
    n+=1

print(f"Processed {n} messages")

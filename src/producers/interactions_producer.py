import json
from kafka import KafkaProducer
from pathlib import Path
import sys

src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from src.models.interaction import Interaction
from env.env import KAFKA_BOOTSTRAP_SERVERS, NEWSTOPIC5,LIKED


def send_interaction(interaction):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    interaction_dict = interaction.to_dict()
    producer.send(NEWSTOPIC5, interaction_dict)
    producer.flush()
    print(f"Sent interaction: {interaction_dict}")


if __name__ == "__main__":
    interaction_instance = Interaction(
        news_id='google_news_225',
        user_id='666d7c7cc2c9c814c5597193',
        features=2222,
        action=LIKED
    )
    
    send_interaction(interaction_instance)

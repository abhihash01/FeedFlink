from dotenv import load_dotenv
import json
import os
from pathlib import Path

load_dotenv()

NEWSTOPIC1 = "NewsTopic1"
NEWSTOPIC2 = "NewsTopic2"
NEWSTOPIC3 = "NewsTopic3"
NEWSTOPIC4 = "NewsTopic4"
NEWSTOPIC5 = "NewsTopic5"

SENDER_ADDRESS=os.getenv("SENDER","")
PASSWORD=os.getenv("EMAIL_PASSWORD","")
ADMIN_EMAIL=os.getenv("ADMIN_EMAIL")

API_KEYS = [ os.getenv("NEWSAPI_KEY", "") ]
LANGS = ["en","fr","es"]
PAGE = 1
PAGE_SIZE = 50
HOURS_PERIOD = 25
TOPIC_QUERY = ["health", "finance", "technology", "politics" ]

NULL_REPLACEMENTS = {
        "":None,
        "[Removed]": None,  
        "https://removed.com": None
}

KAFKA_BOOTSTRAP_SERVERS=os.getenv("KAFKA_BOOTSTRAP_SERVERS","localhost:9092")

SPARK_VERSION = "3.5.1"

DB_NAME="news_recommendation_db"

MONGO_DB_URI=os.getenv("MONGO_DB_URI","mongodb://localhost:27017/")
print(MONGO_DB_URI)
LOCALHOST="localhost"
REDIS_HOST=os.getenv("REDIS_HOST",LOCALHOST)
TIME_OUT=1000
GROUP_TIME_OUT=5000
DISLIKED=-1
SEEN=0
LIKED=1

POSITIVE_SENTIMENT=1
NEGATIVE_SENTIMENT=-1
NEUTRAL_SENTIMENT=0


PROJECT_HOME = Path(__file__).parent.parent.resolve()
SRC_PATH = PROJECT_HOME / 'src'

SRC_PATH = Path(os.getenv("SRC_PATH", str(SRC_PATH)))

TRAINED_MODELS_PATH = Path(os.getenv("TRAINED_MODELS_PATH", str(PROJECT_HOME / 'trained_models')))
CATEGORISATION_MODEL_PATH = TRAINED_MODELS_PATH / 'news_categorization_model'

CATEGORIES_JSON_PATH = CATEGORISATION_MODEL_PATH / 'news_categories.json'
CHECKPOINT_DIR = Path(os.getenv("CHECKPOINT_DIR", str(PROJECT_HOME / 'checkpoint-local')))

with open(CATEGORIES_JSON_PATH, 'r', encoding='utf-8') as f:
    category_mapping = json.load(f)

CATEGORIES_MAPPING = {int(k): v for k, v in category_mapping.items()}

SPARK_KAFKA_PACKAGES="org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,\
org.apache.spark:spark-token-provider-kafka-0-10_2.12:3.5.1"

NEWS2_CHECKPOINT = CHECKPOINT_DIR / 'news2'
NEWS4_CHECKPOINT = CHECKPOINT_DIR / 'news4'
RECOMMENDER_CHECKPOINT = SRC_PATH /'consumer' / 'checkpoint' / 'recommender'
NEWS3_CHECKPOINT = CHECKPOINT_DIR / 'news3'
SPARK_CHECKPOINT=PROJECT_HOME / 'src' / 'processors' / 'checkpoint'
NLTK_DATA_PATH=str(PROJECT_HOME / 'nltk_data')
SPARK_CONNECTION_ID="spark-connection"


TIME_START=2
TIME_DAY=0
from pymongo import MongoClient
import sys
from pathlib import Path

src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from src.models.filtered_news import FilteredNews  

from env.env import DB_NAME,MONGO_DB_URI
class FilteredNewsDB:
    def __init__(self, uri=MONGO_DB_URI, db_name=DB_NAME):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def create_filtered_news(self, news):
        news_dict = news.to_dict_persist()
        result = self.db.filtered_news.insert_one(news_dict)
        return result.inserted_id
    
    def create_many_filtered_news(self, news_list):
        news_dicts = [news.to_dict_persist() for news in news_list]
        result = self.db.filtered_news.insert_many(news_dicts)
        return result.inserted_ids

    def find_filtered_news_by_id(self, news_id):
        news_data = self.db.filtered_news.find_one({"news_id": news_id})
        if news_data:
            return FilteredNews.from_dict(news_data)
        return None

    def find_filtered_news_by_title(self, title):
        news_data = self.db.filtered_news.find_one({"title": title})
        if news_data:
            return FilteredNews.from_dict(news_data)
        return None

    def retrieve_all_filtered_news(self):
        news_cursor = self.db.filtered_news.find()
        return [FilteredNews.from_dict(news_data) for news_data in news_cursor]



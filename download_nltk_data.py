from nltk import download, data
from env.env import NLTK_DATA_PATH


data.path = [NLTK_DATA_PATH]

download('wordnet', download_dir=NLTK_DATA_PATH) 
download('vader_lexicon',download_dir=NLTK_DATA_PATH) 



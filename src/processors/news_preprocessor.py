from pyspark.sql.functions import col, lower, regexp_replace, trim, concat_ws, when
from pyspark.ml.feature import StopWordsRemover, Tokenizer
from nltk import download
from pyspark.ml import PipelineModel
from pyspark.sql.types import StructType, StructField, StringType, IntegerType,DoubleType

from pathlib import Path
import sys

src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from env.env import CATEGORISATION_MODEL_PATH

# 
class NewsPreprocessor:
    def __init__(self, lemmatize_udf): 
        self.lemmatize_udf = lemmatize_udf
        self.categorization_pipeline = PipelineModel.load(CATEGORISATION_MODEL_PATH) 

        self.schema= StructType([
            StructField("id", StringType(), True),
            StructField("title", StringType(), True),
            StructField("description", StringType(), True),
            StructField("content", StringType(), True),
            StructField("source_name", StringType(), True),
            StructField("url", StringType(), True),
            StructField("img_url", StringType(), True),
            StructField("publication_date", IntegerType(), True),
            StructField("lang", StringType(), True),
            StructField("author", StringType(), True),
            ])

    def filter(self,raw_articles):
        """
        Clean the raw articles by removing duplicate rows, rows with missing URL, content, or description.
        """
        articles = raw_articles.dropDuplicates(subset=['id']).dropDuplicates(subset=['description']).dropDuplicates(subset=['url']).dropDuplicates(subset=['title'])
        articles = articles.na.drop(subset=['url', 'content', 'description','title'],how='any')
        
        return articles

    def clean(self, filtered_articles):
        """
        Clean the desrcription of the articles.
        """
    
        
        articles = filtered_articles.withColumn(
            "description_cleaned",
            trim(
                regexp_replace(
                    regexp_replace(col("description"), r'[^a-zA-Z0-9\s]', ''),  
                    r'\s+', ' '  
                )
            )
        )
        articles = articles.withColumn("description_cleaned", lower(col("description_cleaned")))
        return articles

    def tokenize(self, cleaned_articles):
        """
        Tokenize the cleaned description text.
        """
        tokenizer = Tokenizer(inputCol="description_cleaned", outputCol="words")
        return tokenizer.transform(cleaned_articles)

    def lemmatize(self, tokenized_articles):
        """
        Apply the lemmatization UDF to the tokenized words.
        """
        df_lemmatized = tokenized_articles.withColumn("lemmas", self.lemmatize_udf(col("words")))
        return df_lemmatized
    
    def stopwords_removal(self, lemmatized_articles):
        """
        Remove stopwords from the lemmatized words.
        """
        remover = StopWordsRemover(inputCol="lemmas", outputCol="description_filtered")
        return remover.transform(lemmatized_articles)

    def transform(self, cleaned_articles, to_str=True):
        """
        Perform tokenization, lemmatization, and stopwords removal on the cleaned articles.
        Optionally convert the filtered words back to a single string.
        """
        cleaned_articles = cleaned_articles.withColumn(
            "img_url",
            when(col("img_url").startswith("http"), col("img_url")).otherwise(None)
        )
        tokenized_data = self.tokenize(cleaned_articles)
        lemmatized_data = self.lemmatize(tokenized_data)
        filtered_data = self.stopwords_removal(lemmatized_data)
        
        if to_str:
            filtered_data = filtered_data.withColumn("description_filtered_str", concat_ws(" ", "description_filtered"))
        
        return filtered_data

    def preprocess(self,filtered_articles, to_str=True):
        """
        Main preprocessing function to clean and transform the filtered articles.
        """
        cleaned_data = self.clean(filtered_articles)
        transformed_data = self.transform(cleaned_data, to_str=to_str)
        return transformed_data

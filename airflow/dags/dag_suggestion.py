from datetime import timedelta
import sys

import airflow

from pathlib import Path

import pendulum
src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from env.env import TIME_START,TIME_DAY,SRC_PATH,SPARK_KAFKA_PACKAGES, SPARK_CONNECTION_ID

from src.airflow_email import success_email,failure_email

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.today('UTC').subtract(days=TIME_DAY).replace(hour=TIME_START+3)
}


dag = airflow.DAG(
    'dag_suggestion',
    default_args=default_args,
    description='A daily dag for retrieving available news and generating news recommendations.',
    schedule_interval=timedelta(days=1),
    catchup = False,
)

task_news4_retrieval =  airflow.providers.apache.spark.operators.spark_submit.SparkSubmitOperator(
    task_id='news4_retrieval',
    conn_id=SPARK_CONNECTION_ID,
    application=f'{SRC_PATH}/processors/processed_news_forwarder.py',
    dag=dag,
    packages=SPARK_KAFKA_PACKAGES,
    deploy_mode="client"
)

task_news4_suggestion =  airflow.providers.apache.spark.operators.spark_submit.SparkSubmitOperator(
    task_id='news4_suggestion',
    conn_id=SPARK_CONNECTION_ID,
    application=f'{SRC_PATH}/consumers/available_news_recommender.py',
    dag=dag,
    packages=SPARK_KAFKA_PACKAGES,
    deploy_mode="client"
)

task_news4_retrieval >> task_news4_suggestion

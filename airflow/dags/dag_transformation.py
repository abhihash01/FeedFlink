
from airflow import DAG



import airflow
from pathlib import Path

import pendulum
from datetime import timedelta
import sys

src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from env.env import TIME_START,TIME_DAY,SRC_PATH,SPARK_KAFKA_PACKAGES,ADMIN_EMAIL, SPARK_CONNECTION_ID
from src.airflow_email import success_email,failure_email

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.today('UTC').subtract(days=TIME_DAY).replace(hour=TIME_START+1)
}


dag = DAG(
    'dag_transformation',
    default_args=default_args,
    description='A DAG for transformation of news',
    schedule_interval=timedelta(days=1),
    catchup = False,
)


task_news1 = airflow.providers.apache.spark.operators.spark_submit.SparkSubmitOperator(
    task_id='news1_processing',
    conn_id=SPARK_CONNECTION_ID,
    application=f'{SRC_PATH}/processors/raw_news_processor.py',
    dag=dag,
    packages=SPARK_KAFKA_PACKAGES,
    deploy_mode="client"
)


task_news2 = airflow.operators.bash.BashOperator(
    task_id='news2_storage',
    bash_command=f'python3 {SRC_PATH}/consumers/filtered_news_saver.py',
    dag=dag
)
task_news1>>task_news2

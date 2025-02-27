import airflow

from datetime import timedelta

import sys
from pathlib import Path

import pendulum

src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from env.env import SRC_PATH,TIME_START,TIME_DAY,ADMIN_EMAIL, SPARK_CONNECTION_ID

from src.airflow_email import success_email,failure_email


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.today('UTC').subtract(days=TIME_DAY).replace(hour=TIME_START+2)
}



dag = airflow.DAG(
    'dag_interactions',
    default_args=default_args,
    description='A daily dag for storage of user interactions with the news articles.' ,
    schedule_interval=timedelta(days=1),
    catchup = False,
)


task_news5 = airflow.providers.apache.spark.operators.spark_submit.SparkSubmitOperator(
    task_id='news5_storage',
    conn_id=SPARK_CONNECTION_ID,
    application=f'{SRC_PATH}/consumers/interactions_saver.py',
    dag=dag,
    deploy_mode="client"
)


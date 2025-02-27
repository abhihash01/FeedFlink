from pathlib import Path
import airflow
import pendulum
from datetime import timedelta

import sys

src_path = Path(__file__).resolve().parents[2]
sys.path.append(str(src_path))

from env.env import SRC_PATH,TIME_START,TIME_DAY,ADMIN_EMAIL

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.today('UTC').subtract(days=TIME_DAY).replace(hour=TIME_START),
}

dag = airflow.DAG(
    'dag_generation',
    default_args=default_args,
    description='Picks up news from different sources',
    schedule=timedelta(days=1),
    catchup = False,
)

task_newsapi = airflow.operators.bash.BashOperator(
    task_id='newsapi',
    bash_command=f'python3 {SRC_PATH}/producers/news_api_producer.py',
    dag=dag
)
task_googleapi = airflow.operators.bash.BashOperator(
    task_id='googleapi',
    bash_command=f'python3 {SRC_PATH}/producers/google_news_producer.py',
    dag=dag,

)

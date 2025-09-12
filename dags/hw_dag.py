import datetime as dt
import os
import sys

from airflow.models import DAG
from airflow.operators.python import PythonOperator

# Where the project lives (the folder with modules/, data/, etc.)
PROJECT_PATH = os.environ.get('PROJECT_PATH', os.path.expanduser('~/airflow_hw'))
os.environ['PROJECT_PATH'] = PROJECT_PATH
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)


def run_pipeline():
    # Lazy import so DAG parsing doesn't fail (import only when the task runs)
    from modules.pipeline import pipeline as _pipeline
    _pipeline()


def run_predict():
    from modules.predict import predict as _predict
    _predict()


args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2022, 6, 10),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=1),
    'depends_on_past': False,
}

with DAG(
    dag_id='car_price_prediction',
    # 15:00 every day
    schedule='0 15 * * *',
    default_args=args,
    catchup=False,
) as dag:

    pipeline_task = PythonOperator(
        task_id='pipeline',
        python_callable=run_pipeline,
    )

    predict_task = PythonOperator(
        task_id='predict',
        python_callable=run_predict,
    )

    pipeline_task >> predict_task

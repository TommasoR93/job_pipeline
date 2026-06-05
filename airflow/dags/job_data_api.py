from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from src.ingestion import main

defaults_arg = {
    "owner" : "data_eng",
    "depends_on_past" : False,
    "retries" : 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure" : False,
    "email_on_retry" : False
}

with DAG(
    dag_id = "job_data_api",
    default_args=defaults_arg,
    start_date=datetime(2025,6,1),
    schedule="@daily",
    catchup=False,
    tags=["api"]
) as dag:
    
    task = PythonOperator(
        task_id="job_data_api_ingestion",
        python_callable=main,
        op_kwargs={
            "date_path": "{{ds}}",
            "run_id": "{{run_id}}"
        }
    )
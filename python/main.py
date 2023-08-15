import sys
from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from datetime import datetime
from airflow.models import XComArg

sys.path.insert(0, "./producers")
sys.path.insert(0, "./consumers")

def create_kafka_producer_task():
    from kafka import KafkaProducer
    import logging

    logger = logging.getLogger('kafka')
    logger.setLevel(logging.WARN)
    return KafkaProducer(bootstrap_servers="localhost:9093")


default_args = {
    "owner": "airflow",
    "start_date": datetime(2021, 1, 1),
    "schedule_interval": "@daily",
    "catchup": False,
}

with DAG(
    dag_id="GPU_DAG",
    default_args=default_args,
    catchup=False,
) as dag:
        
        from producers import megekko, alternate
    
        start_task = PythonOperator(
        task_id="start_task",
        python_callable=lambda: print("Starting DAG execution...")
        )

        producer = PythonVirtualenvOperator(
        task_id="create_kafka_producer_task",
        python_callable=create_kafka_producer_task,
        requirements=["requests", "bs4", 'kafka'],
        provide_context=True,
        )

        scrape_megekko_task = PythonVirtualenvOperator(
        task_id="scrape_megekko_task",
        python_callable=megekko.scrape,  # Assuming you have this function defined
        provide_context=True,
        requirements=["requests", "bs4"],
        op_args=["gtx 4070"]
        )

        scrape_alternate_task = PythonVirtualenvOperator(
        task_id="scrape_alternate_task",
        python_callable=alternate.scrape,  # Assuming you have this function defined
        provide_context=True,
        requirements=["requests", "bs4"],
        op_args=["gtx 4070"]
        )

        send_megekko_to_kafka_task = PythonVirtualenvOperator(
        task_id="send_megekko_to_kafka_task",
        python_callable=megekko.sendToKafka,  # Assuming you have this function defined
        provide_context=True,
        requirements=["requests", "bs4", "kafka"],
        op_args=[XComArg(task_ids='create_kafka_producer_task', key='return_value'), XComArg(task_ids='scrape_megekko_task', key='return_value')]
        )

        send_alternate_to_kafka_task = PythonVirtualenvOperator(
        task_id="send_alternate_to_kafka_task",
        python_callable=megekko.sendToKafka,  # Assuming you have this function defined
        provide_context=True,
        requirements=["requests", "bs4", "kafka"],
        op_args=[XComArg(task_ids='create_kafka_producer_task', key='return_value'), XComArg(task_ids='scrape_alternate_task', key='return_value')]
        )

        end_task = PythonOperator(
        task_id="end_task",
        python_callable=lambda: print("DAG execution finished.")
        )

        start_task >> create_kafka_producer_task >> [scrape_megekko_task, scrape_alternate_task]
        scrape_megekko_task >> send_megekko_to_kafka_task
        scrape_alternate_task >> send_alternate_to_kafka_task
        [send_megekko_to_kafka_task, send_alternate_to_kafka_task] >> end_task






        


import json
import sys
from producers import megekko, alternate, informatique
from kafka import KafkaProducer
import pandas as pd
import logging
import time
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.models import XComArg


logger = logging.getLogger('kafka')
logger.setLevel(logging.WARN)

sys.path.insert(0, "./producers")
sys.path.insert(0, "./consumers")

#print("Starting megekko")
#megekko_data = megekko.scrape("gtx 4070")
#print("Starting alternate")
#alternate_data = alternate.scrape("gtx 4070")
#informatique.scrape("4070")

producer = KafkaProducer(bootstrap_servers="localhost:9093")

#megekko.sendToKafka(producer, megekko_data)

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
    
        start_task = PythonOperator(
        task_id="start_task",
        python_callable=lambda: print("Starting DAG execution...")
        )

        scrape_megekko_task = PythonOperator(
        task_id="scrape_megekko_task",
        python_callable=megekko.scrape,  # Assuming you have this function defined
        provide_context=True,
        op_args=["gtx 4070"]
        )

        scrape_alternate_task = PythonOperator(
        task_id="scrape_alternate_task",
        python_callable=alternate.scrape,  # Assuming you have this function defined
        provide_context=True,
        op_args=["gtx 4070"]
        )

        send_megekko_to_kafka_task = PythonOperator(
        task_id="send_megekko_to_kafka_task",
        python_callable=megekko.sendToKafka,  # Assuming you have this function defined
        provide_context=True,
        op_args=[producer, XComArg(task_ids='scrape_megekko_task', key='return_value')]
        )

        send_alternate_to_kafka_task = PythonOperator(
        task_id="send_alternate_to_kafka_task",
        python_callable=megekko.sendToKafka,  # Assuming you have this function defined
        provide_context=True,
        op_args=[producer, XComArg(task_ids='scrape_alternate_task', key='return_value')]
        )

        end_task = PythonOperator(
        task_id="end_task",
        python_callable=lambda: print("DAG execution finished.")
        )

        start_task >> [scrape_megekko_task, scrape_alternate_task]
        scrape_megekko_task >> send_megekko_to_kafka_task
        scrape_alternate_task >> send_alternate_to_kafka_task
        [send_megekko_to_kafka_task, send_alternate_to_kafka_task] >> end_task






        


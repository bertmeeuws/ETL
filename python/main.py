import sys
from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from datetime import datetime
from airflow.models.xcom_arg import XComArg
sys.path.append("./producers")
sys.path.append("./consumers")
from producers import megekko, alternate
from airflow.models import XCom



def create_kafka_producer_task():
    import logging
    from kafka import KafkaProducer
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

        # scrape_alternate_task = PythonVirtualenvOperator(
        # task_id="scrape_alternate_task",
        # python_callable=alternate.scrape,  # Assuming you have this function defined
        # provide_context=True,
        # requirements=["requests", "bs4"],
        # op_args=["gtx 4070"]
        # )

        send_megekko_to_kafka_task = PythonVirtualenvOperator(
        task_id="send_megekko_to_kafka_task",
        python_callable=megekko.sendToKafka,  # Assuming you have this function defined
        provide_context=True,
        requirements=["requests", "bs4", "kafka"],
        )

        # send_alternate_to_kafka_task = PythonVirtualenvOperator(
        # task_id="send_alternate_to_kafka_task",
        # python_callable=megekko.sendToKafka,  # Assuming you have this function # defined
        # provide_context=True,
        # requirements=["requests", "bs4", "kafka"],
        # op_args=[XComArg(xcom_task_id='create_kafka_producer_task', # key='return_value'), XComArg(xcom_task_id='scrape_alternate_task', # key='return_value')]
        # )

        end_task = PythonOperator(
        task_id="end_task",
        python_callable=lambda: print("DAG execution finished.")
        )

        start_task >> producer >> scrape_megekko_task
        scrape_megekko_task >> send_megekko_to_kafka_task
        send_megekko_to_kafka_task >> end_task






        


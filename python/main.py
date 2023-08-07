import json
import sys
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError
from producers import megekko, alternate
import pandas as pd
import logging
import time

logger = logging.getLogger('kafka')
logger.setLevel(logging.WARN)

sys.path.insert(0, "./producers")
sys.path.insert(0, "./consumers")

megekko_data = megekko.scrape("gtx 1650")

alternate_data = alternate.scrape("gtx 4070")

for product in alternate_data:
    print(product.to_dict())

# producer = KafkaProducer(bootstrap_servers="localhost:9093")

# megekko.sendToKafka(producer, megekko_data)


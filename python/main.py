import json
import sys
from producers import megekko, alternate, informatique
from kafka import KafkaProducer
import pandas as pd
import logging
import time

logger = logging.getLogger('kafka')
logger.setLevel(logging.WARN)

sys.path.insert(0, "./producers")
sys.path.insert(0, "./consumers")

print("Starting megekko")
#megekko_data = megekko.scrape("gtx 4070")
print("Starting alternate")
#alternate_data = alternate.scrape("gtx 4070")
informatique.scrape("4070")

producer = KafkaProducer(bootstrap_servers="localhost:9093")

#megekko.sendToKafka(producer, megekko_data)


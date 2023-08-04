import json
import sys

# dump into kafka
from kafka import KafkaProducer
from kafka.errors import KafkaError
from producers import megekko

sys.path.insert(0, "./producers")

megekko_json = megekko.scrape("gtx 1650")

producer = KafkaProducer(bootstrap_servers="localhost:9093")

for el in megekko_json:
    byte_array = json.dumps(el.to_dict()).encode('utf-8')

    future = producer.send("products", byte_array)

    try:
        # Wait for the result and check if the message was sent successfully
        record_metadata = future.get(timeout=10)
        print(f"Message sent successfully to topic {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
    except KafkaError as e:
        print(f"Failed to send message: {e}")

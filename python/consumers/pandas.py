from kafka import KafkaConsumer
import pandas as pd
import time
import json

consumer = KafkaConsumer(
    "products",
    bootstrap_servers="localhost:9093",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="my-group",
)

count = 0
df = pd.DataFrame()

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if bool(msg) == False:
            continue
        else:
            # Check if the message is a dictionary (JSON format)
            if isinstance(msg, dict):
                json_data = msg  # It's already a dictionary (JSON format)
            else:
                json_data = json.loads(msg.value().decode('utf-8'))

            print(json_data)  # Replace this with your own processing logic

            
except KeyboardInterrupt:
    pass
finally:
    consumer.close()

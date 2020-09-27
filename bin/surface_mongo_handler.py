import sys,os
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(BASE_DIR)

from adapters.mongo_adapter import MongoAdapter
import argparse
import pika
import json
import datetime as dt

mongo_adapter = MongoAdapter()
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
read_channel = connection.channel()
read_channel.exchange_declare(exchange='surface_mongo_exchange',
                         exchange_type='direct')

parser = argparse.ArgumentParser(description='MongoDB Writer process.')
parser.add_argument('--read_queue', type=str, default='batch')


if __name__ == '__main__':
    args = parser.parse_args()
    read_queue = args.read_queue
    read_channel.queue_declare(queue=read_queue, exclusive=False)
    read_channel.queue_bind(exchange='surface_mongo_exchange', queue=read_queue, routing_key=read_queue)

    def callback(ch, method, properties, body):
        try:
            input_msg = json.loads(body)
            if input_msg.get('symbol'):
                print(f"\nReceived input message for ticker {input_msg['symbol']}")
            time_delta = dt.datetime.now() - dt.datetime.strptime(input_msg['start_time'], "%Y-%m-%d %H:%M:%S.%f")
            mongo_record_id = mongo_adapter.insert_doc(doc=input_msg, db_name='main_db', collection='surfaces',
                                                       return_id=True)
            if input_msg.get('profile_env'):
                if input_msg.get('profile_env') == "True":
                    print(f"{time_delta.total_seconds()} seconds have elapsed")
            print(f"\nInserted surface for ticker {input_msg['symbol']} to MongoDB with id {mongo_record_id}")
        except:
            msg = f"Could not insert surface for ticker {input_msg['symbol']} at {dt.datetime.now()}"
            raise Exception(msg)

    read_channel.basic_consume(queue=read_queue, on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for surfaces. To exit press CTRL+C')

    read_channel.start_consuming()


import sys,os
BASE_DIR = os.path.join(os.path.dirname(__file__),'..')
sys.path.append(BASE_DIR)

from handlers.surface_worker import SurfaceWorker
import argparse
import pika
import json

surf_worker = SurfaceWorker()

# read queue
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
read_channel = connection.channel()
read_channel.exchange_declare(exchange='surface_proc_exchange', exchange_type='direct')

# write queue
write_channel = connection.channel()

parser = argparse.ArgumentParser(description='SurfaceWorker process.')
parser.add_argument('--read_queue', type=str, default='queue1')
parser.add_argument('--write_queue', type=str, default='queue_1')

if __name__ == '__main__':
    args = parser.parse_args()
    read_queue = args.read_queue
    write_queue = args.write_queue


    def callback(ch, method, properties, body):
        input_msg = json.loads(body)
        print(f'\nReceived input message for ticker {input_msg["ticker"]}')
        output_msg = json.dumps(surf_worker.run(input_msg["ticker"], start_time=input_msg["start_time"]))
        write_channel.basic_publish(exchange='surface_mongo_exchange',
                                    routing_key=write_queue,
                                    body=output_msg)
        print(f'\nSent surface for {input_msg["ticker"]} to queue {write_queue}')

    read_channel.queue_declare(queue=read_queue, exclusive=False)
    read_channel.queue_bind(exchange='surface_proc_exchange', queue=read_queue, routing_key=read_queue)

    write_channel.exchange_declare(exchange='surface_mongo_exchange', exchange_type='direct')
    write_channel.queue_declare(queue=write_queue, exclusive=False)
    write_channel.queue_bind(exchange='surface_mongo_exchange', queue=write_queue,
                        routing_key=write_queue)

    read_channel.basic_consume(
        queue=read_queue, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for tickers. To exit press CTRL+C')

    read_channel.start_consuming()


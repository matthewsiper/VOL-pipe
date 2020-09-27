import sys,os
BASE_DIR = os.path.join(os.path.dirname(__file__),'..')
sys.path.append(BASE_DIR)

import pika
from constants import TICKERS_DISTRIBUTED, TICKERS_SYNCHED_AND_UQ, SURFACE_WORKER_QUEUES_DMQ, SURFACE_WORKER_QUEUES_UQ
import json
from handlers.surface_worker import SurfaceWorker
from adapters.mongo_adapter import MongoAdapter
import argparse
import datetime as dt



def build_message(ticker, time, profile_env=None):
    profile_env_str = "False"

    if profile_env:
        if profile_env == True:
            profile_env_str = "True"

    return json.dumps({"ticker": ticker, "start_time": time, "profile_env": profile_env_str})


parser = argparse.ArgumentParser(description='SurfaceProcessor process.')
parser.add_argument('--env', type=str, default='dmq')
parser.add_argument('--profile-env', type=bool, default=False)


if __name__ == '__main__':
    args = parser.parse_args()
    env = args.env
    profile_env = args.profile_env

    if env != 'synchronized':
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='surface_proc_exchange',
                                 exchange_type='direct')

        if env == 'dmq':
            for queue in SURFACE_WORKER_QUEUES_DMQ:
                channel.queue_declare(queue=queue, exclusive=False)
                channel.queue_bind(
                    exchange='surface_proc_exchange', queue=queue, routing_key=queue)
        elif QUEUE_ENVIRON == 'uq':
            for queue in SURFACE_WORKER_QUEUES_UQ:
                channel.queue_declare(queue=queue, exclusive=False)
                channel.queue_bind(
                    exchange='surface_proc_exchange', queue=queue, routing_key=queue)

    start_dt = dt.datetime.now()
    start = str(start_dt)

    if env == 'dmq':
        while True:
            for k, v in TICKERS_DISTRIBUTED.items():
                for ticker in v:
                    print(f"published {ticker} to queue {k}")
                    msg = build_message(ticker, start)
                    channel.basic_publish(exchange='surface_proc_exchange',
                                          routing_key=k,
                                          body=msg)
    elif env == 'uq':
        for k, v in TICKERS_SYNCHED_AND_UQ.items():
            for ticker in v:
                msg = build_message(ticker, start)
                channel.basic_publish(exchange='surface_proc_exchange',
                                      routing_key=k,
                                      body=msg)
    else:
        sw = SurfaceWorker()
        ma = MongoAdapter()
        for k, v in TICKERS_SYNCHED_AND_UQ.items():
            for ticker in v:
                print(f"ticker {ticker}")
                mongo_record_id = ma.insert_doc(doc=sw.run(ticker=ticker, start_time=start), db_name='main_db', collection='surfaces',
                                                   return_id=True)
                print(f"Stored surface with id {mongo_record_id}")
                time_delta = dt.datetime.now() - start_dt
                if profile_env:
                    print(f"{time_delta.total_seconds()} elapsed seconds")
        if profile_env:
            end_time = dt.datetime.now()
            total_time = end_time - start_dt
            print(f"total time is {total_time.total_seconds()}")



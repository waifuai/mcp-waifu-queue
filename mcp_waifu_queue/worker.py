import logging
import redis
from rq import Worker, Queue, Connection

from mcp_waifu_queue.config import Config

config = Config.load()

listen = ['default']

conn = redis.from_url(config.redis_url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        try:
            worker.work()
        except Exception as e:
            logging.exception("Worker failed to start")
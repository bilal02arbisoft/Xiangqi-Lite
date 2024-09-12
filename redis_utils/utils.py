import os

import redis
import redis.asyncio as aioredis
from dotenv import load_dotenv

load_dotenv()

async_redis_pool = None
sync_redis_client = None


async def setup_async_redis_pool():
    """
    Set up an asynchronous Redis connection pool.
    This function checks if the `async_redis_pool` is already set up. If not, it initializes
    a connection pool to the Redis server with the specified host, port, and database.
    """
    global async_redis_pool
    if not async_redis_pool:

        async_redis_pool = aioredis.Redis(
            host=os.environ.get('REDIS_HOST'),
            port=os.environ.get('REDIS_PORT'),
            db=os.environ.get('REDIS_DB'),
            decode_responses=True
        )
    return async_redis_pool


async def get_async_redis_pool():
    """
    Get the existing asynchronous Redis connection pool or set up a new one if it doesn't exist.
    This function ensures the asynchronous Redis pool is initialized and returns the connection pool instance.
    """
    return await setup_async_redis_pool()


def setup_sync_redis_client():
    """
    Set up a synchronous Redis client.
    This function checks if the `sync_redis_client` is already set up. If not, it initializes
    a Redis client connection to the Redis server with the specified host, port, and database.
    """
    global sync_redis_client
    if not sync_redis_client:

        sync_redis_client = redis.ConnectionPool(
            host=os.environ.get('REDIS_HOST'),
            port=os.environ.get('REDIS_PORT'),
            db=os.environ.get('REDIS_DB'),
            decode_responses=True,
            max_connections=10
        )
        sync_redis_client = redis.Redis(connection_pool=sync_redis_client)

    return sync_redis_client


def get_sync_redis_client():
    """
    Get the existing synchronous Redis client or set up a new one if it doesn't exist.
    This function ensures the synchronous Redis client is initialized and returns the client instance.
    """
    return setup_sync_redis_client()

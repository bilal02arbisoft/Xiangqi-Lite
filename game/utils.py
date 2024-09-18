import json

from game.models import ChatMessage, Room
from game.serializers import ChatMessageSerializer
from redis_utils.utils import get_sync_redis_client

redis_client = get_sync_redis_client()

def fetch_messages_from_db(room_name, last_id=None, page_size=30):
    try:
        room = Room.objects.get(name=room_name)
    except Room.DoesNotExist:

        return []

    query = ChatMessage.objects.filter(room=room)
    if last_id:
        query = query.filter(id__lt=last_id)

    messages = query.order_by('-id')[:page_size]

    serialized_messages = ChatMessageSerializer(messages, many=True).data

    serialized_messages.reverse()

    for message_data in serialized_messages:

        redis_client.zadd(room_name, {json.dumps(message_data): message_data['id']})

    return serialized_messages


def fetch_messages_from_cache(cache_key, last_id=None, page_size=30):

    if last_id:
        messages = redis_client.zrevrangebyscore(
            cache_key,
            max=last_id - 1,
            min='-inf',
            start=0,
            num=page_size,
            withscores=False
        )
    else:
        messages = redis_client.zrevrange(
            cache_key,
            start=0,
            end=page_size - 1,
            withscores=False
        )

    messages = [json.loads(message) for message in messages]
    messages.reverse()

    return messages


def get_paginated_messages(room_name, last_id=None, page_size=30):
    if last_id:

        last_id = int(last_id)
    cached_messages = fetch_messages_from_cache(room_name, last_id, page_size)
    if cached_messages:

        return cached_messages

    return fetch_messages_from_db(room_name, last_id, page_size)

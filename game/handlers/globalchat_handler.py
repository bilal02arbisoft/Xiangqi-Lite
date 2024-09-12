
from game.handlers.database import get_userprofile
from game.handlers.utils import create_message_data, get_redis_conn, get_user_id, notify


async def route_event(consumer, data):
    """
    Route the incoming event to the appropriate handler based on the event type.
    """
    event_type = data.get('type')
    handlers = {
        'chat.message':handle_chat_message,
        'chat.join':handle_chat_join,
        'chat.leave':handle_chat_leave,
    }
    handler = handlers.get(event_type)
    if handler:

        await handler(consumer, data)

async def handle_chat_message(consumer, data):
    """
     Handle the receipt and broadcasting of a chat message to a chat group.
    """
    chat_message = data.get('message')
    message_data = create_message_data('chat.message', consumer.scope['user'].id, chat_message)
    await notify(consumer,  consumer.chat_group_name, message_data, is_group=True,
                 exclude_channel=consumer.channel_name)


async def handle_chat_join(consumer,data):
    """
    Handle the event of a user joining a chat group and managing their profile information.
    """
    user_id = get_user_id(consumer)
    redis_conn = get_redis_conn(consumer)
    user_profile_key = f'user_profile:{user_id}'
    user_profile_exists = await redis_conn.exists(user_profile_key)

    if user_profile_exists:

        user_profile = await redis_conn.hgetall(user_profile_key)
    else:
        user_profile = await get_userprofile(consumer)
        async with redis_conn.pipeline(transaction=True) as pipe:
            await pipe.hset(user_profile_key, mapping=user_profile)
            await pipe.expire(user_profile_key, 180)
            await pipe.sadd('connected_chat_users', user_id)
            await pipe.execute()

    await consumer.channel_layer.group_add(consumer.chat_group_name, consumer.channel_name)
    await notify(consumer, consumer.chat_group_name, {'type': 'chat.userprofile', 'message': user_profile},
                 is_group=True)

async def handle_chat_leave(consumer):
    """
    Handle the event of a user leaving a chat group and removing their presence from the system.
    """
    user_id = get_user_id(consumer)
    redis_conn = consumer.redis_conn
    await redis_conn.srem('connected_chat_users', user_id)
    await consumer.channel_layer.group_discard(consumer.chat_group_name, consumer.channel_name)

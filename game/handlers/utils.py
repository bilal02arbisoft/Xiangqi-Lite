
from datetime import datetime, timezone


def get_redis_conn(consumer):

    return consumer.redis_conn

def get_user_id(consumer):

    return consumer.scope['user'].id

async def notify(consumer, target, message_data, is_group=False, exclude_channel=None):
    payload = {
        'type': 'send_message',
        'message_data': message_data
    }
    if exclude_channel:

        payload['exclude_channel'] = exclude_channel

    if is_group:

        return await consumer.channel_layer.group_send(target, payload)
    await consumer.send_message({'message_data': message_data})

def create_message_data(event_type, user_id, message=None, fen=None, move=None, player=None, game_data=None):
    data = {
        'type': event_type,
        'user_id': user_id,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    if message:

        data['message'] = message
    if fen and move and player and game_data:

        data.update({
            'fen': fen,
            'move': move,
            'player': player,
            'red_time_remaining': game_data['red_time_remaining'],
            'black_time_remaining': game_data['black_time_remaining'],
            'server_time': datetime.now().timestamp()
        })

    return data

async def send_error(consumer, message):
    """
    Send an error message to the consumer.
    """
    await notify(consumer, consumer.channel_name, {'type': 'error', 'message': message})

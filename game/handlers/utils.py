
from datetime import datetime, timezone

from game.handlers.database import get_game_details, get_game_users_sync, get_player_by_username, get_viewer_details
from game.handlers.error_handling import GameNotFoundError, PlayerNotFoundError


def get_redis_conn(consumer):
    """
    Retrieve the Redis connection from the consumer.
    """
    return consumer.redis_conn

def get_user_id(consumer):
    """
    Retrieve the user ID from the consumer's scope.
    """
    return consumer.scope['user'].id

async def notify(consumer, target, message_data, is_group=False, exclude_channel=None):
    """
    Send a message notification to a specific target or group via the consumer.
    """
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
    """
    Create a dictionary containing message data, including optional game-related information.
    """
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

def determine_role(game_data):
    """
    Determine the role of a user in a game (player or viewer).
    """
    return 'viewer' if game_data['red_player'] and game_data['black_player'] else 'player'

async def get_game_users(game_id, viewer=None):
    """
    Asynchronously retrieve the list of users in a game, optionally including viewer details.
    """
    users = await get_game_users_sync(game_id)
    if viewer:

        viewer_details = await get_viewer_details(viewer)

        return viewer_details

    return users

async def get_game_or_error(game_id):
    """
    Retrieve game details for a given game ID or raise an error if the game is not found.
    """
    game_data = await get_game_details(game_id)
    if not game_data:

        raise GameNotFoundError(f"Game ID {game_id} not found.")

    return game_data

async def get_player_or_error(username):
    """
    Retrieve player details by username or raise an error if the player is not found.
    """
    player = await get_player_by_username(username)
    if not player:

        raise PlayerNotFoundError(f"Player with username {username} not found.")

    return player


async def game_users_list(consumer, is_group=False):
    """
    Notify the list of users in a game.
    """
    users = await get_game_users(consumer.game_id)
    await notify(consumer, consumer.room_group_name, {'type': 'game.users.list', 'data': users}, is_group=is_group)

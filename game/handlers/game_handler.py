from datetime import datetime, timezone

from channels.db import database_sync_to_async

from game.models import Game
from game.serializers import GameSerializer
from game.utils import hashids
from users.models import CustomUser, Player


async def route_event(consumer, data):
    """
    Route the incoming event to the appropriate handler based on the event type.
    """
    event_type = data.get('type')
    handlers = {
        'game.get': handle_game_get,
        'game.join': handle_game_join,
        'game.move': handle_game_move,
        'game.chat': handle_game_chat,
    }

    handler = handlers.get(event_type)
    if handler:

        await handler(consumer, data)


async def handle_game_chat(consumer, data):
    """
    Handle a game chat message event.
    """
    chat_message = data.get('message')
    if not chat_message:

        await send_error(consumer, 'No message provided.')

        return
    message_data = create_message_data('game.chat', consumer.scope['user'].username, chat_message)
    await notify(consumer, consumer.room_group_name, message_data, is_group=True, exclude_channel=consumer.channel_name)


async def handle_game_join(consumer, data):
    """
    Handle a game join event.
    """
    consumer.game_id = data.get('id')
    consumer.room_group_name = f'game_{consumer.game_id}'
    await consumer.channel_layer.group_add(consumer.room_group_name, consumer.channel_name)
    game_data = await get_game_or_error(consumer, consumer.game_id)
    if not game_data:

        return
    consumer.scope['role'] = determine_role(game_data)
    player = await get_or_create_player(consumer.scope['user'])
    if consumer.scope['role'] == 'viewer':

        await handle_viewer_join(consumer, player)
    else:
        await handle_player_join(consumer, game_data, player)


async def handle_viewer_join(consumer, player):
    """
    Handle a viewer joining a game.
    """
    username = await get_username(player)
    await add_viewer(consumer.game_id, username)
    new_viewer_details = await get_game_users(consumer.game_id, viewer=consumer.scope['user'])
    await notify(consumer, consumer.room_group_name, {'type': 'game.viewer.joined', 'data': new_viewer_details},
                 is_group=True)
    await game_users_list(consumer, is_group=False)


async def handle_player_join(consumer, game_data, player):
    """
    Handle a player joining a game.
    """
    if not game_data['red_player']:

        await update_game_players(consumer.game_id, red_player=player)
    elif not game_data['black_player']:

        game_usernames = await update_game_players(consumer.game_id, black_player=player)
        await notify(consumer, consumer.lobby_group_name, {
            'type': 'lobby.game.join',
            'game_id': consumer.game_id,
            'red_player': game_usernames['red_player'],
            'black_player': game_usernames['black_player'],
        }, is_group=True)
        await handle_game_start(consumer)


async def handle_game_start(consumer):
    """
    Notify that the game has started.
    """
    await notify(consumer, consumer.room_group_name, {
        'type': 'game.start',
        'message': f'The game {consumer.game_id} has started!',
    }, is_group=True)
    await game_users_list(consumer, is_group=True)


async def handle_game_move(consumer, data):
    """
    Handle a game move event.
    """
    fen, player, move, thinking_time = data.get('fen'), data.get('player'), data.get('move'), data.get('thinking_time')
    if not all([fen, player, move, thinking_time is not None]):

        await send_error(consumer, 'Invalid move data received.')

        return

    await update_game_state(consumer.game_id, fen, move, thinking_time)
    game_data = await get_game_details(consumer.game_id)
    message_data = create_game_move_data(fen, move, player, game_data)
    await notify(consumer, consumer.room_group_name, message_data, is_group=True, exclude_channel=consumer.channel_name)


async def handle_game_get(consumer, data):
    """
    Handle a request to get game details.
    """
    game_id = data.get('id')
    game_data = await get_game_or_error(consumer, game_id)
    if game_data:

        await notify(consumer, consumer.channel_name, {'type': 'game.get.success', 'data': game_data})


async def notify(consumer, target, message_data, is_group=False, exclude_channel=None):
    """
    Send a message to a specific target, which can be a single channel or a group.
    """
    payload = {
        'type': 'send_message',
        'message_data': message_data,
    }
    if exclude_channel:

        payload['exclude_channel'] = exclude_channel

    if is_group:

        await consumer.channel_layer.group_send(target, payload)
    else:
        await consumer.send_message({'message_data': message_data})


async def send_error(consumer, message):
    """
    Send an error message to the consumer.
    """
    await notify(consumer, consumer.channel_name, {'type': 'error', 'message': message})


def create_message_data(event_type, username, message):
    """
    Create message data for notifications.
    """
    return {
        'type': event_type,
        'username': username,
        'message': message,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


def create_game_move_data(fen, move, player, game_data):
    """
    Create data for a game move notification.
    """
    return {
        'type': 'game.move',
        'fen': fen,
        'move': move,
        'player': player,
        'red_time_remaining': game_data['red_time_remaining'],
        'black_time_remaining': game_data['black_time_remaining'],
        'server_time': datetime.now().timestamp()
    }


def determine_role(game_data):
    """
    Determine the role of a user in a game (player or viewer).
    """

    return 'viewer' if game_data['red_player'] and game_data['black_player'] else 'player'


async def game_users_list(consumer, is_group=False):
    """
    Notify the list of users in a game.
    """
    users = await get_game_users(consumer.game_id)
    await notify(consumer, consumer.room_group_name, {'type': 'game.users.list', 'data': users}, is_group=is_group)


async def get_game_or_error(consumer, game_id):
    """
    Retrieve game details or send an error if not found.
    """
    game_data = await get_game_details(game_id)
    if not game_data:
        await send_error(consumer, 'Game not found.')

        return None

    return game_data


@database_sync_to_async
def get_or_create_player(user):
    """
    Get or create a player based on the user.
    """

    return Player.objects.get_or_create(user=user)[0]


@database_sync_to_async
def get_username(player):
    """
    Retrieve the username of a player.
    """

    return player.user.username


@database_sync_to_async
def update_game_state(game_id, fen, move, thinking_time):
    """
    Update the game state in the database.
    """
    game = Game.objects.get(id=decode_game_id(game_id))
    game.fen = fen
    game.add_move(move, thinking_time)
    game.save()

@database_sync_to_async
def get_game_users_sync(game_id):
    """
    Retrieve the list of users in a game.
    """
    game = Game.objects.select_related('red_player__user__profile', 'black_player__user__profile').get(
        id=decode_game_id(game_id))

    return [
        get_player_details(game.red_player),
        get_player_details(game.black_player)
    ] if game.red_player or game.black_player else []

async def get_game_users(game_id, viewer=None):
    """
    Asynchronously retrieve the list of users in a game, optionally including viewer details.
    """
    users = await get_game_users_sync(game_id)
    if viewer:

        viewer_details = await get_viewer_details(viewer)  # Ensure it is awaited

        return viewer_details

    return users

@database_sync_to_async
def get_game_details(game_id):
    """
    Retrieve detailed information about a game.
    """
    try:
        game = Game.objects.get(id=decode_game_id(game_id))

        return GameSerializer(game).data
    except Game.DoesNotExist:

        return None


@database_sync_to_async
def update_game_players(game_id, red_player=None, black_player=None):
    """
    Update the players of a game.
    """
    game = Game.objects.select_related('red_player', 'black_player').get(id=decode_game_id(game_id))

    if red_player:

        game.red_player = red_player
    if black_player:

        game.black_player = black_player

    game.save()
    return {
        'red_player': game.red_player.user.username if game.red_player else None,
        'black_player': game.black_player.user.username if game.black_player else None
    }


@database_sync_to_async
def add_viewer(game_id, username):
    """
    Add a viewer to the game.
    """
    game = Game.objects.get(id=decode_game_id(game_id))
    user = CustomUser.objects.get(username=username)
    game.viewers.add(user)
    game.save()


@database_sync_to_async
def get_viewer_details(viewer):
    """
    Retrieve details for a viewer.
    """
    return {
        'username': viewer.username,
        'profile_picture': viewer.profile.profile_picture.url if viewer.profile.profile_picture else None,
        'id': viewer.id,
        'country': viewer.profile.country,
        'rating': viewer.player.rating if hasattr(viewer, 'player') else None
    }

def get_player_details(player):
    """
    Retrieve details for a player.
    """
    if not player:

        return None
    user = player.user

    return {
        'username': user.username,
        'profile_picture': user.profile.profile_picture.url if user.profile.profile_picture else None,
        'id': user.id,
        'country': user.profile.country,
        'rating': player.rating
    }


def decode_game_id(game_id):
    """
    Decode the game ID.
    """

    return hashids.decode(game_id)[0]

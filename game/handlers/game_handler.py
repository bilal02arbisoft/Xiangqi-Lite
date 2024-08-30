from datetime import datetime

from channels.db import database_sync_to_async

from game.models import Game
from game.serializers import GameSerializer
from game.utils import hashids
from users.models import CustomUser


async def route_event(consumer, data):
    event_type = data.get('type')
    handlers = {
        'game.get': handle_game_get,
        'game.users.list': handle_game_users_list,
        'game.join': handle_game_join,
        'game.move': handle_game_move,
    }

    handler = handlers.get(event_type)
    if handler:

        await handler(consumer, data)

async def handle_game_join(consumer, data):
    consumer.game_id = data.get('id')
    consumer.room_group_name = f'game_{consumer.game_id}'

    await consumer.channel_layer.group_add(
        consumer.room_group_name,
        consumer.channel_name
    )

    game_data = await get_game_or_error(consumer, consumer.game_id)
    if not game_data:

        return

    player_username = consumer.scope['user'].username
    if not game_data['red_player']:

        await update_game_players(consumer.game_id, red_player_username=player_username)
    elif not game_data['black_player']:

        game_usernames = await update_game_players(consumer.game_id, black_player_username=player_username)
        game = await get_game_details(consumer.game_id)
        await notify(consumer, consumer.lobby_group_name, {
            'type': 'lobby.game.join',
            'game_id': consumer.game_id,
            'red_player': game_usernames['red_player'],
            'black_player': game_usernames['black_player'],
        }, is_group=True)
        await handle_game_start(consumer, game, game_usernames)
    else:

        await notify(consumer, consumer.channel_name, {'type': 'error', 'message': 'This game is already full.'})


async def handle_game_start(consumer, game, game_usernames):

    # Include initial timer values
    await notify(consumer, consumer.room_group_name, {
        'type': 'game.start',
        'message': f'The game {consumer.game_id} has started!',
        'red_player':  game_usernames['red_player'],
        'black_player': game_usernames['black_player'],
        'turn': 'red',
        'red_time_remaining': game['red_time_remaining'],
        'black_time_remaining': game['black_time_remaining'],
        'server_time': datetime.now().timestamp()
    }, is_group=True)


async def handle_game_move(consumer, data):
    fen = data.get('fen')
    player = data.get('player')
    move = data.get('move')
    thinking_time = data.get('thinking_time')  # Time in seconds that player took for the move

    if not fen or not player or not move or thinking_time is None:
        await notify(consumer, consumer.channel_name, {'type': 'error', 'message': 'Invalid move data received.'})
        return

    await update_game_state(consumer.game_id, fen, move, thinking_time)
    game_data = await get_game_details(consumer.game_id)

    await notify(
        consumer,
        consumer.room_group_name,
        {
            'type': 'game.move',
            'fen': fen,
            'move': move,
            'player': player,
            'red_time_remaining': game_data['red_time_remaining'],
            'black_time_remaining': game_data['black_time_remaining'],
            'server_time': datetime.now().timestamp()
        },
        is_group=True,
        exclude_channel=consumer.channel_name
    )


async def handle_game_users_list(consumer, data):
    game_id = consumer.game_id
    users = await get_game_users(game_id)
    await notify(consumer, consumer.channel_name, {'type': 'game.users.list', 'data': users})

async def handle_game_get(consumer, data):
    game_id = data.get('id')
    game_data = await get_game_or_error(consumer, game_id)
    if game_data:

        await notify(consumer, consumer.channel_name, {'type': 'game.get', 'data': game_data})

async def notify(consumer, target, message_data, is_group=False, exclude_channel=None):
    if is_group:
        if exclude_channel:

            await consumer.channel_layer.group_send(
                target,
                {
                    'type': 'send_message',
                    'message_data': message_data,
                    'exclude_channel': exclude_channel
                }
            )
        else:
            await consumer.channel_layer.group_send(
                target,
                {
                    'type': 'send_message',
                    'message_data': message_data
                }
            )
    else:
        await consumer.send_message({'message_data': message_data})


async def get_game_or_error(consumer, game_id):
    game_data = await get_game_details(game_id)
    if not game_data:

        await notify(consumer, consumer.channel_name, {'type': 'error', 'message': 'Game not found.'})
        return None

    return game_data

@database_sync_to_async
def update_game_state(game_id, fen, move, thinking_time):
    decoded_id = hashids.decode(game_id)
    game = Game.objects.get(id=decoded_id[0])
    game.fen = fen
    game.add_move(move, thinking_time)
    game.save()

@database_sync_to_async
def get_game_users(game_id):
    decoded_id = hashids.decode(game_id)
    game = Game.objects.get(id=decoded_id[0])
    return {
        'red_player': game.red_player.username if game.red_player else None,
        'black_player': game.black_player.username if game.black_player else None
    }

@database_sync_to_async
def get_game_details(game_id):
    try:
        decoded_id = hashids.decode(game_id)
        game = Game.objects.get(id=decoded_id[0])
        serializer = GameSerializer(game)
        return serializer.data

    except Game.DoesNotExist:
        return None

@database_sync_to_async
def update_game_players(game_id, red_player_username=None, black_player_username=None):
    decoded_id = hashids.decode(game_id)
    game = Game.objects.get(id=decoded_id[0])

    if red_player_username:

        red_player = CustomUser.objects.get(username=red_player_username)
        game.red_player = red_player
    if black_player_username:

        black_player = CustomUser.objects.get(username=black_player_username)
        game.black_player = black_player
    game.save()
    return {
        'red_player': game.red_player.username if game.red_player else None,
        'black_player': game.black_player.username if game.black_player else None
    }

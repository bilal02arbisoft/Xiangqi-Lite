from channels.db import database_sync_to_async
from game.models import Game
from game.serializers import GameSerializer
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

    player_username = consumer.scope["user"].username
    if not game_data['red_player']:

        await update_game_players(consumer.game_id, red_player_username=player_username)
    elif not game_data['black_player']:

        game_data = await update_game_players(consumer.game_id, black_player_username=player_username)

        await notify(consumer, consumer.lobby_group_name, {
            'type': 'lobby.game.join',
            'game_id': consumer.game_id,
            'red_player': game_data['red_player'],
            'black_player': game_data['black_player'],
        }, is_group=True)
        await handle_game_start(consumer, game_data)
    else:
        await notify(consumer, consumer.channel_name, {'type': 'error', 'message': 'This game is already full.'})

async def handle_game_start(consumer, game_data):
    red_player_username = game_data['red_player']
    black_player_username = game_data['black_player']
    await notify(consumer, consumer.room_group_name, {
        'type': 'game.start',
        'message': f'The game {consumer.game_id} has started!',
        'red_player': red_player_username,
        'black_player': black_player_username,
        'turn': 'red',
    }, is_group=True)

async def handle_game_move(consumer, data):
    fen = data.get('fen')
    player = data.get('player')

    if not fen or not player:
        await notify(consumer, consumer.channel_name, {'type': 'error', 'message': 'Invalid move data received.'})

        return

    await update_game_state(consumer.game_id, fen, player)
    await notify(
        consumer,
        consumer.room_group_name,
        {
            'type': 'game.move',
            'fen': fen,
            'player': player
        },
        is_group=True,
        exclude_channel=consumer.channel_name
    )

async def handle_game_users_list(consumer, data):
    game_id = data.get('id')
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
def update_game_state(game_id, fen, player):
    game = Game.objects.get(game_id=game_id)
    game.fen = fen
    game.turn = 'black' if player == 'red' else 'red'
    game.save()

@database_sync_to_async
def get_game_users(game_id):
    game = Game.objects.get(game_id=game_id)
    return {
        'red_player': game.red_player.username if game.red_player else None,
        'black_player': game.black_player.username if game.black_player else None
    }

@database_sync_to_async
def get_game_details(game_id):
    try:
        game = Game.objects.get(game_id=game_id)
        serializer = GameSerializer(game)
        return serializer.data
    except Game.DoesNotExist:
        return None

@database_sync_to_async
def update_game_players(game_id, red_player_username=None, black_player_username=None):
    game = Game.objects.get(game_id=game_id)
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

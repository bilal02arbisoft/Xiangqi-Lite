from datetime import datetime, timezone

from channels.db import database_sync_to_async

from game.models import Game
from game.serializers import GameSerializer
from game.utils import hashids
from users.models import CustomUser, Player


async def route_event(consumer, data):
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
    chat_message = data.get('message')
    if not chat_message:

        await notify(consumer, consumer.channel_name, {'type': 'error',
                                                       'message': 'No message provided.'})

        return
    message_data = {
        'type': 'game.chat',
        'username': consumer.scope['user'].username,
        'message': chat_message,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    await notify(
        consumer,
        consumer.room_group_name,
        message_data,
        is_group=True,
        exclude_channel=consumer.channel_name
    )

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
    if game_data['red_player'] and game_data['black_player']:

        role = 'viewer'
    else:
        role = 'player'
    consumer.scope['role'] = role
    player = await get_or_create_player(consumer.scope['user'])
    if role == 'viewer':

        username = await get_username(player)
        await add_viewer(consumer.game_id, username)

        new_viewer_details = await get_game_users(consumer.game_id, viewer=consumer.scope['user'])
        await notify(
            consumer,
            consumer.room_group_name,
            {
                'type': 'game.viewer.joined',
                'data': new_viewer_details
            },
            is_group=True
        )
        await game_users_list(consumer, is_group=False)

    elif not game_data['red_player']:
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
    await notify(consumer, consumer.room_group_name, {
        'type': 'game.start',
        'message': f'The game {consumer.game_id} has started!',
    }, is_group=True)
    await game_users_list(consumer, is_group=True)


async def handle_game_move(consumer, data):
    fen = data.get('fen')
    player = data.get('player')
    move = data.get('move')
    thinking_time = data.get('thinking_time')
    if not fen or not player or not move or thinking_time is None:

        await notify(consumer, consumer.channel_name, {'type': 'error',
                                                       'message': 'Invalid move data received.'})
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


async def game_users_list(consumer, is_group=False):
    game_id = consumer.game_id
    users = await get_game_users(game_id)
    await notify(consumer, consumer.room_group_name,
                 {'type': 'game.users.list', 'data': users}, is_group=is_group)

async def handle_game_get(consumer, data):
    game_id = data.get('id')
    game_data = await get_game_or_error(consumer, game_id)
    if game_data:

        await notify(consumer, consumer.channel_name, {'type': 'game.get.success',
                                                       'data': game_data})


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

        await notify(consumer, consumer.channel_name, {'type': 'error',
                                                       'message': 'Game not found.'})

        return None

    return game_data

@database_sync_to_async
def get_or_create_player(user):
    player, created = Player.objects.get_or_create(user=user)

    return player

@database_sync_to_async
def get_username(player):

    return player.user.username


@database_sync_to_async
def update_game_state(game_id, fen, move, thinking_time):
    decoded_id = hashids.decode(game_id)
    game = Game.objects.get(id=decoded_id[0])
    game.fen = fen
    game.add_move(move, thinking_time)
    game.save()


@database_sync_to_async
def get_game_users(game_id, viewer=None):
    decoded_id = hashids.decode(game_id)

    game = Game.objects.select_related('red_player__user', 'red_player__user__profile',
                                       'black_player__user', 'black_player__user__profile').get(id=decoded_id[0])

    if viewer:

        viewer_details = {
            'username': viewer.username,
            'profile_picture': (viewer.profile.profile_picture.url
                                if viewer.profile.profile_picture else None),
            'id': viewer.id,
            'country': viewer.profile.country,
            'rating': viewer.player.rating if hasattr(viewer, 'player') else None
        }

        return viewer_details

    users = []
    if game.red_player:
        red_player_details = {
            'username': game.red_player.user.username,
            'profile_picture': (game.red_player.user.profile.profile_picture.url
                                if game.red_player.user.profile.profile_picture else None),
            'id': game.red_player.user.id,
            'country': game.red_player.user.profile.country,
            'rating': game.red_player.rating
        }
        users.append(red_player_details)

    if game.black_player:
        black_player_details = {
            'username': game.black_player.user.username,
            'profile_picture': (game.black_player.user.profile.profile_picture.url
                                if game.black_player.user.profile.profile_picture else None),
            'bio': game.black_player.user.profile.bio,
            'id': game.black_player.user.id,
            'country': game.black_player.user.profile.country,
            'rating': game.black_player.rating
        }
        users.append(black_player_details)

    return users


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
def update_game_players(game_id, red_player=None, black_player=None):
    decoded_id = hashids.decode(game_id)
    game = Game.objects.select_related('red_player', 'black_player').get(id=decoded_id[0])

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
    decoded_id = hashids.decode(game_id)
    game = Game.objects.get(id=decoded_id[0])
    user = CustomUser.objects.get(username=username)
    game.viewers.add(user)
    game.save()

@database_sync_to_async
def get_viewer_details(player):
    user = player.user
    viewer_details = {
        'username': user.username,
        'profile_picture': (user.profile.profile_picture.url
                            if user.profile.profile_picture else None),
        'id': user.id,
        'country': user.profile.country,
        'rating': player.rating  # Assuming the Player model has a rating field
    }
    return viewer_details

from channels.db import database_sync_to_async

from game.handlers.database import (
    add_viewer,
    end_game_update,
    get_game_details,
    get_game_users_sync,
    get_or_create_player,
    get_player_by_username,
    get_username,
    get_viewer_details,
    update_game_players,
    update_game_state,
)
from game.handlers.error_handling import GameNotFoundError, PlayerNotFoundError, exception_handler
from game.handlers.utils import create_message_data, notify, send_error


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
        'game.end': handle_game_end,
    }
    handler = handlers.get(event_type)
    if handler:

        await handler(consumer, data)

@exception_handler
async def handle_game_chat(consumer, data):
    """
    Handle a game chat message event.
    """
    chat_message = data.get('message')
    if not chat_message:

        await send_error(consumer, 'No message provided.')

        return
    message_data = create_message_data('game.chat', consumer.scope['user'].id, chat_message)
    await notify(consumer, consumer.room_group_name, message_data, is_group=True, exclude_channel=consumer.channel_name)

@exception_handler
async def handle_game_join(consumer, data):
    """
    Handle a game join event.
    """
    consumer.game_id = data.get('id')
    consumer.room_group_name = f'game_{consumer.game_id}'
    await consumer.channel_layer.group_add(consumer.room_group_name, consumer.channel_name)
    game_data = await get_game_or_error(consumer.game_id)
    if not game_data:

        return
    consumer.scope['role'] = determine_role(game_data)
    player = await get_or_create_player(consumer.scope['user'])
    if consumer.scope['role'] == 'viewer':

        await handle_viewer_join(consumer, player)
    else:
        await handle_player_join(consumer, game_data, player)

@exception_handler
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

@exception_handler
async def handle_player_join(consumer, game_data, player):
    """
    Handle a player joining a game.
    """
    if not game_data['red_player']:

        await update_game_players(consumer.game_id, red_player=player)
    elif not game_data['black_player']:

        await update_game_players(consumer.game_id, black_player=player)
        await handle_game_start(consumer)

@exception_handler
async def handle_game_start(consumer):
    """
    Notify that the game has started.
    """
    await notify(consumer, consumer.room_group_name, {
        'type': 'game.start',
        'message': f'The game {consumer.game_id} has started!',
    }, is_group=True)
    await game_users_list(consumer, is_group=True)

@exception_handler
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
    message_data = create_message_data('game.move', consumer.scope['user'].id,
                                       fen=fen, move=move, player=player, game_data=game_data)
    await notify(consumer, consumer.room_group_name, message_data, is_group=True, exclude_channel=consumer.channel_name)

@exception_handler
async def handle_game_get(consumer, data):
    """
    Handle a request to get game details.
    """
    game_id = data.get('id')
    game_data = await get_game_or_error(game_id)
    if game_data:

        await notify(consumer, consumer.channel_name, {'type': 'game.get.success', 'data': game_data})

@exception_handler
async def game_users_list(consumer, is_group=False):
    """
    Notify the list of users in a game.
    """
    users = await get_game_users(consumer.game_id)
    await notify(consumer, consumer.room_group_name, {'type': 'game.users.list', 'data': users}, is_group=is_group)


@exception_handler
async def handle_game_end(consumer, data):
    """
    Handle a game end event.
    """
    losing_username = data.get('losing_player')

    if not losing_username:
        await send_error(consumer, 'Invalid data: No losing username provided.')

        return

    game_data = await get_game_or_error(consumer.game_id)
    if not game_data:

        return

    losing_player = await get_player_by_username(losing_username)
    if not losing_player:
        await send_error(consumer, 'Losing player not found.')

        return

    winning_player = None

    if game_data['red_player'] == losing_username:

        winning_player = await get_player_by_username(game_data['black_player'])
    elif game_data['black_player'] == losing_username:

        winning_player = await get_player_by_username(game_data['red_player'])

    if not winning_player:

        await send_error(consumer, 'Winning player not found.')

        return
    await end_game_update(consumer.game_id, winning_player, losing_player)
    winning_username = await database_sync_to_async(lambda: winning_player.user.username)()
    await notify(
        consumer,
        consumer.room_group_name,
        {'type': 'game.end.success', 'message':  winning_username},
        is_group=True
    )

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
    game_data = await get_game_details(game_id)
    if not game_data:

        raise GameNotFoundError(f"Game ID {game_id} not found.")

    return game_data

async def get_player_or_error(username):
    player = await get_player_by_username(username)
    if not player:

        raise PlayerNotFoundError(f"Player with username {username} not found.")

    return player


def determine_role(game_data):
    """
    Determine the role of a user in a game (player or viewer).
    """
    return 'viewer' if game_data['red_player'] and game_data['black_player'] else 'player'

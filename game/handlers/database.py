from channels.db import database_sync_to_async

from game.handlers.utils import get_user_id
from game.models import Game
from game.serializers import GameSerializer
from game.utils import hashids
from users.models import CustomUser, Player


@database_sync_to_async
def end_game_update(game_id, winning_player, losing_player):
    """
    Update game status to completed and update player statistics.
    """
    game = Game.objects.get(id=decode_game_id(game_id))
    game.status = 'completed'
    game.save()

    winning_player.games_played += 1
    winning_player.games_won += 1
    winning_player.rating += 20
    winning_player.save()

    losing_player.games_played += 1
    losing_player.games_lost += 1
    losing_player.rating -= 20
    losing_player.save()


@database_sync_to_async
def get_or_create_player(user):
    """
    Get or create a player based on the user.
    """
    return Player.objects.get_or_create(user=user)[0]


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
def get_player_by_username(username):
    """
    Retrieve a Player instance by username.
    """
    try:
        user = CustomUser.objects.get(username=username)

        return Player.objects.get(user=user)
    except (CustomUser.DoesNotExist, Player.DoesNotExist):

        return None


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

def decode_game_id(game_id):
    decoded = hashids.decode(game_id)
    if not decoded:

        raise ValueError(f"Invalid game ID: {game_id}")

    return decoded[0]

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
@database_sync_to_async
def get_userprofile(consumer):

    user_id = get_user_id(consumer)
    user_profile = {
        'user_id': user_id,
        'username': consumer.scope['user'].username,
        'profile_pic': consumer.scope['user'].profile.profile_picture.url
    }

    return user_profile

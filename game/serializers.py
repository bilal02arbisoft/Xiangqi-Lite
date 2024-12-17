from rest_framework import serializers

from game.models import Game


class GameSerializer(serializers.ModelSerializer):
    """
    Serializer for the Game model.
    This serializer is responsible for transforming Game model instances into JSON format and vice versa.
    It includes additional fields like `game_id`, `red_player`, and `black_player` which are computed using
    custom methods.
    """
    game_id = serializers.SerializerMethodField()
    red_player = serializers.SerializerMethodField()
    black_player = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ('game_id', 'red_player', 'black_player', 'fen', 'initial_fen',
                  'moves', 'turn', 'status', 'started_at', 'last_updated',
                  'red_time_remaining', 'black_time_remaining')
        read_only_fields = ('game_id',)

    def get_game_id(self, obj):
        """
         Returns the unique identifier for the game instance.
        This is retrieved from the `get_game_id` method in the Game model.
        """
        return obj.get_game_id()

    def get_red_player(self, obj):
        """
         Returns the username of the red player if available, or `None` if the red player is not assigned.
        """
        return obj.red_player.user.username if obj.red_player else None

    def get_black_player(self, obj):
        """
        Returns the username of the black player if available, or `None` if the black player is not assigned.
        """
        return obj.black_player.user.username if obj.black_player else None

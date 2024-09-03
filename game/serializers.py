from rest_framework import serializers

from game.models import Game


class GameSerializer(serializers.ModelSerializer):
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

        return obj.get_game_id()

    def get_red_player(self, obj):

        return obj.red_player.user.username if obj.red_player else None

    def get_black_player(self, obj):

        return obj.black_player.user.username if obj.black_player else None

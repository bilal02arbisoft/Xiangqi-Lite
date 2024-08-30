from django.db import models

from game.utils import hashids
from users.models import CustomUser


class Game(models.Model):
    red_player = models.ForeignKey(CustomUser, related_name='red_player', on_delete=models.SET_NULL,
                                   null=True, blank=True)
    black_player = models.ForeignKey(CustomUser, related_name='black_player', on_delete=models.SET_NULL,
                                     null=True, blank=True)
    fen = models.CharField(max_length=500)
    initial_fen = models.CharField(max_length=500)
    moves = models.JSONField(blank=True, default=list)
    turn = models.CharField(max_length=10, choices=[('red', 'Red'), ('black', 'Black')])
    status = models.CharField(max_length=10, choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'),
                                                      ('draw', 'Draw'), ('abandoned', 'Abandoned')],
                              default='ongoing')
    started_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    red_time_remaining = models.IntegerField(default=600)
    black_time_remaining = models.IntegerField(default=600)

    def add_move(self, uci_move, thinking_time):

        current_moves = self.moves or []
        current_moves.append(uci_move)
        self.moves = current_moves

        if self.turn == 'red':
            self.red_time_remaining -= thinking_time
        else:
            self.black_time_remaining -= thinking_time

        self.turn = 'black' if self.turn == 'red' else 'red'

        self.save()

    def get_game_id(self):

        return hashids.encode(self.id)

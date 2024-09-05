from django.db import models

from game.utils import hashids
from users.models import CustomUser, Player


class Game(models.Model):
    TURN_CHOICES = [('red', 'Red'), ('black', 'Black')]
    STATUS_CHOICES = [('ongoing', 'Ongoing'), ('completed', 'Completed'),
                      ('draw', 'Draw'), ('abandoned', 'Abandoned')]
    red_player = models.ForeignKey(Player, related_name='red_player', on_delete=models.CASCADE,
                                   null=True, blank=True)
    black_player = models.ForeignKey(Player, related_name='black_player', on_delete=models.CASCADE,
                                     null=True, blank=True)
    fen = models.CharField(max_length=500)
    initial_fen = models.CharField(max_length=500)
    moves = models.JSONField(blank=True, default=list)
    turn = models.CharField(max_length=10, choices=TURN_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ongoing')
    started_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    red_time_remaining = models.IntegerField(default=300)
    black_time_remaining = models.IntegerField(default=300)
    viewers = models.ManyToManyField(CustomUser, related_name='viewers', blank=True)

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

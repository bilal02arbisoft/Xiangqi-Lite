from django.conf import settings
from django.db import models
from hashids import Hashids

from users.models import CustomUser, Player

salt = settings.SECRET_KEY
hashids = Hashids(salt=salt, min_length=6)

class Game(models.Model):
    """
    Model representing a game instance between two players.
    This model tracks the state of a game, including players, game status, moves, turn, and remaining time.
    It supports storing the current and initial board configuration (FEN notation), player turns, and
    the history of moves. The game can also have viewers and keeps track of when it was started and
    last updated.
    """
    TURN_CHOICES = [('red', 'Red'), ('black', 'Black')]
    STATUS_CHOICES = [('ongoing', 'Ongoing'), ('completed', 'Completed'),('draw', 'Draw')]
    red_player = models.ForeignKey(Player, related_name='red_player', on_delete=models.CASCADE,
                                   null=True, blank=True)
    black_player = models.ForeignKey(Player, related_name='black_player', on_delete=models.CASCADE,
                                     null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ongoing')
    viewers = models.ManyToManyField(CustomUser, related_name='viewers', blank=True)
    turn = models.CharField(max_length=10, choices=TURN_CHOICES)
    fen = models.CharField(max_length=500)
    initial_fen = models.CharField(max_length=500)
    moves = models.JSONField(blank=True, default=list)
    started_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    red_time_remaining = models.IntegerField(default=300)
    black_time_remaining = models.IntegerField(default=300)

    class Meta:
        indexes  = [
            models.Index(fields=['red_player']),
            models.Index(fields=['black_player'])
        ]

    def add_move(self, uci_move, thinking_time):
        """
        Adds a move to the game and updates the player's remaining time.
        This method appends a move (in UCI format) to the game's move history and updates the remaining time
        for the current player based on how long they took to make the move. The turn is then switched to the
        other player, and the game state is saved.
        """
        current_moves = self.moves or []
        current_moves.append(uci_move)
        self.moves = current_moves
        if self.turn == 'red':

            self.red_time_remaining -= thinking_time
            self.turn = 'black' if self.turn == 'red' else 'red'

            return
        self.black_time_remaining -= thinking_time
        self.turn = 'black' if self.turn == 'red' else 'red'
        self.save()

    def get_game_id(self):
        """
        Returns the encoded game ID using Hashids.
        """

        return hashids.encode(self.id)


class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):

        return self.name

class ChatMessage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['room', 'id']),
        ]

    def __str__(self):
        return f"Message from {self.sender.username} in room {self.room.name}"

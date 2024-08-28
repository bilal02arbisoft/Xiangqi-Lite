import shortuuid
from django.db import models
from users.models import CustomUser

def generate_game_id():
    return shortuuid.ShortUUID().random(length=6)

class Game(models.Model):
    game_id = models.CharField(max_length=6, unique=True, default=generate_game_id, editable=False)
    red_player = models.ForeignKey(CustomUser, related_name='red_player', on_delete=mo, null=True, blank=True)
    black_player = models.ForeignKey(CustomUser, related_name='black_player', on_delete=models.SET_NULL, null=True,blank=True)
    fen = models.CharField(max_length=500)
    initial_fen = models.CharField(max_length=500)
    moves = models.TextField()
    turn = models.CharField(max_length=10, choices=[('red', 'Red'), ('black', 'Black')])
    status = models.CharField(max_length=10, choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'),
                                                      ('draw', 'Draw'),
                                                      ('abandoned', 'Abandoned')], default='ongoing')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

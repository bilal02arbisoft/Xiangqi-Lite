from django.urls import path
from game.views import GameCreateView, GameUpdateView, GameDetailView

urlpatterns = [
    path('create/', GameCreateView.as_view(), name='game-create'),
    path('update/<uuid:pk>/', GameUpdateView.as_view(), name='game-update'),
    path('detail/<str:game_id>/', GameDetailView.as_view(), name='game-detail'),
]

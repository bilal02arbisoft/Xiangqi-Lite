from django.urls import path

from game.views import GameCreateView, GameDetailView, GameUpdateView

urlpatterns = [
    path('create/', GameCreateView.as_view(), name='game-create'),
    path('update/<str:game_id>/', GameUpdateView.as_view(), name='game-update'),
    path('detail/<str:game_id>/', GameDetailView.as_view(), name='game-detail'),
]

from django.urls import re_path

from game.consumers import XiangqiConsumer

websocket_urlpatterns = [
    re_path(r'ws/game/$', XiangqiConsumer.as_asgi()),
]

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xiangqi_lite.settings')
django.setup()

from game.middleware import JWTAuthMiddlewareStack
from game.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JWTAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

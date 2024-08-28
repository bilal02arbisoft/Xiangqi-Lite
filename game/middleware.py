from urllib.parse import parse_qs
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.conf import settings
from users.models import CustomUser as User
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError
from jwt import decode as jwt_decode

import logging

logger = logging.getLogger(__name__)
class JWTAuthMiddleware:
    """Middleware to authenticate user for channels"""

    def __init__(self, app):
        """Initialize the app."""
        self.app = app

    async def __call__(self, scope, receive, send):
        close_old_connections()
        try:
            token = parse_qs(scope["query_string"].decode("utf8")).get('token', None)[0]
            logger.info(f"Received token: {token}")

            data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            scope['user'] = await self.get_user(data['user_id'])
            logger.info(f"Authenticated user: {scope['user']}")
        except (TypeError, KeyError, InvalidSignatureError, ExpiredSignatureError, DecodeError) as e:
            logger.error(f"Authentication failed: {str(e)}")
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        """Return the user based on user ID."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()

def JWTAuthMiddlewareStack(app):
    """This function wraps channels authentication stack with JWTAuthMiddleware."""
    return JWTAuthMiddleware(AuthMiddlewareStack(app))

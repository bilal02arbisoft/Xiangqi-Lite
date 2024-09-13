from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from jwt import decode as jwt_decode

from users.models import CustomUser as User


class JWTAuthMiddleware:
    """
    Middleware to authenticate user for channels
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        close_old_connections()
        try:
            token = parse_qs(scope['query_string'].decode('utf8')).get('token', None)[0]
            data = jwt_decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            scope['user'] = await self.get_user(data['user_id'])

        except (TypeError, KeyError, InvalidSignatureError, ExpiredSignatureError, DecodeError):
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Return the user based on user ID.
        """
        try:

            return User.objects.get(id=user_id)
        except User.DoesNotExist:

            return AnonymousUser()

def JWTAuthMiddlewareStack(app):
    """
    This function wraps channels authentication stack with JWTAuthMiddleware.
    """
    return JWTAuthMiddleware(AuthMiddlewareStack(app))

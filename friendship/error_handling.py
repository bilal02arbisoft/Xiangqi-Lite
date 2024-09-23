from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound, ParseError, PermissionDenied
from rest_framework.response import Response

from friendship.models import FriendRequest
from users.error_handling import logger
from users.models import CustomUser


def handle_exceptions(func):
    """
    Unified decorator to handle specific exceptions uniformly across views, serializers,
    and general functions in the Friendship app.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ObjectDoesNotExist as e:
            if isinstance(e, FriendRequest.DoesNotExist):

                message = 'Friend request not found.'
            elif isinstance(e, CustomUser.DoesNotExist):

                message = 'User not found.'
            else:
                message = 'Resource not found'

            return Response({'error': message, 'details': str(e)}, status=status.HTTP_404_NOT_FOUND)

        except PermissionDenied as e:

            return Response({'error': 'Permission denied', 'details': str(e)}, status=status.HTTP_403_FORBIDDEN)

        except NotFound as e:

            return Response({'error': 'Resource not found', 'details': str(e)}, status=status.HTTP_404_NOT_FOUND)

        except AuthenticationFailed as e:

            return Response({'error': 'Authentication failed', 'details': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        except ParseError as e:

            return Response({'error': 'Malformed input data', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:

            return Response({'error': 'Database integrity error occurred'}, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:

            return Response({'error': 'Invalid value', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(e)

            return Response({'error': 'An unexpected error occurred', 'details': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper

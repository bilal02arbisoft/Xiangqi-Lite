import logging
from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotFound, ParseError, PermissionDenied
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def handle_exceptions(func):
    """
    Unified decorator to handle specific exceptions uniformly across views, serializers, managers,
    and general functions in Django.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:

            return func(*args, **kwargs)

        except ObjectDoesNotExist as e:

         return Response({'error': 'Resource not found', 'details': str(e)}, status=status.HTTP_404_NOT_FOUND)

        except PermissionDenied as e:

            return Response({'error': 'Permission denied', 'details': str(e)}, status=status.HTTP_403_FORBIDDEN)

        except NotFound as e:

            return Response({'error': 'Resource not found', 'details': str(e)}, status=status.HTTP_404_NOT_FOUND)

        except AuthenticationFailed as e:

            return Response({'error': 'Authentication failed', 'details': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        except ParseError as e:

            return Response({'error': 'Malformed input data', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:

            return Response({'error': 'A database integrity error occurred'}, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:

            return Response({'error': 'Value error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
                logger.exception(e)

                return Response({'error': 'An unexpected error occurred', 'details': str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper

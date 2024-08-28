from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed, NotFound, ParseError, PermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response


def handle_exceptions(func):
    """
    Unified decorator to handle specific exceptions uniformly across views, serializers, managers,
    and general functions in Django.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:

            return func(*args, **kwargs)

        except (DRFValidationError, DjangoValidationError) as e:

            if 'request' in kwargs or 'view' in kwargs:

                return Response({'error': 'Invalid input data', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise serializers.ValidationError(e.messages if hasattr(e, 'messages') else str(e))

        except ObjectDoesNotExist as e:

            if 'request' in kwargs or 'view' in kwargs:

                return Response({'error': 'Resource not found', 'details': str(e)}, status=status.HTTP_404_NOT_FOUND)
            else:
                raise serializers.ValidationError('The requested object does not exist.')

        except PermissionDenied as e:

            return Response({'error': 'Permission denied', 'details': str(e)}, status=status.HTTP_403_FORBIDDEN)

        except NotFound as e:

            return Response({'error': 'Resource not found', 'details': str(e)}, status=status.HTTP_404_NOT_FOUND)

        except AuthenticationFailed as e:

            return Response({'error': 'Authentication failed', 'details': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        except ParseError as e:

            return Response({'error': 'Malformed input data', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:

            raise serializers.ValidationError('A database integrity error occurred.')

        except ValueError as e:

            raise ValueError(str(e))

        except Exception as e:

            if 'request' in kwargs or 'view' in kwargs:

                return Response({'error': 'An unexpected error occurred', 'details': str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                raise Exception(f"An error occurred: {e}")

    return wrapper

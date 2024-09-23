import functools

from users.error_handling import logger


class GameNotFoundError(Exception):
    """
    Exception raised when a game cannot be found.
    """
    pass

class PlayerNotFoundError(Exception):
    """
    Exception raised when a player cannot be found.
    """
    pass

class InvalidMoveError(Exception):
    """
    Exception raised when an invalid move is made in the game.
    """
    pass

class UnauthorizedError(Exception):
    """
    Exception raised when an unauthorized action is attempted.
    """
    pass


def exception_handler(func):
    """
     A decorator that wraps a function with exception handling logic.
     If any of the predefined exceptions are raised within the wrapped function,
     an appropriate error message will be sent to the consumer using the
    send_error handler.
    """
    @functools.wraps(func)
    async def wrapper(consumer, *args, **kwargs):
        from game.handlers.game_handler import send_error
        try:

            return await func(consumer, *args, **kwargs)
        except GameNotFoundError as e:
            await send_error(consumer, str(e))
        except PlayerNotFoundError as e:
            await send_error(consumer, str(e))
        except InvalidMoveError as e:
            await send_error(consumer, str(e))
        except UnauthorizedError as e:
            await send_error(consumer, str(e))
        except Exception as e:
            logger.exception(e)
            await send_error(consumer, 'An unexpected error occurred.')

    return wrapper

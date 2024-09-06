import functools


class GameNotFoundError(Exception):
    pass

class PlayerNotFoundError(Exception):
    pass

class InvalidMoveError(Exception):
    pass

class UnauthorizedError(Exception):
    pass


def exception_handler(func):
    from game.handlers.game_handler import send_error

    @functools.wraps(func)
    async def wrapper(consumer, *args, **kwargs):

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
        except Exception:
            await send_error(consumer, 'An unexpected error occurred.')

    return wrapper

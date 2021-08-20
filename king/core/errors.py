from .utils.color import colorify


class CacheNotFoundError(Exception):
    """Class used to indicate that an entry was not found within the cache.
    """

    def __init__(self, message) -> None:
        super().__init__(colorify("ERROR", message))


class DatabaseNotFoundError(Exception):
    """Class used to indicate thatan entry was not found within the database."""

    def __init__(self, message) -> None:
        super().__init__(colorify("ERROR", message))

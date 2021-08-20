import asyncio
from .base import Database
from .settings_caches import PrefixManager, BlacklistManager
from .utils.color import printer


class PrefixDatabase(Database):
    collection_name = "prefixes"
    loop = asyncio.get_event_loop()

    def __init__(self, config) -> None:

        self._config = config
        self._collection = config['CLUSTER'][PrefixDatabase.collection_name]

        # still using caching in order to avoid querying the database all the time.
        self._cache_manager = PrefixManager(self._config)

        printer("INFO", "SYNCING PREFIX DATABASE AND CACHE")
        self._cache_manager.cache = self.find()

    async def _find(self) -> dict:
        ret = self._collection.find({})
        ret = await ret.to_list(length=None)
        ret = {
            str(c.pop("_id")): c
            for c in ret
        }
        return ret


class BlacklistDatabase(Database):

    collection_name = "blacklist"
    loop = asyncio.get_event_loop()

    def __init__(self, config) -> None:
        self._config = config
        self._collection = config['CLUSTER'][BlacklistDatabase.collection_name]

        # still using caching in order to avoid querying the database all the time.
        self._cache_manager = BlacklistManager(self._config)

        printer("INFO", "SYNCING BLACKLIST DATABASE AND CACHE")
        self._cache_manager.cache = self.find()

    async def _find(self) -> list:
        ret = self._collection.find({})
        ret = await ret.to_list(length=None)
        ret = {
            str(c.pop("_id")): c for c in ret
        }
        return ret

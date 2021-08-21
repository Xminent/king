from abc import ABC, abstractmethod
import asyncio
import json
from pathlib import Path
import time
from cachetools import LFUCache
from motor.motor_asyncio import AsyncIOMotorCollection
import yaml
from .errors import CacheNotFoundError, DatabaseNotFoundError
from .utils.color import printer


class Manager:
    """Common class that represents a manager of YAML and cached data.
    """

    dir_ = Path("core/data")

    def __init__(self, path_, config: dict):
        Path.mkdir(Manager.dir_, parents=True, exist_ok=True)
        Path.touch(path_, exist_ok=True)

        with open(path_) as p:
            started = time.time()
            self.name = self.__class__.__name__[:-7].upper()
            self._config = config
            self._max_size = self._config["CACHE_SIZE"]
            self._cached: LFUCache = LFUCache(self._max_size)
            local_storage: dict = yaml.load(
                p, Loader=yaml.FullLoader)
            self._cached.update(local_storage) if local_storage else {}
            elapsed = time.time() - started
            printer(
                "DATA", f"{self.name} CACHE WAS SET IN {elapsed}SECONDS and MAXSIZE IS {self._cached.maxsize}")

    def _fetch_yaml(self) -> dict:
        """Returns a dictionary version of the YAML configuration.

        Returns:
            dict: Dict representation of the YAML file.
        """
        with open(self.path_) as p:
            return yaml.load(
                p, Loader=yaml.FullLoader)

    def _append_yaml(self, extra_config: dict) -> None:
        """Appends to the existing YAML config.
        Creates an empty YAML config if there is none found.

        Args:
            extra_config (dict): The additional data to be passed down to the config.
        """

        with open(self.path_) as p:
            prefixes: dict = yaml.load(p, Loader=yaml.FullLoader)
            prefixes = prefixes if prefixes else {}

        with open(self.path_, "w") as pp:
            prefixes.update(extra_config)
            yaml.safe_dump(prefixes, pp)

    def _set_yaml(self, new_config: dict) -> None:
        """Completely replaces the existing configuration found within the YAML file."

        Args:
            new_config (dict): The new configuration to set the YAML file to.
        """
        with open(self.path_, 'w') as p:
            printer(
                "INFO", f"SYNCING YAML WITH {self.name} CACHE \n{new_config}\n")

            yaml.safe_dump(new_config, p)

    @staticmethod
    def dict_to_cache(dict_: dict, size: int) -> LFUCache:
        l = LFUCache(maxsize=size)
        l.update(dict_)
        return l

    @property
    def cache(self) -> dict:
        return self._cached

    @cache.setter
    def cache(self, new_cache: dict) -> None:
        """Replaces the existing cache with the provided one.

        Args:
            new_cache (dict): The new configuration to set the cache on.
        """
        new_cache = self.dict_to_cache(new_cache, self._max_size)
        if new_cache == self._cached:
            return

        self._cached = new_cache
        self._set_yaml(dict(self._cached))
        return

    async def find_one(self, entry: dict) -> dict:
        """Looks at the cache for the given entry and returns the results. If no entry is found, the actual file will be looked at and the cache will be updated.

        Args:
            entry (dict): The dictionary of the value to look up.

        Raises:
            KeyError: If the value for the given dictionary is not found within either the cache or the YAML.

        Returns:
            list[str]: A list of results from the queried entry.
        """
        key = str(list(entry.values())[0])

        # we can do this since there will always be a default assigned
        ret = self._cached.get(key, None)
        if ret:
            return ret

        # Tries with refreshed cache in case it fails
        ret = self._fetch_yaml().get(key, None)
        if ret:
            self._cached.update({key: ret})
            return ret
        raise CacheNotFoundError(
            f"No {self.name} entry found in cache for given key. {key}")

    async def insert_one(self, key: int, value: dict) -> None:
        """Inserts a value into the yaml configuration, updating the cached config as well.

        Args:
            key (int): The guild id of the guild's config to update.
            value (dict): The dictionary to add to the configuration.
        """
        key = str(key)
        self._cached[key] = value
        self._append_yaml(self._cached)


class Database(ABC):
    """Common class that represents a database.
    """

    def __init__(self, config: dict, collection_name: str) -> None:
        self._config: dict = config
        self._collection: AsyncIOMotorCollection = config['CLUSTER'][collection_name]
        self.loop = asyncio.get_event_loop()

    @property
    def cache(self) -> dict:
        return self._cache_manager.cache

    @staticmethod
    def dict_to_yaml(dict_: dict) -> None:
        """Serializes an object, expectedly a dictionary into a YAML stream. While redundant-looking this solution works.

        Args:
            dict_ (dict): The Python object to serialize.
        """
        return yaml.load(yaml.dump(json.loads(json.dumps(dict_))), Loader=yaml.FullLoader)

    def find(self) -> list:
        return self.loop.run_until_complete(self._find())

    @abstractmethod
    async def _find(self) -> dict:
        raise NotImplementedError()

    async def insert_one(self, guild_id: int, entry: dict) -> None:
        """Inserts the given entry into the MongoDB database, as well as the cache and YAML file.

        Args:
            guild_id (int): The id of the guild.
            entry (dict): The config to upload, expected to be a prefixes key.
        """
        to_insert = {"_id": guild_id}
        to_insert.update(entry)

        await self._collection.insert_one(to_insert)
        await self._cache_manager.insert_one(guild_id, entry)

    async def find_one(self, entry: dict) -> dict:
        """Much like :Manager:find_one: but includes searching the database as a last resort.

        Args:
            entry (dict): The dictionary of the value to look up.

        Raises:
            DatabaseNotFoundError: Error which indicates that the entry does not exist in the database.

        Returns:
            dict: A dictionary representing the result.
        """
        name = self.collection_name

        # This will try from the cache first and then YAML
        try:
            ret = await self._cache_manager.find_one(entry)
            if ret:
                return ret
        except CacheNotFoundError as e:
            pass

            # Contact database as the last resort
            ret = await self._collection.find_one(entry)
            if ret:
                self._cache_manager.cache.update(entry)
                return ret

            raise DatabaseNotFoundError(
                f"No {name} entry found in database for given key. {list(entry.values())[0]}")

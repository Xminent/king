from abc import ABC, abstractmethod
import json
from pathlib import Path
import yaml
from .errors import CacheNotFoundError, DatabaseNotFoundError
from .utils.color import printer


class Manager:
    """Common class that represents a manager of YAML and cached data.
    """

    dir_ = Path("core/data")

    def __init__(self, path_):
        Path.mkdir(Manager.dir_, parents=True, exist_ok=True)
        Path.touch(path_, exist_ok=True)

        with open(path_) as p:
            name = self.__class__.__name__[:-7].upper()
            self._cached: dict = yaml.load(
                p, Loader=yaml.FullLoader)
            self._cached = self._cached if self._cached else {}
            printer("DATA", f"{name} CACHE IS {self._cached}")

    def _fetch_yaml(self) -> dict:
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
        name = self.__class__.__name__[:-7].upper()
        with open(self.path_, 'w') as p:
            printer(
                "INFO", f"SYNCING YAML WITH {name} CACHE \n{new_config}\n")

            yaml.safe_dump(new_config, p)

    @property
    def cache(self) -> dict:
        return self._cached

    @cache.setter
    def cache(self, new_cache: dict) -> None:
        """Replaces the existing cache with the provided one.

        Args:
            new_cache (dict): The new configuration to set the cache on.
        """
        name = self.__class__.__name__[:-7].upper()
        if new_cache == self._cached:
            printer(
                "ERROR", f"{name} CACHE AND DATABASE ALREADY MATCH")
            return

            # only indexing -7 because I know the class name will never change

        self._cached = new_cache
        printer(
            "DATA", f"{name} CACHE IS NOW {self._cached}")
        self._set_yaml(self._cached)
        return printer("DATA", f"NEW {name} CACHE IS {self._cached}")

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
        self._cached = self._fetch_yaml()
        ret = self._cached.get(key, None)
        if ret:
            return ret
        raise CacheNotFoundError(
            f"No value found for given key. {key}")

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
        # This will try from the cache first and then YAML
        try:
            ret = await self._cache_manager.find_one(entry)
            if ret:
                return ret
        except CacheNotFoundError:

            # Contact database as the last resort
            ret = await self._collection.find_one(entry)
            if ret:
                return ret

            raise DatabaseNotFoundError(
                f"No value found for given key. {list(entry.values())[0]}")

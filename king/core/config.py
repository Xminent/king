from pathlib import Path
from typing import Union
import motor.motor_asyncio as motor
import yaml
from .errors import CacheNotFoundError, DatabaseNotFoundError
from .settings_db import BlacklistDatabase, PrefixDatabase
from .settings_caches import BlacklistManager, PrefixManager
from .utils.color import colorify, printer


class Config:
    def __init__(self, config_path: Path) -> None:
        # load config yaml file
        with open(config_path) as stream:
            _config: dict = yaml.load(stream, Loader=yaml.FullLoader)
            config: dict = _config.copy()  # keeping copy of config

        # BASE CONFIGURATION
        self.NAME: str = config.pop("name", "KingBot")
        self.BOT_TOKEN: str = config.pop("bot_token", None)
        self.CACHE_SIZE: int = config.pop("cache_size", 100)
        self.MONGO_DB_URI: str = config.pop("mongo_db_uri", None)
        self.PREFIX: str = config.pop("prefix", "!")
        self.OWNER: int = config.pop("owner", 155780111197536256)
        self.ONLINE_LOG_CHANNEL: int = config.pop("online_log_channel", None)
        self.SCOPES: list = config.pop("scopes", ["bot"])
        self.PERMISSIONS: int = config.pop("permissions", 8526491377)

        if self.MONGO_DB_URI:  # if MONGO_DB_URI is provided
            config.update({"local": False})
            self.CLUSTER = motor.AsyncIOMotorClient(
                self.MONGO_DB_URI)[self.NAME]
        else:
            config.update({"local": True})

        # prep OG config for dumping by copying new values
        _config.update(config)

        self.PREFIXES: list = config.pop("prefixes", None)
        self.BLACKLIST: list = config.pop("blacklist", None)
        self.LOCAL: bool = config.pop("local")

        # Raises to prevent any additional unwanted variables
        if config:  # if it has been previously set
            raise TypeError(
                colorify(
                    "ERROR",
                    f"Unexpected config variables: {list(config.keys())}"
                )
            )

        with open(config_path, "w") as stream:
            yaml.safe_dump(_config, stream)

        self.__dict__.update(_config)

        if self.LOCAL:
            self._prefixes = PrefixManager(self.__dict__.copy())
            self._blacklist = BlacklistManager(self.__dict__.copy())
        else:
            self._prefixes = PrefixDatabase(self.__dict__.copy())
            self._blacklist = BlacklistDatabase(self.__dict__.copy())

        printer("DATA", f"STORAGE IS LOCAL?: {self.LOCAL}")

    @property
    def prefixes(self) -> Union[PrefixManager, PrefixDatabase]:
        return self._prefixes

    @property
    def blacklist(self) -> Union[BlacklistManager, BlacklistDatabase]:
        return self._blacklist

    async def register_guild_default(self, guild_id: int) -> None:
        exists = False
        try:
            exists = await self.prefixes.find_one({"_id": guild_id})
        except (CacheNotFoundError, DatabaseNotFoundError) as e:
            print(e)
        finally:
            if not exists:
                printer("INFO", f"REGISTERED GUILD {guild_id}")
                return await self.prefixes.insert_one(
                    guild_id,
                    {"prefixes": [self.PREFIX]},
                )
            return

    async def register_blacklisted_user(self, guild_id: int, user_id: int, reason: str) -> None:
        """Registers the user for blacklisting from a specific guild.

        Args:
            guild_id (int): The ID of the guild to blacklist the user from.
            user_id (int): The ID of the user to blacklist.
            reason (str): The reason for the blacklisting.
        """
        exists = False
        try:
            exists = await self.blacklist.find_one({"_id": guild_id})

        except (CacheNotFoundError, DatabaseNotFoundError) as e:
            print(e)

        finally:
            if not exists:
                printer("INFO", f"BLACKLISTED USER {user_id}")
                return await self.blacklist.insert_one(
                    guild_id,
                    {"blacklist": {
                        str(user_id): {
                            "reason": reason,
                        }
                    }
                    },
                )
            return

    async def is_blacklisted(self, guild_id: int, user_id: int) -> bool:
        """Checks whether a user is blacklisted for a given guild.

        Args:
            guild_id (int): The ID of the guild to check.
            user_id (int): The ID of the user to check.

        Returns:
            bool: Whether or not the user is blacklisted.
        """
        exists = False

        try:
            exists = await self.blacklist.find_one({"_id": guild_id})

        except (CacheNotFoundError, DatabaseNotFoundError):
            pass

        finally:
            if not exists:  # if no blacklist for guild exists..
                return False

            elif str(user_id) in exists.get("blacklist"):
                return True
            return False

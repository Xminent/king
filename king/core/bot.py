import os
from typing import Union
import discord
from discord.ext.commands import *
from .config import Config
from .settings_db import BlacklistDatabase, PrefixDatabase
from .events import init_events
from .settings_caches import BlacklistManager, PrefixManager
from .utils.color import colorify, printer, Color
from .utils.embed import embed


# Some metadata about the bot
description = '''
Xminent's discord bot, developed with discord.py
A full list of all commands are available here: https://github.com/Xminent/king
'''


class KingBot(AutoShardedBot):
    """Class Representing an instance of King."""

    def __init__(self, config: dict, *args, **kwargs) -> None:
        super().__init__(description=description, *args, **kwargs)

        # DEV MODE
        self.dev: bool = kwargs.pop('dev', False)

        # DB COLLECTIONS
        self._config: Config = Config(config)
        self._prefixes: Union[PrefixDatabase,
                              PrefixManager] = self._config.prefixes
        self._blacklist: Union[BlacklistDatabase,
                               BlacklistManager] = self._config.blacklist

    @property
    def config(self) -> Config:
        return self._config

    @property
    def name(self) -> str:
        return self.config.NAME

    @property
    def default_prefix(self) -> str:
        return self.config.PREFIX

    # we can use app info here because it will be set during the intialization of the bot found in the `on_ready` event
    @property
    def invite_url(self) -> str:
        permissions = discord.Permissions(self.config.PERMISSIONS)
        scopes = self.config.SCOPES
        return discord.utils.oauth_url(self.app_info.id, permissions, scopes=scopes)

    def user_is_admin(self, user: discord.User) -> bool:
        return user.guild_permissions.administrator

    async def load_extensions(self, dirname: str) -> None:
        """Loads the extensions found in the given directory.

        Args:
            dirname (str): The name/path of the directory to load the cogs from.
        """
        await self.wait_until_ready()

        cogs_text = ""
        i = 0
        cogs = [file for file in os.listdir(dirname) if file.endswith(
            '.py') and not file.startswith('__init__')]

        for cog in cogs:
            try:
                self.load_extension(
                    f'{dirname[2:].replace("/", ".")}.{cog[:-3]}')
                cogs_text += f"🟢 Loaded {cog[:-3]}\n"
                i += 1
            except (ExtensionNotFound, ExtensionAlreadyLoaded, NoEntryPointError, ExtensionFailed) as e:
                cogs_text += f"🔴 Unable to load {cog[:-3]} | {e}\n"

        if self.config.ONLINE_LOG_CHANNEL:
            await self.get_channel(self.config.ONLINE_LOG_CHANNEL).send(embed=embed("Cogs Loaded", f"```{cogs_text}```"))

        printer(
            "INFO", f"Loaded {i}/{len(cogs)} extensions from {Color.blue(dirname)}")

    async def get_prefix(self, message: discord.Message) -> list:
        """Override of the default get_prefix command

        Prefix fetching is done on a cache-first strategy.

        Args:
            `message (discord.Message)`: The message context to get the prefix of.

        Returns:
            :class:`str`: A single prefix that the bot is listening for
        """
        if not message.guild:
            printer("ERROR", "NO GUILD FOUND FOR MESSAGE")
            return [self.config.PREFIX]

        guild_id = message.guild.id

        # finds prefix that matches the messsage guild ID
        q = await self._prefixes.find_one({"_id": guild_id})
        if q:
            prefixes = q.get("prefixes")
            if prefixes:
                return prefixes

        raise TypeError(colorify("ERROR", "command_prefix must be plain string, iterable of strings, or callable "
                        "returning either of these, not {}".format(q.__class__.__name__)))

    async def start(self, *args, **kwargs) -> None:
        """
        Overridden start which ensures cog load and other pre-connection tasks are handled
        """
        init_events(self)
        return await super().start(self.config.BOT_TOKEN, *args, **kwargs)

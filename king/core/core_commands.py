import discord
from core.bot import KingBot


class CoreLogic:

    def __init__(self, bot: KingBot) -> None:
        self.bot = bot

    async def _invite_url(self) -> str:
        """
        Generates the invite URL for the bot.

        Returns
        -------
        str
            Invite URL.
        """
        app_info = await self.bot.application_info()
        data = await self.bot._config
        scopes = data["scopes"]
        perms_int = data["permissions"]
        permissions = discord.Permissions(perms_int)
        return discord.utils.oauth_url(app_info.id, permissions, scopes=scopes)

import discord
from discord.ext import commands
from ..bot import KingBot


class Mod(commands.Cog):

    def __init__(self, bot: KingBot):
        self.bot = bot

    @commands.command()
    async def blacklist(self, ctx, user: discord.Member, *, reason: str) -> None:
        await self.bot.config.register_blacklisted_user(ctx.guild.id, user.id, reason)
        await ctx.send(f"Blacklisted user {user}")


def setup(bot):
    bot.add_cog(Mod(bot))

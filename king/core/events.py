from art import text2art
import discord
from .utils.color import printer, Color


def init_events(bot):
    @bot.event
    async def on_ready():
        bot.app_info = await bot.application_info()
        # await bot.get_blacklisted_users()
        printer("BANNER", text2art(bot.name))
        printer("INFO", f"Logged in as {Color.blue(bot.user)}")
        printer(
            "INFO", f'Bot-Name: {Color.blue(bot.user.name) + Color.RESET} {Color.yellow("| ID:")} {Color.blue(bot.user.id) + Color.RESET}')
        printer("INFO", f'Dev Mode: {Color.blue(bot.dev)}')
        printer("INFO", f'Discord Version: {Color.blue(discord.__version__)}')

        printer("INFO", f'Invite URL: {Color.blue(bot.invite_url)}')

        await bot.load_extensions('./core/cogs')

    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return
        if isinstance(message.channel, discord.DMChannel):
            await message.author.send(':x: Sorry, but I don\'t accept commands through direct messages! Please use the `#bots` channel of your corresponding server!')
            return
        if message.guild:
            if await bot.config.is_blacklisted(message.guild.id, message.author.id):
                return
        if bot.dev and not await bot.is_owner(message.author):
            return
        if bot.user.mentioned_in(message) and message.mention_everyone is False:
            if 'help' in message.content.lower():
                await message.channel.send(f'A full list of all commands is available here using the {bot.default_prefix}help command!')
            else:
                await message.add_reaction('👀')
        await bot.process_commands(message)

    @bot.event
    async def on_guild_join(guild: discord.Guild):
        embed = discord.Embed(
            title=':white_check_mark: Guild Added', type='rich', color=0x2ecc71)
        embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name='Name', value=guild.name, inline=True)
        embed.add_field(name='ID', value=guild.id, inline=True)
        embed.add_field(name='Owner',
                        value=f'{guild.owner} ({guild.owner.id})', inline=True)
        embed.add_field(name='Region', value=guild.region, inline=True)
        embed.add_field(name='Members', value=guild.member_count, inline=True)
        embed.add_field(name='Created On', value=guild.created_at, inline=True)
        printer("SUCCESS", f"GUILD {guild.id} ADDED BOT TO THEIR SERVER")
        await bot.app_info.owner.send(embed=embed)

        await bot._config.register_guild_default(guild.id)

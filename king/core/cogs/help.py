import itertools
from discord import Embed
from discord.ext import commands
from discord.ext.commands import HelpCommand, DefaultHelpCommand
from discord.ext.commands.core import Group


class KingHelp(HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.paginator = None
        self.spacer = "\u1160 "

    async def send_pages(self, header=False, footer=False, title=False, destination=False):
        if not destination:
            destination = self.get_destination()

        embed = Embed(
            color=0x2ECC71,
        )

        if title:
            embed.title = title[0]
            embed.description = title[1]

        if header:
            embed.set_author(
                name=self.context.bot.description,
                icon_url=self.context.bot.user.avatar_url
            )
            embed.description = f"• To change your prefix or your server's prefix use `{self.clean_prefix}help prefix`\n• Suggestions or support? Join my [Support Server](https://discord.gg/cWKZAMc)!\n• Like what I do? Consider donating to my patreon at https://www.patreon.com/kingbot.\n• Don't like my commands? `blacklist` them!\n• Use `{self.clean_prefix}help help` to see available commands in your channel."

        for category, entries in self.paginator:
            embed.add_field(
                name=category,
                value=entries,
                inline=False
            )
        if footer:
            embed.set_footer(
                text=f'Prefix: {self.clean_prefix} | Server Prefix: {self.clean_prefix}'
            )
        await destination.send(embed=embed)

    async def send_bot_help(self, destination=None):
        ctx = self.context
        bot = ctx.bot

        def get_category(command):
            cog = command.cog
            return cog.qualified_name + ':' if cog is not None else 'Help:'

        filtered = await self.filter_commands(
            bot.commands,
            sort=True,
            key=get_category
        )
        to_iterate = itertools.groupby(filtered, key=get_category)
        for cog_name, command_grouper in to_iterate:
            cmds = sorted(command_grouper, key=lambda c: c.name)
            category = f'❯ {cog_name.upper()}'
            if len(cmds) == 1:
                entries = f'{self.spacer}{cmds[0].name} → {cmds[0].short_doc}'
            else:
                entries = ''
                while len(cmds) > 0:
                    entries += self.spacer
                    entries += ' **|** '.join([cmd.name for cmd in cmds[0:8]])
                    cmds = cmds[8:]
                    entries += '\n' if cmds else ''
            self.paginator.append((category, entries))
        await self.send_pages(header=True, footer=True, destination=destination)

    async def send_command_help(self, command):

        # add the usage text [REQUIRED]
        usage = command.usage if command.usage else "`None`"
        self.paginator.append(
            ("❯ Usage",  usage)
        )

        # add examples text [REQUIRED]
        examples = command.brief if command.brief else "`None`"
        self.paginator.append(
            ("❯ Examples",  examples)
        )

        # add aliases text [REQUIRED]
        aliases = " **|** ".join(
            f'`{alias}`' for alias in command.aliases) if command.aliases else "None"

        self.paginator.append(
            ("❯ Aliases",  aliases)
        )

        await self.send_pages(title=(command.name.title(), command.help), footer=True)

    async def prepare_help_command(self, ctx, command=None):
        self.paginator = []
        await super().prepare_help_command(ctx, command)

    async def send_error_message(self):
        """This is the override of the default error message method and we consider not passing a command as a parameter an error. Much like Bongo Bot's functionality, it will DM you the list of commands if you do not specify the command as an inference that you do not know the commands.
        """
        destination = self.context.author
        await self.send_bot_help(destination=destination)
        await self.get_destination().send('`✅` I have DMed you my commands!')

    async def on_help_command_error(self, ctx, error):
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))

    async def command_callback(self, ctx, *, command=None):
        await self.prepare_help_command(ctx, command)
        bot = ctx.bot

        if command is None:
            return await self.send_error_message()

        if command.lower() == 'help':
            return await self.send_bot_help()

        # Check if it's a cog
        cog = bot.get_cog(command)
        if cog is not None:
            return await self.send_cog_help(cog)

        # If it's not a cog then it's a command.
        # Since we want to have detailed errors when someone
        # passes an invalid subcommand, we need to walk through
        # the command group chain ourselves.
        keys = command.split(' ')
        cmd = bot.all_commands.get(keys[0])
        if cmd is None:
            return await self.send_error_message()

        for key in keys[1:]:
            try:
                found = cmd.all_commands.get(key)
            except AttributeError:
                return await self.send_error_message()
            else:
                if found is None:
                    return await self.send_error_message()
                cmd = found

        if isinstance(cmd, Group):
            return await self.send_group_help(cmd)
        else:
            return await self.send_command_help(cmd)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = KingHelp(
            command_attrs={
                'aliases': ['halp'],
                'help': 'Shows help about the bot, a command, or a category',
                'hidden': True
            }
        )

    async def cog_check(self, ctx):
        return self.bot.user_is_admin(ctx.author)

    def cog_unload(self):
        self.bot.get_command('help').hidden = False
        self.bot.help_command = DefaultHelpCommand()

    @commands.command(
        aliases=['halpall'],
        hidden=True
    )
    async def helpall(self, ctx, *, text=None):
        """Print bot help including all hidden commands."""
        self.bot.help_command = KingHelp(show_hidden=True)
        if text:
            await ctx.send_help(text)
        else:
            await ctx.send_help()
        self.bot.help_command = KingHelp()


def setup(bot):
    bot.add_cog(Help(bot))

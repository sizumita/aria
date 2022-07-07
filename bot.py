from discord.ext import commands
from os import environ
from lib.database import Database
import discord


class Aria(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=commands.when_mentioned_or(environ.get('PREFIX', 'aria ')),
            help_command=None,
            intents=intents
        )
        self.db = Database(self)

    async def setup_hook(self) -> None:
        extensions = [
            "cogs.manage",
            "cogs.game_controller",
            "cogs.help",
            "cogs.admin",
        ]
        for extension in extensions:
            await self.load_extension(extension)

    async def on_ready(self) -> None:
        status = discord.Game("Aria - War of incantation")
        await self.change_presence(activity=status)

    async def on_command_error(self, context: commands.Context, exception: Exception) -> None:
        if isinstance(exception, commands.CommandNotFound):
            return

        if isinstance(exception, commands.CommandOnCooldown):
            return

        await super(Aria, self).on_command_error(context, exception)

from discord.ext import commands
from os import environ
from lib.database import Database
import discord


class Aria(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=commands.when_mentioned_or(
            environ.get('PREFIX', 'aria ')))
        self.db = Database(self)

    async def on_ready(self) -> None:
        status = discord.Game("Aria - War of incantation")
        await self.change_presence(activity=status)

    async def on_command_error(self, context, exception):
        if isinstance(exception, commands.CommandNotFound):
            return

        if isinstance(exception, commands.CommandOnCooldown):
            return

        await super(Aria, self).on_command_error(context, exception)

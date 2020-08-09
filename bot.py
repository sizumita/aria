from discord.ext import commands
from os import environ
from lib.database import Database
import discord


class Aria(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=commands.when_mentioned_or(
            environ.get('PREFIX', 'aria ')))
        self.db = Database()

    async def on_ready(self) -> None:
        status = discord.Game("Aria - War of incantation")
        await self.change_presence(activity=status)

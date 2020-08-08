from discord.ext import commands
from os import environ
from lib.database import Database


class Aria(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(environ.get('PREFIX', 'aria ')))
        self.db = Database()

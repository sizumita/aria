import discord
from discord.ext import commands
from os import environ
from lib.database import Database


class Aria(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(environ.get('PREFIX', 'aria ')))
        self.db = Database()
    
    async def on_ready(self):
        await client.change_presence(activity=discord.Game(name='Aria - War of incantation'))

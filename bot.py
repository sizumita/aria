from discord.ext import commands


class Aria(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('spell '))

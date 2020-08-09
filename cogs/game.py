import discord
from discord.ext import commands
import textwrap

REACTION_YES = "\U0001f44d"
REACTION_NO = "\U0001f44e"
REACTIONS = [REACTION_YES, REACTION_NO]


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db


def setup(bot):
    bot.add_cog(Game(bot))

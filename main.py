from bot import Aria
from os import environ


bot = Aria()

bot.run(environ['BOT_TOKEN'])

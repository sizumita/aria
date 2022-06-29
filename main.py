from bot import Aria
from os import environ

bot = Aria()

@bot.listen
async def setup_hook():
    extensions = [
        "cogs.manage",
        "cogs.game_controller",
        "cogs.help",
        "cogs.admin",
    ]
    for extension in extensions:
        await bot.load_extension(extension)

bot.run(environ['BOT_TOKEN'])

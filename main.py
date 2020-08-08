from bot import Aria
from os import environ
from dotenv import load_dotenv

# .envファイルからロード
load_dotenv()

bot = Aria()

extensions = ["cogs.manage"]
for extension in extensions:
    bot.load_extension(extension)

bot.run(environ['BOT_TOKEN'])

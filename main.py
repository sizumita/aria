from bot import Aria
from os import environ
from dotenv import load_dotenv

# .envファイルからロード
load_dotenv()

bot = Aria()

extensions = ["manage"]
for cog in extensions:
    bot.load_extension(f"cogs.{cog}")

bot.run(environ['BOT_TOKEN'])

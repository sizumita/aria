from bot import Aria
from os import environ
from dotenv import load_dotenv

# .envファイルからロード
load_dotenv()

bot = Aria()

extensions = []

bot.run(environ['BOT_TOKEN'])

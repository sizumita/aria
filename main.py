from bot import Aria
from os import environ
from os.path import join, dirname
from dotenv import load_dotenv

# .envファイルからロード
load_dotenv()

bot = Aria()

extensions = []

bot.run(environ.get('BOT_TOKEN'))

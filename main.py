from bot import Aria
from os import environ
from os.path import join, dirname
from dotenv import load_dotenv

# .envファイルからロード
load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

bot = Aria()

extensions = []

bot.run(environ.get('BOT_TOKEN'))

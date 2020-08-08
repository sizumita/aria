import asyncio
import os
from collections import namedtuple
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Database:
    """CREATE TABLE users (user_id bigint, hp integer, mp integer, PRIMARY KEY(user_id))"""
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        if self.db_url is None:
            raise Exception('DATABASE_URL Not Found.')
        self.conn = None
        asyncio.create_task(self.check_database())
        asyncio.create_task(self.setup)

    async def check_database(self):
        conn = self.conn or await self.setup()
        try:
            await conn.execute('select "users"::regclass')
        except asyncpg.exceptions.UndefinedColumnError:
            await conn.execute('CREATE TABLE users (user_id bigint, hp integer, mp integer, PRIMARY KEY(user_id))')

    async def setup(self):
        self.conn = await asyncpg.connect(self.db_url)
        return self.conn

    async def close(self):
        await self.conn.close()

    async def get_user(self, user_id):
        conn = self.conn or await self.setup()
        data = await conn.fetch('SELECT hp mp FROM users WHERE user_id=$1', user_id)
        if data.get('user_id'):
            hp = data.get('hp')
            mp = data.get('mp')
            User = namedtuple('User', ('user_id', 'hp', 'mp'))
            return User(user_id, hp, mp)
        else:
            return None

    async def create_user(self, user_id):
        conn = self.conn or await self.setup()
        await conn.execute('INSERT INTO users ($1, $2, $3)', user_id, 100, 100)
        return await self.get_user(user_id)

    async def update_user(self, user_id, hp, mp):
        conn = self.conn or await self.setup()
        await conn.execute('UPDATE users SET hp = $1, mp = $2 WHERE user_id = $3', hp, mp, user_id)
        return await self.get_user(user_id)

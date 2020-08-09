import os
from typing import NamedTuple

import asyncpg

User = NamedTuple('User', [('id', int), ('hp', int), ('mp', int)])


class Database:
    """CREATE TABLE users (user_id bigint, hp integer, mp integer, PRIMARY KEY(user_id))"""
    def __init__(self, bot):
        self.bot = bot
        self.db_url = os.environ['DATABASE_URL']
        self.conn = None

    async def check_database(self):
        conn = self.conn or await self.setup()
        try:
            await conn.execute('select "users"::regclass')
        except asyncpg.exceptions.UndefinedColumnError:
            await conn.execute('CREATE TABLE users (user_id bigint, hp integer, mp integer, PRIMARY KEY(user_id))')

    async def setup(self):
        self.conn = await asyncpg.connect(
            host='mydb',
            port=5432,
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            database=os.environ['POSTGRES_DB'],
            loop=self.bot.loop,
        )
        return self.conn

    async def close(self):
        await self.conn.close()

    async def get_user(self, user_id):
        conn = self.conn or await self.setup()
        data = await conn.fetch('SELECT hp mp FROM users WHERE user_id=$1', user_id)
        if data.get('user_id'):
            hp = data.get('hp')
            mp = data.get('mp')
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

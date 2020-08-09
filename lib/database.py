import os
from typing import NamedTuple

import asyncpg

User = NamedTuple('User', [('id', int), ('hp', int), ('mp', int)])


class Database:
    """CREATE TABLE users (user_id bigint, hp integer, mp integer, PRIMARY KEY(user_id))"""
    def __init__(self):
        self.db_url = os.environ['DATABASE_URL']
        self.conn = None

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
        data = await conn.fetch('SELECT * FROM users WHERE user_id=$1', user_id)
        if not data:
            return None

        target = list(data[0])
        return User(target[0], target[1], target[2])

    async def create_user(self, user_id):
        conn = self.conn or await self.setup()
        await conn.execute('INSERT INTO users (user_id, hp, mp) VALUES ($1, $2, $3)', user_id, 100, 100)
        return await self.get_user(user_id)

    async def update_user(self, user_id, hp, mp):
        conn = self.conn or await self.setup()
        await conn.execute('UPDATE users SET hp = $1, mp = $2 WHERE user_id = $3', hp, mp, user_id)
        return await self.get_user(user_id)

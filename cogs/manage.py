import textwrap
from typing import Any

import discord
from discord.ext import commands


class ManageCog(commands.Cog):
    def __init__(self, bot: Any) -> None:
        self.bot = bot
        self.db = bot.db

    @commands.command()
    async def register(self, ctx: commands.Context) -> None:
        user = await self.db.get_user(ctx.author.id)
        if user is not None:
            await ctx.send("あなたはすでに登録されています")
            return

        await self.db.create_user(ctx.author.id)
        await ctx.send("ユーザー登録を行いました")
        # メッセージは要検討

    @commands.command()
    async def status(self, ctx: commands.Context, user: discord.User = None) -> None:
        target_user = user if user else ctx.author
        user_data = await self.db.get_user(target_user.id)
        if user_data is None:
            await ctx.send("まだ登録されていません")
            return

        msg_text = f"""\
        {target_user.mention} さんのステータス
        HP: {user_data.hp}HP
        MP: {user_data.mp}MP
        """
        await ctx.send(textwrap.dedent(msg_text))
        return

    @commands.command()
    async def ranking(self, ctx: commands.Context) -> None:
        users_ranking = await self.db.get_user_rankings()
        ranking_message = ""

        for user_ranking in users_ranking:
            user = self.bot.get_user(user_ranking[0].id)
            user_data = user_ranking[0]

            ranking_message += f"`{user_ranking[1]}位: {user.display_name}(`{user.mention}`), HP: {user_data.hp}, MP: {user_data.mp}`\n"

        if not discord.utils.find(lambda u: u[0].id == ctx.author.id, users_ranking):
            if rank := await self.db.get_user_ranking(ctx.author.id):
                user_data = await self.bot.db.get_user(ctx.author.id)
                ranking_message += f"\n`{rank}位: {ctx.author.display_name}(`{ctx.author.mention}`), HP: {user_data.hp}, MP: {user_data.mp}`"

        await ctx.send(ranking_message, allowed_mentions=discord.AllowedMentions(users=False))


def setup(bot: Any) -> None:
    bot.add_cog(ManageCog(bot))

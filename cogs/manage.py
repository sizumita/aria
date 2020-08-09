import discord
from discord.ext import commands
from bot import Aria
import textwrap


class ManageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.command()
    async def register(self, ctx):
        user = self.db.get_user(ctx.author.id)
        if user is not None:
            return await ctx.send("あなたはすでに登録されています")
        self.db.create_user(ctx.author.id)
        await ctx.send("ユーザー登録を行いました")
        # メッセージは要検討

    @commands.command()
    async def status(self, ctx, user: discord.User = None):
        target_user = user if user else ctx.author
        user_data = await self.db.get_user(target_user.id)
        if user_data is None:
            return await ctx.send("まだ登録されていません")

        msg_text = f"""\
        {target_user.mention} さんのステータス
        HP: {user_data.hp}HP
        MP: {user_data.mp}MP
        """
        return await ctx.send(textwrap.dedent(msg_text))


def setup(bot):
    bot.add_cog(ManageCog(bot))

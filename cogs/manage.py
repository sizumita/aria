from discord.ext import commands
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
    async def status(self, ctx):
        user = self.db.get_user(ctx.author.id)
        if user is None:
            return ctx.send("あなたはまだ登録されていません")
        
        msg_text = f"""\
        {ctx.author.mention} さんのステータス
        HP: {user.hp}HP
        MP: {user.mp}MP
        """
        return await ctx.send(textwrap.dedent(msg_text))


def setup(bot):
    bot.add_cog(ManageCog(bot))

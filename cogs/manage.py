from discord.ext import commands


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


def setup(bot):
    bot.add_cog(ManageCog(bot))

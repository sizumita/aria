from discord.ext import commands
from bot import Aria


class ManageCog(commands.Cog):
    def __init__(self, bot: Aria) -> None:
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


def setup(bot: Aria) -> None:
    bot.add_cog(ManageCog(bot))

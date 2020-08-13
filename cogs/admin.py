from discord.ext import commands
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Aria # noqa


@dataclass
class Admin(commands.Cog):
    bot: 'Aria'

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def reload(self, ctx: commands.Context) -> None:
        """全てのextensionをリロードする"""
        for extension in list(self.bot.extensions):
            try:
                self.bot.reload_extension(extension)
            except Exception as e:
                await ctx.send(f'An error was occurred: {e} (in extension: {extension})')
                return
        await ctx.send('Reload all extensions.')

    @commands.command(aliases=['exit', 'quit'])
    async def down(self, ctx: commands.Context) -> None:
        await ctx.send('down bot')
        await self.bot.close()


def setup(bot: 'Aria'):
    bot.add_cog(Admin(bot))

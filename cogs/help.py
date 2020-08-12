from discord.ext import commands
from typing import TYPE_CHECKING
import discord

if TYPE_CHECKING:
    from bot import Aria # noqa


command_list = [
    '`help` -> このメッセージを表示します。',
    '`register` -> ユーザー登録をします。',
    '`status` -> 現在のあなたの最大HPとMPを表示します。',
    '`ranking` -> HPとMPの合計値の最大のランキングを表示します。',
    '`apply @メンション` -> 指定したユーザーをゲームに誘います。',
]


class Help(commands.Cog):
    def __init__(self, bot: 'Aria') -> None:
        self.bot = bot

    @commands.command()
    async def help(self, ctx: commands.Context) -> None:
        embed = discord.Embed(
            title='Aria - War of incantation',
            description='Ariaのコマンド一覧を表示します。',
            timestamp=ctx.message.created_at,
            color=0x1976D2,
        )
        embed.add_field(
            name='リンク一覧',
            value='[公式wiki](https://github.com/sizumita/aria/wiki/トップページ)\n'
                  '[招待URL](https://discord.com/api/oauth2/authorize?client_id='
                  '741807660894257284&permissions=388160&scope=bot)\n'
                  '不明な点があったら[こいつのtwitter](https://twitter.com/sizumita)にDMしてくれな。',
            inline=False,
        )
        embed.add_field(
            name='コマンド一覧',
            value='\n'.join([f'{ctx.prefix}' + cmd for cmd in command_list]),
            inline=False,
        )
        await ctx.send(embed=embed)


def setup(bot: 'Aria') -> None:
    bot.add_cog(Help(bot))

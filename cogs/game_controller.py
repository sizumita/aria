import discord
from discord.ext import commands
from lib.game import DiscordGame, TestMode
import asyncio
from typing import TYPE_CHECKING, Dict, List
import textwrap

if TYPE_CHECKING:
    from bot import Aria # noqa

REACTION_YES = "\U0001f44d"
REACTION_NO = "\U0001f44e"
REACTIONS = [REACTION_YES, REACTION_NO]


class Game(commands.Cog):
    def __init__(self, bot: 'Aria') -> None:
        self.bot = bot
        self.db = self.bot.db
        self.games: Dict[int, DiscordGame] = {}
        self.game_members: List[int] = []

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def apply(self, ctx: commands.Context, target_member: discord.Member) -> None:
        if ctx.author.id == target_member.id:
            await ctx.send('あなた自身を選ぶことはできません。')
            return
        if target_member.bot:
            await ctx.send('Botを相手に選ぶことはできません。')
            return
        if ctx.channel.id in self.games.keys():
            await ctx.send('このチャンネルではすでにゲームが開始しています。')
            return
        if ctx.author.id in self.game_members:
            await ctx.send('あなたはすでにゲームを開始しています。')
            return
        if target_member.id in self.game_members:
            await ctx.send('あなたが指定したメンバーはすでにゲームに参加しています。')
            return

        author_data = await self.db.get_user(ctx.author.id)
        if author_data is None:
            await ctx.send("あなたはユーザー登録されていません。")
            return
        target_member_data = await self.db.get_user(target_member.id)
        if target_member_data is None:
            await ctx.send("対戦申し込み先のユーザーがユーザー登録されていません。")
            return

        msg_text = f"""\
        {target_member.mention}
        {ctx.author.mention} に対決を申し込まれました。
        受ける場合は :+1:
        拒否する場合は :-1:
        """
        confirm_msg: discord.Message = await ctx.send(textwrap.dedent(msg_text))
        for reaction_emoji in REACTIONS:
            await confirm_msg.add_reaction(reaction_emoji)

        def check(check_reaction: discord.Reaction, member: discord.Member) -> bool:
            if check_reaction.message.id != confirm_msg.id:
                return False
            if str(check_reaction.emoji) not in REACTIONS:
                return False
            if member != target_member:
                return False
            return True

        try:
            reaction: discord.Reaction
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send("60秒以内にリアクションされなかったため対戦はキャンセルされました。")
            return

        if str(reaction.emoji) == REACTION_NO:
            await ctx.send("拒否リアクションが押されたため対戦はキャンセルされました。")
            return

        await ctx.send("対戦が受けられました。ゲームを開始しています...")
        game = DiscordGame(self.bot, ctx.author, target_member, ctx.channel, ctx.send)

        # ゲーム開始
        self.games[ctx.channel.id] = game
        self.game_members.append(ctx.author.id)
        self.game_members.append(target_member.id)
        await game.start()

        # ゲーム終了
        del self.games[ctx.channel.id]
        self.game_members.remove(ctx.author.id)
        self.game_members.remove(target_member.id)

    @apply.error
    async def apply_error(self, ctx: commands.Context, err: commands.CommandInvokeError) -> None:
        if isinstance(err, commands.CommandOnCooldown):
            await ctx.send("再申し込みするには30秒間のクールダウンが必要です。")
        elif isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("引数に対戦申し込みしたいユーザーのメンションを入れて実行してください。")
        else:
            await self.bot.on_command_error(ctx, err)

    @commands.command()
    async def test(self, ctx: commands.Context) -> None:
        game = TestMode(self.bot, ctx.author, ctx.author, ctx.channel, ctx.send)
        self.games[ctx.channel.id] = game
        self.game_members.append(ctx.author.id)

        await game.start()

        # ゲーム終了
        del self.games[ctx.channel.id]
        self.game_members.remove(ctx.author.id)


async def setup(bot: 'Aria') -> None:
    await bot.add_cog(Game(bot))

import discord
from discord.ext import commands
from lib.game import DiscordGame
import asyncio
from typing import Any
import textwrap

REACTION_YES = "\U0001f44d"
REACTION_NO = "\U0001f44e"
REACTIONS = [REACTION_YES, REACTION_NO]


class Game(commands.Cog):
    def __init__(self, bot: Any):
        self.bot = bot
        self.db = self.bot.db

    @commands.command()
    @commands.cooldown(1, 30)
    async def apply(self, ctx: commands.Context, target_user: discord.User):
        author_data = await self.db.get_user(ctx.author.id)
        if author_data is None:
            return await ctx.send("あなたはユーザー登録されていません。")
        target_user_data = await self.db.get_user(target_user.id)
        if target_user_data is None:
            return await ctx.send("対戦申し込み先のユーザーがユーザー登録されていません。")

        msg_text = f"""\
        {target_user.mention}
        {ctx.author.mention} に対決を申し込まれました。
        受ける場合は :+1:
        拒否する場合は :-1:
        """
        confirm_msg: discord.Message = await ctx.send(textwrap.dedent(msg_text))
        for reaction in REACTIONS:
            await confirm_msg.add_reaction(reaction)

        def check(reaction: discord.Reaction, user: discord.Member):
            if not str(reaction.emoji) in REACTIONS:
                return
            if not user == target_user:
                return
            return True

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return await ctx.send("60秒以内にリアクションされなかったため対戦はキャンセルされました。")

        if str(reaction.emoji) == REACTION_NO:
            return await ctx.send("拒否リアクションが押されたため対戦はキャンセルされました。")

        await ctx.send("対戦が受けられました。ゲームを開始しています...")
        game = DiscordGame(self.bot, ctx.author, target_user, ctx.channel, ctx.send)
        await game.start()

    @apply.error
    async def apply_error(self, ctx, err):
        if isinstance(err, commands.CommandOnCooldown):
            return await ctx.send("再申し込みするには30秒間のクールダウンが必要です。")
        elif isinstance(err, commands.MissingRequiredArgument):
            return await ctx.send("引数に対戦申し込みしたいユーザーのメンションを入れて実行してください。")

        await self.bot.on_command_error(ctx, err)


def setup(bot):
    bot.add_cog(Game(bot))

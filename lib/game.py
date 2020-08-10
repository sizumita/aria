from discord.ext import commands
import discord
from typing import Any, Callable, Union
from lib.spell import Spell
from asyncio import Task, Event, sleep


class Game:
    def __init__(self, bot: Any, alpha: discord.Member, beta: discord.Member, ctx: commands.Context) -> None:
        self.bot = bot
        self.alpha = alpha
        self.beta = beta
        self.ctx = ctx
        self.channel = ctx.channel
        self.guild = ctx.guild
        self.finish = False
        self.alpha_spell: Union[None, Spell] = None
        self.beta_spell: Union[None, Spell] = None
        self.alpha_loop: Union[None, Task] = None
        self.beta_loop: Union[None, Task] = None
        self.alpha_hp = 100
        self.beta_hp = 100
        self.alpha_mp = 100
        self.beta_mp = 100
        self.ready_to_raise = False
        self.battle_finish_flag = Event(loop=self.bot.loop)

    def alpha_check(self, message: discord.Message) -> bool:
        return message.channel.id == self.channel.id \
               and message.author.id == self.alpha.id

    def beta_check(self, message: discord.Message) -> bool:
        return message.channel.id == self.channel.id \
               and message.author.id == self.beta.id

    async def recv_command(self, check: Callable, user: str) -> Union[Spell, None]:
        spell = Spell()
        while not self.bot.is_closed() and not self.finish:
            message: discord.Message = await self.bot.wait_for('message', check=check, timeout=60)
            if message.content == 'execute':
                if not self.use_mp(user, 5):
                    await self.ctx.send('MPが枯渇しました。')
                    return None
                break

            if not spell.can_aria(message.created_at):
                return None

            if mp := spell.receive_command(message.content, message.created_at):
                await self.ctx.send('コマンドを受け取りました。')
                if not self.use_mp(user, mp):
                    await self.ctx.send('MPが枯渇しました。')
                    return None
                continue

            return None

        return spell

    async def raise_spell(self) -> None:
        self.ready_to_raise = True
        await sleep(5)

        alpha_to_beta_damage: int
        beta_to_alpha_damage: int

        if self.alpha_spell is None:
            alpha_to_beta_damage = 0
            beta_to_alpha_damage = self.beta_spell.calculate_damage(self.alpha_spell) \
                if self.beta_spell is not None else 0

        elif self.beta_spell is None:
            alpha_to_beta_damage = self.alpha_spell.calculate_damage(self.beta_spell)\
                if self.alpha_spell is not None else 0
            beta_to_alpha_damage = 0

        else:
            alpha_to_beta_damage = \
                self.alpha_spell.calculate_damage(self.beta_spell) \
                - self.beta_spell.calculate_defence(self.alpha_spell)
            beta_to_alpha_damage = \
                self.beta_spell.calculate_damage(self.alpha_spell) \
                - self.alpha_spell.calculate_defence(self.beta_spell)

        alpha_to_beta_damage = alpha_to_beta_damage if alpha_to_beta_damage >= 0 else 0
        beta_to_alpha_damage = beta_to_alpha_damage if beta_to_alpha_damage >= 0 else 0

        await self.ctx.send(f'{self.alpha.mention} から {self.beta.mention} に {alpha_to_beta_damage} ダメージ！')
        await self.ctx.send(f'{self.beta.mention} から {self.alpha.mention} に {beta_to_alpha_damage} ダメージ！')

        self.alpha_hp -= beta_to_alpha_damage
        self.beta_hp -= alpha_to_beta_damage

        if self.alpha_hp <= 0 and self.beta_hp <= 0:
            await self.ctx.send('相打ち！両者HPが0になったため、相打ちとなります。')
            self.finish = True
        elif self.alpha_hp <= 0:
            await self.ctx.send(f'{self.beta.mention} の勝ち！')
            self.finish = True
        elif self.beta_hp <= 0:
            await self.ctx.send(f'{self.alpha.mention} の勝ち！')
            self.finish = True
        else:
            await self.ctx.send(f'{self.alpha.mention}\n HP: {self.alpha_hp}\n MP: {self.alpha_mp}',
                                allowed_mentions=discord.AllowedMentions(users=False))
            await self.ctx.send(f'{self.beta.mention}\n HP: {self.beta_hp}\n MP: {self.beta_mp}',
                                allowed_mentions=discord.AllowedMentions(users=False))

        self.battle_finish_flag.set()
        self.battle_finish_flag.clear()
        self.alpha_spell = None
        self.beta_spell = None
        self.ready_to_raise = False

    def use_mp(self, user: str, mp: int = 1) -> bool:
        if user == 'alpha':
            self.alpha_mp -= mp
            if self.alpha_mp < 0:
                return False
            return True
        else:
            self.beta_mp -= mp
            if self.beta_mp < 0:
                return False
            return True

    async def loop(self, check: Callable, user: str) -> None:

        while not self.bot.is_closed() and not self.finish:
            message = await self.bot.wait_for('message', check=check, timeout=60)
            if message.content != 'aria command':
                continue
            await self.ctx.send('魔法の発動を開始します。')
            message = await self.bot.wait_for('message', check=check, timeout=60)
            if message.content != 'generate element':
                await self.ctx.send('魔法の発動に失敗しました。')
                continue
            if not self.use_mp(user):
                await self.ctx.send('MPが枯渇しました。')
                return

            await self.ctx.send('物質生成が完了しました。')
            spell = await self.recv_command(check, user)
            if spell is None:
                await self.ctx.send('魔法の発動に失敗しました。')
                continue
            await self.ctx.send('魔法の発動を開始します。')
            if user == 'alpha':
                self.alpha_spell = spell
            else:
                self.beta_spell = spell
            if self.ready_to_raise:
                await self.battle_finish_flag.wait()
                continue
            await self.raise_spell()

    async def start(self) -> None:
        alpha_db_user = await self.bot.db.get_user(self.alpha.id)
        beta_db_user = await self.bot.db.get_user(self.beta.id)
        self.alpha_hp = alpha_db_user.hp
        self.alpha_mp = alpha_db_user.mp
        self.beta_hp = beta_db_user.hp
        self.beta_mp = beta_db_user.mp

        await self.ctx.send('ゲームスタート！')
        self.bot.loop.create_task(self.loop(self.alpha_check, 'alpha'))
        self.bot.loop.create_task(self.loop(self.beta_check, 'beta'))
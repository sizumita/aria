import discord
from typing import Callable, Optional, NamedTuple, TYPE_CHECKING
from lib.spell import Spell
from asyncio import Task, Event, sleep, iscoroutinefunction
import datetime

if TYPE_CHECKING:
    from bot import Aria # noqa


Message = NamedTuple('Message', (('content', str), ('created_at', datetime.datetime)))


def _calc_damage(my_spell: Optional[Spell], enemy_spell: Optional[Spell]) -> int:
    if my_spell is None:
        return 0
    if enemy_spell is None:
        return my_spell.calculate_damage(enemy_spell)

    damage = my_spell.calculate_damage(enemy_spell) - enemy_spell.calculate_defence(my_spell)
    if damage < 0:
        return 0

    return damage


class Game:
    def __init__(self,
                 bot: 'Aria',
                 alpha: discord.Member,
                 beta: discord.Member,
                 channel: discord.TextChannel,
                 send_callable: Callable = print,
                 ) -> None:
        self.bot = bot
        self.alpha = alpha
        self.beta = beta
        self.channel = channel
        self.finish = False
        self.alpha_spell: Optional[Spell] = None
        self.beta_spell: Optional[Spell] = None
        self.alpha_loop: Optional[Task] = None
        self.beta_loop: Optional[Task] = None
        self.alpha_hp = 100
        self.beta_hp = 100
        self.alpha_mp = 100
        self.beta_mp = 100
        self.ready_to_raise = False
        self.send_callable = send_callable
        self.battle_finish_flag = Event()

    async def send(self, *args, **kwargs) -> None:  # type: ignore
        if iscoroutinefunction(self.send_callable):
            await self.send_callable(*args, **kwargs)
        else:
            self.send_callable(*args, **kwargs)

    async def wait_for(self, *args, **kwargs) -> Message:  # type: ignore
        content = input()
        return Message(content, datetime.datetime.now())

    def alpha_check(self, message: discord.Message) -> bool:
        return message.channel.id == self.channel.id and message.author.id == self.alpha.id

    def beta_check(self, message: discord.Message) -> bool:
        return message.channel.id == self.channel.id and message.author.id == self.beta.id

    async def recv_command(self, check: Callable, user: str) -> Optional[Spell]:
        spell = Spell()
        while not self.bot.is_closed() and not self.finish:
            message = await self.wait_for('message', check=check, timeout=60)
            if message.content == 'execute':
                if not self.use_mp(user, 5):
                    await self.send('MPが枯渇しました。')
                    return None
                break

            if not spell.can_aria(message.created_at):
                return None

            if mp := spell.receive_command(message.content, message.created_at):
                await self.send('コマンドを受け取りました。')
                if not self.use_mp(user, mp):
                    await self.send('MPが枯渇しました。')
                    return None
                continue

            return None

        return spell

    async def raise_spell(self) -> None:
        if self.finish:
            return

        self.ready_to_raise = True
        await sleep(5)

        alpha_to_beta_damage = _calc_damage(self.alpha_spell, self.beta_spell)
        beta_to_alpha_damage = _calc_damage(self.beta_spell, self.alpha_spell)

        await self.send(f'{self.alpha.mention} から {self.beta.mention} に {alpha_to_beta_damage} ダメージ！')
        await self.send(f'{self.beta.mention} から {self.alpha.mention} に {beta_to_alpha_damage} ダメージ！')

        self.alpha_hp -= beta_to_alpha_damage
        self.beta_hp -= alpha_to_beta_damage

        if self.alpha_hp <= 0 and self.beta_hp <= 0:
            await self.send('相打ち！両者HPが0になったため、相打ちとなります。')
            self.finish = True
        elif self.alpha_hp <= 0:
            await self.send(f'{self.beta.mention} の勝ち！')
            self.finish = True
        elif self.beta_hp <= 0:
            await self.send(f'{self.alpha.mention} の勝ち！')
            self.finish = True
        else:
            await self.send(
                f'{self.alpha.mention}\n HP: {self.alpha_hp}\n MP: {self.alpha_mp}',
                allowed_mentions=discord.AllowedMentions(users=False)
            )
            await self.send(
                f'{self.beta.mention}\n HP: {self.beta_hp}\n MP: {self.beta_mp}',
                allowed_mentions=discord.AllowedMentions(users=False)
            )

        self.battle_finish_flag.set()
        self.battle_finish_flag.clear()
        self.alpha_spell = None
        self.beta_spell = None
        self.ready_to_raise = False

    def use_mp(self, user: str, mp: int = 1) -> bool:
        if user == 'alpha':
            self.alpha_mp -= mp
            if self.alpha_mp < 0:
                self.alpha_mp = 0
                return False
            return True
        else:
            self.beta_mp -= mp
            if self.beta_mp < 0:
                self.beta_mp = 0
                return False
            return True

    async def loop(self, check: Callable, user: str) -> None:

        while not self.bot.is_closed() and not self.finish:
            message = await self.wait_for('message', check=check, timeout=60)
            if message.content != 'aria command':
                continue
            await self.send('魔法の発動を開始します。')
            message = await self.wait_for('message', check=check, timeout=60)

            if message.content != 'generate element':
                await self.send('魔法の発動に失敗しました。')
                continue

            if not self.use_mp(user):
                await self.send('MPが枯渇しました。')
                return

            await self.send('物質生成が完了しました。')
            spell = await self.recv_command(check, user)
            if spell is None:
                await self.send('魔法の発動に失敗しました。')
                continue
            await self.send('魔法の発動を開始します。')
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

        await self.send('ゲームスタート！')
        self.bot.loop.create_task(self.loop(self.alpha_check, 'alpha'))
        self.bot.loop.create_task(self.loop(self.beta_check, 'beta'))


class DiscordGame(Game):
    async def wait_for(self, *args, **kwargs) -> Message:  # type: ignore
        message = await self.bot.wait_for(*args, **kwargs)
        return Message(message.content, message.created_at)

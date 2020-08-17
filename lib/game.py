import discord
from typing import Callable, Optional, NamedTuple, TYPE_CHECKING, Union
from lib.spell import Spell
from lib.test_class import TestBot, TestMember, TestChannel
from asyncio import Task, Event, sleep, iscoroutinefunction, TimeoutError
from lib.database import User
import datetime
import random

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


def _print(*args, **kwargs) -> None:  # type: ignore
    print(args, kwargs)


class Game:
    def __init__(self,
                 bot: 'Union[Aria, TestBot]',
                 alpha: Union[discord.Member, TestMember],
                 beta: Union[discord.Member, TestMember],
                 channel: Union[discord.TextChannel, TestChannel],
                 send_callable: Callable = _print,
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
        self.alpha_db_user: Optional[User] = None
        self.beta_db_user: Optional[User] = None
        self.alpha_hp = 100
        self.beta_hp = 100
        self.alpha_mp = 100
        self.beta_mp = 100
        self.ready_to_raise = False
        self.send_callable = send_callable
        self.battle_finish_flag = Event()
        self.game_finish_flag = Event()

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
            try:
                message = await self.wait_for('message', check=check, timeout=60)
            except TimeoutError:
                return None
            if message.content in ['execute', 'discharge']:
                if not self.use_mp(user, 5):
                    await self.send('システム: MPが枯渇しました。')
                    return None
                break

            if not spell.can_aria(message.created_at):
                return None

            mp, msg = spell.receive_command(message.content, message.created_at)
            if mp is not None:
                await self.send('システム: ' + msg)
                if not self.use_mp(user, mp):
                    await self.send('システム: MPが枯渇しました。')
                    return None
                continue

            return None

        return spell

    async def win(self, winner: Union[discord.Member, TestMember], loser: Union[discord.Member, TestMember]) -> None:
        await self.send(f'{winner.mention} の勝利!')
        winner_db_user = await self.bot.db.get_user(winner.id)
        loser_db_user = await self.bot.db.get_user(loser.id)
        hp_or_mp = random.choice([0, 1])  # 0=hp 1=mp

        def get_num(_user: User) -> int:
            return _user.hp if not hp_or_mp else _user.mp

        diff = (winner_db_user.hp + winner_db_user.mp) / (loser_db_user.hp + loser_db_user.mp)
        # hp
        if diff <= 0.5:
            # めっちゃ勝った
            get_ = int(get_num(loser_db_user) * 0.15 * (random.random() + 1))
            lost_ = int(get_num(loser_db_user) * 0.15)
        elif diff <= 0.6:
            # 結構勝った
            get_ = int(get_num(loser_db_user) * 0.12 * (random.random() + 1))
            lost_ = int(get_num(loser_db_user) * 0.12)
        elif diff <= 0.7:
            # まあまあ勝った
            get_ = int(get_num(loser_db_user) * 0.1 * (random.random() + 1))
            lost_ = int(get_num(loser_db_user) * 0.1)
        elif diff <= 0.8:
            # ちょい勝った
            get_ = int(get_num(loser_db_user) * 0.07 * (random.random() + 1))
            lost_ = int(get_num(loser_db_user) * 0.07)
        elif diff <= 0.9:
            # ほんとちょびっと勝った
            get_ = int(get_num(loser_db_user) * 0.06 * (random.random() + 1))
            lost_ = int(get_num(loser_db_user) * 0.06)
        elif diff <= 1.1:
            # 同じくらい
            get_ = int(get_num(loser_db_user) * 0.05 * (random.random() + 1))
            lost_ = int(get_num(loser_db_user) * 0.05)
        elif diff <= 1.2:
            # ちょっと弱い
            get_ = int(get_num(loser_db_user) * 0.03)
            lost_ = int(get_num(loser_db_user) * 0.02)
        elif diff <= 1.4:
            # 結構弱い
            get_ = int(get_num(loser_db_user) * 0.02)
            lost_ = int(get_num(loser_db_user) * 0.02)
        elif diff <= 1.8:
            get_ = int(get_num(loser_db_user) * 0.01)
            lost_ = int(get_num(loser_db_user) * 0.01)
        else:
            get_ = 0
            lost_ = 0

        if not hp_or_mp:
            await self.bot.db.update_user(winner.id, winner_db_user.hp + get_, winner_db_user.mp)
            await self.bot.db.update_user(loser.id, loser_db_user.hp - lost_, loser_db_user.mp)

            await self.send(f'{winner.mention}, HP: {winner_db_user.hp} -> {winner_db_user.hp + get_}')
            await self.send(f'{loser.mention}, HP: {loser_db_user.hp} -> {loser_db_user.hp - lost_}')
        else:
            await self.bot.db.update_user(winner.id, winner_db_user.hp, winner_db_user.mp + get_)
            await self.bot.db.update_user(loser.id, loser_db_user.hp, loser_db_user.mp - lost_)

            await self.send(f'{winner.mention}, MP: {winner_db_user.mp} -> {winner_db_user.mp + get_}')
            await self.send(f'{loser.mention}, MP: {loser_db_user.mp} -> {loser_db_user.mp - lost_}')

    async def raise_spell(self, wait_time: int = 5) -> None:
        if self.finish:
            return

        self.ready_to_raise = True
        await sleep(wait_time)

        alpha_to_beta_damage = _calc_damage(self.alpha_spell, self.beta_spell)
        beta_to_alpha_damage = _calc_damage(self.beta_spell, self.alpha_spell)

        await self.send(f'{self.alpha.mention} から {self.beta.mention} に {alpha_to_beta_damage} ダメージ！')
        await self.send(f'{self.beta.mention} から {self.alpha.mention} に {beta_to_alpha_damage} ダメージ！')

        self.alpha_hp -= beta_to_alpha_damage
        self.beta_hp -= alpha_to_beta_damage

        if self.alpha_hp <= 0 and self.beta_hp <= 0:
            await self.send('相打ち！両者HPが0になったため、相打ちとなります。')
            self.finish = True
            self.game_finish_flag.set()

        elif self.alpha_hp <= 0:
            await self.win(self.beta, self.alpha)
            self.finish = True
            self.game_finish_flag.set()

        elif self.beta_hp <= 0:
            await self.win(self.alpha, self.beta)
            self.finish = True
            self.game_finish_flag.set()

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

    async def force_end_game(self) -> None:
        await self.send('入力がなかったためゲームを終了します。')
        self.game_finish_flag.set()
        self.battle_finish_flag.set()
        self.finish = True

    async def loop(self, check: Callable, user: str) -> None:

        while not self.bot.is_closed() and not self.finish:
            try:
                message = await self.wait_for('message', check=check, timeout=1000)
            except TimeoutError:
                return await self.force_end_game()

            if message.content != 'aria command':
                continue

            await self.send('システム: 魔法の発動開始を確認。物質生成フェーズへ移行します。')

            spell = await self.recv_command(check, user)
            if spell is None:
                await self.send('システム: 魔法の発動に失敗しました。')
                continue
            await self.send('システム: 魔法の発動を開始します。')
            if user == 'alpha':
                self.alpha_spell = spell
            else:
                self.beta_spell = spell
            if self.ready_to_raise:
                await self.battle_finish_flag.wait()
                continue
            await self.raise_spell(5 - spell.burst)

    async def auto_heal_loop(self) -> None:
        while not self.finish:
            if self.alpha_db_user is None:
                continue
            if self.beta_db_user is None:
                continue
            self.alpha_mp += (self.alpha_db_user.mp // 50)
            self.beta_mp += (self.beta_db_user.mp // 50)

            if self.alpha_db_user.mp < self.alpha_mp:
                self.alpha_mp = self.alpha_db_user.mp
            if self.beta_db_user.mp < self.beta_mp:
                self.beta_mp = self.beta_db_user.mp
            await sleep(10)

    async def start(self) -> None:
        alpha_db_user = await self.bot.db.get_user(self.alpha.id)
        beta_db_user = await self.bot.db.get_user(self.beta.id)
        self.alpha_hp = alpha_db_user.hp
        self.alpha_mp = alpha_db_user.mp
        self.beta_hp = beta_db_user.hp
        self.beta_mp = beta_db_user.mp
        self.alpha_db_user = alpha_db_user
        self.beta_db_user = beta_db_user

        await self.send('ゲームスタート！')
        tasks = [self.bot.loop.create_task(self.loop(self.alpha_check, 'alpha')),
                 self.bot.loop.create_task(self.loop(self.beta_check, 'beta')),
                 self.bot.loop.create_task(self.auto_heal_loop())]

        await self.game_finish_flag.wait()

        for task in tasks:
            if not task.done():
                task.cancel()


class DiscordGame(Game):
    async def wait_for(self, *args, **kwargs) -> Message:  # type: ignore
        message = await self.bot.wait_for(*args, **kwargs)
        return Message(message.content, message.created_at)


class TestMode(DiscordGame):
    async def win(self, winner: Union[discord.Member, TestMember], loser: Union[discord.Member, TestMember]) -> None:
        await self.send('システム: テストモード終了。')
        self.finish = True
        self.game_finish_flag.set()

    async def start(self) -> None:
        alpha_db_user = await self.bot.db.get_user(self.alpha.id)
        beta_db_user = await self.bot.db.get_user(self.beta.id)
        self.alpha_hp = alpha_db_user.hp
        self.alpha_mp = alpha_db_user.mp
        self.beta_hp = beta_db_user.hp
        self.beta_mp = beta_db_user.mp
        self.alpha_db_user = alpha_db_user
        self.beta_db_user = beta_db_user

        await self.send('ゲームスタート！')
        tasks = [self.bot.loop.create_task(self.loop(self.alpha_check, 'alpha')),
                 self.bot.loop.create_task(self.auto_heal_loop())]

        await self.game_finish_flag.wait()

        for task in tasks:
            if not task.done():
                task.cancel()

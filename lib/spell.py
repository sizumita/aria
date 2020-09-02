from __future__ import annotations
import re
import datetime
import random
from typing import NamedTuple, Union, Tuple
form_compiled = re.compile(r'^change element (sword|spear|bow|wall|rod)$')
feature_compiled = re.compile(r'^change feature (flame|water|earth|light|umbra)$')
copy_compiled = re.compile(r'^copy element ([0-9]+)$')
generate_compiled = re.compile(r'^generate (flame|water|earth|light|umbra) element$')
magnification_compiled = re.compile(r'^enhance element (attack|defence|defense)$')
burst_compiled = re.compile(r'^burst element$')


class Form(NamedTuple):
    damage: int
    defence: int


forms = {
    'sword': Form(10, 20),
    'spear': Form(20, 10),
    'bow': Form(5, 5),
    'wall': Form(2, 30),
    'rod': Form(15, 15),
}

# 各属性の強い属性
strong_features = {
    'flame': 'earth',
    'water': 'flame',
    'earth': 'water',
    'light': 'umbra',
    'umbra': 'light',
}


def _calc_feature(num: Union[int, float], self_spell: Spell, enemy_spell: Spell) -> Union[int, float]:
    if self_spell.feature is not None and enemy_spell.feature is not None:
        if strong_features[self_spell.feature] == enemy_spell.feature:
            num *= 1.2
        elif strong_features[enemy_spell.feature] == self_spell.feature:
            num *= 0.8

    return num


class Spell:
    def __init__(self) -> None:
        self.form: Union[None, str] = None
        self.feature: Union[None, str] = None
        self.copy = 1
        self.last_aria_command_time: Union[None, datetime.datetime] = None
        self.before_generate = True
        self.attack_magnification = 1.
        self.defence_magnification = 1.
        self.random_spec = random.random() + 0.5
        self.burst = 0
        if self.random_spec >= 1:
            self.random_spec = 1

    def calculate_damage(self, enemy_spell: Union[None, Spell]) -> int:
        total_damage: Union[int, float]
        if self.form is None:
            total_damage = 2
        else:
            total_damage = forms[self.form].damage

        # 属性有利不利
        if enemy_spell is not None:
            total_damage = _calc_feature(total_damage, self, enemy_spell)

        return int(total_damage * self.copy * self.attack_magnification * self.random_spec)

    def calculate_defence(self, enemy_spell: Union[None, Spell]) -> int:
        total_defence: Union[int, float]
        if self.form is None:
            total_defence = 2
        else:
            total_defence = forms[self.form].defence

        # 属性有利不利
        if enemy_spell is not None:
            total_defence = _calc_feature(total_defence, self, enemy_spell)

        return int(total_defence * self.copy * self.defence_magnification * self.random_spec)

    def receive_command(self, command: str, aria_command_time: datetime.datetime) -> Union[Tuple[int, str], Tuple[None, None]]:
        """
        コマンドを受け取り、自分のインスタンス変数を変化させ、Trueを返す
        もしコマンドがおかしかった場合、Falseを返す。
        :param command: コマンドの文
        :param aria_command_time: コマンドを実行した時間
        :return: 消費するmp or False, message
        """
        if self.before_generate:
            if match := generate_compiled.match(command):
                self.before_generate = False
                self.feature = match.groups()[0]
                self.last_aria_command_time = aria_command_time
                return 4, "物質の生成を確認。コマンド入力フェーズへ移行します。"

            if command == "generate element":
                self.before_generate = False
                self.last_aria_command_time = aria_command_time
                return 2, "物質の生成を確認。コマンド入力フェーズへ移行します。"

            return None, None

        if match := form_compiled.match(command):
            self.form = match.groups()[0]
            self.last_aria_command_time = aria_command_time

            return 2, "物質の形状変化を確認。"

        elif match := feature_compiled.match(command):
            self.feature = match.groups()[0]
            self.last_aria_command_time = aria_command_time

            return 3, "物質の属性変化を確認。"

        elif match := copy_compiled.match(command):
            self.copy = int(match.groups()[0])
            self.last_aria_command_time = aria_command_time

            if self.form == 'bow':
                return 5 * self.copy, "物質の複製を確認。"
            return int(2.9 ** self.copy), "物質の複製を確認。"

        elif match := magnification_compiled.match(command):
            if match.groups()[0] == 'attack':
                self.attack_magnification += round(random.random(), 2)
                self.last_aria_command_time = aria_command_time

                return 5, f"攻撃力のエンハンス完了。{round(self.attack_magnification, 2)}倍に変化。"

            self.defence_magnification += round(random.random(), 2)
            self.last_aria_command_time = aria_command_time

            return 5, f"防御力のエンハンス完了。{round(self.defence_magnification, 2)}倍に変化。"\

        elif burst_compiled.match(command):
            if self.burst == 5:
                return 0, "これ以上のバーストは不可能です。"

            self.burst += 1

            return 6, f"バースト完了。バースト値: {self.burst}"

        else:
            return None, None

    def can_aria(self, will_aria_time: datetime.datetime) -> bool:
        """
        制限時間15.0秒を過ぎていないかチェックする関数
        :param will_aria_time: 次にコマンドを発動する時間
        :return: bool
        """

        # 一度も実行されていなかった場合
        if self.last_aria_command_time is None:
            return True

        diff = will_aria_time - self.last_aria_command_time

        return True if diff.total_seconds() <= 15.0 else False

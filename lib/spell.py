from __future__ import annotations
import re
import datetime
from typing import NamedTuple, Union
form_compiled = re.compile(r'^change element (sword|spear|bow|wall|rod)$')
feature_compiled = re.compile(r'^change feature (flame|water|earth|light|umbra)$')
copy_compiled = re.compile(r'^copy ([0-9]+)$')


class Form(NamedTuple):
    damage: int
    defence: int


forms = {
    'sword': Form(10, 20),
    'spear': Form(20, 10),
    'bow': Form(2, 2),
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

    def calculate_damage(self, enemy_spell: Union[None, Spell]) -> int:
        total_damage: Union[int, float]
        if self.form is None:
            total_damage = 2
        else:
            total_damage = forms[self.form].damage

        # 属性有利不利
        if enemy_spell is not None:
            total_damage = _calc_feature(total_damage, self, enemy_spell)

        return int(total_damage) * self.copy  # 少数になる可能性もあるため

    def calculate_defence(self, enemy_spell: Union[None, Spell]) -> int:
        total_defence: Union[int, float]
        if self.form is None:
            total_defence = 2
        else:
            total_defence = forms[self.form].defence

        # 属性有利不利
        if enemy_spell is not None:
            total_defence = _calc_feature(total_defence, self, enemy_spell)

        return int(total_defence) * self.copy  # 少数になる可能性もあるため

    def receive_command(self, command: str, aria_command_time: datetime.datetime) -> Union[int, bool]:
        """
        コマンドを受け取り、自分のインスタンス変数を変化させ、Trueを返す
        もしコマンドがおかしかった場合、Falseを返す。
        :param command: コマンドの文
        :param aria_command_time: コマンドを実行した時間
        :return: 消費するmp or False
        """
        if match := form_compiled.match(command):
            self.form = match.groups()[0]
            self.last_aria_command_time = aria_command_time

            return 2

        elif match := feature_compiled.match(command):
            self.feature = match.groups()[0]
            self.last_aria_command_time = aria_command_time

            return 3

        elif match := copy_compiled.match(command):
            self.copy = int(match.groups()[0])
            self.last_aria_command_time = aria_command_time

            if self.form == 'bow':
                return 3 * self.copy
            return int(2.7 ** self.copy)

        else:
            return False

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

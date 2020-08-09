import re
import datetime
form_compiled = re.compile(r'^change element (sword|spear|bow|wall|rod)$')
feature_compiled = re.compile(r'^change feature (flame|water|earth|light|umbra)$')
form_damages = {
    'sword': 10,
    'spear': 20,
    'bow': 5,
    'wall': 2,
    'rod': 15,
}

# 各属性の強い属性
strong_features = {
    'flame': 'earth',
    'water': 'flame',
    'earth': 'water',
    'light': 'umbra',
    'umbra': 'light',
}


class Spell:
    def __init__(self) -> None:
        self.form = None
        self.feature = None
        self.last_aria_command_time = None

    def calculate_damage(self, enemy_spell) -> int:
        total_damage = form_damages[self.form]

        # 属性有利不利
        if strong_features[self.feature] == enemy_spell.feature:
            total_damage *= 1.2
        elif strong_features[enemy_spell.feature] == self.feature:
            total_damage *= 0.8

        return int(total_damage)  # 少数になる可能性もあるため

    def receive_command(self, command: str, aria_command_time: datetime.datetime) -> bool:
        """
        コマンドを受け取り、自分のインスタンス変数を変化させ、Trueを返す
        もしコマンドがおかしかった場合、Falseを返す。
        :param command: コマンドの文
        :param aria_command_time: コマンドを実行した時間
        :return: bool
        """
        if match := form_compiled.match(command):
            self.form = match.group(0)

        elif match := feature_compiled.match(command):
            self.feature = match.group(0)

        else:
            return False

        self.last_aria_command_time = aria_command_time

        return True

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

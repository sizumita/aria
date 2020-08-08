import re
import datetime
form_compile = re.compile(r'^change element (sword|spear|bow|wall|rod)$')
feature_compile = re.compile(r'^change feature (flame|water|earth|light|umbra)$')


class Spell:
    def __init__(self):
        self.form = None
        self.feature = None
        self.last_aria_command_time = None

    def receive_command(self, command: str, aria_command_time: datetime.datetime):
        """
        コマンドを受け取り、自分のインスタンス変数を変化させ、Trueを返す
        もしコマンドがおかしかった場合、Falseを返す。
        :param command: コマンドの文
        :param aria_command_time: コマンドを実行した時間
        :return: bool
        """
        if match := form_compile.match(command):
            self.form = match.group(0)

        elif match := feature_compile.match(command):
            self.feature = match.group(0)

        else:
            return False

        self.last_aria_command_time = aria_command_time

        return True

    def can_aria(self, will_aria_time: datetime.datetime):
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

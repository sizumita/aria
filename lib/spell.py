import re
import datetime
form_compile = re.compile(r'^change element (sword|spear|bow|wall|rod)')
feature_compile = re.compile(r'^change feature (flame|water|earth|light|umbra)$')


class Spell:
    def __init__(self):
        self.form = None
        self.feature = None
        self.last_aria_command_time = None

    def receive_command(self, command: str, aria_command_time: datetime.datetime):
        if match := form_compile.match(command):
            self.form = match.group(0)

        elif match := feature_compile.match(command):
            self.feature = match.group(0)

        else:
            return False

        self.last_aria_command_time = aria_command_time

        return True

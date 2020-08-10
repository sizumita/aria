from dataclasses import dataclass


@dataclass
class TestBot:
    closed: bool = False

    def is_closed(self) -> bool:
        return self.closed


@dataclass
class TestMember:
    id: int = 212513828641046529
    mention: str = '@すみどら#8931'


@dataclass
class TestChannel:
    id: int = 111111111111111111

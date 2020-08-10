import pytest


@pytest.mark.asyncio
async def test_spear():
    from lib.game import Game
    from lib.spell import Spell
    from lib.test_class import TestBot, TestChannel, TestMember
    game = Game(
        bot=TestBot(),
        alpha=TestMember(),
        beta=TestMember(id=570243143958528010, mention='@daima3629#1235'),
        channel=TestChannel(),
    )
    alpha_spell = Spell()
    alpha_spell.form = 'spear'
    game.alpha_spell = alpha_spell
    await game.raise_spell()
    assert game.beta_hp == 80

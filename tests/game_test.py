import pytest
from typing import Optional
from lib.game import Game
from lib.spell import Spell, forms
from lib.test_class import TestBot, TestChannel, TestMember


def get_game() -> Game:
    return Game(
        bot=TestBot(),
        alpha=TestMember(),
        beta=TestMember(id=570243143958528010, mention='@daima3629#1235'),
        channel=TestChannel(),
    )


async def do_game(
        alpha: bool = True,
        beta: bool = True,
        alpha_form: Optional[str] = None,
        beta_form: Optional[str] = None,
        alpha_feature: Optional[str] = None,
        beta_feature: Optional[str] = None,
        alpha_num: int = 1,
        beta_num: int = 1) -> Game:
    game = get_game()
    alpha_spell = Spell()
    alpha_spell.form = alpha_form
    alpha_spell.feature = alpha_feature
    alpha_spell.copy = alpha_num

    beta_spell = Spell()
    beta_spell.form = beta_form
    beta_spell.feature = beta_feature
    beta_spell.copy = beta_num

    if alpha:
        game.alpha_spell = alpha_spell
    if beta:
        game.beta_spell = beta_spell

    await game.raise_spell(0)
    return game


@pytest.mark.asyncio
async def test_spear():
    game = await do_game(beta=False, alpha_form='spear')

    assert game.beta_hp == 100 - forms['spear'].damage


@pytest.mark.asyncio
async def test_wall():
    game = await do_game(beta=False, alpha_form='wall')

    assert game.beta_hp == 100 - forms['wall'].damage


@pytest.mark.asyncio
async def test_sword():
    game = await do_game(beta=False, alpha_form='sword')

    assert game.beta_hp == 100 - forms['sword'].damage


@pytest.mark.asyncio
async def test_bow():
    game = await do_game(beta=False, alpha_form='bow')

    assert game.beta_hp == 100 - forms['bow'].damage


@pytest.mark.asyncio
async def test_rod():
    game = await do_game(beta=False, alpha_form='rod')

    assert game.beta_hp == 100 - forms['rod'].damage


@pytest.mark.asyncio
async def test_spear_spear():
    game = await do_game(alpha_form='spear', beta_form='spear')

    assert game.alpha_hp == 100 + forms['spear'].defence - forms['spear'].damage
    assert game.beta_hp == 100 + forms['spear'].defence - forms['spear'].damage


@pytest.mark.asyncio
async def test_wall_two_spear():
    """計算式: 防御力100 - (20 * 2 - 30) = 90"""
    game = await do_game(alpha_form='wall', beta_form='spear', beta_num=2)

    assert game.alpha_hp == 90

"""Tests for the coin upgrade economy and player application."""

import pytest

from constants import MAX_HEALTH
from sprites.player import Player
from utils.save_manager import SaveManager
import utils.upgrades as up


@pytest.fixture
def fresh_save(tmp_path, monkeypatch):
    """Point the save singleton at a throwaway file with a coin balance."""
    import utils.save_manager as sm_module

    sm = SaveManager(str(tmp_path / "save.json"))
    monkeypatch.setattr(sm_module, "_manager", sm)
    return sm


def test_cost_increases_per_level(fresh_save):
    spec = up.UPGRADES["max_health"]
    assert up.cost_for_next("max_health") == spec["base_cost"]
    fresh_save.set("upgrades", {"max_health": 1})
    assert up.cost_for_next("max_health") == spec["base_cost"] + spec["cost_step"]


def test_purchase_deducts_coins_and_raises_level(fresh_save):
    fresh_save.set("coins", 100)
    cost = up.cost_for_next("max_health")
    assert up.purchase("max_health") is True
    assert up.get_level("max_health") == 1
    assert fresh_save.get("coins") == 100 - cost


def test_cannot_buy_without_enough_coins(fresh_save):
    fresh_save.set("coins", 0)
    assert up.can_afford("max_health") is False
    assert up.purchase("max_health") is False
    assert up.get_level("max_health") == 0


def test_cannot_exceed_max_level(fresh_save):
    fresh_save.set("coins", 100000)
    spec = up.UPGRADES["double_jump"]
    for _ in range(spec["max_level"]):
        assert up.purchase("double_jump") is True
    assert up.is_maxed("double_jump")
    assert up.cost_for_next("double_jump") is None
    assert up.purchase("double_jump") is False  # already maxed


def test_apply_upgrades_to_player(fresh_save):
    fresh_save.set("upgrades", {"max_health": 2, "move_speed": 1, "double_jump": 1})
    p = Player()  # Player.__init__ already calls apply_upgrades
    assert p.max_health == MAX_HEALTH + 2
    assert p.run_accel_mult == pytest.approx(1.0 + up.SPEED_STEP)
    assert p.has_double_jump is True


def test_apply_upgrades_does_not_compound_across_constructions(fresh_save):
    fresh_save.set("upgrades", {"max_health": 3})
    p1 = Player()
    p2 = Player()
    assert p1.max_health == p2.max_health == MAX_HEALTH + 3

"""Unit tests for utils/cosmetics.py.

Follows the same SaveManager isolation pattern used by test_upgrades.py and
test_database_logic.py — each test gets a fresh, temporary save so nothing
bleeds across runs and save.json on disk is never touched.
"""

import pytest
from utils.save_manager import SaveManager


@pytest.fixture(autouse=True)
def temp_save(tmp_path, monkeypatch):
    """Isolate the global save singleton for every test in this module."""
    import utils.save_manager as sm_module
    monkeypatch.setattr(sm_module, "_manager", SaveManager(str(tmp_path / "save.json")))


# ---------------------------------------------------------------------------
# Default state
# ---------------------------------------------------------------------------

def test_default_skin_is_classic():
    from utils.cosmetics import get_skin
    assert get_skin() == 0


def test_default_hat_is_none():
    from utils.cosmetics import get_hat
    assert get_hat() == "none"


def test_classic_skin_always_owned():
    from utils.cosmetics import owns_skin, owned_skins
    assert owns_skin(0)
    assert 0 in owned_skins()


def test_no_hat_always_owned():
    from utils.cosmetics import owns_hat, owned_hats
    assert owns_hat("none")
    assert "none" in owned_hats()


# ---------------------------------------------------------------------------
# Buying
# ---------------------------------------------------------------------------

def test_buy_skin_deducts_coins():
    import utils.database_logic as db
    from utils.cosmetics import buy_skin, owns_skin

    db.SetCoins(100)
    result = buy_skin(1)  # Green skin costs 40

    assert result is True
    assert db.GetCoins() == 60
    assert owns_skin(1)


def test_buy_skin_fails_when_broke():
    from utils.cosmetics import buy_skin, owns_skin

    result = buy_skin(1)  # no coins
    assert result is False
    assert not owns_skin(1)


def test_buy_skin_fails_when_already_owned():
    import utils.database_logic as db
    from utils.cosmetics import buy_skin

    db.SetCoins(200)
    assert buy_skin(1) is True   # first purchase
    coins_after_first = db.GetCoins()
    assert buy_skin(1) is False  # already owned
    assert db.GetCoins() == coins_after_first  # no second deduction


def test_buy_hat_deducts_coins():
    import utils.database_logic as db
    from utils.cosmetics import buy_hat, owns_hat

    db.SetCoins(100)
    result = buy_hat("cap")  # Cap costs 30

    assert result is True
    assert db.GetCoins() == 70
    assert owns_hat("cap")


def test_buy_hat_fails_when_broke():
    from utils.cosmetics import buy_hat, owns_hat

    result = buy_hat("crown")  # 60 coins, none in wallet
    assert result is False
    assert not owns_hat("crown")


def test_buy_hat_fails_when_already_owned():
    import utils.database_logic as db
    from utils.cosmetics import buy_hat

    db.SetCoins(200)
    assert buy_hat("cap") is True
    coins_after = db.GetCoins()
    assert buy_hat("cap") is False
    assert db.GetCoins() == coins_after


def test_buy_skin_equips_it_immediately():
    import utils.database_logic as db
    from utils.cosmetics import buy_skin, get_skin

    db.SetCoins(100)
    buy_skin(2)  # Red skin
    assert get_skin() == 2


def test_buy_hat_equips_it_immediately():
    import utils.database_logic as db
    from utils.cosmetics import buy_hat, get_hat

    db.SetCoins(100)
    buy_hat("cap")
    assert get_hat() == "cap"


# ---------------------------------------------------------------------------
# Equip-only-if-owned guard
# ---------------------------------------------------------------------------

def test_set_skin_only_when_owned():
    from utils.cosmetics import set_skin, get_skin

    set_skin(3)  # Teal — not owned
    assert get_skin() == 0  # unchanged


def test_set_hat_only_when_owned():
    from utils.cosmetics import set_hat, get_hat

    set_hat("crown")  # not owned
    assert get_hat() == "none"  # unchanged


# ---------------------------------------------------------------------------
# Reset clears cosmetics
# ---------------------------------------------------------------------------

def test_reset_progress_clears_cosmetics():
    import utils.database_logic as db
    from utils.cosmetics import buy_skin, buy_hat, get_skin, get_hat, owned_skins, owned_hats

    db.SetCoins(200)
    buy_skin(1)
    buy_hat("cap")
    assert get_skin() == 1
    assert get_hat() == "cap"

    db.ResetProgress()

    # After reset defaults are restored
    from utils.cosmetics import get_skin as gs, get_hat as gh
    assert gs() == 0
    assert gh() == "none"
    assert owned_skins() == [0]
    assert owned_hats() == ["none"]


# ---------------------------------------------------------------------------
# Achievement reward coins granted on hat purchase
# ---------------------------------------------------------------------------

def test_hat_purchase_triggers_hat_collector_achievement():
    """Buying any hat should unlock the hat_collector achievement (if not already done)."""
    import utils.database_logic as db
    from utils.achievements import achievement_manager

    db.SetCoins(100)
    # Reset the achievement so the test is repeatable regardless of order.
    ach = achievement_manager.achievements.get("hat_collector")
    if ach:
        ach.unlocked = False
        ach.progress = 0

    # The shop's _handle_hat calls check_hat_achievement() after buy_hat().
    # We invoke the same flow manually here.
    from utils.cosmetics import buy_hat
    from utils.achievements import check_hat_achievement

    assert buy_hat("cap") is True
    check_hat_achievement()
    assert achievement_manager.achievements["hat_collector"].unlocked is True


def test_achievement_reward_coins_granted():
    """Unlocking an achievement with a non-zero reward must add coins to the wallet."""
    import utils.database_logic as db
    from utils.achievements import achievement_manager

    db.SetCoins(0)
    ach = achievement_manager.achievements.get("first_level")
    assert ach is not None
    # Reset so it can be unlocked again.
    ach.unlocked = False
    ach.progress = 0
    reward = ach.reward  # 5 coins

    result = achievement_manager.check_achievement("first_level", 1)
    assert result is not None
    assert result.unlocked is True
    assert db.GetCoins() == reward

"""Tests for the JSON SaveManager and the database_logic facade."""

import json

import pytest

from utils.save_manager import SaveManager


def test_round_trip_persists_to_disk(tmp_path):
    path = tmp_path / "save.json"
    sm = SaveManager(str(path))
    sm.set("score", 7)
    sm.set("coins", 42)
    # A fresh manager reading the same file sees the saved values.
    reloaded = SaveManager(str(path))
    assert reloaded.get("score") == 7
    assert reloaded.get("coins") == 42


def test_defaults_when_no_save(tmp_path):
    sm = SaveManager(str(tmp_path / "save.json"))
    assert sm.get("score") == 1
    assert sm.get("highscore") == 0
    assert sm.get("coins") == 0
    assert sm.get("hat") == "0"


def test_corrupt_save_falls_back_to_defaults(tmp_path):
    path = tmp_path / "save.json"
    path.write_text("{ this is not valid json ]")
    sm = SaveManager(str(path))  # must not raise
    assert sm.get("score") == 1
    assert sm.get("coins") == 0


def test_migrates_from_legacy_txt_files(tmp_path):
    txt = tmp_path / "txts"
    txt.mkdir()
    (txt / "Score.txt").write_text("5")
    (txt / "Highscore.txt").write_text("9")
    (txt / "coins.txt").write_text("123")
    (txt / "Hat.txt").write_text("hat")

    path = tmp_path / "save.json"
    sm = SaveManager(str(path), txt_folder=str(txt))
    assert sm.get("score") == 5
    assert sm.get("highscore") == 9
    assert sm.get("coins") == 123
    assert sm.get("hat") == "hat"
    # Migration writes the JSON save out.
    assert json.loads(path.read_text())["score"] == 5


@pytest.fixture
def fresh_facade(tmp_path, monkeypatch):
    """Point the database_logic facade at a throwaway SaveManager."""
    import utils.save_manager as sm_module

    monkeypatch.setattr(sm_module, "_manager", SaveManager(str(tmp_path / "save.json")))
    import utils.database_logic as db

    return db


def test_facade_score_round_trip(fresh_facade):
    db = fresh_facade
    db.SetScore(8)
    assert db.GetScore() == 8


def test_facade_add_coins(fresh_facade):
    db = fresh_facade
    db.SetCoins(10)
    assert db.AddCoins(5) == 15
    assert db.GetCoins() == 15


def test_facade_highscore_only_increases(fresh_facade):
    db = fresh_facade
    db.manualSetHighScore(10)
    db.SetHighScore(5)   # lower -> ignored
    assert db.GetHighScore() == 10
    db.SetHighScore(15)  # higher -> applied
    assert db.GetHighScore() == 15


def test_facade_gamestate_is_runtime_only(fresh_facade):
    db = fresh_facade
    db.SetGamestate("GAME")
    assert db.GetGamestate() == "GAME"


def test_update_writes_many_keys_once(tmp_path):
    path = tmp_path / "save.json"
    sm = SaveManager(str(path))
    sm.update({"score": 4, "coins": 99})
    reloaded = SaveManager(str(path))
    assert reloaded.get("score") == 4
    assert reloaded.get("coins") == 99


def test_add_increments_and_returns_total(tmp_path):
    sm = SaveManager(str(tmp_path / "save.json"))
    sm.set("coins", 10)
    assert sm.add("coins", 5) == 15
    assert sm.get("coins") == 15


def test_reset_named_keys_only(tmp_path):
    sm = SaveManager(str(tmp_path / "save.json"))
    sm.update({"coins": 50, "score": 7, "highscore": 9})
    sm.reset("coins", "score")
    assert sm.get("coins") == 0
    assert sm.get("score") == 1
    assert sm.get("highscore") == 9  # untouched


def test_wears_hat_requires_owned_and_equipped(fresh_facade):
    db = fresh_facade
    # Owned and equipped -> wears the hat.
    db.SetHat("hat")
    db.SetChar(1)
    assert db.WearsHat() is True
    # Regression: owned but switched back to "Normal" -> no hat.
    db.SetChar(0)
    assert db.WearsHat() is False
    # Equipped but not owned (shouldn't happen via UI, but be defensive).
    db.SetHat("0")
    db.SetChar(1)
    assert db.WearsHat() is False


def test_reset_progress_keeps_settings(fresh_facade):
    db = fresh_facade
    sm = db.get_save_manager()
    sm.set("settings", {"music_volume": 0.5})
    db.SetCoins(50)
    db.SetScore(7)
    db.ResetProgress()
    assert db.GetCoins() == 0
    assert db.GetScore() == 1
    assert sm.get("settings") == {"music_volume": 0.5}  # preserved

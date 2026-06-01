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

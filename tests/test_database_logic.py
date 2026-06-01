"""Round-trip tests for the file-based persistence helpers.

Only the helpers that honour the module-level ``TXT_FOLDER_PATH`` constant are
exercised here, pointed at a temp dir so the real save files are never touched.
These pin current behaviour ahead of the SaveManager migration (Phase 1.4).
"""

import importlib


def _patched_db(tmp_path, monkeypatch):
    db = importlib.import_module("utils.database_logic")
    monkeypatch.setattr(db, "TXT_FOLDER_PATH", str(tmp_path))
    return db


def test_score_round_trip(tmp_path, monkeypatch):
    db = _patched_db(tmp_path, monkeypatch)
    db.SetScore(7)
    assert db.GetScore() == 7


def test_score_default_when_missing(tmp_path, monkeypatch):
    db = _patched_db(tmp_path, monkeypatch)
    # No file written yet -> defensive default of 1.
    assert db.GetScore() == 1


def test_coins_round_trip_and_add(tmp_path, monkeypatch):
    db = _patched_db(tmp_path, monkeypatch)
    db.SetCoins(10)
    assert db.GetCoins() == 10
    assert db.AddCoins(5) == 15
    assert db.GetCoins() == 15


def test_coins_default_when_missing(tmp_path, monkeypatch):
    db = _patched_db(tmp_path, monkeypatch)
    assert db.GetCoins() == 0

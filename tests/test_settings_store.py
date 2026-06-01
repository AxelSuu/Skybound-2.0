"""Tests for persistent audio settings (the previously-unsaved settings bug)."""

import pytest

from utils.save_manager import SaveManager


@pytest.fixture
def fresh_save(tmp_path, monkeypatch):
    import utils.save_manager as sm_module

    sm = SaveManager(str(tmp_path / "save.json"))
    monkeypatch.setattr(sm_module, "_manager", sm)
    return sm


def test_settings_round_trip(fresh_save):
    from utils import settings_store as store

    store.save_settings({
        "sfx_volume": 0.25,
        "music_volume": 0.9,
        "sfx_enabled": False,
        "music_enabled": True,
    })
    loaded = store.load_settings()
    assert loaded["sfx_volume"] == 0.25
    assert loaded["music_volume"] == 0.9
    assert loaded["sfx_enabled"] is False
    assert loaded["music_enabled"] is True


def test_defaults_when_unset(fresh_save):
    from utils import settings_store as store

    loaded = store.load_settings()
    # All known keys are present even with nothing saved.
    for key in ("sfx_volume", "music_volume", "sfx_enabled", "music_enabled"):
        assert key in loaded


def test_load_and_apply_pushes_to_sound_manager(fresh_save):
    from utils import settings_store as store
    from utils.sound_effects import sound_manager

    store.save_settings({
        "sfx_volume": 0.1,
        "music_volume": 0.2,
        "sfx_enabled": False,
        "music_enabled": False,
    })
    store.load_and_apply()
    assert sound_manager.sfx_volume == pytest.approx(0.1)
    assert sound_manager.music_volume == pytest.approx(0.2)
    assert sound_manager.sfx_enabled is False
    assert sound_manager.music_enabled is False

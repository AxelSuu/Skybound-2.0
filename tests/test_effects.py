"""Tests for EffectsManager hit-stop (gameplay freeze) bookkeeping."""

from utils.effects import EffectsManager


def test_hit_stop_starts_inactive():
    em = EffectsManager()
    assert not em.is_hit_stopped()


def test_hit_stop_counts_down_over_frames():
    em = EffectsManager()
    em.start_hit_stop(3)
    assert em.is_hit_stopped()
    em.update()  # 3 -> 2
    em.update()  # 2 -> 1
    assert em.is_hit_stopped()
    em.update()  # 1 -> 0
    assert not em.is_hit_stopped()


def test_start_hit_stop_takes_the_longer_freeze():
    em = EffectsManager()
    em.start_hit_stop(3)
    em.start_hit_stop(8)  # a bigger hit extends the freeze
    assert em.hit_stop == 8
    em.start_hit_stop(2)  # a smaller one does not shorten it
    assert em.hit_stop == 8

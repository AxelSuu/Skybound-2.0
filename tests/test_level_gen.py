"""Tests for procedural level reachability.

build_reachable_platforms must produce layouts that are always climbable:
every platform within one jump of the one below it, and fully on screen.
"""

import random

from constants import MAX_REACH_V, MAX_REACH_H
from levels.level1 import build_reachable_platforms

WIDTH, HEIGHT = 480, 600
FLOOR_TOP = HEIGHT - 40


def _all_reachable(plats):
    """Every step from the floor upward is within the jump budget."""
    # plats are sorted highest-first; walk them bottom (near floor) to top.
    chain = sorted(plats, key=lambda r: -r.y)  # lowest (largest y) first
    prev_cx, prev_y = WIDTH // 2, FLOOR_TOP
    for r in chain:
        v_gap = prev_y - r.y
        h_gap = abs(r.centerx - prev_cx)
        if v_gap > MAX_REACH_V or h_gap > MAX_REACH_H:
            return False
        prev_cx, prev_y = r.centerx, r.y
    return True


def test_layouts_are_always_reachable_across_levels_and_seeds():
    for level in range(1, 40):
        for seed in range(25):
            rng = random.Random(seed)
            plats = build_reachable_platforms(6, level, WIDTH, HEIGHT, rng=rng)
            assert plats, f"no platforms generated (level={level}, seed={seed})"
            assert _all_reachable(plats), f"unreachable layout (level={level}, seed={seed})"


def test_platforms_stay_on_screen():
    rng = random.Random(1)
    plats = build_reachable_platforms(8, 10, WIDTH, HEIGHT, rng=rng)
    for r in plats:
        assert r.left >= 0
        assert r.right <= WIDTH
        assert 0 < r.y < HEIGHT


def test_sorted_highest_first():
    rng = random.Random(2)
    plats = build_reachable_platforms(6, 5, WIDTH, HEIGHT, rng=rng)
    ys = [r.y for r in plats]
    assert ys == sorted(ys)  # index 0 is the highest platform (smallest y)

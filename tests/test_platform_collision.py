"""Tests for the one-way (pass-through) platform landing logic.

The collision rule lives in ``PhysicsSprite.resolve_platform_landing`` so it can
be exercised without the full game loop. A body snaps onto a platform top only
when it crossed that top edge moving downward this frame (feet at/above the top
last frame, and not moving up). Walking into a side or rising through a platform
must never snap.
"""

import pygame as pg

from sprites.player import Player


class FakePlatform:
    """Minimal stand-in for Platform2 — only ``.rect`` is used by the logic."""

    def __init__(self, x, y, w, h):
        self.rect = pg.Rect(x, y, w, h)


def _place(body, feet_y, prev_bottom, vel_y):
    """Position ``body`` so its feet are at ``feet_y`` with the given history."""
    body.pos.y = feet_y
    body.rect.midbottom = (body.pos.x, feet_y)
    if hasattr(body, "hitbox"):
        body.hitbox.midbottom = body.rect.midbottom
    body.prev_bottom = prev_bottom
    body.vel.y = vel_y
    body.on_floor = False


def test_falling_onto_platform_from_above_snaps():
    p = Player()
    plat = FakePlatform(p.hitbox.left - 5, 300, p.hitbox.width + 10, 20)
    # Feet pushed just past the top this frame; previous feet were above it.
    _place(p, feet_y=305, prev_bottom=298, vel_y=4)
    assert p.resolve_platform_landing([plat]) is True
    assert p.on_floor is True
    assert p.vel.y == 0
    assert p.hitbox.bottom == plat.rect.top


def test_walking_into_side_does_not_snap():
    p = Player()
    # A raised platform whose top is well above the player's feet.
    plat = FakePlatform(p.hitbox.left - 5, 200, p.hitbox.width + 10, 80)
    # Feet (and previous feet) are deep inside / below the platform top.
    _place(p, feet_y=270, prev_bottom=270, vel_y=2)
    assert p.resolve_platform_landing([plat]) is False
    assert p.on_floor is False


def test_moving_up_through_platform_does_not_snap():
    p = Player()
    plat = FakePlatform(p.hitbox.left - 5, 300, p.hitbox.width + 10, 20)
    # Overlapping the top while rising (vel.y < 0) must pass through.
    _place(p, feet_y=305, prev_bottom=320, vel_y=-6)
    assert p.resolve_platform_landing([plat]) is False
    assert p.on_floor is False


def test_resting_body_re_snaps_and_stays_put():
    p = Player()
    plat = FakePlatform(p.hitbox.left - 5, 300, p.hitbox.width + 10, 20)
    # Resting: previous feet exactly at the top; gravity nudged feet down 0.75px.
    _place(p, feet_y=300.75, prev_bottom=300, vel_y=0.5)
    assert p.resolve_platform_landing([plat]) is True
    assert p.pos.y == 300
    assert p.hitbox.bottom == 300


def test_no_platform_clears_on_floor():
    p = Player()
    p.on_floor = True
    assert p.resolve_platform_landing([]) is False
    assert p.on_floor is False

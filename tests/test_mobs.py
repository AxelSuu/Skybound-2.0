"""Tests for the new dive-bomber enemy and boss."""

import pygame as pg

from sprites.mob_types import DiveBomberMob, BossMob, create_random_mob


def test_dive_bomber_constructs_and_updates():
    m = DiveBomberMob(200, 150)
    assert m.state == "hover"
    player = pg.Vector2(220, 450)  # player below -> should be divable
    for _ in range(200):
        m.update(player)
    # It exercised both states without error and stayed a valid sprite.
    assert m.rect is not None
    assert m.state in ("hover", "dive")


def test_dive_bomber_enters_dive_when_player_below():
    m = DiveBomberMob(200, 150)
    m.ai_timer = m.dive_interval  # ready to commit
    player = pg.Vector2(200, 500)
    m.update(player)
    assert m.state == "dive"
    assert m.vel.y > 0  # heading downward


def test_boss_telegraphs_then_fires_spread():
    b = BossMob(240, 150)
    player = pg.Vector2(240, 500)
    fired = False
    saw_charge = False
    for _ in range(b.shoot_interval + 1):
        b.update(player)
        if b.charging:
            saw_charge = True
        if len(b.projectiles) > 0:
            fired = True
            break
    assert saw_charge, "boss never telegraphed before firing"
    assert fired, "boss never fired a volley"
    assert len(b.projectiles) >= 3  # a spread, not a single shot


def test_boss_image_changes_while_charging():
    b = BossMob(240, 150)
    assert b.image is b._base_image
    # Land inside the telegraph window (charging) but before the volley fires.
    b.shoot_timer = b.shoot_interval - b.telegraph_frames
    b.update(pg.Vector2(240, 500))
    assert b.charging
    assert b.image is b._charge_image


def test_dive_bomber_in_high_level_mob_pool():
    seen = {type(create_random_mob(100, 100, level=8)).__name__ for _ in range(200)}
    assert "DiveBomberMob" in seen

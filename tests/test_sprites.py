"""Construction smoke tests — sprites must initialise without crashing.

These guard the Phase 1.3 PhysicsSprite refactor: the public state that the
game loop relies on (pos/vel/acc vectors, rect, on_floor) must keep existing.
"""

import pygame as pg

from sprites.mob import Mob
from sprites.player import Player


def test_mob_constructs_with_physics_state():
    mob = Mob()
    assert isinstance(mob.pos, pg.Vector2)
    assert isinstance(mob.vel, pg.Vector2)
    assert isinstance(mob.acc, pg.Vector2)
    assert mob.on_floor is False
    assert mob.rect is not None


def test_player_constructs_with_physics_state():
    player = Player()
    assert isinstance(player.pos, pg.Vector2)
    assert isinstance(player.vel, pg.Vector2)
    assert isinstance(player.acc, pg.Vector2)
    assert player.rect is not None
    assert player.health > 0


def test_mob_update_advances_without_error():
    mob = Mob()
    start_y = mob.pos.y
    mob.update()
    # Gravity pulls it down a touch on the first tick.
    assert mob.pos.y >= start_y

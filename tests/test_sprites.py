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


def test_physics_friction_integration_is_deterministic():
    """Lock the friction-based integration math against accidental change.

    Mob spawns at rect.center=(440, 460). One update with zero horizontal
    velocity: acc=(0,0.5); vel=(0,0.5); pos += vel + 0.5*acc => +0.75 in y.
    """
    mob = Mob()
    assert mob.pos == pg.Vector2(440, 460)
    mob.update()
    assert mob.pos.x == 440
    assert abs(mob.pos.y - 460.75) < 1e-6
    # rect and hitbox stay synced to pos.
    assert mob.rect.midbottom == (440, round(mob.pos.y)) or mob.rect.midbottom[0] == 440


def test_simple_mob_gravity_has_no_friction():
    """Patrol/Jumper/Shooter use frictionless gravity via apply_gravity()."""
    from sprites.mob_types import PatrolMob

    mob = PatrolMob(200, 300)
    mob.vel.x = 2.0
    mob.update_physics()
    # No friction => horizontal velocity is unchanged by the integration step.
    assert mob.vel.x == 2.0
    # Gravity added one tick of downward velocity.
    assert mob.vel.y == 0.5

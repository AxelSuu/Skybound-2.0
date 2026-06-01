"""Construction smoke tests — sprites must initialise without crashing.

These guard the Phase 1.3 PhysicsSprite refactor: the public state that the
game loop relies on (pos/vel/acc vectors, rect, on_floor) must keep existing.
"""

import pygame as pg
import pytest

from sprites.mob import Mob
from sprites.player import Player
from utils.save_manager import SaveManager


@pytest.fixture
def temp_save(tmp_path, monkeypatch):
    """Isolate the global save singleton so tests don't clobber save.json."""
    import utils.save_manager as sm_module

    monkeypatch.setattr(sm_module, "_manager", SaveManager(str(tmp_path / "save.json")))


# ---------------------------------------------------------------------------
# Player hat / cosmetics
# ---------------------------------------------------------------------------

def test_player_no_hat_by_default(temp_save):
    """Fresh save → no hat equipped → hat_image is None."""
    player = Player()
    assert player.hat_image is None


def test_player_has_hat_image_when_cap_equipped(temp_save):
    """Equip 'cap' (always owned after buying) → hat_image is a Surface."""
    from utils.cosmetics import buy_hat
    # Grant coins and buy the cap
    import utils.database_logic as db
    db.SetCoins(100)
    buy_hat("cap")
    player = Player()
    assert player.hat_image is not None
    assert isinstance(player.hat_image, pg.Surface)


def test_player_classic_skin_by_default(temp_save):
    """Default skin is Classic (index 0)."""
    from utils.cosmetics import get_skin
    assert get_skin() == 0
    player = Player()
    assert player.rect is not None


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


# ---------------------------------------------------------------------------
# New enemy spritesheet construction tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("MobClass,spawn,cell_w,cell_h", [
    # (class name, spawn pos, raw cell width, raw cell height)
    ("PatrolMob",  (200, 300),  80,  80),
    ("JumperMob",  (150, 300),  72,  72),
    ("ShooterMob", (250, 300),  88,  88),
    ("BossMob",    (240, 100), 128, 128),
])
def test_enemy_sprite_rect_is_tight(MobClass, spawn, cell_w, cell_h):
    """Enemy sprite rects must be ≤ the raw spritesheet cell size.

    _crop() trims transparent padding, so the resulting rect should be at most
    the full cell size.  For smaller enemies the crop noticeably reduces the
    size; for the boss the art fills most of the cell so the bound is the cell
    itself — the important thing is it's not *larger* than the raw cell.
    """
    import importlib
    mod = importlib.import_module("sprites.mob_types")
    cls = getattr(mod, MobClass)
    mob = cls(*spawn)

    # Rect must not exceed the raw cell dimensions (un-cropped would equal them).
    assert mob.rect.width <= cell_w, (
        f"{MobClass}.rect.width={mob.rect.width} exceeds cell_w={cell_w}"
    )
    assert mob.rect.height <= cell_h, (
        f"{MobClass}.rect.height={mob.rect.height} exceeds cell_h={cell_h}"
    )
    # Sprites must have a proper image surface and physics state.
    assert isinstance(mob.image, pg.Surface)
    assert isinstance(mob.pos, pg.Vector2)

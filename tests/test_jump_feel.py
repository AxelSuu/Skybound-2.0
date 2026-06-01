"""Tests for coyote time and jump buffering on the Player.

The jump decision is isolated in ``Player._update_jump(space_held)`` so it can
be tested without pygame keyboard state. ``space_held`` is the boolean for
"is the jump key down this frame".
"""

from constants import JUMP_VELOCITY, COYOTE_FRAMES
from sprites.player import Player


def _grounded(player):
    player.on_floor = True
    player.vel.y = 0
    player.jump_pressed = False
    player.coyote_timer = 0
    player.jump_buffer_timer = 0


def test_jump_from_ground():
    p = Player()
    _grounded(p)
    p._update_jump(space_held=True)
    assert p.vel.y == JUMP_VELOCITY


def test_coyote_time_allows_jump_just_after_leaving_ledge():
    p = Player()
    _grounded(p)
    # Simulate walking off a ledge: airborne, falling, but still within coyote.
    p.on_floor = False
    p.vel.y = 3
    p.coyote_timer = COYOTE_FRAMES
    p.jump_pressed = False
    p._update_jump(space_held=True)
    assert p.vel.y == JUMP_VELOCITY


def test_no_jump_after_coyote_window_expires():
    p = Player()
    _grounded(p)
    p.on_floor = False
    p.vel.y = 3
    p.coyote_timer = 0          # grace already used up
    p.has_double_jump = False   # and no double jump available
    p.jump_pressed = False
    p._update_jump(space_held=True)
    assert p.vel.y == 3         # still falling, no jump granted


def test_jump_buffer_fires_on_landing_while_held():
    p = Player()
    _grounded(p)
    # Press jump while airborne with no coyote left -> buffered, no jump yet.
    p.on_floor = False
    p.vel.y = 5
    p.coyote_timer = 0
    p.jump_pressed = False
    p._update_jump(space_held=True)
    assert p.vel.y == 5                 # nothing happened yet
    assert p.jump_buffer_timer > 0      # but the intent is buffered

    # Next frame: player lands (still holding the key) -> buffered jump fires.
    p.on_floor = True
    p.vel.y = 0
    p._update_jump(space_held=True)
    assert p.vel.y == JUMP_VELOCITY


def test_held_key_does_not_auto_rejump_in_air():
    p = Player()
    _grounded(p)
    p._update_jump(space_held=True)      # jump off the ground
    assert p.vel.y == JUMP_VELOCITY
    # Key stays held; now airborne and rising. Should not jump again.
    p.on_floor = False
    p.has_double_jump = False
    p.vel.y = -5
    p._update_jump(space_held=True)
    assert p.vel.y == -5


def test_ground_jump_triggers_stretch():
    p = Player()
    _grounded(p)
    p._update_jump(space_held=True)
    assert p.squash < 0  # negative = stretch on take-off


def test_landing_triggers_squash():
    p = Player()
    p.land()
    assert p.squash > 0  # positive = squash on touchdown


def test_squash_decays_back_to_neutral():
    p = Player()
    p.land()
    # Apply over enough frames and it eases back to exactly zero.
    for _ in range(40):
        p._apply_squash()
    assert p.squash == 0.0


def test_squash_deforms_the_rendered_image():
    p = Player()
    base_size = p.image.get_size()
    p.land()  # squash -> wider, shorter
    p._apply_squash()
    new_size = p.image.get_size()
    assert new_size != base_size
    assert new_size[0] >= base_size[0]  # wider
    assert new_size[1] <= base_size[1]  # shorter

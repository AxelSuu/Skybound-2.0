#!/usr/bin/env python3
"""
Shared physics base class for moving sprites.

Player, Mob and the mob_types enemies all simulated the same vector physics
(gravity, horizontal screen-wrap, rect/hitbox syncing) with their own copy of
the code. PhysicsSprite centralises that scaffolding.

Two integration styles are intentionally preserved so behaviour does not change:
  * ``apply_physics()`` — friction-based motion (Player, Mob, ChaserMob).
  * ``apply_gravity()`` — simple gravity, no friction (Patrol/Jumper/Shooter).

Subclasses create ``self.rect`` (and usually ``self.hitbox``) from a loaded
image, call ``seed_body()`` to anchor the motion vectors, then each frame set
``self.acc`` and call one of the integration helpers.
"""

import pygame as pg

from constants import WIDTH, HEIGHT, PLAYER_ACC, FRICTION


class PhysicsSprite(pg.sprite.Sprite):
    """A pygame sprite with shared 2D motion: gravity, friction, screen-wrap."""

    def __init__(self, acc=PLAYER_ACC, friction=FRICTION, width=WIDTH, height=HEIGHT):
        pg.sprite.Sprite.__init__(self)
        self.ACC = acc            # Gravity / acceleration magnitude
        self.FRICTION = friction  # Horizontal friction coefficient
        self.WIDTH = width
        self.HEIGHT = height
        self.pos = pg.Vector2(0, 0)
        self.vel = pg.Vector2(0, 0)
        self.acc = pg.Vector2(0, 0)
        self.on_floor = False
        # Feet position at the end of the previous frame, used by the one-way
        # platform test in resolve_platform_landing().
        self.prev_bottom = 0.0

    def seed_body(self, center):
        """Anchor the motion vectors at ``center`` (typically ``rect.center``)."""
        self.pos = pg.Vector2(center)
        self.vel = pg.Vector2(0, 0)
        self.acc = pg.Vector2(0, 0)
        self.on_floor = False

    def apply_physics(self, hitbox_dx=0, hitbox_dy=0):
        """Friction-based integration + wrap + rect/hitbox sync."""
        self.acc.x += self.vel.x * self.FRICTION
        self.vel += self.acc
        self.pos += self.vel + self.ACC * self.acc
        self._wrap_and_sync(hitbox_dx, hitbox_dy)

    def apply_gravity(self, hitbox_dx=0, hitbox_dy=0):
        """Simple gravity integration (no friction) + wrap + rect/hitbox sync."""
        self.acc = pg.Vector2(0, self.ACC)
        self.vel += self.acc
        self.pos += self.vel
        self._wrap_and_sync(hitbox_dx, hitbox_dy)

    def resolve_platform_landing(self, platforms):
        """One-way (pass-through) platform landing.

        Snap the feet onto a platform top only when the body crossed that top
        edge moving downward this frame: it is not moving up, it overlaps the
        platform horizontally, and its feet went from at/above the top last
        frame (``prev_bottom``) to at/below the top now. Walking into a side or
        jumping up through a platform never snaps. Returns True if it landed.

        The test is on the *crossing*, not on current rect overlap, so a body
        resting exactly on a 1px-thin top edge stays planted (integer rects
        only touch, never overlap, at the rest position).
        """
        collider = getattr(self, "hitbox", self.rect)
        self.on_floor = False
        if self.vel.y < 0:
            return False
        current_bottom = self.pos.y  # feet this frame (rect.midbottom == pos)
        for plat in platforms:
            # Require horizontal overlap with the platform span.
            if collider.right <= plat.rect.left or collider.left >= plat.rect.right:
                continue
            plat_top = plat.rect.top
            if self.prev_bottom <= plat_top <= current_bottom:
                self.pos.y = plat_top
                self.vel.y = 0
                self.on_floor = True
                # Re-sync the collision rects so the feet rest exactly on the
                # surface and prev_bottom == plat_top next frame (stable rest).
                self.rect.bottom = plat_top
                if hasattr(self, "hitbox"):
                    self.hitbox.bottom = plat_top
                return True
        return False

    def _wrap_and_sync(self, hitbox_dx=0, hitbox_dy=0):
        """Wrap horizontally across the screen and sync rect + hitbox to pos."""
        # Remember last frame's feet before re-syncing, for the one-way test.
        self.prev_bottom = self.rect.bottom
        if self.pos.x > self.WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = self.WIDTH
        self.rect.midbottom = self.pos
        if hasattr(self, "hitbox"):
            self.hitbox.topleft = (self.rect.left + hitbox_dx, self.rect.top + hitbox_dy)

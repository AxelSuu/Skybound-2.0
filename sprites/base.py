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
        if not self.on_floor:
            self.acc = pg.Vector2(0, self.ACC)
            self.vel += self.acc
        self.pos += self.vel
        self._wrap_and_sync(hitbox_dx, hitbox_dy)

    def _wrap_and_sync(self, hitbox_dx=0, hitbox_dy=0):
        """Wrap horizontally across the screen and sync rect + hitbox to pos."""
        if self.pos.x > self.WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = self.WIDTH
        self.rect.midbottom = self.pos
        if hasattr(self, "hitbox"):
            self.hitbox.topleft = (self.rect.left + hitbox_dx, self.rect.top + hitbox_dy)

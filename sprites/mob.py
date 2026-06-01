import pygame as pg
import os
from utils.spritesheet import Spritesheet
from sprites.base import PhysicsSprite
from constants import MOB_ACC, MOB_FRICTION

""" Class for mob sprite. Shares vector physics with the player via
    PhysicsSprite (friction-based motion + screen wrap)."""


class Mob(PhysicsSprite):
    def __init__(self):
        super().__init__(acc=MOB_ACC, friction=MOB_FRICTION)
        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )

        # Load the spritesheet
        self.spritesheet = Spritesheet("Mobsheet.png")

        # Loading mob frames for animations
        self.walk_frames = [
            self.spritesheet.parse_sprite("midle1.png"),
            self.spritesheet.parse_sprite("mw1.png"),
            self.spritesheet.parse_sprite("midle2.png"),
            self.spritesheet.parse_sprite("mw2.png"),
        ]

        self.image = self.walk_frames[0]  # Start with the first frame
        self.frame_index = 0  # Track animation frame
        self.animation_timer = 0  # Track time for animation

        self.rect = self.image.get_rect()
        self.rect.center = (440, self.HEIGHT * 3 / 4 + 10)
        self.seed_body(self.rect.center)

        self.hitbox = pg.Rect(
            self.rect.left, self.rect.top, self.rect.width, self.rect.height
        )

    def update(self, player_pos=None):
        self.acc = pg.Vector2(0, self.ACC)

        self.animation_timer += 2

        if self.animation_timer % 20 == 0:
            self.frame_index = (self.frame_index + 1) % len(self.walk_frames)
            self.image = self.walk_frames[self.frame_index]

        # Friction-based motion + screen wrap + rect/hitbox sync (shared base)
        self.apply_physics()

"""Spritesheet parsing against the real game atlases."""

import pygame as pg

from utils.spritesheet import Spritesheet


def test_parse_mob_sprite_returns_surface():
    sheet = Spritesheet("Mobsheet.png")
    image = sheet.parse_sprite("mw1.png")
    assert isinstance(image, pg.Surface)
    assert image.get_width() > 0
    assert image.get_height() > 0


def test_get_sprite_matches_requested_size():
    sheet = Spritesheet("Mobsheet.png")
    sprite = sheet.get_sprite(0, 0, 24, 18)
    assert sprite.get_size() == (24, 18)

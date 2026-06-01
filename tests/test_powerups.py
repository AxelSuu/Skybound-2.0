"""Tests for the new CoinMagnet and ExtraLife power-ups."""

import pygame as pg

from sprites.player import Player
from sprites.powerups import Coin, CoinMagnet, ExtraLife, PowerUpManager


def test_extra_life_raises_max_health_and_heals():
    p = Player()
    max_before = p.max_health
    health_before = p.health
    ExtraLife(0, 0).collect(p)
    assert p.max_health == max_before + 1
    assert p.health == health_before + 1


def test_coin_magnet_activates_timer():
    p = Player()
    assert p.magnet_timer == 0
    CoinMagnet(0, 0).collect(p)
    assert p.magnet_timer > 0


def test_magnet_pulls_nearby_coin_toward_player():
    p = Player()
    p.pos = pg.Vector2(240, 300)
    p.magnet_timer = 100

    mgr = PowerUpManager()
    coin = Coin(240 + 100, 300)  # within MAGNET_RADIUS (150)
    mgr.power_ups.add(coin)

    before = pg.Vector2(p.pos).distance_to(coin.pos)
    mgr._apply_magnet(p)
    after = pg.Vector2(p.pos).distance_to(coin.pos)
    assert after < before  # coin moved closer


def test_magnet_does_nothing_when_inactive():
    p = Player()
    p.pos = pg.Vector2(240, 300)
    p.magnet_timer = 0  # inactive

    mgr = PowerUpManager()
    coin = Coin(240 + 100, 300)
    mgr.power_ups.add(coin)
    start = pg.Vector2(coin.pos)
    mgr._apply_magnet(p)
    assert pg.Vector2(coin.pos) == start  # unchanged


def test_magnet_ignores_far_coins():
    p = Player()
    p.pos = pg.Vector2(0, 0)
    p.magnet_timer = 100

    mgr = PowerUpManager()
    coin = Coin(400, 400)  # well beyond MAGNET_RADIUS
    mgr.power_ups.add(coin)
    start = pg.Vector2(coin.pos)
    mgr._apply_magnet(p)
    assert pg.Vector2(coin.pos) == start

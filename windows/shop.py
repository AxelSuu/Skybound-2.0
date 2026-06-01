#!/usr/bin/env python3
"""
Skybound Upgrade Shop screen.

Spend coins (earned by collecting them in-game) on permanent upgrades that
carry across every run. The economy lives in utils/upgrades.py; this is just
the presentation/input layer, following the blocking-scene pattern used by the
other windows.

Author: Axel Suu (revived 2026)
"""

import pygame as pg

from utils.draw_text import draw_text
from utils.database_logic import GetCoins, SetCoins, Hat, SetHat
from utils import upgrades as up

HAT_COST = 50  # coin cost of the cosmetic hat unlock


class Shop:
    """Blocking shop scene: list upgrades, buy with coins, ESC to return."""

    WIDTH = 480
    HEIGHT = 600
    LIGHTBLUE = (135, 206, 235)
    BLACK = (0, 0, 0)
    GREEN = (60, 180, 75)
    GREY = (160, 160, 160)
    PANEL = (255, 255, 255)

    def __init__(self):
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.active = True
        self.message = ""
        self.run()

    def _draw(self):
        """Render one frame and return the clickable (rect, id, maxed) buttons."""
        self.screen.fill(self.LIGHTBLUE)
        draw_text(self.screen, "Upgrade Shop", 40, self.WIDTH / 2, 40)
        draw_text(self.screen, f"Coins: {GetCoins()}", 26, self.WIDTH / 2, 82)

        buttons = []
        y = 120
        for uid, spec in up.UPGRADES.items():
            level = up.get_level(uid)
            maxed = up.is_maxed(uid)

            # Upgrade name + level pips and description.
            draw_text(self.screen, f"{spec['name']}   Lv {level}/{spec['max_level']}",
                      22, self.WIDTH / 2, y)
            draw_text(self.screen, spec["desc"], 15, self.WIDTH / 2, y + 22)

            # Buy button: green if affordable, grey if not / maxed.
            btn = pg.Rect(self.WIDTH / 2 - 75, y + 40, 150, 30)
            if maxed:
                pg.draw.rect(self.screen, self.GREY, btn)
                label = "MAXED"
            else:
                pg.draw.rect(self.screen, self.GREEN if up.can_afford(uid) else self.GREY, btn)
                label = f"Buy  {up.cost_for_next(uid)}"
            pg.draw.rect(self.screen, self.BLACK, btn, 2)
            draw_text(self.screen, label, 18, self.WIDTH / 2, y + 55)

            buttons.append((btn, uid, maxed))
            y += 105

        # Cosmetic unlock: the hat (a coin-gated unlockable).
        owned = Hat() == "hat"
        draw_text(self.screen, "Red Hat (cosmetic)", 22, self.WIDTH / 2, y)
        hat_btn = pg.Rect(self.WIDTH / 2 - 75, y + 24, 150, 30)
        if owned:
            pg.draw.rect(self.screen, self.GREY, hat_btn)
            hat_label = "OWNED"
        else:
            pg.draw.rect(self.screen, self.GREEN if GetCoins() >= HAT_COST else self.GREY, hat_btn)
            hat_label = f"Buy  {HAT_COST}"
        pg.draw.rect(self.screen, self.BLACK, hat_btn, 2)
        draw_text(self.screen, hat_label, 18, self.WIDTH / 2, y + 39)
        buttons.append((hat_btn, "_hat", owned))

        if self.message:
            draw_text(self.screen, self.message, 18, self.WIDTH / 2, self.HEIGHT - 58)
        draw_text(self.screen, "Press ESC to return", 16, self.WIDTH / 2, self.HEIGHT - 28)
        return buttons

    def run(self):
        while self.active:
            buttons = self._draw()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.active = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.active = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self._handle_click(pg.mouse.get_pos(), buttons)

            pg.display.flip()

    def _handle_click(self, mouse_pos, buttons):
        for btn, uid, owned_or_maxed in buttons:
            if not btn.collidepoint(mouse_pos):
                continue
            if uid == "_hat":
                self._buy_hat(owned_or_maxed)
            elif owned_or_maxed:
                self.message = "Already maxed out!"
            elif up.purchase(uid):
                self.message = f"Purchased {up.UPGRADES[uid]['name']}!"
            else:
                self.message = "Not enough coins!"
            return

    def _buy_hat(self, owned):
        if owned:
            self.message = "Hat already owned!"
        elif GetCoins() >= HAT_COST:
            SetCoins(GetCoins() - HAT_COST)
            SetHat("hat")
            self.message = "Unlocked the Red Hat!"
        else:
            self.message = "Not enough coins!"

#!/usr/bin/env python3
"""
Skybound Upgrade & Cosmetics Shop screen.

Spend coins (earned by collecting them in-game) on permanent upgrades and
cosmetics (skins + hats) that carry across every run.

The screen is split into three pages (tabs):
  - Upgrades  — permanent stat boosts (utils/upgrades.py catalogue)
  - Skins     — player recolors      (utils/cosmetics.SKINS)
  - Hats      — headwear cosmetics   (utils/cosmetics.HATS)

Author: Axel Suu (revived 2026)
"""

import pygame as pg

from utils.draw_text import draw_text
from utils.database_logic import GetCoins
from utils import upgrades as up
from utils import cosmetics as cosm

# Tab identifiers
TAB_UPGRADES = 0
TAB_SKINS = 1
TAB_HATS = 2
TAB_LABELS = ["Upgrades", "Skins", "Hats"]


class Shop:
    """Blocking shop scene with three tabs.  ESC to return to the main menu."""

    WIDTH = 480
    HEIGHT = 600
    LIGHTBLUE = (135, 206, 235)
    BLACK = (0, 0, 0)
    GREEN = (60, 180, 75)
    GREY = (160, 160, 160)
    BLUE = (70, 130, 220)
    SELECTED = (255, 215, 0)  # gold highlight for selected/equipped items

    def __init__(self):
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.active = True
        self.message = ""
        self.tab = TAB_UPGRADES
        self.run()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        while self.active:
            buttons, tab_buttons = self._draw()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.active = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.active = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self._handle_click(pg.mouse.get_pos(), buttons, tab_buttons)
            pg.display.flip()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw(self):
        """Render one frame; return (content_buttons, tab_buttons)."""
        self.screen.fill(self.LIGHTBLUE)
        draw_text(self.screen, "Shop", 38, self.WIDTH / 2, 28)
        draw_text(self.screen, f"Coins: {GetCoins()}", 22, self.WIDTH / 2, 60)

        # --- Tab bar ---
        tab_buttons = self._draw_tabs()

        # --- Content area ---
        if self.tab == TAB_UPGRADES:
            buttons = self._draw_upgrades()
        elif self.tab == TAB_SKINS:
            buttons = self._draw_skins()
        else:
            buttons = self._draw_hats()

        if self.message:
            draw_text(self.screen, self.message, 16, self.WIDTH / 2, self.HEIGHT - 40)
        draw_text(self.screen, "Press ESC to return", 14, self.WIDTH / 2, self.HEIGHT - 18)
        return buttons, tab_buttons

    def _draw_tabs(self):
        """Draw the three tab buttons; return list of (rect, tab_id)."""
        tab_w = self.WIDTH // 3
        tab_h = 28
        tab_y = 80
        tab_buttons = []
        for i, label in enumerate(TAB_LABELS):
            rect = pg.Rect(i * tab_w, tab_y, tab_w, tab_h)
            color = self.BLUE if i == self.tab else self.GREY
            pg.draw.rect(self.screen, color, rect)
            pg.draw.rect(self.screen, self.BLACK, rect, 1)
            draw_text(self.screen, label, 16, rect.centerx, rect.centery)
            tab_buttons.append((rect, i))
        return tab_buttons

    def _draw_upgrades(self):
        """Render permanent upgrade rows; return list of (rect, uid, maxed)."""
        buttons = []
        y = 120
        for uid, spec in up.UPGRADES.items():
            level = up.get_level(uid)
            maxed = up.is_maxed(uid)
            draw_text(self.screen, f"{spec['name']}   Lv {level}/{spec['max_level']}",
                      20, self.WIDTH / 2, y)
            draw_text(self.screen, spec["desc"], 13, self.WIDTH / 2, y + 20)
            btn = pg.Rect(self.WIDTH / 2 - 70, y + 36, 140, 26)
            if maxed:
                pg.draw.rect(self.screen, self.GREY, btn)
                label = "MAXED"
            else:
                pg.draw.rect(self.screen, self.GREEN if up.can_afford(uid) else self.GREY, btn)
                label = f"Buy  {up.cost_for_next(uid)}"
            pg.draw.rect(self.screen, self.BLACK, btn, 2)
            draw_text(self.screen, label, 16, self.WIDTH / 2, y + 49)
            buttons.append((btn, uid, maxed))
            y += 90
        return buttons

    def _draw_skins(self):
        """Render skin rows; return list of (rect, skin_idx, owned)."""
        buttons = []
        y = 120
        owned_list = cosm.owned_skins()
        current = cosm.get_skin()
        for idx, spec in cosm.SKINS.items():
            owned = idx in owned_list
            equipped = idx == current
            # Row label
            label_color = self.SELECTED if equipped else self.BLACK
            draw_text(self.screen, spec["name"], 20, self.WIDTH / 2, y, color=label_color)
            # Buy / equip button
            btn = pg.Rect(self.WIDTH / 2 - 70, y + 22, 140, 26)
            if owned:
                if equipped:
                    pg.draw.rect(self.screen, self.SELECTED, btn)
                    btn_label = "EQUIPPED"
                else:
                    pg.draw.rect(self.screen, self.GREEN, btn)
                    btn_label = "Equip"
            else:
                affordable = GetCoins() >= spec["cost"]
                pg.draw.rect(self.screen, self.GREEN if affordable else self.GREY, btn)
                btn_label = f"Buy  {spec['cost']}"
            pg.draw.rect(self.screen, self.BLACK, btn, 2)
            draw_text(self.screen, btn_label, 15, self.WIDTH / 2, y + 35)
            buttons.append((btn, idx, owned))
            y += 72
        return buttons

    def _draw_hats(self):
        """Render hat rows; return list of (rect, hat_id, owned)."""
        buttons = []
        y = 120
        owned_list = cosm.owned_hats()
        current = cosm.get_hat()
        for hat_id, spec in cosm.HATS.items():
            owned = hat_id in owned_list
            equipped = hat_id == current
            label_color = self.SELECTED if equipped else self.BLACK
            draw_text(self.screen, spec["name"], 20, self.WIDTH / 2, y, color=label_color)
            btn = pg.Rect(self.WIDTH / 2 - 70, y + 22, 140, 26)
            if owned:
                if equipped:
                    pg.draw.rect(self.screen, self.SELECTED, btn)
                    btn_label = "EQUIPPED"
                else:
                    pg.draw.rect(self.screen, self.GREEN, btn)
                    btn_label = "Equip"
            else:
                affordable = GetCoins() >= spec["cost"]
                pg.draw.rect(self.screen, self.GREEN if affordable else self.GREY, btn)
                btn_label = f"Buy  {spec['cost']}"
            pg.draw.rect(self.screen, self.BLACK, btn, 2)
            draw_text(self.screen, btn_label, 15, self.WIDTH / 2, y + 35)
            buttons.append((btn, hat_id, owned))
            y += 72
        return buttons

    # ------------------------------------------------------------------
    # Click handling
    # ------------------------------------------------------------------

    def _handle_click(self, mouse_pos, buttons, tab_buttons):
        # Check tab buttons first
        for rect, tab_id in tab_buttons:
            if rect.collidepoint(mouse_pos):
                self.tab = tab_id
                self.message = ""
                return

        # Content buttons
        for btn, item_id, owned in buttons:
            if not btn.collidepoint(mouse_pos):
                continue
            if self.tab == TAB_UPGRADES:
                self._handle_upgrade(item_id, owned)
            elif self.tab == TAB_SKINS:
                self._handle_skin(item_id, owned)
            elif self.tab == TAB_HATS:
                self._handle_hat(item_id, owned)
            return

    def _handle_upgrade(self, uid, maxed):
        if maxed:
            self.message = "Already maxed out!"
        elif up.purchase(uid):
            self.message = f"Purchased {up.UPGRADES[uid]['name']}!"
        else:
            self.message = "Not enough coins!"

    def _handle_skin(self, idx, owned):
        if owned:
            cosm.set_skin(idx)
            self.message = f"Equipped {cosm.SKINS[idx]['name']} skin!"
        elif cosm.buy_skin(idx):
            self.message = f"Unlocked {cosm.SKINS[idx]['name']} skin!"
        else:
            self.message = "Not enough coins!"

    def _handle_hat(self, hat_id, owned):
        if owned:
            cosm.set_hat(hat_id)
            self.message = f"Equipped {cosm.HATS[hat_id]['name']} hat!"
        elif cosm.buy_hat(hat_id):
            self.message = f"Unlocked {cosm.HATS[hat_id]['name']} hat!"
            from utils.achievements import check_hat_achievement
            check_hat_achievement()
        else:
            self.message = "Not enough coins!"

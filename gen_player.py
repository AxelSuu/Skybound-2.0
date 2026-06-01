"""Generate alternate player skins and new cosmetic hats.

Skins: palette-swap the existing Playersheet.png so every animation frame stays
pixel-aligned (idle/walk/jump/fall, L+R) — they drop straight into the existing
Spritesheet loader with the same JSON. We remap the character's purple clothing
hue to new hues while leaving skin tone and outline intact.

Hats: small ~30x18 PNGs drawn to sit at the same head anchor the code already
uses for hat1.png (blitted at (0,-8) left / (10,-8) right).
"""
from pixlib import *
from PIL import Image
import colorsys, os

IMGS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Skybound-2.0", "imgs"))

def load_player_sheet():
    return Image.open(os.path.join(IMGS, "Playersheet.png")).convert("RGBA")

def hue_shift_clothes(img, target_hue, sat_boost=1.0):
    """Recolour only the purple/blue clothing pixels to a new hue.

    The character's clothes sit in the blue-purple band (hue ~0.6-0.85). Skin
    (orange) and the dark outline are left untouched so the new skin reads as
    'same character, different outfit'.
    """
    src = img.load()
    out = img.copy()
    o = out.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            if a < 40:
                continue
            hh, ss, vv = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            # clothing = purplish/blue with some saturation (skip near-black outline & orange skin)
            if 0.55 <= hh <= 0.92 and ss > 0.18 and vv > 0.12:
                nr, ng, nb = colorsys.hsv_to_rgb(target_hue, min(1.0, ss*sat_boost), vv)
                o[x, y] = (int(nr*255), int(ng*255), int(nb*255), a)
    return out

# Skins: (name, target_hue). Hue in 0..1.
SKINS = [
    ("player_green",  0.33),   # forest green outfit
    ("player_red",    0.99),   # crimson outfit
    ("player_teal",   0.50),   # teal outfit
    ("player_gold",   0.12),   # gold/amber outfit
]

def build_skins():
    base = load_player_sheet()
    results = {}
    for name, hue in SKINS:
        results[name] = hue_shift_clothes(base, hue, sat_boost=1.05)
    return results

# ---------------------------------------------------------------------------
# Hats — drawn on a 30x18 canvas, transparent, anchored to match hat1.png.
# ---------------------------------------------------------------------------
S = 1  # hats are already drawn near final size for the 50px-wide head

def hat_crown():
    img, d = canvas(30, 18)
    gold = (255, 205, 60); gold_d = shade(gold, -0.35); gold_l = shade(gold, 0.4)
    # band
    rect(d, 6, 12, 26, 16, gold)
    rect(d, 6, 15, 26, 16, gold_d)
    # points
    for bx in (6, 12, 18, 24):
        poly(d, [(bx, 12), (bx+4, 12), (bx+2, 5)], gold)
    # jewels
    for jx in (9, 15, 21):
        px(d, jx+1, 13, (220, 40, 60, 255))
    # highlight
    line(d, 7, 13, 25, 13, gold_l)
    return outline_sprite(img)

def hat_wizard():
    img, d = canvas(30, 20)
    cloth = (90, 70, 200); cloth_d = shade(cloth,-0.4); star=(255,230,120)
    # cone
    poly(d, [(7, 17), (25, 17), (20, 0)], cloth)
    poly(d, [(16, 8), (25, 17), (20, 0)], cloth_d)  # shaded side
    # brim
    rect(d, 4, 16, 27, 19, cloth)
    rect(d, 4, 18, 27, 19, cloth_d)
    # stars
    for sx, sy in ((13,11),(17,6)):
        px(d, sx, sy, star); px(d, sx-1, sy, star); px(d, sx+1, sy, star)
        px(d, sx, sy-1, star); px(d, sx, sy+1, star)
    return outline_sprite(img)

def hat_cap():
    img, d = canvas(30, 16)
    red=(210,60,60); red_d=shade(red,-0.35); red_l=shade(red,0.3)
    # dome
    ellipse(d, 6, 4, 26, 16, red)
    rect(d, 6, 10, 26, 14, red)
    ellipse(d, 9, 5, 18, 10, red_l)
    # brim (forward)
    rect(d, 2, 12, 12, 15, red_d)
    # button
    px(d, 16, 5, (255,255,255,255))
    return outline_sprite(img)

def hat_halo():
    img, d = canvas(30, 16)
    gold=(255,230,120); glow=(255,248,200)
    ellipse(d, 5, 6, 25, 13, None, outline=gold, w=2)
    ellipse(d, 7, 7, 23, 11, None, outline=glow, w=1)
    return img  # no dark outline — it should glow

def hat_horns():
    img, d = canvas(30, 16)
    bone=(235,225,205); bone_d=shade(bone,-0.3)
    poly(d, [(7,15),(12,15),(4,5)], bone)
    poly(d, [(23,15),(18,15),(26,5)], bone)
    line(d, 4,5, 7,15, bone_d)
    line(d, 26,5, 23,15, bone_d)
    return outline_sprite(img)

HATS = {
    "hat_crown":  hat_crown,
    "hat_wizard": hat_wizard,
    "hat_cap":    hat_cap,
    "hat_halo":   hat_halo,
    "hat_horns":  hat_horns,
}

if __name__ == "__main__":
    for name, img in build_skins().items():
        img.save(f"{name}.png")
        print(name, img.size)
    for name, fn in HATS.items():
        img = fn()
        img.save(f"{name}.png")
        print(name, img.size)

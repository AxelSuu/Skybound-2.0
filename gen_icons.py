"""Generate 16x16 HUD icons for power-ups and stats.

Names match the effect labels used by Player.get_active_effects()
("Speed", "Jump", "Shield", "Double Jump", "Magnet") plus Health and Coin for
the rest of the HUD. Drawn at 16x16 with a subtle dark outline so they read on
both light and dark backgrounds.
"""
from pixlib import *

def icon_speed():
    img, d = canvas(16, 16)
    c=(255,225,60); cd=shade(c,-0.3)
    poly(d, [(9,1),(4,9),(8,9),(6,15),(13,6),(9,6)], c)
    poly(d, [(9,1),(4,9),(8,9),(6,15),(13,6),(9,6)], None)
    line(d, 9,1, 4,9, cd)
    return outline_sprite(img)

def icon_jump():
    img, d = canvas(16, 16)
    c=(80,220,110); cd=shade(c,-0.3)
    # up arrow
    poly(d, [(8,1),(2,8),(6,8),(6,15),(10,15),(10,8),(14,8)], c)
    line(d, 8,1, 2,8, shade(c,0.3))
    return outline_sprite(img)

def icon_shield():
    img, d = canvas(16, 16)
    c=(70,170,240); cl=shade(c,0.35); cd=shade(c,-0.35)
    poly(d, [(8,1),(14,4),(14,8),(8,15),(2,8),(2,4)], c)
    poly(d, [(8,1),(8,15),(2,8),(2,4)], cl)   # left half highlight
    # cross
    rect(d, 7,4, 9,11, (255,255,255,255))
    rect(d, 4,6, 12,8, (255,255,255,255))
    return outline_sprite(img)

def icon_double_jump():
    img, d = canvas(16, 16)
    c=(220,90,230)
    for oy in (0, 5):
        poly(d, [(8,1+oy),(3,6+oy),(6,6+oy),(6,8+oy),(10,8+oy),(10,6+oy),(13,6+oy)], c)
    return outline_sprite(img)

def icon_magnet():
    img, d = canvas(16, 16)
    red=(220,60,60); silver=(200,210,225)
    # horseshoe
    d.arc([2,2,13,16], 180, 360, fill=red, width=4)
    rect(d, 2, 9, 5, 15, red)
    rect(d, 10, 9, 13, 15, red)
    # poles
    rect(d, 2, 13, 5, 15, silver)
    rect(d, 10, 13, 13, 15, silver)
    return outline_sprite(img)

def icon_health():
    img, d = canvas(16, 16)
    c=(230,50,70); cl=shade(c,0.4)
    poly(d, [(8,14),(1,6),(3,3),(8,6),(13,3),(15,6)], c)
    ellipse(d, 2,2, 8,8, c); ellipse(d, 8,2, 14,8, c)
    ellipse(d, 3,3, 6,6, cl)
    return outline_sprite(img)

def icon_coin():
    img, d = canvas(16, 16)
    g=(255,205,60); gd=shade(g,-0.35); gl=shade(g,0.4)
    ellipse(d, 1,1, 14,14, g, outline=gd, w=1)
    ellipse(d, 4,4, 11,11, gl)
    # star/dollar mark
    rect(d, 7,4, 8,11, gd)
    line(d, 5,6, 10,6, gd); line(d, 5,9, 10,9, gd)
    return outline_sprite(img)

ICONS = {
    "icon_speed": icon_speed,
    "icon_jump": icon_jump,
    "icon_shield": icon_shield,
    "icon_double_jump": icon_double_jump,
    "icon_magnet": icon_magnet,
    "icon_health": icon_health,
    "icon_coin": icon_coin,
}

S = 2  # store at 32x32 so they're sharp; code can scale down if needed

if __name__ == "__main__":
    for name, fn in ICONS.items():
        img = scale(fn(), S)
        img.save(f"{name}.png")
        print(name, img.size)

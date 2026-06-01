"""Generate animated pixel-art spritesheets for the four enemies.

Design goals:
- Distinct silhouette + palette per enemy so behaviour reads instantly.
- 2 frames of animation each (Boss gets idle + charge to drive its telegraph).
- Sized to roughly match the rectangles the code currently uses, so collision
  feel is unchanged.

Output sheets follow the existing Mobsheet.json convention (sprites + meta).
"""
from pixlib import *

S = 4  # upscale factor (draw small, scale crisp)

# ---------------------------------------------------------------------------
# PatrolMob — armoured spiky crawler. ~40x40 in code -> draw 20x18 grid.
# Two frames: legs/spikes shift for a scuttle.
# ---------------------------------------------------------------------------
def patrol_frame(step):
    w, h = 20, 18
    img, d = canvas(w, h)
    body = (196, 64, 64)      # red
    body_d = shade(body, -0.35)
    body_l = shade(body, 0.3)
    spike = (235, 220, 200)
    # body dome
    ellipse(d, 2, 5, 17, 16, body)
    rect(d, 2, 10, 17, 15, body)
    # shading band
    rect(d, 2, 12, 17, 15, body_d)
    ellipse(d, 4, 6, 12, 11, body_l)  # highlight
    # back spikes
    for sx in (5, 9, 13):
        poly(d, [(sx, 5), (sx+2, 5), (sx+1, 1)], spike)
    # eyes (angry)
    eye = (255, 240, 120)
    px(d, 6, 9, (20,20,20,255)); px(d, 7, 9, eye)
    px(d, 12, 9, eye); px(d, 13, 9, (20,20,20,255))
    # legs (animate)
    legc = body_d
    feet = [3, 7, 12, 16]
    yoff = 0 if step == 0 else 1
    for i, fx in enumerate(feet):
        ly = 16 + ((i + step) % 2)
        line(d, fx, 15, fx, ly + 1, legc)
    return outline_sprite(img)

# ---------------------------------------------------------------------------
# JumperMob — springy slime. ~35x35 -> draw 18x18.
# Frame 0 = squashed (crouched, about to jump), Frame 1 = stretched (airborne).
# ---------------------------------------------------------------------------
def jumper_frame(step):
    w, h = 18, 18
    img, d = canvas(w, h)
    body = (74, 201, 120)     # green
    body_d = shade(body, -0.35)
    body_l = shade(body, 0.35)
    if step == 0:  # squashed
        ellipse(d, 1, 8, 16, 17, body)
        ellipse(d, 4, 9, 12, 13, body_l)
        rect(d, 1, 14, 16, 17, body_d)
        ey = 12
    else:          # stretched
        ellipse(d, 3, 2, 14, 17, body)
        ellipse(d, 5, 4, 11, 9, body_l)
        rect(d, 3, 14, 14, 17, body_d)
        ey = 8
    # eyes
    wht = (255,255,255,255); blk=(20,20,20,255)
    px(d, 6, ey, wht); px(d, 7, ey, blk)
    px(d, 11, ey, wht); px(d, 12, ey, blk)
    # little mouth
    px(d, 9, ey+3, body_d)
    # drip shine
    px(d, 9, (4 if step else 10), shade(body,0.6))
    return outline_sprite(img)

# ---------------------------------------------------------------------------
# ShooterMob — one-eyed floating turret. ~45x45 -> draw 22x22.
# Frame 0 = eye open (aiming), Frame 1 = eye narrowed (firing).
# ---------------------------------------------------------------------------
def shooter_frame(step):
    w, h = 22, 22
    img, d = canvas(w, h)
    body = (90, 120, 230)     # blue
    body_d = shade(body, -0.4)
    body_l = shade(body, 0.35)
    metal = (180, 195, 220)
    # hull
    ellipse(d, 2, 2, 19, 19, body)
    ellipse(d, 5, 4, 14, 12, body_l)
    rect(d, 2, 12, 19, 18, body_d)
    ellipse(d, 2, 8, 19, 19, None, outline=None)
    # barrel pointing down-left
    rect(d, 0, 14, 6, 17, metal)
    rect(d, 0, 14, 6, 17, None)
    line(d, 0, 14, 0, 17, shade(metal,-0.3))
    # big eye
    ec = (255, 90, 90) if step == 0 else (255, 200, 90)
    er = 5 if step == 0 else 3
    ellipse(d, 11-er, 9-er, 11+er, 9+er, (240,240,255,255))
    ellipse(d, 9, 7, 13, 11, ec)
    px(d, 11, 9, (20,20,20,255))
    # rivets
    for rx, ry in ((4,4),(17,5),(5,17),(16,16)):
        px(d, rx, ry, metal)
    return outline_sprite(img)

# ---------------------------------------------------------------------------
# BossMob — large horned demon head. 64x64 in code -> draw 32x32.
# base (idle) + charge (glowing, wider eyes) frames.
# ---------------------------------------------------------------------------
def boss_frame(charging):
    w, h = 32, 32
    img, d = canvas(w, h)
    base = (170, 30, 50)
    if charging:
        base = (235, 80, 60)
    base_d = shade(base, -0.4)
    base_l = shade(base, 0.3)
    horn = (245, 235, 215)
    horn_d = shade(horn, -0.25)
    # horns
    poly(d, [(4,10),(9,11),(2,0)], horn)
    poly(d, [(4,10),(9,11),(2,0)], None)
    poly(d, [(28,10),(23,11),(30,0)], horn)
    line(d, 2,0, 4,10, horn_d)
    line(d, 30,0, 28,10, horn_d)
    # head
    ellipse(d, 3, 6, 28, 30, base)
    ellipse(d, 7, 9, 20, 19, base_l)
    rect(d, 3, 22, 28, 29, base_d)
    # brow
    rect(d, 6, 12, 25, 14, base_d)
    # eyes
    glow = (255, 240, 120) if charging else (255, 200, 60)
    er = 4 if charging else 3
    ellipse(d, 10-er, 16-er, 10+er, 16+er, glow)
    ellipse(d, 22-er, 16-er, 22+er, 16+er, glow)
    px(d, 10, 16, (40,0,0,255)); px(d, 22, 16, (40,0,0,255))
    # angry brows
    line(d, 6,12, 12,14, base_d, 2)
    line(d, 26,12, 20,14, base_d, 2)
    # fanged frown
    line(d, 11, 25, 21, 25, (30,0,10,255), 1)
    for fx in (12, 16, 20):
        poly(d, [(fx,25),(fx+2,25),(fx+1,28)], horn)
    if charging:  # extra glow flecks
        for gx, gy in ((6,20),(26,21),(16,7)):
            px(d, gx, gy, (255,255,200,255))
    return outline_sprite(img)


def build_enemy_sheets():
    out = {}

    # --- Patrol (2 frames, 20x18 -> scaled) ---
    cell = (20*S, 20*S)
    frames = [scale(patrol_frame(i), S) for i in (0, 1)]
    sheet, meta = pack_sheet(frames, 2, cell[0], cell[1],
                             ["patrol1.png", "patrol2.png"], "Patrolsheet.png")
    out["Patrolsheet"] = (sheet, meta)

    # --- Jumper (2 frames, 18x18) ---
    cell = (18*S, 18*S)
    frames = [scale(jumper_frame(i), S) for i in (0, 1)]
    sheet, meta = pack_sheet(frames, 2, cell[0], cell[1],
                             ["jumper1.png", "jumper2.png"], "Jumpersheet.png")
    out["Jumpersheet"] = (sheet, meta)

    # --- Shooter (2 frames, 22x22) ---
    cell = (22*S, 22*S)
    frames = [scale(shooter_frame(i), S) for i in (0, 1)]
    sheet, meta = pack_sheet(frames, 2, cell[0], cell[1],
                             ["shooter1.png", "shooter2.png"], "Shootersheet.png")
    out["Shootersheet"] = (sheet, meta)

    # --- Boss (idle + charge, 32x32) ---
    cell = (32*S, 32*S)
    frames = [scale(boss_frame(False), S), scale(boss_frame(True), S)]
    sheet, meta = pack_sheet(frames, 2, cell[0], cell[1],
                             ["boss_idle.png", "boss_charge.png"], "Bosssheet.png")
    out["Bosssheet"] = (sheet, meta)

    return out


if __name__ == "__main__":
    sheets = build_enemy_sheets()
    for name, (sheet, meta) in sheets.items():
        sheet.save(f"{name}.png")
        with open(f"{name}.json", "w") as f:
            json.dump(meta, f, indent=2)
        print(f"{name}.png  {sheet.size}")
    # contact sheet preview (scaled cells side by side at 2x of their stored size)
    print("done")

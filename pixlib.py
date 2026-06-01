"""Tiny pixel-art helpers for Skybound sprite generation.

Everything is drawn on a low-res grid then nearest-neighbour scaled up, so the
output is crisp blocky pixel art that matches the game's existing hand-drawn
look. All sprites are RGBA with a transparent background.
"""
from PIL import Image, ImageDraw
import math, json, os

def canvas(w, h):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)

def px(d, x, y, color):
    d.point((x, y), fill=color)

def rect(d, x0, y0, x1, y1, color):
    d.rectangle([x0, y0, x1, y1], fill=color)

def ellipse(d, x0, y0, x1, y1, color, outline=None, w=1):
    d.ellipse([x0, y0, x1, y1], fill=color, outline=outline, width=w)

def line(d, x0, y0, x1, y1, color, w=1):
    d.line([x0, y0, x1, y1], fill=color, width=w)

def poly(d, pts, color, outline=None):
    d.polygon(pts, fill=color, outline=outline)

def scale(img, factor):
    return img.resize((img.width * factor, img.height * factor), Image.NEAREST)

def outline_sprite(img, color=(0, 0, 0, 255)):
    """Add a 1px dark outline around opaque pixels (classic pixel-art look)."""
    px_in = img.load()
    out = img.copy()
    px_out = out.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if px_in[x, y][3] == 0:
                # transparent: outline if a neighbour is opaque
                neigh = False
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h and px_in[nx, ny][3] > 200:
                        neigh = True; break
                if neigh:
                    px_out[x, y] = color
    return out

def shade(color, amt):
    """Lighten (amt>0) or darken (amt<0) an RGB(A) color."""
    r, g, b = color[:3]
    a = color[3] if len(color) == 4 else 255
    f = amt
    if f >= 0:
        r = int(r + (255 - r) * f); g = int(g + (255 - g) * f); b = int(b + (255 - b) * f)
    else:
        r = int(r * (1 + f)); g = int(g * (1 + f)); b = int(b * (1 + f))
    return (max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b)), a)

def pack_sheet(frames, cols, cell_w, cell_h, names, image_name):
    """Pack frames left-to-right, top-to-bottom into a sheet + JSON metadata.

    frames: list of PIL images (already at final cell size).
    Returns (sheet_image, metadata_dict).
    """
    rows = math.ceil(len(frames) / cols)
    sheet = Image.new("RGBA", (cols * cell_w, rows * cell_h), (0, 0, 0, 0))
    meta = {"sprites": {}, "meta": {"image": image_name,
            "size": {"w": cols * cell_w, "h": rows * cell_h}, "scale": 1}}
    for i, fr in enumerate(frames):
        cx = (i % cols) * cell_w
        cy = (i // cols) * cell_h
        # center the frame in its cell
        ox = cx + (cell_w - fr.width) // 2
        oy = cy + (cell_h - fr.height) // 2
        sheet.alpha_composite(fr, (ox, oy))
        meta["sprites"][names[i]] = {"width": cell_w, "height": cell_h,
                                     "x": cx, "y": cy}
    return sheet, meta

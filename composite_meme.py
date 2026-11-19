#!/usr/bin/env python3
"""Composite the GTA 6 x make.fun meme: Vice City scene + meme text + real make.fun ghost mark."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = "/home/hatch/workspace/makefun/gta6-meme/media-generation-gta6-vice-city-scene-0-5e4f17d0-fc1a-4622-8bb4-b6a4e740e094.png"
GHOST = "/home/hatch/workspace/makefun/gta6-meme/ghost-mark.png"
OUT = "/home/hatch/workspace/makefun/gta6-meme/meme.png"
W = 1080
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

img = Image.open(BASE).convert("RGB").resize((W, W), Image.LANCZOS)
d = ImageDraw.Draw(img, "RGBA")

def band(y0, y1, max_alpha=170):
    """Vertical dark gradient band for text legibility."""
    overlay = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    h = y1 - y0
    for y in range(h):
        if y0 == 0:
            a = int(max_alpha * (1 - abs(y - h / 2) / (h / 2)) ** 0.7)
        else:
            a = int(max_alpha * (y / h) ** 1.2)
        od.line([(0, y0 + y), (W, y0 + y)], fill=(0, 0, 0, a))
    global img
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def text_center(y, text, font, fill=(255, 255, 255), stroke=6):
    f = ImageFont.truetype(FONT, font)
    d.text((W / 2, y), text, font=f, fill=fill, anchor="ma",
           stroke_width=stroke, stroke_fill=(0, 0, 0))

def text_center_mixed(y, segments, size, stroke=5):
    """segments: list of (text, fill). Drawn centered as one line."""
    f = ImageFont.truetype(FONT, size)
    widths = [d.textlength(s, font=f) for s, _ in segments]
    x = (W - sum(widths)) / 2
    for (s, fill), w in zip(segments, widths):
        d.text((x, y), s, font=f, fill=fill, anchor="la",
               stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += w

# legibility bands
band(0, 210)          # top
band(830, 1080)       # bottom (gradient stronger at bottom)
d = ImageDraw.Draw(img, "RGBA")  # redraw object: band() replaced img

# top text
text_center(28, "ME: GRINDING GTA VI", 74)
text_center(112, "ALL LAUNCH WEEK", 74)

# ghost sticker bottom-right, white ring behind it
ghost = Image.open(GHOST).convert("RGBA")
gs = 300
ghost = ghost.resize((gs, gs), Image.LANCZOS)
ring = Image.new("RGBA", (gs + 16, gs + 16), (0, 0, 0, 0))
rd = ImageDraw.Draw(ring)
rd.ellipse([0, 0, gs + 15, gs + 15], fill=(255, 255, 255, 255))
img.paste(ring, (W - gs - 8 - 16, W - gs - 8 - 16), ring)
img.paste(ghost, (W - gs - 8 - 8, W - gs - 8 - 8), ghost)

# bottom text, left of the ghost (region x 20..760)
d2 = ImageDraw.Draw(img, "RGBA")
YELLOW = (255, 214, 10)
# line 1 centered in left region
f1 = ImageFont.truetype(FONT, 56)
t1 = "MY AI AGENT GRINDED"
w1 = d2.textlength(t1, font=f1)
d2.text(((20 + 760 - w1) / 2, 872), t1, font=f1, fill=(255, 255, 255),
        stroke_width=5, stroke_fill=(0, 0, 0))
# line 2 mixed colour, centered in left region
f2 = ImageFont.truetype(FONT, 56)
segs = [("MAKE.FUN", YELLOW), (" — GOT PAID", (255, 255, 255))]
widths = [d2.textlength(s, font=f2) for s, _ in segs]
x = (20 + 760 - sum(widths)) / 2
for (s, fill), w in zip(segs, widths):
    d2.text((x, 948), s, font=f2, fill=fill, stroke_width=5, stroke_fill=(0, 0, 0))
    x += w

img.save(OUT, "PNG")
print("saved", OUT, img.size)

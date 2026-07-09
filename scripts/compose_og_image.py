#!/usr/bin/env python3
"""One-off script: compose a branded 1200x630 Open Graph share image."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 1200, 630
BG = (22, 21, 26)
FG = (239, 236, 230)
MUTED = (155, 154, 158)
BERGHAIN = (143, 180, 201)
PANORAMA = (217, 143, 61)

# Background photo, treated like the in-page carousel (desaturated + darkened)
photo = Image.open("assets/carousel/night.jpg").convert("RGB")
photo_ratio = W / H
src_ratio = photo.width / photo.height
if src_ratio > photo_ratio:
    new_h = H
    new_w = int(H * src_ratio)
else:
    new_w = W
    new_h = int(W / src_ratio)
photo = photo.resize((new_w, new_h), Image.LANCZOS)
left = (new_w - W) // 2
top = (new_h - H) // 2
photo = photo.crop((left, top, left + W, top + H))
photo = ImageEnhance.Color(photo).enhance(0.6)
photo = ImageEnhance.Contrast(photo).enhance(1.05)
photo = ImageEnhance.Brightness(photo).enhance(0.55)

canvas = Image.new("RGB", (W, H), BG)
canvas.paste(photo, (0, 0))

# Dark gradient overlay (left->right) so text on the left stays legible
overlay = Image.new("L", (W, H), 0)
odraw = ImageDraw.Draw(overlay)
for x in range(W):
    t = x / W
    alpha = int(235 * (1 - min(t / 0.72, 1)) ** 1.4) if t < 0.85 else int(235 * 0.05)
    odraw.line([(x, 0), (x, H)], fill=alpha)
dark = Image.new("RGB", (W, H), BG)
canvas = Image.composite(dark, canvas, overlay)

draw = ImageDraw.Draw(canvas)

eyebrow_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28)
headline_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 76)
sub_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 32)

def tracked_text(draw, pos, text, font, fill, tracking=0):
    x, y = pos
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        w = draw.textlength(ch, font=font)
        x += w + tracking

margin = 72
tracked_text(draw, (margin, 96), "BERLIN  ·  21–22.08.2026", eyebrow_font, PANORAMA, tracking=2)
draw.text((margin, 150), "YOUR BERGHAIN", font=headline_font, fill=FG)
draw.text((margin, 234), "WEEKEND", font=headline_font, fill=FG)
draw.text((margin, 358), "REEF (Fri)  +  Klubnacht (Sat)  —  25 DJs, bios, sets & links", font=sub_font, fill=MUTED)

# Small staircase motif, bottom-left, echoing the page's own divider
step_y = 470
step_h = 26
steps = [
    (margin, step_y + step_h * 2, 70, BERGHAIN),
    (margin + 70, step_y + step_h, 70, PANORAMA),
    (margin + 140, step_y, 70, BERGHAIN),
]
for x, y, w, color in steps:
    draw.rectangle([x, y, x + w, y + step_h], fill=color)

canvas.save("assets/og-image.jpg", quality=85)
print("Saved assets/og-image.jpg", canvas.size)

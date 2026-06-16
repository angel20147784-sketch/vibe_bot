#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate course day images for Telegram bot"""

from PIL import Image, ImageDraw, ImageFont
import os
from course_data import COURSE_DAYS, WEEK_NAMES

WEEK_COLORS = {
    1: (108, 92, 231),
    2: (0, 184, 148),
    3: (225, 112, 85),
    4: (9, 132, 227),
    5: (232, 67, 147),
}

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

def get_font(size, bold=False):
    font_paths = [
        "C:/Windows/Fonts/DejaVuSans-Bold.ttf" if bold else "C:/Windows/Fonts/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def generate_day_image(day_num: int) -> str:
    day = COURSE_DAYS.get(day_num)
    if not day:
        return None

    week = (day_num - 1) // 7 + 1
    cr, cg, cb = WEEK_COLORS[week]

    W, H = 800, 420
    img = Image.new("RGB", (W, H), (248, 249, 250))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 90], fill=(cr, cg, cb))

    font_title = get_font(36, bold=True)
    font_week = get_font(14)
    font_body = get_font(18)
    font_small = get_font(14)
    font_day_num = get_font(48, bold=True)
    font_tip = get_font(15, bold=True)

    draw.text((30, 18), f"ДЕНЬ {day_num}", font=font_title, fill=(255, 255, 255))
    draw.text((30, 60), f"Неделя {week}: {WEEK_NAMES[week]}", font=font_week, fill=(220, 220, 255))

    draw.text((W - 120, 20), str(day_num), font=font_day_num, fill=(255, 255, 255, 180))

    y = 110
    draw.text((30, y), day["title"], font=font_body, fill=(45, 54, 54))
    y += 35

    draw.line([(30, y), (W - 30, y)], fill=(cr, cg, cb), width=2)
    y += 15

    for sec_title, items in day.get("sections", [])[:2]:
        draw.rounded_rectangle([30, y, W - 30, y + 28], radius=5, fill=(cr, cg, cb))
        draw.text((40, y + 5), sec_title, font=font_tip, fill=(255, 255, 255))
        y += 38

        for item in items[:3]:
            draw.text((50, y), f"  {item}", font=font_small, fill=(80, 80, 80))
            y += 22
        y += 10

    if day.get("tip"):
        draw.rounded_rectangle([30, H - 70, W - 30, H - 20], radius=8, fill=(255, 243, 224))
        draw.text((45, H - 58), day["tip"], font=font_small, fill=(180, 100, 30))

    path = os.path.join(IMG_DIR, f"day_{day_num}.png")
    img.save(path, "PNG")
    return path


def generate_all():
    os.makedirs(IMG_DIR, exist_ok=True)
    for day_num in range(1, 31):
        path = generate_day_image(day_num)
        if path:
            print(f"Day {day_num}: {path}")
    print(f"Done! {len(os.listdir(IMG_DIR))} images in {IMG_DIR}")


if __name__ == "__main__":
    generate_all()

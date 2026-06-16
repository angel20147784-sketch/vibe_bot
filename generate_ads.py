#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate advertising creatives"""

from PIL import Image, ImageDraw, ImageFont
import os

FONT_DIR = "C:/Windows/Fonts"

def get_font(size, bold=False):
    font_paths = [
        "C:/Windows/Fonts/DejaVuSans-Bold.ttf" if bold else "C:/Windows/Fonts/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def create_instagram_post():
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), (248, 249, 250))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 200], fill=(108, 92, 231))

    font_big = get_font(60, bold=True)
    font_med = get_font(36, bold=True)
    font_small = get_font(28)

    draw.text((60, 50), "ВАЙБКОДИНГ", font=font_big, fill=(255, 255, 255))
    draw.text((60, 130), "за 30 дней", font=font_med, fill=(200, 200, 255))

    draw.text((60, 250), "Научись создавать", font=font_med, fill=(45, 54, 54))
    draw.text((60, 300), "приложения с помощью ИИ", font=font_med, fill=(45, 54, 54))

    benefits = [
        "Без опыта программирования",
        "Cursor + Claude + v0.dev",
        "Реальные проекты",
        "Деплой за 5 минут",
    ]
    y = 400
    for b in benefits:
        draw.text((80, y), f"  {b}", font=font_small, fill=(80, 80, 80))
        y += 50

    draw.rounded_rectangle([60, H-200, W-60, H-100], radius=15, fill=(0, 184, 148))
    draw.text((W//2 - 100, H-170), "Начни бесплатно!", font=font_med, fill=(255, 255, 255))

    draw.text((60, H-80), "@CODEScodingbot", font=font_small, fill=(108, 92, 231))

    path = os.path.join("ads", "instagram_post.png")
    os.makedirs("ads", exist_ok=True)
    img.save(path, "PNG")
    return path


def create_twitter_post():
    W, H = 1200, 675
    img = Image.new("RGB", (W, H), (29, 161, 242))
    draw = ImageDraw.Draw(img)

    font_big = get_font(48, bold=True)
    font_med = get_font(32, bold=True)
    font_small = get_font(24)

    draw.text((60, 60), "ВАЙБКОДИНГ", font=font_big, fill=(255, 255, 255))
    draw.text((60, 130), "за 30 дней", font=font_med, fill=(200, 230, 255))

    draw.text((60, 220), "Создавай приложения", font=font_med, fill=(255, 255, 255))
    draw.text((60, 270), "с помощью ИИ", font=font_med, fill=(255, 255, 255))

    draw.text((60, 350), "Cursor + Claude + v0.dev", font=font_small, fill=(200, 230, 255))
    draw.text((60, 390), "Без опыта программирования", font=font_small, fill=(200, 230, 255))

    draw.rounded_rectangle([60, H-130, 480, H-50], radius=12, fill=(255, 255, 255))
    draw.text((80, H-110), "t.me/CODEScodingbot", font=font_med, fill=(0, 0, 0))

    path = os.path.join("ads", "twitter_post.png")
    os.makedirs("ads", exist_ok=True)
    img.save(path, "PNG")
    return path


def create_tiktok_cover():
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_big = get_font(80, bold=True)
    font_med = get_font(48, bold=True)
    font_small = get_font(36)
    font_link = get_font(44, bold=True)

    draw.rectangle([0, 0, W, 400], fill=(108, 92, 231))
    draw.text((60, 100), "ВАЙБКОДИНГ", font=font_big, fill=(255, 255, 255))
    draw.text((60, 220), "за 30 дней", font=font_med, fill=(200, 200, 255))

    draw.text((60, 500), "Создал приложение", font=font_med, fill=(255, 255, 255))
    draw.text((60, 570), "за 1 ЧАС", font=font_big, fill=(0, 184, 148))

    draw.text((60, 700), "Без опыта программирования", font=font_small, fill=(200, 200, 200))

    draw.rounded_rectangle([40, H-250, W-40, H-160], radius=15, fill=(108, 92, 231))
    draw.text((80, H-230), "Курс бесплатно", font=font_med, fill=(255, 255, 255))

    draw.rounded_rectangle([40, H-140, W-40, H-50], radius=15, fill=(0, 184, 148))
    draw.text((80, H-115), "t.me/CODEScodingbot", font=font_link, fill=(255, 255, 255))

    path = os.path.join("ads", "tiktok_cover.png")
    os.makedirs("ads", exist_ok=True)
    img.save(path, "PNG")
    return path


if __name__ == "__main__":
    print(create_instagram_post())
    print(create_twitter_post())
    print(create_tiktok_cover())
    print("Done!")

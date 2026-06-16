#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PDF из pptxgenjs кода — тёмный стиль с карточками"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

FONT_DIR = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont("DV", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVB", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVM", os.path.join(FONT_DIR, "DejaVuSansMono.ttf")))

F, FB, FM = "DV", "DVB", "DVM"
W, H = A4
M = 1.5 * cm


def hex_to_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb(hex_str):
    return hex_to_rgb(hex_str)


# Palette from pptxgenjs
BG = hex_to_rgb("1A1A2E")
PURPLE = hex_to_rgb("6B46F5")
PURPLE_LT = hex_to_rgb("8B6BF8")
PURPLE_DARK = hex_to_rgb("4A2FCE")
PURPLE_BG = hex_to_rgb("2A1A6E")
WHITE = (255, 255, 255)
CARD_BG = (255, 255, 255)
TEXT_DARK = hex_to_rgb("1A1A2E")
TEXT_GRAY = hex_to_rgb("666680")
ACCENT = PURPLE
GREEN = hex_to_rgb("2E7D4F")
RED = hex_to_rgb("C94040")
ORANGE = hex_to_rgb("B07A10")
TEAL = hex_to_rgb("1A6E6E")
BORDER = hex_to_rgb("E8E8F0")
TIP_BG = hex_to_rgb("EDE8FF")
TIP_BORDER = hex_to_rgb("D4C8FF")
DARK_NUM = hex_to_rgb("3D2FAA")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb(hex_str):
    return hex_to_rgb(hex_str)


class PDF:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.page = 0

    def save(self):
        self.c.save()

    def bg(self, r, g, b):
        self.c.setFillColorRGB(r / 255, g / 255, b / 255)
        self.c.rect(0, 0, W, H, fill=1, stroke=0)

    def rect(self, x, y, w, h, r, g, b):
        self.c.setFillColorRGB(r / 255, g / 255, b / 255)
        self.c.rect(x, y, w, h, fill=1, stroke=0)

    def rrect(self, x, y, w, h, r, g, b, border=None):
        self.c.setFillColorRGB(r / 255, g / 255, b / 255)
        if border:
            self.c.setStrokeColorRGB(border[0] / 255, border[1] / 255, border[2] / 255)
            self.c.setLineWidth(0.5)
            self.c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
        else:
            self.c.roundRect(x, y, w, h, 4, fill=1, stroke=0)

    def card(self, x, y, w, h, border=True):
        self.c.setFillColorRGB(1, 1, 1)
        if border:
            self.c.setStrokeColorRGB(BORDER[0] / 255, BORDER[1] / 255, BORDER[2] / 255)
            self.c.setLineWidth(0.5)
            self.c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
        else:
            self.c.roundRect(x, y, w, h, 4, fill=1, stroke=0)

    def circle(self, x, y, r, cr, cg, cb):
        self.c.setFillColorRGB(cr / 255, cg / 255, cb / 255)
        self.c.circle(x, y, r, fill=1, stroke=0)

    def txt(self, x, y, text, font=F, size=10, r=26, g=26, b=46):
        self.c.setFillColorRGB(r / 255, g / 255, b / 255)
        self.c.setFont(font, size)
        self.c.drawString(x, y, text)

    def txtc(self, x, y, text, font=F, size=10, r=26, g=26, b=46):
        self.c.setFillColorRGB(r / 255, g / 255, b / 255)
        self.c.setFont(font, size)
        self.c.drawCentredString(x, y, text)

    def txtr(self, x, y, text, font=F, size=10, r=26, g=26, b=46):
        self.c.setFillColorRGB(r / 255, g / 255, b / 255)
        self.c.setFont(font, size)
        self.c.drawRightString(x, y, text)

    def wrap(self, x, y, text, font=F, size=9, r=26, g=26, b=46, max_w=170, lh=4.5):
        self.c.setFillColorRGB(r / 255, g / 255, b / 255)
        self.c.setFont(font, size)
        words = text.split()
        line = ""
        cy = y
        for word in words:
            test = f"{line} {word}" if line else word
            if self.c.stringWidth(test, font, size) < max_w:
                line = test
            else:
                if line:
                    self.c.drawString(x, cy, line)
                    cy -= lh
                line = word
        if line:
            self.c.drawString(x, cy, line)
            cy -= lh
        return cy

    def step(self, x, y, num, title, desc, cr, cg, cb):
        self.rrect(x, y, 190, 12, 255, 255, 255, border=(cr, cg, cb))
        self.circle(x + 7, y + 6, 5, cr, cg, cb)
        self.c.setFillColorRGB(1, 1, 1)
        self.c.setFont(FB, 7)
        self.c.drawCentredString(x + 7, y + 4, str(num))
        self.txt(x + 16, y + 5, title, FB, 7.5, cr, cg, cb)
        self.wrap(x + 16, y + 0.5, desc, F, 6.5, *TEXT_GRAY, max_w=170, lh=3.5)
        return y - 14

    def new_page(self):
        if self.page > 0:
            self.c.showPage()
        self.page += 1
        self.bg(*BG)

    def footer(self):
        self.c.setFillColorRGB(0.4, 0.4, 0.6)
        self.c.setFont(F, 6)
        self.c.drawCentredString(W / 2, 8, f"@codesergo | стр. {self.page}")


def build(pdf):
    # ============ SLIDE 1: TITLE ============
    pdf.new_page()
    pdf.circle(520, H - 100, 150, 61, 31, 168)
    pdf.c.setFillColorRGB(0.4, 0.4, 0.6)
    pdf.c.setFont(F, 9)
    pdf.c.drawString(M + 5, H - 50, "#vibe_coding")
    pdf.c.setFont(FB, 90)
    pdf.c.setFillColorRGB(1, 1, 1)
    pdf.c.drawString(M + 5, H - 140, "30")
    pdf.c.setFont(FB, 36)
    pdf.c.drawString(M + 130, H - 130, "DNEY")
    pdf.c.setFont(FB, 18)
    pdf.c.setFillColorRGB(*PURPLE_LT)
    pdf.c.drawString(M + 5, H - 170, "PO VAYBKODINGU")

    pdf.rrect(M + 5, H - 205, 140, 14, *PURPLE)
    pdf.txtc(M + 75, H - 202, "POLNYY KURS", FB, 10, *WHITE)

    feats = [
        "Sozvay prilozheniya s pomoshchyu I bez opyta",
        ">> Poshagovye instruktsii s kartinkami",
        ">> Prakticheskie zadaniya posle kazhdogo dnya",
        ">> Sovety i layfhaki ot praktika",
    ]
    cy = H - 225
    for i, f in enumerate(feats):
        pdf.txt(M + 5, cy, f, F, 9 if i == 0 else 8, *(WHITE if i == 0 else (153, 153, 187)))
        cy -= 14

    pdf.txt(M + 5, 30, "Telegram: @codesergo", F, 9, 119, 119, 170)
    pdf.footer()

    # ============ SLIDE 2: OB ETOM KURSE ============
    pdf.new_page()
    pdf.rrect(M, H - 50, W - 2 * M, 18, *PURPLE_BG)
    pdf.txtc(W / 2, H - 45, "OB ETOM KURSE", FB, 14, *WHITE)

    items = [
        ("30", "poshagovykh urokov", "Kazhdyy den - novaya tema", PURPLE),
        ("I", "Kartinki i skhemy", "Naglyadnye materialy", GREEN),
        ("V", "Prakticheskie zadaniya", "Posle kazhdogo uroka", RED),
        ("L", "Gotovye prompty", "Kollektsiya proverennykh", ORANGE),
    ]
    positions = [(M, H - 110), (105, H - 110), (M, H - 210), (105, H - 210)]

    for i, (icon, title, sub, col) in enumerate(items):
        cx, cy = positions[i]
        pdf.card(cx, cy, 90, 55)
        pdf.circle(cx + 15, cy + 40, 10, *col)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 8)
        pdf.c.drawCentredString(cx + 15, cy + 38, icon)
        pdf.txt(cx + 28, cy + 40, title, FB, 10, *TEXT_DARK)
        pdf.wrap(cx + 28, cy + 33, sub, F, 7, *TEXT_GRAY, max_w=55, lh=4)

    pdf.rrect(M, H - 280, W - 2 * M, 35, *TIP_BG, border=TIP_BORDER)
    pdf.txt(M + 10, H - 258, "Chto ponadobitsya:", FB, 9, *ACCENT)
    pdf.txt(M + 10, H - 270, "Kompyuter s internetom  |  Brauzer Chrome  |  30 dney po 1-2 chasa", F, 8, *TEXT_DARK)
    pdf.footer()

    # ============ SLIDE 3: CONTENTS ============
    pdf.new_page()
    pdf.rrect(M, H - 50, W - 2 * M, 18, *PURPLE_BG)
    pdf.txtc(W / 2, H - 45, "SODERZHANIE KURSA", FB, 14, *WHITE)

    sections = [
        ("01", "Znakomstvo s vaybkodingom", "Dni 1-7", PURPLE),
        ("02", "Instrumenty i tekhniki", "Dni 8-14", GREEN),
        ("03", "Pervyy real'nyy proekt", "Dni 15-21", RED),
        ("04", "Prodvintye tekhniki", "Dni 22-28", ORANGE),
        ("05", "Final: Itogi i plany", "Dni 29-30", TEAL),
    ]

    y = H - 85
    for num, title, days, col in sections:
        pdf.card(M, y, W - 2 * M, 24)
        pdf.rrect(M, y, 26, 24, *col)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 14)
        pdf.c.drawCentredString(M + 13, y + 6, num)
        pdf.txt(M + 35, y + 8, title, FB, 11, *TEXT_DARK)
        pdf.txtr(W - M - 5, y + 8, days, FB, 9, *col)
        y -= 30

    # ============ SLIDE 4: WEEK 1 DIVIDER ============
    pdf.new_page()
    pdf.circle(420, H - 80, 180, 61, 31, 168)
    pdf.c.setFillColorRGB(0.24, 0.19, 0.67)
    pdf.c.setFont(FB, 100)
    pdf.c.drawString(M + 10, H - 130, "01")
    pdf.rrect(M + 10, H - 200, 260, 18, *PURPLE)
    pdf.txtc(M + 140, H - 196, "ZNATOMSTVO S VAYBKODINGOM", FB, 14, *WHITE)
    pdf.txtc(M + 140, H - 225, "Dni 1-7  |  7 urokov", F, 11, 153, 153, 204)

    days = [
        "D.1: Chto takoe vaybkoding", "D.2: Kak I ponimaet tebya",
        "D.3: Pervye shagi v Cursor", "D.4: Cursor vs Windsurf vs Replit",
        "D.5: Claude vs ChatGPT vs Gemini", "D.6: v0.dev - generatsiya interfeysov",
        "D.7: Nastrojka rabochego mesta"
    ]
    y = H - 280
    for i, d in enumerate(days):
        col = i % 2 == 0
        dx = M if col else 105
        dy = y - (i // 2) * 20
        pdf.rrect(dx, dy, 90, 16, 34, 24, 85, border=PURPLE)
        pdf.txt(dx + 5, dy + 5, d, F, 7, 204, 204, 238)
    pdf.footer()

    # ============ SLIDE 5: DAY 1 ============
    pdf.new_page()
    pdf.rrect(M, H - 40, 90, 12, *PURPLE)
    pdf.txtc(M + 45, H - 38, "N1 -> D1", FB, 7, *WHITE)
    pdf.txt(M + 5, H - 65, "Chto takoe vaybkoding?", FB, 20, *WHITE)
    pdf.txt(M + 5, H - 80, "Segodnya razberomsya, pochemu mir interesuyetsya vaybkodingom!", F, 9, 153, 153, 187)

    pdf.card(M, H - 155, 90, 55)
    pdf.txt(M + 8, H - 115, "Prostymi slovami", FB, 10, *ACCENT)
    simple = [
        "Govorish' chto hochesh' - I pishet kod",
        "NE NUZHNO znat' programmirovanie",
        "Kak zakaz v restorane",
    ]
    for i, t in enumerate(simple):
        pdf.txt(M + 8, H - 128 - i * 12, ">>  " + t, F, 7, *TEXT_DARK)

    pdf.card(M, H - 220, 90, 50)
    pdf.txt(M + 8, H - 182, "Pochemu eto kruto?", FB, 10, *ACCENT)
    why = [
        "Lyuboy mozhet sozdat' prilozhenie za chas",
        "Stoimost' razrabotki padayet v 100 raz",
        "Proekty dostupny kazhdomy",
    ]
    for i, t in enumerate(why):
        pdf.txt(M + 8, H - 195 - i * 11, ">>  " + t, F, 7, *TEXT_DARK)

    pdf.card(105, H - 155, 90, 80)
    pdf.txt(113, H - 115, "Poshagovaya instruktsiya", FB, 10, *ACCENT)
    steps = [
        ("1", "Skachay Cursor", "cursor.com -> Download"),
        ("2", "Sozday akkaunt", "Sign Up -> GitHub"),
        ("3", "Sozday papku", "Novaya papka -> Moy_proekt"),
        ("4", "Otkroy proekt", "File -> Open Folder"),
    ]
    sy = H - 130
    for n, t, s in steps:
        pdf.circle(113, sy + 3, 5, *PURPLE)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 6)
        pdf.c.drawCentredString(113, sy + 1, n)
        pdf.txt(122, sy + 3, t, FB, 7.5, *TEXT_DARK)
        pdf.txt(122, sy - 3, s, F, 6, *TEXT_GRAY)
        sy -= 18

    pdf.rrect(M, 28, W - 2 * M, 14, *TIP_BG, border=TIP_BORDER)
    pdf.txt(M + 8, 31, "Ne boysya eksperimentirovat'! Vaybkoding - eto praktika!", F, 8, *ACCENT)
    pdf.footer()

    # ============ SLIDE 6: DAY 2 ============
    pdf.new_page()
    pdf.rrect(M, H - 40, 90, 12, *PURPLE)
    pdf.txtc(M + 45, H - 38, "N1 -> D2", FB, 7, *WHITE)
    pdf.txt(M + 5, H - 65, "Kak I ponimaet tebya", FB, 20, *WHITE)
    pdf.txt(M + 5, H - 80, "I - modeli obucheny na millionakh strok - oni ponimayut kontekst!", F, 9, 153, 153, 187)

    pdf.card(M, H - 155, 90, 55)
    pdf.txt(M + 8, H - 115, "Kak rabotaet I", FB, 10, *ACCENT)
    for i, t in enumerate([
        "Claude, ChatGPT obucheny na mln strok",
        "Ponimayut chto knopka = HTML + CSS",
        "Luchshe opisanie - tochniy rezul'tat"
    ]):
        pdf.txt(M + 8, H - 128 - i * 12, ">>  " + t, F, 7, *TEXT_DARK)

    pdf.card(M, H - 220, 90, 50)
    pdf.txt(M + 8, H - 182, "Formula prompta", FB, 10, *ACCENT)
    for i, t in enumerate([
        "Konkretika: synya knopka 120x40",
        "Kontekst: dlya React + Tailwind",
        "Primery: pokazhi kak dolzhno vyglyadet'"
    ]):
        pdf.txt(M + 8, H - 195 - i * 11, ">>  " + t, F, 7, *TEXT_DARK)

    pdf.card(105, H - 155, 90, 70)
    pdf.txt(113, H - 115, "Poshagovaya instruktsiya", FB, 10, *ACCENT)
    steps = [
        ("1", "Plokhoy prompt", "Sdelay knopku - I ne znaet tsvet", RED),
        ("2", "Khoroshiy prompt", "Synya knopka 120x40, tekst Otvavit'", ORANGE),
        ("3", "Otlichnyy prompt", "Dlya React: fioletovaya, hover", GREEN),
    ]
    sy = H - 130
    for n, t, s, col in steps:
        pdf.circle(113, sy + 3, 5, *col)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 6)
        pdf.c.drawCentredString(113, sy + 1, n)
        pdf.txt(122, sy + 3, t, FB, 7.5, *TEXT_DARK)
        pdf.txt(122, sy - 3, s, F, 6, *TEXT_GRAY)
        sy -= 18

    pdf.rrect(M, 28, W - 2 * M, 14, *TIP_BG, border=TIP_BORDER)
    pdf.txt(M + 8, 31, "Sokhranyay udachnye prompty v fail prompts.md!", F, 8, *ACCENT)
    pdf.footer()

    # ============ SLIDE 7: DAY 3 ============
    pdf.new_page()
    pdf.rrect(M, H - 40, 90, 12, *PURPLE)
    pdf.txtc(M + 45, H - 38, "N1 -> D3", FB, 7, *WHITE)
    pdf.txt(M + 5, H - 65, "Pervye shagi v Cursor", FB, 20, *WHITE)
    pdf.txt(M + 5, H - 80, "Cursor - moshchnyy redaktor so vstroyennym I. Segodnya sozdash' sayt!", F, 9, 153, 153, 187)

    pdf.card(M, H - 155, 90, 55)
    pdf.txt(M + 8, H - 115, "Chto takoe Cursor", FB, 10, *ACCENT)
    for i, t in enumerate([
        "Redaktor koda so vstroyennym I",
        "Ponimayet ves' proekt celikom",
        "Sozdayet faily, pishet kod"
    ]):
        pdf.txt(M + 8, H - 128 - i * 12, ">>  " + t, F, 7, *TEXT_DARK)

    pdf.card(105, H - 155, 90, 85)
    pdf.txt(113, H - 115, "Poshagovaya instruktsiya", FB, 10, *ACCENT)
    steps = [
        ("1", "Otkroy Cursor", "Zapusti programm"),
        ("2", "Sozday fail", "File -> New File -> index.html"),
        ("3", "Otkroy I", "Ctrl+L (Cmd+L na Mac)"),
        ("4", "Napishi prompt", "Sozday stranitsu Privet mir"),
        ("5", "Primeni", "Nazhmi Apply"),
        ("6", "Zapusti!", "Otkroy v brauzere"),
    ]
    sy = H - 130
    for n, t, s in steps:
        pdf.circle(113, sy + 3, 4, *PURPLE)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 5)
        pdf.c.drawCentredString(113, sy + 1, n)
        pdf.txt(120, sy + 3, t, FB, 7, *TEXT_DARK)
        pdf.txt(120, sy - 2, s, F, 5.5, *TEXT_GRAY)
        sy -= 13

    pdf.card(M, H - 230, 90, 50, border=GREEN)
    pdf.txt(M + 8, H - 192, "Pozdravlyayu!", FB, 10, *GREEN)
    pdf.wrap(M + 8, H - 202, "Ty sozdal svoyu pervuyu stranicu s pomoshch'yu I!", F, 7, *TEXT_DARK, max_w=75)

    pdf.rrect(M, 28, W - 2 * M, 14, *TIP_BG, border=TIP_BORDER)
    pdf.txt(M + 8, 31, "Fail index.html - etot tvoy pervyy proekt!", F, 8, *ACCENT)
    pdf.footer()

    # ============ SLIDE 8: DAY 4 ============
    pdf.new_page()
    pdf.rrect(M, H - 40, 90, 12, *PURPLE)
    pdf.txtc(M + 45, H - 38, "N1 -> D4", FB, 7, *WHITE)
    pdf.txt(M + 5, H - 65, "Cursor vs Windsurf vs Replit", FB, 20, *WHITE)
    pdf.txt(M + 5, H - 80, "Sravnim instrumenty, chtoby ty vybral luchshiy!", F, 9, 153, 153, 187)

    tools = [
        ("Cursor", "Rekomenduetsya", "Korol' redaktorov. Vstroyennyy I", PURPLE),
        ("Windsurf", "Eksperiment", "Drugie I-modeli, podkhod", GREEN),
        ("Replit", "Onlayn", "V brauzere, bez ustanovki", RED),
    ]
    for i, (name, tag, desc, col) in enumerate(tools):
        x = M + i * 64
        pdf.card(x, H - 195, 58, 75)
        pdf.circle(x + 29, H - 165, 12, *col)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 8)
        pdf.c.drawCentredString(x + 29, H - 167, name[0])
        pdf.txtc(x + 29, H - 145, name, FB, 12, *TEXT_DARK)
        pdf.rrect(x + 5, H - 165, 48, 8, *col)
        pdf.txtc(x + 29, H - 164, tag, FB, 6, *WHITE)
        pdf.wrap(x + 3, H - 185, desc, F, 7, *TEXT_GRAY, max_w=52, lh=4)

    pdf.rrect(M, 28, W - 2 * M, 14, *TIP_BG, border=TIP_BORDER)
    pdf.txt(M + 8, 31, "Nachni s Cursor - on samyy udobnyy!", F, 8, *ACCENT)
    pdf.footer()

    # ============ SLIDE 9: DAY 5 ============
    pdf.new_page()
    pdf.rrect(M, H - 40, 90, 12, *PURPLE)
    pdf.txtc(M + 45, H - 38, "N1 -> D5", FB, 7, *WHITE)
    pdf.txt(M + 5, H - 65, "Claude vs ChatGPT vs Gemini", FB, 20, *WHITE)
    pdf.txt(M + 5, H - 80, "Vyberem luchshego I-assistenta dlya vaybkodinga!", F, 9, 153, 153, 187)

    ais = [
        ("Claude", "Luchshiy dlya koda", "Ponimaet kontekst, otlichnaya generatsiya", PURPLE, True),
        ("ChatGPT", "Universal'nyy", "Khorosh dlya ob'yasneniy", GREEN, False),
        ("Gemini", "Bystryy", "Rabotaet s Google-servisami", RED, False),
    ]
    for i, (name, best, desc, col, rec) in enumerate(ais):
        x = M + i * 64
        pdf.card(x, H - 195, 58, 75, border=(col if rec else BORDER))
        if rec:
            pdf.rrect(x + 5, H - 148, 48, 8, *col)
            pdf.txtc(x + 29, H - 147, "REKOMENDUETSYA", FB, 5, *WHITE)
        pdf.circle(x + 29, H - 175, 12, *col)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 8)
        pdf.c.drawCentredString(x + 29, H - 177, name[0])
        pdf.txtc(x + 29, H - 155, name, FB, 12, *TEXT_DARK)
        pdf.rrect(x + 5, H - 165, 48, 8, *col)
        pdf.txtc(x + 29, H - 164, best, FB, 5, *WHITE)
        pdf.wrap(x + 3, H - 185, desc, F, 7, *TEXT_GRAY, max_w=52, lh=4)

    pdf.rrect(M, 28, W - 2 * M, 14, *TIP_BG, border=TIP_BORDER)
    pdf.txt(M + 8, 31, "Rekomendatsiya: Claude - luchshiy dlya vaybkodinga!", F, 8, *ACCENT)
    pdf.footer()

    # ============ SLIDE 10: WEEK 2 DIVIDER ============
    pdf.new_page()
    pdf.circle(420, H - 80, 180, 26, 92, 58)
    pdf.c.setFillColorRGB(0.1, 0.36, 0.24)
    pdf.c.setFont(FB, 100)
    pdf.c.drawString(M + 10, H - 130, "02")
    pdf.rrect(M + 10, H - 200, 260, 18, *GREEN)
    pdf.txtc(M + 140, H - 196, "INSTRUMENTY I TEKHIRIKI", FB, 14, *WHITE)
    pdf.txtc(M + 140, H - 225, "Dni 8-14  |  7 urokov", F, 11, 153, 204, 170)

    days2 = [
        "D.8: Planirovanie proekta", "D.9: Pervyy komponent",
        "D.10: Sborka za chas", "D.11: Prompt-inzhiniring",
        "D.12: Prodvinutyy prompt", "D.13: Rabota s API",
        "D.14: Bazy dannykh"
    ]
    y = H - 280
    for i, d in enumerate(days2):
        col = i % 2 == 0
        dx = M if col else 105
        dy = y - (i // 2) * 20
        pdf.rrect(dx, dy, 90, 16, 15, 61, 36, border=GREEN)
        pdf.txt(dx + 5, dy + 5, d, F, 7, 153, 221, 170)
    pdf.footer()

    # ============ SLIDE 11: DAY 11 ============
    pdf.new_page()
    pdf.rrect(M, H - 40, 95, 12, *PURPLE)
    pdf.txtc(M + 47, H - 38, "N2 -> D11", FB, 7, *WHITE)
    pdf.txt(M + 5, H - 65, "Prompt-inzhiniring: osnovy", FB, 20, *WHITE)
    pdf.txt(M + 5, H - 80, "Prompt - instruktsiya dlya I. Ot kachestva zavisit rezul'tat!", F, 9, 153, 153, 187)

    rules = [
        ("1", "Konkretika", "Synya knopka 120x40", PURPLE),
        ("2", "Kontekst", "Dlya React + Tailwind", RED),
        ("3", "Primery", "Pokazhi kak dolzhno byt'", GREEN),
        ("4", "Format", "Verni React-komponent", ORANGE),
    ]
    for i, (num, rule, ex, col) in enumerate(rules):
        x = M + (i % 2) * 98
        y = H - 140 - (i // 2) * 65
        pdf.card(x, y, 90, 55)
        pdf.circle(x + 15, y + 38, 10, *col)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 10)
        pdf.c.drawCentredString(x + 15, y + 35, num)
        pdf.txt(x + 28, y + 38, rule, FB, 11, *TEXT_DARK)
        pdf.txt(x + 28, y + 30, ex, F, 8, *col)
        pdf.txt(x + 8, y + 12, f'"{ex}"', F, 7, *TEXT_GRAY)

    pdf.rrect(M, 28, W - 2 * M, 14, *TIP_BG, border=TIP_BORDER)
    pdf.txt(M + 8, 31, "Formula: Rol' + Zadacha + Kontekst + Ogranicheniya", FB, 8, *ACCENT)
    pdf.footer()

    # ============ SLIDE 12: WEEK 3 DIVIDER ============
    pdf.new_page()
    pdf.circle(420, H - 80, 180, 108, 21, 21)
    pdf.c.setFillColorRGB(0.42, 0.08, 0.08)
    pdf.c.setFont(FB, 100)
    pdf.c.drawString(M + 10, H - 130, "03")
    pdf.rrect(M + 10, H - 200, 260, 18, *RED)
    pdf.txtc(M + 140, H - 196, "PERVYY REAL'NYY PROEKT", FB, 14, *WHITE)
    pdf.txtc(M + 140, H - 225, "Dni 15-21  |  7 urokov", F, 11, 255, 170, 170)

    days3 = [
        "D.15: Avtorizatsiya", "D.16: Deploy bez DevOps",
        "D.17: Domain i SSL", "D.18: Monetizatsiya",
        "D.19: SaaS za den'", "D.20: Telegram-bot",
        "D.21: Prodazhi i marketing"
    ]
    y = H - 280
    for i, d in enumerate(days3):
        col = i % 2 == 0
        dx = M if col else 105
        dy = y - (i // 2) * 20
        pdf.rrect(dx, dy, 90, 16, 61, 15, 15, border=RED)
        pdf.txt(dx + 5, dy + 5, d, F, 7, 255, 170, 170)
    pdf.footer()

    # ============ SLIDE 13: DAY 18 ============
    pdf.new_page()
    pdf.rrect(M, H - 40, 95, 12, *PURPLE)
    pdf.txtc(M + 47, H - 38, "N3 -> D18", FB, 7, *WHITE)
    pdf.txt(M + 5, H - 65, "Kak monetizirovat' navyki", FB, 20, *WHITE)
    pdf.txt(M + 5, H - 80, "Vaybkoding - ne khobbi. Segodnya razberem zarabotok!", F, 9, 153, 153, 187)

    ways = [
        ("Frilans", "Sayty na zakaz", "15-50 tys. rub.", PURPLE),
        ("SaaS", "Servis s podpiskoy", "Passivnyy dokhod", GREEN),
        ("Marketpleysy", "Shablony i pluginy", "Gotovye produkty", RED),
        ("Obuchenie", "Kursy, kanal", "Obuchay drugikh", ORANGE),
    ]
    for i, (name, desc, money, col) in enumerate(ways):
        x = M + (i % 2) * 98
        y = H - 140 - (i // 2) * 65
        pdf.card(x, y, 90, 55)
        pdf.circle(x + 15, y + 38, 10, *col)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 8)
        pdf.c.drawCentredString(x + 15, y + 36, name[0])
        pdf.txt(x + 28, y + 38, name, FB, 10, *TEXT_DARK)
        pdf.txt(x + 28, y + 30, desc, F, 7, *TEXT_GRAY)
        pdf.rrect(x + 28, y + 15, 55, 8, *col)
        pdf.txtc(x + 55, y + 16, money, FB, 6, *WHITE)

    pdf.rrect(M, 28, W - 2 * M, 14, *TIP_BG, border=TIP_BORDER)
    pdf.txt(M + 8, 31, "Vaybkoder mozhet zarabatyvat' 100-300 tys. rub./mes!", FB, 8, *ACCENT)
    pdf.footer()

    # ============ SLIDE 14: WEEK 4 DIVIDER ============
    pdf.new_page()
    pdf.circle(420, H - 80, 180, 122, 80, 0)
    pdf.c.setFillColorRGB(0.48, 0.31, 0.06)
    pdf.c.setFont(FB, 100)
    pdf.c.drawString(M + 10, H - 130, "04")
    pdf.rrect(M + 10, H - 200, 260, 18, *ORANGE)
    pdf.txtc(M + 140, H - 196, "PRODVINTYE TEKHNIKI", FB, 14, *WHITE)
    pdf.txtc(M + 140, H - 225, "Dni 22-28  |  7 urokov", F, 11, 255, 221, 170)

    days4 = [
        "D.22: Obzor instrumentov", "D.23: Optimizatsiya",
        "D.24: Bezopasnost'", "D.25: Testirovanie",
        "D.26: Masshtabirovanie", "D.27: Soobshchestvo",
        "D.28: Portfoliyo"
    ]
    y = H - 280
    for i, d in enumerate(days4):
        col = i % 2 == 0
        dx = M if col else 105
        dy = y - (i // 2) * 20
        pdf.rrect(dx, dy, 90, 16, 61, 40, 0, border=ORANGE)
        pdf.txt(dx + 5, dy + 5, d, F, 7, 255, 221, 170)
    pdf.footer()

    # ============ SLIDE 15: DAY 28 ============
    pdf.new_page()
    pdf.rrect(M, H - 40, 95, 12, *PURPLE)
    pdf.txtc(M + 47, H - 38, "N4 -> D28", FB, 7, *WHITE)
    pdf.txt(M + 5, H - 65, "Portfoliyo", FB, 20, *WHITE)
    pdf.txt(M + 5, H - 80, "Portfoliyo - tvoya vitrina dlya klientov i rabotodateley!", F, 9, 153, 153, 187)

    pdf.card(M, H - 155, 90, 55)
    pdf.txt(M + 8, H - 115, "Kak sozdat'", FB, 10, *ACCENT)
    for i, t in enumerate([
        "Personal'nyy sayt s proektami",
        "Skrinshoty i demo-ssylki",
        "3 sil'nykh proekta luchshe 10"
    ]):
        pdf.txt(M + 8, H - 128 - i * 12, ">>  " + t, F, 7, *TEXT_DARK)

    pdf.card(105, H - 155, 90, 80)
    pdf.txt(113, H - 115, "Poshagovaya instruktsiya", FB, 10, *ACCENT)
    steps = [
        ("1", "Sozday sayt", "Skazhi Claude: Sozday portfoliyo"),
        ("2", "Opihi proekty", "Chto delaet, tekhnologii"),
        ("3", "Zadeploy", "Vlozhi na Vercel"),
        ("4", "Rasskazhi", "Telegram, LinkedIn, GitHub"),
    ]
    sy = H - 130
    for n, t, s in steps:
        pdf.circle(113, sy + 3, 5, *PURPLE)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 6)
        pdf.c.drawCentredString(113, sy + 1, n)
        pdf.txt(122, sy + 3, t, FB, 7.5, *TEXT_DARK)
        pdf.txt(122, sy - 3, s, F, 6, *TEXT_GRAY)
        sy -= 18

    pdf.card(M, H - 230, 90, 50, border=ORANGE)
    pdf.txt(M + 8, H - 192, "Portfoliyo - samyy tsennyy aktiv!", FB, 9, *ORANGE)
    pdf.wrap(M + 8, H - 202, "Imenno portfoliyo prineset pervykh klientov.", F, 7, *TEXT_DARK, max_w=75)

    pdf.rrect(M, 28, W - 2 * M, 14, *TIP_BG, border=TIP_BORDER)
    pdf.txt(M + 8, 31, "Portfoliyo - tvoya vizitnaya kartochka!", FB, 8, *ACCENT)
    pdf.footer()

    # ============ SLIDE 16: FINALE ============
    pdf.new_page()
    pdf.circle(400, H - 60, 200, 61, 31, 168)
    pdf.rrect(M, H - 50, W - 2 * M, 18, *PURPLE_BG)
    pdf.txtc(W / 2, H - 45, "DEN' 30 - FINAL", FB, 14, *WHITE)

    pdf.txtc(W / 2, H - 120, "POZDRAVLYAEM!", FB, 32, *WHITE)
    pdf.txtc(W / 2, H - 150, "Ty proshel ves' 30-dnevnyy kurs! Neveroyatnoye dostizheniye!", F, 10, 204, 204, 238)

    pdf.card(M, H - 270, 90, 70)
    pdf.txt(M + 8, H - 215, "Chto osvoeno:", FB, 10, *ACCENT)
    mastered = ["Cursor - I", "Claude - I", "v0.dev - UI",
                "Prompt-inzhiniring", "API", "Bazy dannykh",
                "Deploy", "Monetizatsiya"]
    for i, m in enumerate(mastered):
        col = i % 2 == 0
        dx = M + 8 if col else M + 48
        dy = H - 228 - (i // 2) * 10
        pdf.txt(dx, dy, "V  " + m, F, 7, *TEXT_DARK)

    pdf.card(105, H - 270, 90, 70)
    pdf.txt(113, H - 215, "Sleduyushchie shagi:", FB, 10, *ACCENT)
    next_steps = [
        "Pervyy proekt",
        "Telegram-bot",
        "Frilans",
        "Svoy kurs!"
    ]
    for i, s in enumerate(next_steps):
        pdf.txt(113, H - 228 - i * 12, "->  " + s, F, 8, *TEXT_DARK)

    pdf.rrect(M, 28, W - 2 * M, 12, *PURPLE)
    pdf.txtc(W / 2, 31, "Telegram: @codesergo  |  GitHub: github.com/codesergo  |  codesergo.com", F, 7, *WHITE)
    pdf.footer()


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vaybkoding_30_dney.pdf")
    pdf = PDF(path)
    build(pdf)
    pdf.save()
    print(f"PDF создан: {path}")

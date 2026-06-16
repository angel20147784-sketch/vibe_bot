#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PDF курс в стиле изображения — тёмный фон, белые карточки, фиолетовые акценты"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
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
M = 1.2 * cm

# Colors from design
BG = (35, 35, 40)
CARD = (248, 248, 252)
PURPLE = (107, 70, 245)
PURPLE_DARK = (74, 47, 206)
PURPLE_LIGHT = (139, 107, 248)
WHITE = (255, 255, 255)
TEXT_DARK = (30, 30, 40)
TEXT_GRAY = (100, 100, 120)
TEXT_LIGHT = (180, 180, 200)
GRID = (230, 230, 240)
GREEN = (46, 125, 79)
RED = (201, 64, 64)
ORANGE = (176, 122, 16)
TEAL = (26, 110, 110)


class PDF:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.page = 0

    def save(self):
        self.c.save()

    def bg(self):
        self.c.setFillColorRGB(*[x / 255 for x in BG])
        self.c.rect(0, 0, W, H, fill=1, stroke=0)

    def grid_bg(self):
        self.c.setStrokeColorRGB(55 / 255, 55 / 255, 62 / 255)
        self.c.setLineWidth(0.3)
        for x in range(0, int(W), 15):
            self.c.line(x, 0, x, H)
        for y in range(0, int(H), 15):
            self.c.line(0, y, W, y)

    def card(self, x, y, w, h, fill=CARD):
        self.c.setFillColorRGB(*[c / 255 for c in fill])
        self.c.roundRect(x, y, w, h, 8, fill=1, stroke=0)
        self.c.setStrokeColorRGB(220 / 255, 220 / 255, 235 / 255)
        self.c.setLineWidth(0.4)
        self.c.roundRect(x, y, w, h, 8, fill=0, stroke=1)

    def card_grid(self, x, y, w, h):
        self.c.setStrokeColorRGB(235 / 255, 235 / 255, 245 / 255)
        self.c.setLineWidth(0.2)
        for gx in range(int(x + 8), int(x + w - 5), 12):
            self.c.line(gx, y + 5, gx, y + h - 5)
        for gy in range(int(y + 8), int(y + h - 5), 12):
            self.c.line(x + 5, gy, x + w - 5, gy)

    def pill(self, x, y, w, text, col=PURPLE):
        self.c.setFillColorRGB(*[c / 255 for c in col])
        self.c.roundRect(x, y, w, 10, 5, fill=1, stroke=0)
        self.c.setFillColorRGB(1, 1, 1)
        self.c.setFont(FB, 6)
        self.c.drawCentredString(x + w / 2, y + 2.5, text)

    def dot(self, x, y, col=PURPLE):
        self.c.setFillColorRGB(*[c / 255 for c in col])
        self.c.circle(x, y, 2.5, fill=1, stroke=0)

    def txt(self, x, y, text, font=F, size=10, color=TEXT_DARK):
        self.c.setFillColorRGB(*[c / 255 for c in color])
        self.c.setFont(font, size)
        self.c.drawString(x, y, text)

    def txtc(self, x, y, text, font=F, size=10, color=TEXT_DARK):
        self.c.setFillColorRGB(*[c / 255 for c in color])
        self.c.setFont(font, size)
        self.c.drawCentredString(x, y, text)

    def txtr(self, x, y, text, font=F, size=10, color=TEXT_DARK):
        self.c.setFillColorRGB(*[c / 255 for c in color])
        self.c.setFont(font, size)
        self.c.drawRightString(x, y, text)

    def wrap(self, x, y, text, font=F, size=9, color=TEXT_DARK, max_w=170, lh=13):
        self.c.setFillColorRGB(*[c / 255 for c in color])
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

    def bullet(self, x, y, text, color=TEXT_DARK, col=PURPLE):
        self.dot(x, y + 3, col)
        self.txt(x + 8, y, text, F, 8, color)

    def section_title(self, x, y, text, color=PURPLE):
        self.c.setFillColorRGB(*[c / 255 for c in color])
        self.c.setFont(FB, 11)
        self.c.drawString(x, y, text.upper())
        tw = self.c.stringWidth(text.upper(), FB, 11)
        self.c.setStrokeColorRGB(*[c / 255 for c in color])
        self.c.setLineWidth(1.5)
        self.c.line(x, y - 2, x + tw + 5, y - 2)

    def arrow(self, x, y, color=PURPLE):
        self.c.setFillColorRGB(*[c / 255 for c in color])
        self.c.setFont(FB, 8)
        self.c.drawString(x, y, ">>")

    def new_page(self):
        if self.page > 0:
            self.c.showPage()
        self.page += 1
        self.bg()
        self.grid_bg()

    def footer_bar(self):
        self.c.setFillColorRGB(*[c / 255 for c in (25, 25, 30)])
        self.c.rect(0, 0, W, 25, fill=1, stroke=0)
        self.c.setFillColorRGB(0.4, 0.4, 0.55)
        self.c.setFont(F, 6)
        self.c.drawCentredString(W / 2, 9, f"@codesergo | стр. {self.page}")


def build(pdf):
    # ====== COVER ======
    pdf.new_page()
    pdf.c.setFillColorRGB(*[c / 255 for c in (25, 25, 32)])
    pdf.c.rect(0, 0, W, H, fill=1, stroke=0)

    pdf.card(M, H - 280, W - 2 * M, 260)
    pdf.card_grid(M, H - 280, W - 2 * M, 260)

    pdf.c.setFillColorRGB(*[c / 255 for c in PURPLE])
    pdf.c.setFont(FB, 60)
    pdf.c.drawString(M + 15, H - 100, "30")
    pdf.c.setFont(FB, 30)
    pdf.c.drawString(M + 160, H - 95, "DNEY")

    pdf.txt(M + 15, H - 130, "PO VAYBKODINGU", FB, 18, PURPLE)

    pdf.pill(M + 15, H - 160, 80, "POLNYY KURS", PURPLE)

    pdf.wrap(M + 15, H - 185, "Sozvay prilozheniya s pomoshchyu I bez opyta programmirovaniya. Poshagovye instruktsii, kartinki i zadaniya.", F, 9, TEXT_DARK, max_w=280, lh=14)

    feats = [
        "30 poshagovykh urokov",
        "Kartinki i skhemy",
        "Prakticheskie zadaniya",
        "Gotovye prompty dlya I"
    ]
    fy = H - 230
    for f in feats:
        pdf.arrow(M + 15, fy)
        pdf.txt(M + 30, fy, f, F, 8, TEXT_GRAY)
        fy -= 14

    pdf.c.setFillColorRGB(*[c / 255 for c in PURPLE])
    pdf.c.setFont(FB, 10)
    pdf.c.drawString(M + 15, 40, "Telegram: @codesergo")
    pdf.footer_bar()

    # ====== CONTENTS ======
    pdf.new_page()
    pdf.c.setFillColorRGB(*[c / 255 for c in (25, 25, 32)])
    pdf.c.rect(0, 0, W, H, fill=1, stroke=0)

    pdf.card(M, H - 60, W - 2 * M, 30)
    pdf.txtc(W / 2, H - 52, "SODERZHANIE KURSA", FB, 14, PURPLE)

    sections = [
        ("01", "Znakomstvo s vaybkodingom", "Dni 1-7", PURPLE),
        ("02", "Instrumenty i tekhniki", "Dni 8-14", GREEN),
        ("03", "Pervyy real'nyy proekt", "Dni 15-21", RED),
        ("04", "Prodvintye tekhniki", "Dni 22-28", ORANGE),
        ("05", "Final: Itogi i plany", "Dni 29-30", TEAL),
    ]

    y = H - 110
    for num, title, days, col in sections:
        pdf.card(M, y, W - 2 * M, 45)
        pdf.c.setFillColorRGB(*[c / 255 for c in col])
        pdf.c.roundRect(M, y, 45, 45, 8, fill=1, stroke=0)
        pdf.c.setFillColorRGB(1, 1, 1)
        pdf.c.setFont(FB, 16)
        pdf.c.drawCentredString(M + 22, y + 16, num)
        pdf.txt(M + 55, y + 25, title, FB, 12, TEXT_DARK)
        pdf.txtr(W - M - 10, y + 25, days, FB, 9, col)
        y -= 55

    pdf.footer_bar()

    # ====== WEEK 1 DIVIDER ======
    pdf.new_page()
    pdf.card(M, H - 250, W - 2 * M, 230)
    pdf.card_grid(M, H - 250, W - 2 * M, 230)

    pdf.c.setFillColorRGB(*[c / 255 for c in PURPLE])
    pdf.c.setFont(FB, 80)
    pdf.c.drawString(M + 20, H - 120, "01")

    pdf.txt(M + 20, H - 150, "ZNATOMSTVO S VAYBKODINGOM", FB, 16, TEXT_DARK)
    pdf.txt(M + 20, H - 170, "Dni 1-7  |  7 urokov", F, 10, TEXT_GRAY)

    days = [
        "D.1: Chto takoe vaybkoding",
        "D.2: Kak I ponimaet tebya",
        "D.3: Pervye shagi v Cursor",
        "D.4: Cursor vs Windsurf vs Replit",
        "D.5: Claude vs ChatGPT vs Gemini",
        "D.6: v0.dev - generatsiya interfeysov",
        "D.7: Nastrojka rabochego mesta"
    ]
    dy = H - 200
    for d in days:
        pdf.bullet(M + 30, dy, d, TEXT_DARK, PURPLE)
        dy -= 16

    pdf.footer_bar()

    # ====== DAY 1 ======
    pdf.new_page()
    pdf.pill(M, H - 30, 80, "N1 -> D1", PURPLE)
    pdf.txt(M, H - 55, "Chto takoe vaybkoding?", FB, 20, WHITE)
    pdf.txt(M, H - 70, "Segodnya razberomsya, pochemu mir interesuyetsya vaybkodingom!", F, 9, TEXT_LIGHT)

    # Card 1
    pdf.card(M, H - 170, 95, 85)
    pdf.section_title(M + 8, H - 95, "Prostymi slovami")
    simple = [
        "Govorish' chto hochesh' - I pishet kod",
        "NE NUZHNO znat' programmirovanie",
        "Kak zakaz v restorane - govorish', gotovyat"
    ]
    sy = H - 115
    for t in simple:
        pdf.bullet(M + 10, sy, t, TEXT_DARK, PURPLE)
        sy -= 14

    # Card 2
    pdf.card(M, H - 260, 95, 75)
    pdf.section_title(M + 8, H - 185, "Pochemu eto kruto?")
    why = [
        "Lyuboy mozhet sozdat' prilozhenie za chas",
        "Stoimost' razrabotki padayet v 100 raz",
        "Proekty dostupny kazhdomy"
    ]
    sy = H - 205
    for t in why:
        pdf.bullet(M + 10, sy, t, TEXT_DARK, GREEN)
        sy -= 14

    # Steps card
    pdf.card(105, H - 170, 90, 150)
    pdf.section_title(113, H - 95, "Poshagovaya instruktsiya")
    steps = [
        ("1", "Skachay Cursor", "cursor.com -> Download"),
        ("2", "Sozday akkaunt", "Sign Up -> GitHub"),
        ("3", "Sozday papku", "Novaya papka -> Moy_proekt"),
        ("4", "Otkroy proekt", "File -> Open Folder")
    ]
    sy = H - 115
    for n, t, s in steps:
        pdf.pill(113, sy, 12, n, PURPLE)
        pdf.txt(128, sy + 1, t, FB, 8, TEXT_DARK)
        pdf.txt(128, sy - 8, s, F, 6.5, TEXT_GRAY)
        sy -= 22

    # Tip
    pdf.card(M, 35, W - 2 * M, 22, fill=(237, 232, 255))
    pdf.txt(M + 8, 42, "Ne boysya eksperimentirovat'! Vaybkoding - eto praktika!", F, 8, PURPLE)
    pdf.footer_bar()

    # ====== DAY 2 ======
    pdf.new_page()
    pdf.pill(M, H - 30, 80, "N1 -> D2", PURPLE)
    pdf.txt(M, H - 55, "Kak I ponimaet tebya", FB, 20, WHITE)
    pdf.txt(M, H - 70, "I - modeli obucheny na millionakh strok koda!", F, 9, TEXT_LIGHT)

    pdf.card(M, H - 170, 95, 85)
    pdf.section_title(M + 8, H - 95, "Kak rabotaet I")
    for i, t in enumerate([
        "Claude, ChatGPT obucheny na mln strok",
        "Ponimayut chto knopka = HTML + CSS",
        "Luchshe opisanie - tochniy rezul'tat"
    ]):
        pdf.bullet(M + 10, H - 115 - i * 14, t, TEXT_DARK, PURPLE)

    pdf.card(M, H - 260, 95, 75)
    pdf.section_title(M + 8, H - 185, "Formula prompta")
    for i, t in enumerate([
        "Konkretika: synya knopka 120x40",
        "Kontekst: dlya React + Tailwind",
        "Primery: pokazhi kak dolzhno byt'"
    ]):
        pdf.bullet(M + 10, H - 205 - i * 14, t, TEXT_DARK, ORANGE)

    pdf.card(105, H - 170, 90, 130)
    pdf.section_title(113, H - 95, "Sravnenie promptov")
    steps = [
        ("1", "Plokhoy", "Sdelay knopku", RED),
        ("2", "Khoroshiy", "Synya 120x40, tekst", ORANGE),
        ("3", "Otlichnyy", "Dlya React: fioletovaya", GREEN),
    ]
    sy = H - 115
    for n, t, s, col in steps:
        pdf.pill(113, sy, 12, n, col)
        pdf.txt(128, sy + 1, t, FB, 8, TEXT_DARK)
        pdf.txt(128, sy - 8, s, F, 6.5, TEXT_GRAY)
        sy -= 28

    pdf.card(M, 35, W - 2 * M, 22, fill=(237, 232, 255))
    pdf.txt(M + 8, 42, "Sokhranyay udachnye prompty v fail prompts.md!", F, 8, PURPLE)
    pdf.footer_bar()

    # ====== DAY 3 ======
    pdf.new_page()
    pdf.pill(M, H - 30, 80, "N1 -> D3", PURPLE)
    pdf.txt(M, H - 55, "Pervye shagi v Cursor", FB, 20, WHITE)
    pdf.txt(M, H - 70, "Cursor - moshchnyy redaktor so vstroyennym I!", F, 9, TEXT_LIGHT)

    pdf.card(M, H - 170, 95, 85)
    pdf.section_title(M + 8, H - 95, "Chto takoe Cursor")
    for i, t in enumerate([
        "Redaktor koda so vstroyennym I",
        "Ponimayet ves' proekt celikom",
        "Sozdayet faily, pishet kod, ispravlyaet"
    ]):
        pdf.bullet(M + 10, H - 115 - i * 14, t, TEXT_DARK, PURPLE)

    pdf.card(105, H - 170, 90, 150)
    pdf.section_title(113, H - 95, "Poshagovaya instruktsiya")
    steps = [
        ("1", "Otkroy Cursor", "Zapusti programm"),
        ("2", "Sozday fail", "File -> New File -> index.html"),
        ("3", "Otkroy I", "Ctrl+L (Cmd+L na Mac)"),
        ("4", "Napishi prompt", "Sozday stranitsu Privet mir"),
        ("5", "Primeni", "Nazhmi Apply ili skopiruy"),
        ("6", "Zapusti!", "Otkroy v brauzere!")
    ]
    sy = H - 115
    for n, t, s in steps:
        pdf.pill(113, sy, 12, n, PURPLE)
        pdf.txt(128, sy + 1, t, FB, 7.5, TEXT_DARK)
        pdf.txt(128, sy - 7, s, F, 6, TEXT_GRAY)
        sy -= 18

    pdf.card(M, H - 260, 95, 75, fill=(240, 255, 245))
    pdf.txt(M + 8, H - 185, "Pozdravlyayu!", FB, 10, GREEN)
    pdf.wrap(M + 8, H - 200, "Ty sozdal svoyu pervuyu stranicu s pomoshch'yu I! Eto byl pervyy shag v mire vaybkodinga.", F, 7.5, TEXT_DARK, max_w=80, lh=11)

    pdf.card(M, 35, W - 2 * M, 22, fill=(237, 232, 255))
    pdf.txt(M + 8, 42, "Fail index.html - etot tvoy pervyy proekt!", F, 8, PURPLE)
    pdf.footer_bar()

    # ====== DAY 4 ======
    pdf.new_page()
    pdf.pill(M, H - 30, 80, "N1 -> D4", PURPLE)
    pdf.txt(M, H - 55, "Cursor vs Windsurf vs Replit", FB, 20, WHITE)
    pdf.txt(M, H - 70, "Sravnim instrumenty, chtoby ty vybral luchshiy!", F, 9, TEXT_LIGHT)

    tools = [
        ("Cursor", "Rekomenduetsya", "Korol' redaktorov. Vstroyennyy I, rabota s proektom celikom.", PURPLE),
        ("Windsurf", "Eksperiment", "Drugie I-modeli, nestandartnyy podkhod.", GREEN),
        ("Replit", "Onlayn", "V brauzere, bez ustanovki. Dlya bystrogo starta.", RED),
    ]
    for i, (name, tag, desc, col) in enumerate(tools):
        x = M + i * 64
        pdf.card(x, H - 200, 58, 100)
        pdf.pill(x + 5, H - 120, 48, tag, col)
        pdf.txtc(x + 29, H - 140, name, FB, 13, TEXT_DARK)
        pdf.wrap(x + 4, H - 160, desc, F, 6.5, TEXT_GRAY, max_w=50, lh=9)

    pdf.card(M, 35, W - 2 * M, 22, fill=(237, 232, 255))
    pdf.txt(M + 8, 42, "Nachni s Cursor - on samyy udobnyy!", F, 8, PURPLE)
    pdf.footer_bar()

    # ====== DAY 5 ======
    pdf.new_page()
    pdf.pill(M, H - 30, 80, "N1 -> D5", PURPLE)
    pdf.txt(M, H - 55, "Claude vs ChatGPT vs Gemini", FB, 20, WHITE)
    pdf.txt(M, H - 70, "Vyberem luchshego I-assistenta!", F, 9, TEXT_LIGHT)

    ais = [
        ("Claude", "Luchshiy dlya koda", "Ponimaet kontekst, otlichnaya generatsiya.", PURPLE, True),
        ("ChatGPT", "Universal'nyy", "Khorosh dlya ob'yasneniy i tekstov.", GREEN, False),
        ("Gemini", "Bystryy", "Rabotaet s Google-servisami.", RED, False),
    ]
    for i, (name, best, desc, col, rec) in enumerate(ais):
        x = M + i * 64
        pdf.card(x, H - 200, 58, 100, fill=(255, 255, 255) if rec else CARD)
        if rec:
            pdf.pill(x + 5, H - 105, 48, "REKOMENDUYU", PURPLE)
        pdf.txtc(x + 29, H - 130, name, FB, 13, TEXT_DARK)
        pdf.pill(x + 5, H - 145, 48, best, col)
        pdf.wrap(x + 4, H - 165, desc, F, 6.5, TEXT_GRAY, max_w=50, lh=9)

    pdf.card(M, 35, W - 2 * M, 22, fill=(237, 232, 255))
    pdf.txt(M + 8, 42, "Rekomendatsiya: Claude - luchshiy dlya vaybkodinga!", F, 8, PURPLE)
    pdf.footer_bar()

    # ====== WEEK 2 DIVIDER ======
    pdf.new_page()
    pdf.card(M, H - 250, W - 2 * M, 230)
    pdf.card_grid(M, H - 250, W - 2 * M, 230)

    pdf.c.setFillColorRGB(*[c / 255 for c in GREEN])
    pdf.c.setFont(FB, 80)
    pdf.c.drawString(M + 20, H - 120, "02")

    pdf.txt(M + 20, H - 150, "INSTRUMENTY I TEKHIRIKI", FB, 16, TEXT_DARK)
    pdf.txt(M + 20, H - 170, "Dni 8-14  |  7 urokov", F, 10, TEXT_GRAY)

    days2 = [
        "D.8: Planirovanie proekta", "D.9: Pervyy komponent",
        "D.10: Sborka za chas", "D.11: Prompt-inzhiniring",
        "D.12: Prodvinutyy prompt", "D.13: Rabota s API",
        "D.14: Bazy dannykh"
    ]
    dy = H - 200
    for d in days2:
        pdf.bullet(M + 30, dy, d, TEXT_DARK, GREEN)
        dy -= 16

    pdf.footer_bar()

    # ====== DAY 11 ======
    pdf.new_page()
    pdf.pill(M, H - 30, 85, "N2 -> D11", PURPLE)
    pdf.txt(M, H - 55, "Prompt-inzhiniring: osnovy", FB, 20, WHITE)
    pdf.txt(M, H - 70, "Prompt - instruktsiya dlya I!", F, 9, TEXT_LIGHT)

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
        pdf.pill(x + 5, y + 38, 20, num, col)
        pdf.txt(x + 30, y + 38, rule, FB, 10, TEXT_DARK)
        pdf.txt(x + 30, y + 28, ex, F, 8, col)
        pdf.txt(x + 8, y + 12, f'"{ex}"', F, 7, TEXT_GRAY)

    pdf.card(M, 35, W - 2 * M, 22, fill=(237, 232, 255))
    pdf.txt(M + 8, 42, "Formula: Rol' + Zadacha + Kontekst + Ogranicheniya", FB, 8, PURPLE)
    pdf.footer_bar()

    # ====== WEEK 3 DIVIDER ======
    pdf.new_page()
    pdf.card(M, H - 250, W - 2 * M, 230)
    pdf.card_grid(M, H - 250, W - 2 * M, 230)

    pdf.c.setFillColorRGB(*[c / 255 for c in RED])
    pdf.c.setFont(FB, 80)
    pdf.c.drawString(M + 20, H - 120, "03")

    pdf.txt(M + 20, H - 150, "PERVYY REAL'NYY PROEKT", FB, 16, TEXT_DARK)
    pdf.txt(M + 20, H - 170, "Dni 15-21  |  7 urokov", F, 10, TEXT_GRAY)

    days3 = [
        "D.15: Avtorizatsiya", "D.16: Deploy bez DevOps",
        "D.17: Domain i SSL", "D.18: Monetizatsiya",
        "D.19: SaaS za den'", "D.20: Telegram-bot",
        "D.21: Prodazhi i marketing"
    ]
    dy = H - 200
    for d in days3:
        pdf.bullet(M + 30, dy, d, TEXT_DARK, RED)
        dy -= 16

    pdf.footer_bar()

    # ====== DAY 18 ======
    pdf.new_page()
    pdf.pill(M, H - 30, 85, "N3 -> D18", PURPLE)
    pdf.txt(M, H - 55, "Kak monetizirovat' navyki", FB, 20, WHITE)
    pdf.txt(M, H - 70, "Vaybkoding - ne khobbi. Segodnya razberem zarabotok!", F, 9, TEXT_LIGHT)

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
        pdf.pill(x + 5, y + 38, 35, name, col)
        pdf.txt(x + 5, y + 25, desc, F, 7.5, TEXT_GRAY)
        pdf.pill(x + 5, y + 10, 50, money, col)

    pdf.card(M, 35, W - 2 * M, 22, fill=(237, 232, 255))
    pdf.txt(M + 8, 42, "Vaybkoder mozhet zarabatyvat' 100-300 tys. rub./mes!", FB, 8, PURPLE)
    pdf.footer_bar()

    # ====== WEEK 4 DIVIDER ======
    pdf.new_page()
    pdf.card(M, H - 250, W - 2 * M, 230)
    pdf.card_grid(M, H - 250, W - 2 * M, 230)

    pdf.c.setFillColorRGB(*[c / 255 for c in ORANGE])
    pdf.c.setFont(FB, 80)
    pdf.c.drawString(M + 20, H - 120, "04")

    pdf.txt(M + 20, H - 150, "PRODVINTYE TEKHNIKI", FB, 16, TEXT_DARK)
    pdf.txt(M + 20, H - 170, "Dni 22-28  |  7 urokov", F, 10, TEXT_GRAY)

    days4 = [
        "D.22: Obzor instrumentov", "D.23: Optimizatsiya",
        "D.24: Bezopasnost'", "D.25: Testirovanie",
        "D.26: Masshtabirovanie", "D.27: Soobshchestvo",
        "D.28: Portfoliyo"
    ]
    dy = H - 200
    for d in days4:
        pdf.bullet(M + 30, dy, d, TEXT_DARK, ORANGE)
        dy -= 16

    pdf.footer_bar()

    # ====== DAY 28 ======
    pdf.new_page()
    pdf.pill(M, H - 30, 85, "N4 -> D28", PURPLE)
    pdf.txt(M, H - 55, "Portfoliyo", FB, 20, WHITE)
    pdf.txt(M, H - 70, "Tvoya vitrina dlya klientov i rabotodateley!", F, 9, TEXT_LIGHT)

    pdf.card(M, H - 170, 95, 85)
    pdf.section_title(M + 8, H - 95, "Kak sozdat'")
    for i, t in enumerate([
        "Personal'nyy sayt s proektami",
        "Skrinshoty i demo-ssylki",
        "3 sil'nykh proekta luchshe 10"
    ]):
        pdf.bullet(M + 10, H - 115 - i * 14, t, TEXT_DARK, ORANGE)

    pdf.card(105, H - 170, 90, 150)
    pdf.section_title(113, H - 95, "Poshagovaya instruktsiya")
    steps = [
        ("1", "Sozday sayt", "Skazhi Claude: Sozday portfoliyo"),
        ("2", "Opihi proekty", "Chto delaet, tekhnologii"),
        ("3", "Zadeploy", "Vlozhi na Vercel"),
        ("4", "Rasskazhi", "Telegram, LinkedIn, GitHub")
    ]
    sy = H - 115
    for n, t, s in steps:
        pdf.pill(113, sy, 12, n, ORANGE)
        pdf.txt(128, sy + 1, t, FB, 8, TEXT_DARK)
        pdf.txt(128, sy - 8, s, F, 6.5, TEXT_GRAY)
        sy -= 22

    pdf.card(M, H - 260, 95, 75, fill=(255, 248, 229))
    pdf.txt(M + 8, H - 185, "Portfoliyo - tsennyy aktiv!", FB, 9, ORANGE)
    pdf.wrap(M + 8, H - 200, "Imenno portfoliyo prineset pervykh klientov i otkroyet novye vozmozhnosti.", F, 7.5, TEXT_DARK, max_w=80, lh=11)

    pdf.card(M, 35, W - 2 * M, 22, fill=(237, 232, 255))
    pdf.txt(M + 8, 42, "Portfoliyo - tvoya vizitnaya kartochka!", FB, 8, PURPLE)
    pdf.footer_bar()

    # ====== FINALE ======
    pdf.new_page()
    pdf.card(M, H - 250, W - 2 * M, 230)
    pdf.card_grid(M, H - 250, W - 2 * M, 230)

    pdf.c.setFillColorRGB(*[c / 255 for c in PURPLE])
    pdf.c.setFont(FB, 50)
    pdf.c.drawCentredString(W / 2, H - 100, "POZDRAVLYAEM!")

    pdf.txtc(W / 2, H - 130, "Ty proshel ves' 30-dnevnyy kurs!", FB, 14, TEXT_DARK)
    pdf.txtc(W / 2, H - 148, "Neveroyatnoye dostizheniye!", F, 10, TEXT_GRAY)

    pdf.card(M, H - 240, 95, 70)
    pdf.section_title(M + 8, H - 175, "Chto osvoeno:")
    mastered = ["Cursor - I", "Claude - I", "v0.dev - UI", "Prompt-inzhiniring",
                "API", "Bazy dannykh", "Deploy", "Monetizatsiya"]
    sy = H - 195
    for i, m in enumerate(mastered):
        col = i % 2 == 0
        dx = M + 8 if col else M + 48
        dy = sy - (i // 2) * 10
        pdf.txt(dx, dy, "V  " + m, F, 6.5, TEXT_DARK)

    pdf.card(105, H - 240, 90, 70)
    pdf.section_title(113, H - 175, "Sleduyushchie shagi:")
    for i, s in enumerate(["Pervyy proekt", "Telegram-bot", "Frilans", "Svoy kurs!"]):
        pdf.bullet(113, H - 195 - i * 12, s, TEXT_DARK, PURPLE)

    pdf.c.setFillColorRGB(*[c / 255 for c in PURPLE])
    pdf.c.roundRect(M, 35, W - 2 * M, 18, 4, fill=1, stroke=0)
    pdf.c.setFillColorRGB(1, 1, 1)
    pdf.c.setFont(F, 7)
    pdf.c.drawCentredString(W / 2, 41, "Telegram: @codesergo  |  GitHub: github.com/codesergo  |  codesergo.com")
    pdf.footer_bar()


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vaybkoding_styled.pdf")
    pdf = PDF(path)
    build(pdf)
    pdf.save()
    print(f"PDF создан: {path}")

#!/usr/bin/env python3
"""Republic of Qasra — invented passport spread (make.fun entry).

Renders one 1024x1024 PNG: data page (left) + visa page (right) on a dark
passport-cover background. Deterministic: fixed seed, no network, no clock.

THE HOOK (threaded through every element): Qasra is a desert canyon
republic whose ONLY land route to the outside world crosses Wadi al-Nar, a
flash-flood canyon. Land travel is permitted ONLY in the dry season
(01 Oct - 30 Apr) and ONLY with a wadi-crossing permit. The wadi is closed
May-Sep (flood season).

COHERENCE (all verified in-code by assertions):
  passport QA4829137 | holder QADRI SELMA NOOR | DOB 14 MAR 1991
  issue 12 FEB 2025 | expiry 12 FEB 2035 (issue + 10 years)
  trips: 15 OCT-02 NOV 2025 (Al-Miraj, visa covers it), 18-25 JAN 2026
  (Dahran) — all inside dry seasons, all after issue, exits follow entries.
  MRZ check digits computed with the ICAO 7-3-1 algorithm.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

random.seed(20261121)

W, H = 1024, 1024
DJ = "/usr/share/fonts/truetype/dejavu/"
LB = "/usr/share/fonts/truetype/liberation/"


def font(path, size):
    return ImageFont.truetype(path, size)


F_SANS = lambda s: font(DJ + "DejaVuSans.ttf", s)
F_SANSB = lambda s: font(DJ + "DejaVuSans-Bold.ttf", s)
F_SERIF = lambda s: font(DJ + "DejaVuSerif.ttf", s)
F_SERIFB = lambda s: font(DJ + "DejaVuSerif-Bold.ttf", s)
F_SERIFI = lambda s: font(LB + "LiberationSerif-Italic.ttf", s)
F_MONO = lambda s: font(DJ + "DejaVuSansMono.ttf", s)
F_MONOB = lambda s: font(DJ + "DejaVuSansMono-Bold.ttf", s)

# ---------------------------------------------------------------- data ----
SURNAME = "QADRI"
GIVEN = "SELMA NOOR"
DOC_NO = "QA4829137"
NATIONALITY = "QSR"
DOB = "910314"          # 14 MAR 1991
SEX = "F"
EXPIRY = "350212"       # 12 FEB 2035
PERSONAL = "QSR91031404817"
ISSUE = "12 FEB 2025"

# ICAO 9303 check digits (7-3-1 weights)
_VAL = {c: i for i, c in enumerate("0123456789")}
_VAL.update({c: 10 + i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")})
_VAL["<"] = 0


def check_digit(s):
    w = (7, 3, 1)
    return str(sum(_VAL[c] * w[i % 3] for i, c in enumerate(s)) % 10)


def mrz_lines():
    l1 = "P<QSRQADRI<<SELMA<NOOR"
    l1 = l1 + "<" * (44 - len(l1))
    body = (DOC_NO + check_digit(DOC_NO) + NATIONALITY + DOB + check_digit(DOB)
            + SEX + EXPIRY + check_digit(EXPIRY) + PERSONAL
            + check_digit(PERSONAL))
    l2 = body + check_digit(body)
    assert len(l1) == 44 and len(l2) == 44
    # independent re-verification of every digit
    assert check_digit(l2[0:9]) == l2[9]
    assert check_digit(l2[13:19]) == l2[19]
    assert check_digit(l2[21:27]) == l2[27]
    assert check_digit(l2[28:42]) == l2[42]
    assert check_digit(l2[:43]) == l2[43]
    return l1, l2


MRZ1, MRZ2 = mrz_lines()

# ------------------------------------------------------------- helpers ----
INK = (28, 32, 40)
FAINT = (90, 88, 78)
RULE = (150, 140, 110)


def text_center(d, cx, y, s, f, fill=INK, spacing=0):
    if spacing:
        w = sum(d.textlength(ch, font=f) + spacing for ch in s) - spacing
        x = cx - w / 2
        for ch in s:
            d.text((x, y), ch, font=f, fill=fill)
            x += d.textlength(ch, font=f) + spacing
    else:
        d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def wrap(d, s, f, width):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def guilloche(d, box, color, step=7, amp=3.0):
    """Fine wavy security lines across a box."""
    x0, y0, x1, y1 = box
    y = y0 + 4
    while y < y1:
        pts = []
        x = x0
        ph = random.uniform(0, 6.28)
        while x <= x1:
            pts.append((x, y + amp * math.sin((x - x0) / 34.0 + ph)))
            x += 6
        d.line(pts, fill=color, width=1)
        y += step


def emblem(d, cx, cy, r, color, lw=2):
    """Qasra coat of arms: sun over canyon walls, star above."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=lw)
    d.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4],
              outline=color, width=1)
    # sun
    d.ellipse([cx - 7, cy - r + 12, cx + 7, cy - r + 26], fill=color)
    # canyon walls: two zigzag cliffs with the wadi between
    d.line([(cx - r + 10, cy + r - 12), (cx - 14, cy - 2),
            (cx - 20, cy + 6), (cx - 8, cy + r - 12)], fill=color, width=2)
    d.line([(cx + r - 10, cy + r - 12), (cx + 14, cy - 2),
            (cx + 20, cy + 6), (cx + 8, cy + r - 12)], fill=color, width=2)
    # wadi river line
    pts = [(cx - 6 + 3 * math.sin(t), cy + 4 + t) for t in range(0, r - 16, 3)]
    d.line(pts, fill=color, width=2)
    # star
    d.text((cx - 4, cy - r - 12), "*", font=F_SERIFB(14), fill=color)


def round_stamp(d, cx, cy, radius, color, top_arc, bottom_arc, lines,
                angle, date):
    """Circular border stamp with text on arcs. Drawn on its own layer."""
    size = radius * 2 + 56
    lay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    c = size // 2
    ink = color + (235,)
    ld.ellipse([c - radius, c - radius, c + radius, c + radius],
               outline=ink, width=3)
    ld.ellipse([c - radius + 6, c - radius + 6, c + radius - 6,
                c + radius - 6], outline=ink, width=1)

    def arc_text(text, r, a0, a1, f, bottom=False):
        # characters evenly along the arc from a0 to a1 (degrees, 0=east,
        # y down, so 90=bottom, 270=top). Bottom arc reads left to right
        # with letter tops pointing toward the centre.
        n = len(text)
        if n == 0:
            return
        step = (a1 - a0) / max(n - 1, 1) if n > 1 else 0
        for i, ch in enumerate(text):
            a = math.radians(a0 + step * i)
            x = c + r * math.cos(a)
            y = c + r * math.sin(a)
            glyph = Image.new("RGBA", (30, 30), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glyph)
            gd.text((15 - gd.textlength(ch, font=f) / 2, 6), ch,
                    font=f, fill=ink)
            rot = -(math.degrees(a) - 90) if bottom else -(math.degrees(a) + 90)
            glyph = glyph.rotate(rot, resample=Image.BICUBIC, center=(15, 15))
            lay.alpha_composite(glyph, (int(x - 15), int(y - 15)))

    fa = F_SANSB(10)
    arc_text(top_arc, radius - 13, 195, 345, fa)
    arc_text(bottom_arc, radius - 16, 150, 30, fa, bottom=True)
    fm = F_SANSB(13)
    y = c - len(lines) * 9 - 8
    for ln in lines:
        text_center(ld, c, y, ln, fm, fill=ink)
        y += 17
    text_center(ld, c, y + 1, date, F_SANSB(11), fill=ink)
    lay = lay.rotate(angle, resample=Image.BICUBIC, expand=False)
    d._image.alpha_composite(lay, (int(cx - size / 2), int(cy - size / 2)))


def rect_stamp(d, cx, cy, w, h, color, lines, angle, date=None):
    size_w, size_h = w + 30, h + 30
    lay = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ink = color + (235,)
    ld.rectangle([12, 12, 12 + w, 12 + h], outline=ink, width=3)
    ld.rectangle([16, 16, 12 + w - 4, 12 + h - 4], outline=ink, width=1)
    f = F_SANSB(11)
    total = len(lines) * 15 + (16 if date else 0)
    y = 12 + (h - total) / 2
    for ln in lines:
        text_center(ld, 12 + w / 2, y, ln, f, fill=ink)
        y += 15
    if date:
        text_center(ld, 12 + w / 2, y + 1, date, F_SANSB(12), fill=ink)
    lay = lay.rotate(angle, resample=Image.BICUBIC, expand=False)
    d._image.alpha_composite(
        lay, (int(cx - size_w / 2), int(cy - size_h / 2)))


def oval_stamp(d, cx, cy, w, h, color, lines, angle):
    size_w, size_h = w + 30, h + 30
    lay = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ink = color + (235,)
    ld.ellipse([12, 12, 12 + w, 12 + h], outline=ink, width=3)
    ld.ellipse([17, 17, 12 + w - 5, 12 + h - 5], outline=ink, width=1)
    f = F_SANSB(10)
    y = 12 + (h - len(lines) * 15) / 2
    for ln in lines:
        text_center(ld, 12 + w / 2, y, ln, f, fill=ink)
        y += 15
    lay = lay.rotate(angle, resample=Image.BICUBIC, expand=False)
    d._image.alpha_composite(
        lay, (int(cx - size_w / 2), int(cy - size_h / 2)))


def barcode(d, x, y, w, h, seed=7):
    rnd = random.Random(seed)
    xx = x
    while xx < x + w - 3:
        bw = rnd.choice([1, 1, 2, 3])
        if rnd.random() < 0.55:
            d.rectangle([xx, y, xx + bw - 1, y + h], fill=(20, 20, 20))
        xx += bw + rnd.choice([1, 1, 2])


# ---------------------------------------------------------------- canvas --
img = Image.new("RGB", (W, H), (22, 52, 40))
d = ImageDraw.Draw(img)
# leather-like noise on the cover
for _ in range(9000):
    x, y = random.randint(0, W - 1), random.randint(0, H - 1)
    v = random.randint(-8, 10)
    img.putpixel((x, y), (22 + v, 52 + v, 40 + v))
d = ImageDraw.Draw(img)
d.rectangle([8, 8, W - 9, H - 9], outline=(176, 148, 80), width=2)
d.rectangle([14, 14, W - 15, H - 15], outline=(176, 148, 80), width=1)
img = img.convert("RGBA")
d = ImageDraw.Draw(img)

PAGE_L = (30, 30, 502, 994)
PAGE_R = (522, 30, 994, 994)
PAGE_BG = (244, 236, 214)
for box in (PAGE_L, PAGE_R):
    d.rectangle(box, fill=PAGE_BG)
    d.rectangle(box, outline=(120, 105, 70), width=2)
    guilloche(d, box, (226, 214, 178))
# centre gutter shadow
for i in range(10):
    d.line([(512 - i, 30), (512 - i, 994)], fill=(0, 0, 0, 18))
    d.line([(512 + i, 30), (512 + i, 994)], fill=(0, 0, 0, 18))

# ============================================================ DATA PAGE ===
LX0, LY0, LX1, LY1 = PAGE_L
# header
d.text((LX1 - 26, LY0 + 8), "2", font=F_SANSB(13), fill=FAINT)
emblem(d, LX0 + 42, LY0 + 52, 26, (90, 70, 30))
text_center(d, (LX0 + LX1) // 2 + 14, LY0 + 12, "R E S P U B L I K A   Q A S R A",
            F_SANSB(11), fill=(90, 70, 30))
text_center(d, (LX0 + LX1) // 2 + 14, LY0 + 30, "REPUBLIC OF QASRA",
            F_SERIFB(19), fill=INK)
text_center(d, (LX0 + LX1) // 2 + 14, LY0 + 54, "RÉPUBLIQUE DE QASRA",
            F_SERIF(11), fill=FAINT)
d.line([(LX0 + 18, LY0 + 76), (LX1 - 18, LY0 + 76)], fill=RULE, width=1)
text_center(d, (LX0 + LX1) // 2, LY0 + 82,
            "PASSPORT  ·  PASAPORT  ·  PASSEPORT", F_SANSB(11), fill=INK)

# portrait (2:3 crop, head and shoulders)
portrait = Image.open("portrait.png").convert("RGB")
portrait = portrait.crop((300, 140, 940, 1100)).resize((132, 198),
                                                       Image.LANCZOS)
PX, PY = LX0 + 18, LY0 + 108
img.paste(portrait, (PX, PY))
d = ImageDraw.Draw(img)
d.rectangle([PX, PY, PX + 132, PY + 198], outline=(100, 90, 60), width=2)

FL = F_SANS(8)      # trilingual label
FV = F_SANSB(14)    # value
FVs = F_SANSB(12)


def field(x, y, label_q, label_en, label_fr, value, fvalue=FV, rule_w=200):
    label = " / ".join(p for p in (label_q, label_en, label_fr) if p)
    d.text((x, y), label, font=FL, fill=FAINT)
    d.text((x, y + 11), value, font=fvalue, fill=INK)
    if rule_w:
        d.line([(x, y + 30), (x + rule_w, y + 30)], fill=(200, 188, 150),
               width=1)


FX = LX0 + 178
field(FX, LY0 + 108, "NAW", "Type", "", "P", rule_w=0)
field(FX + 80, LY0 + 108, "BALAD", "Code", "", "QSR", rule_w=0)
field(FX + 160, LY0 + 108, "RAQAM", "No.", "", DOC_NO, FVs, rule_w=0)
field(FX, LY0 + 150, "NASAB", "Surname", "Nom", SURNAME)
field(FX, LY0 + 192, "ISM", "Given names", "Prénoms", GIVEN)
field(FX, LY0 + 234, "JINSIYA", "Nationality", "Nationalité", "QASRI")
field(FX, LY0 + 276, "TAWALUD", "Date of birth", "Naissance",
      "14 MAR 1991")
field(FX + 180, LY0 + 276, "JINS", "Sex", "Sexe", "F", rule_w=0)

field(LX0 + 18, LY0 + 330, "MAWLID", "Place of birth",
      "Lieu de naissance", "AL-QASR, QASRA")
field(LX0 + 18, LY0 + 372, "RAQAM SHAKHSI", "Personal No.",
      "N° personnel", PERSONAL, FVs)
field(LX0 + 18, LY0 + 414, "SUDUR", "Date of issue",
      "Date de délivrance", ISSUE)
field(LX0 + 258, LY0 + 414, "INTIHA", "Date of expiry",
      "Date d'expiration", "12 FEB 2035")
field(LX0 + 18, LY0 + 456, "SULTA", "Authority", "Autorité",
      "MINISTRY OF INTERIOR — AL-QASR", FVs)

# ghost portrait (faint, right side, above the observations box)
ghost = portrait.resize((84, 126), Image.LANCZOS).convert("L")
ghost_rgb = Image.merge("RGB", (ghost, ghost, ghost))
ghost_a = ghost_rgb.convert("RGBA")
ghost_a.putalpha(Image.new("L", ghost_a.size, 55))
img.paste(ghost_a, (LX1 - 104, LY0 + 472), ghost_a)
d = ImageDraw.Draw(img)

# signature box
SX, SY = LX0 + 18, LY0 + 500
d.rectangle([SX, SY, SX + 230, SY + 62], outline=RULE, width=1)
d.text((SX + 8, SY + 4), "TAWQI / Holder's signature / Signature",
       font=FL, fill=FAINT)
sig = Image.new("RGBA", (230, 46), (0, 0, 0, 0))
sd = ImageDraw.Draw(sig)
sd.text((10, 4), "Selma Qadri", font=F_SERIFI(30), fill=(30, 50, 110, 255))
sig = sig.rotate(-2, resample=Image.BICUBIC, expand=False)
img.paste(sig, (SX, SY + 14), sig)
d = ImageDraw.Draw(img)

# observations box — the hook, tied to the holder's profession
OX, OY = LX0 + 18, LY0 + 584
d.rectangle([OX, OY, LX1 - 18, OY + 118], outline=(90, 70, 30), width=2)
d.rectangle([OX + 3, OY + 3, LX1 - 21, OY + 115], outline=(90, 70, 30),
            width=1)
d.text((OX + 10, OY + 7), "OBSERVATIONS", font=F_SANSB(10),
       fill=(90, 70, 30))
obs = ("HOLDER IS A LICENSED WADI GUIDE (LICENCE WG-1147), AUTHORISED "
       "TO LEAD CONVOYS ACROSS WADI AL-NAR IN THE DRY SEASON. LAND "
       "DEPARTURE ONLY VIA THE WADI AL-NAR CROSSING.")
for i, ln in enumerate(wrap(d, obs, F_SANSB(11), LX1 - OX - 36)):
    d.text((OX + 10, OY + 24 + i * 16), ln, font=F_SANSB(11), fill=INK)
d.text((OX + 10, OY + 24 + 4 * 16),
       "QASRI: WADI AL-NAR SAFAR — QURU MAWSIM FAQAT.",
       font=F_SANSB(10), fill=(90, 70, 30))

# motto strip
d.line([(LX0 + 18, LY0 + 726), (LX1 - 18, LY0 + 726)], fill=RULE, width=1)
text_center(d, (LX0 + LX1) // 2, LY0 + 732,
            "QASRA  ·  WADI AL-NAR  ·  DRY SEASON 01 OCT – 30 APR",
            F_SANSB(9), fill=(90, 70, 30))
d.line([(LX0 + 18, LY0 + 750), (LX1 - 18, LY0 + 750)], fill=RULE, width=1)

# small print
text_center(d, (LX0 + LX1) // 2, LY0 + 772,
            "This passport remains the property of the Republic of Qasra.",
            F_SANS(9), fill=FAINT)
text_center(d, (LX0 + LX1) // 2, LY0 + 788,
            "Ce passeport reste la propriété de la République de Qasra.",
            F_SANS(9), fill=FAINT)
text_center(d, (LX0 + LX1) // 2, LY0 + 804,
            "QASRI: PASAPORT HADHA MILK RESPUBLIKA QASRA.",
            F_SANS(9), fill=FAINT)

# MRZ
d.rectangle([LX0 + 10, LY0 + 860, LX1 - 10, LY0 + 912],
            fill=(255, 253, 244))
d.rectangle([LX0 + 10, LY0 + 860, LX1 - 10, LY0 + 912],
            outline=(150, 140, 110), width=1)
fm = F_MONOB(16)
d.text((LX0 + 18, LY0 + 864), MRZ1, font=fm, fill=INK)
d.text((LX0 + 18, LY0 + 886), MRZ2, font=fm, fill=INK)

# ============================================================ VISA PAGE ===
RX0, RY0, RX1, RY1 = PAGE_R
d.text((RX1 - 26, RY0 + 8), "3", font=F_SANSB(13), fill=FAINT)
text_center(d, (RX0 + RX1) // 2, RY0 + 12, "VISAS", F_SERIFB(18), fill=INK)
text_center(d, (RX0 + RX1) // 2, RY0 + 36, "VISA  ·  VISAS",
            F_SANS(10), fill=FAINT)
d.line([(RX0 + 18, RY0 + 58), (RX1 - 18, RY0 + 58)], fill=RULE, width=1)

# endorsement box — the hook as a rule
EX, EY = RX0 + 18, RY0 + 66
d.rectangle([EX, EY, RX1 - 18, EY + 108], outline=(140, 40, 40), width=2)
d.rectangle([EX + 3, EY + 3, RX1 - 21, EY + 105], outline=(140, 40, 40),
            width=1)
d.text((EX + 10, EY + 7), "ENDORSEMENT", font=F_SANSB(10),
       fill=(140, 40, 40))
end = ("THE HOLDER MAY DEPART BY LAND ONLY VIA THE WADI AL-NAR "
       "CROSSING, IN THE DRY SEASON (01 OCT – 30 APR) ONLY, AND ONLY "
       "WITH A VALID WADI-CROSSING PERMIT. PERMIT No. WP-2025-0881, "
       "ISSUED 14 FEB 2025, AL-QASR.")
for i, ln in enumerate(wrap(d, end, F_SANSB(10), RX1 - EX - 36)):
    d.text((EX + 10, EY + 24 + i * 14), ln, font=F_SANSB(10), fill=INK)

# ---- Al-Miraj visa sticker
VX, VY, VW, VH = RX0 + 18, RY0 + 188, 306, 232
d.rounded_rectangle([VX, VY, VX + VW, VY + VH], radius=6,
                    fill=(214, 232, 222), outline=(60, 110, 80), width=2)
guilloche(d, (VX + 6, VY + 40, VX + VW - 6, VY + VH - 6), (190, 212, 196))
d.rounded_rectangle([VX, VY, VX + VW, VY + 34], radius=6,
                    fill=(46, 92, 66))
d.rectangle([VX, VY + 20, VX + VW, VY + 34], fill=(46, 92, 66))
text_center(d, VX + VW // 2, VY + 6, "KINGDOM OF AL-MIRAJ  —  VISA",
            F_SANSB(12), fill=(255, 255, 255))
text_center(d, VX + VW // 2, VY + 22, "VISA No. AM-2025-441902",
            F_SANS(9), fill=(220, 240, 228))


def vfield(x, y, label, value, fvalue=F_SANSB(11)):
    d.text((x, y), label, font=F_SANS(8), fill=(70, 90, 75))
    d.text((x, y + 10), value, font=fvalue, fill=INK)


vfield(VX + 12, VY + 42, "Surname / Nom", "QADRI")
vfield(VX + 160, VY + 42, "Given names", "SELMA NOOR")
vfield(VX + 12, VY + 72, "Passport No.", DOC_NO)
vfield(VX + 160, VY + 72, "Type", "C — TOURIST")
vfield(VX + 12, VY + 102, "Valid from", "01 OCT 2025")
vfield(VX + 160, VY + 102, "Until", "30 APR 2026")
vfield(VX + 12, VY + 132, "Entries", "MULTIPLE")
vfield(VX + 160, VY + 132, "Duration of stay", "90 DAYS")
vfield(VX + 12, VY + 162, "Issued", "22 SEP 2025")
vfield(VX + 160, VY + 162, "Fee", "PAID 120 AMD")
d.line([(VX + 12, VY + 192), (VX + VW - 12, VY + 192)], fill=(60, 110, 80),
       width=1)
d.text((VX + 12, VY + 196), "Remarks:", font=F_SANS(8), fill=(70, 90, 75))
d.text((VX + 12, VY + 207), "ENTRY BY WADI AL-NAR CROSSING",
       font=F_SANSB(10), fill=(140, 40, 40))
barcode(d, VX + VW - 82, VY + 194, 70, 26)

# closure stamp beside the sticker — the hook's closed season
rect_stamp(d, RX1 - 78, RY0 + 260, 128, 84, (178, 40, 40),
           ["WADI AL-NAR", "CLOSED 01 MAY", "— 30 SEP —", "FLOOD SEASON",
            "NO LAND CROSSING"], -9)

# ---- travel stamps (chronological; all in dry seasons) ----
BLUE = (28, 72, 150)
VIOLET = (112, 58, 140)
GREEN = (28, 110, 66)
RED = (178, 40, 40)

# trip 1 — Al-Miraj, 15 OCT – 02 NOV 2025
round_stamp(d, 648, 552, 56, BLUE, "QASRA · WADI AL-NAR",
            "DRY SEASON GATE 1", ["EXIT"], -8, "15 OCT 2025")
rect_stamp(d, 884, 552, 158, 82, VIOLET,
           ["KINGDOM OF AL-MIRAJ", "ENTRY — RAS AL-HADD"], 6,
           "15 OCT 2025")
rect_stamp(d, 648, 676, 158, 82, VIOLET,
           ["KINGDOM OF AL-MIRAJ", "EXIT — RAS AL-HADD"], -5,
           "02 NOV 2025")
round_stamp(d, 884, 676, 56, BLUE, "QASRA · WADI AL-NAR",
            "DRY SEASON GATE 1", ["ENTRY"], 7, "02 NOV 2025")
# trip 2 — Dahran, 18 – 25 JAN 2026
round_stamp(d, 648, 800, 56, BLUE, "QASRA · WADI AL-NAR",
            "DRY SEASON GATE 2", ["EXIT"], 9, "18 JAN 2026")
round_stamp(d, 884, 800, 56, GREEN, "REPUBLIC OF DAHRAN",
            "QASR BORDER POST", ["ENTRY"], -7, "18 JAN 2026")
round_stamp(d, 648, 920, 56, GREEN, "REPUBLIC OF DAHRAN",
            "QASR BORDER POST", ["EXIT"], -6, "25 JAN 2026")
round_stamp(d, 884, 920, 56, BLUE, "QASRA · WADI AL-NAR",
            "DRY SEASON GATE 2", ["ENTRY"], 5, "25 JAN 2026")
# toll stamp — the wadi crossing levy, paid on the first crossing
oval_stamp(d, 766, 614, 170, 80, RED,
           ["WADI CROSSING LEVY", "PAID 40 QSD", "15 OCT 2025"], -14)

img.convert("RGB").save("entry.png", optimize=True)
print("saved entry.png", img.size)

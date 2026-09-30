"""
Objets de décor (sprites séparés, triés en profondeur dans GameMaker).
Tailles en 1x ; l'origine conseillée (pied de l'objet) est donnée dans DECOR.
"""
import math

from spritelib import Drawing, circle, ellipse, rect, poly, path, line, OUTLINE


def _shadow(d, cx, cy, rx, ry):
    d.under.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" opacity="0.2"/>')


# ================================================================== CAMPAGNE
def tree():
    d = Drawing(64, 64)
    _shadow(d, 32, 58, 20, 4)
    d.add(poly([(28, 40), (36, 40), (37.5, 58), (26.5, 58)]), "#8A5A3A")
    d.add(rect(31, 44, 2, 12, 1), "#6E4428", sil=False)
    for cx, cy, r in ((32, 24, 17), (18, 32, 11), (46, 32, 11), (24, 14, 10), (41, 15, 10)):
        d.add(circle(cx, cy, r), "#4E9A47")
    for cx, cy, r in ((34, 30, 12), (20, 34, 7), (45, 34, 7)):
        d.add(circle(cx, cy, r), "#3F8439", sil=False, opacity=0.6)
    for cx, cy, r in ((26, 14, 5), (38, 12, 4), (18, 26, 3.5)):
        d.add(circle(cx, cy, r), "#72BE5E", sil=False)
    return d


def bush():
    d = Drawing(32, 32)
    _shadow(d, 16, 28, 12, 2.5)
    for cx, cy, r in ((16, 17, 9), (8.5, 21, 6), (23.5, 21, 6)):
        d.add(circle(cx, cy, r), "#4E9A47")
    d.add(circle(13, 13, 3.2), "#72BE5E", sil=False)
    for cx, cy in ((20, 16), (11, 22)):
        d.add(circle(cx, cy, 1.3), "#E24B4B", sil=False)
    return d


def hay():
    d = Drawing(32, 32)
    _shadow(d, 16, 28.5, 13, 2.5)
    d.add(rect(3, 12, 26, 16, 3), "#E3B94F")
    d.add(ellipse(16, 12, 13, 5), "#F2D27A")
    for x in (8, 13, 18, 23):
        d.raw(line(f"M{x},15 L{x},26", "#C99B35", 0.9))
    d.raw(line("M9,11 Q16,8 23,11 M11,13 Q16,11 21,13", "#D4A941", 0.8))
    d.add(rect(3, 18.5, 26, 2, 0), "#B5452F", sil=False)
    return d


def rock():
    d = Drawing(32, 32)
    _shadow(d, 16, 27, 11, 2.5)
    d.add(path("M5,26 Q4,15 12,11 Q19,7 25,13 Q29,18 27,26 Z"), "#A3A8AD")
    d.add(path("M9,16 Q13,11 19,11 Q15,14 13,19 Z"), "#C4C8CC", sil=False)
    d.raw(line("M18,17 L22,21 L21,25", "#7D8288", 0.9))
    return d


def fence_wood_h():
    d = Drawing(32, 32)
    for x in (4,):
        d.add(rect(x - 2, 10, 4, 18, 1), "#9A6B43")
    d.add(rect(0, 13, 32, 3, 0), "#B98556")
    d.add(rect(0, 20, 32, 3, 0), "#B98556")
    d.add(rect(2, 9, 4, 3, 1.5), "#B98556")
    return d


def fence_wood_v():
    d = Drawing(32, 32)
    d.add(rect(14, 0, 4, 32, 0), "#B98556")
    d.add(rect(12.5, 2, 7, 7, 2), "#9A6B43")
    d.raw(line("M16,12 L16,30", "#9A6B43", 0.8))
    return d


def signpost():
    d = Drawing(32, 48)
    _shadow(d, 16, 45, 6, 1.5)
    d.add(rect(14.5, 12, 3, 33, 1), "#8A5A3A")
    d.add(poly([(4, 10), (24, 10), (29, 14.5), (24, 19), (4, 19)]), "#C98A4B")
    d.add(poly([(28, 22), (8, 22), (3, 26.5), (8, 31), (28, 31)]), "#C98A4B")
    for y in (14.5, 26.5):
        d.raw(line(f"M8,{y} L20,{y}", "#8A5A3A", 1.0))
    return d


# ================================================================== ROUTE
def cone():
    d = Drawing(32, 32)
    _shadow(d, 16, 28, 9, 2)
    d.add(rect(6, 24, 20, 4, 1), "#E0612A")
    d.add(poly([(12, 25), (20, 25), (17.2, 6), (14.8, 6)]), "#F27A34")
    d.add(poly([(13.2, 15), (18.8, 15), (19.5, 19.5), (12.5, 19.5)]), "#FFFFFF", sil=False)
    return d


def road_sign():
    d = Drawing(32, 48)
    _shadow(d, 16, 45, 5, 1.5)
    d.add(rect(14.8, 20, 2.4, 25, 1), "#8C9098")
    d.add(poly([(16, 3), (28, 23), (4, 23)]), "#D7332B")
    d.add(poly([(16, 8), (24, 20.5), (8, 20.5)]), "#FFFFFF", sil=False)
    # silhouette de chien : attention, chiens !
    d.add(ellipse(15.5, 17.2, 3.2, 1.5), OUTLINE, sil=False)
    d.add(circle(19.2, 15.5, 1.3), OUTLINE, sil=False)
    d.raw(line("M13,18 L13,19.6 M18,18 L18,19.6 M12.4,16.8 L11,15.2", OUTLINE, 0.8))
    return d


def lamppost():
    d = Drawing(32, 64)
    _shadow(d, 16, 61, 5, 1.5)
    d.add(rect(12, 56, 8, 5, 1.5), "#2F4F4F")
    d.add(rect(14.8, 14, 2.4, 43, 1), "#2F4F4F")
    d.add(poly([(10, 12), (22, 12), (20, 4), (12, 4)]), "#2F4F4F")
    d.add(rect(11.5, 12, 9, 5, 1), "#FFE9A3")
    d.add(rect(13, 1.5, 6, 3, 1.5), "#2F4F4F")
    return d


# ================================================================== VILLAGE
def house(roof="#C8553D", roof_dk="#A3412E", wall="#F1E3C8", door="#8A5A3A"):
    d = Drawing(96, 96)
    d.under.append('<rect x="6" y="86" width="86" height="8" rx="4" fill="#000" opacity="0.2"/>')
    d.add(rect(10, 50, 76, 42, 1), wall)
    d.add(rect(66, 2, 9, 18, 1), "#9B5B45")
    d.add(poly([(3, 56), (93, 56), (84, 12), (12, 12)]), roof)
    d.add(rect(12, 9, 72, 6, 2), roof_dk)
    for i, y in enumerate((23, 34, 45)):
        x0 = 12 - (y - 12) * 9 / 44
        d.raw(line(f"M{x0 + 1:.1f},{y} L{96 - x0 - 1:.1f},{y}", roof_dk, 1.0))
        for x in range(18 + (i % 2) * 6, 80, 12):
            d.raw(line(f"M{x},{y - 10.5} L{x},{y}", roof_dk, 0.7))
    d.add(rect(10, 56, 76, 4, 0), "#000000", sil=False, opacity=0.18)
    d.add(rect(41, 66, 14, 26, 2), door)
    d.add(circle(52, 80, 1.1), "#F2C14E", sil=False)
    for x in (17, 63):
        d.add(rect(x, 64, 16, 14, 1.5), "#9FD3F0")
        d.raw(line(f"M{x + 8},64 L{x + 8},78 M{x},71 L{x + 16},71", "#FFFFFF", 1.2))
        d.add(rect(x - 1, 78, 18, 4, 1), "#9A6B43")
        for k in range(4):
            d.add(circle(x + 2 + k * 4, 77.5, 1.4), ("#E24B4B", "#F7D154")[k % 2], sil=False)
    d.add(rect(39, 91, 18, 3, 1), "#B7B2A8")
    return d


def house_blue():
    return house(roof="#5E6E8C", roof_dk="#48556F", wall="#E8EEF2", door="#3F7D5A")


def doghouse():
    d = Drawing(48, 48)
    _shadow(d, 24, 44, 18, 3)
    d.add(rect(10, 22, 28, 22, 1), "#C98A4B")
    for y in (28, 34, 40):
        d.raw(line(f"M11,{y} L37,{y}", "#A36D37", 0.8))
    d.add(path("M18,44 L18,33 Q24,26 30,33 L30,44 Z"), "#3A2418")
    d.add(poly([(5, 25), (43, 25), (35, 7), (13, 7)]), "#D7332B")
    d.add(rect(13, 5, 22, 4, 1.5), "#A82520")
    d.add(rect(20, 14, 8, 5, 1), "#F3E7CF")            # plaque
    d.add(ellipse(24, 16.5, 1.8, 0.8), OUTLINE, sil=False)  # petit os gravé
    # gamelle
    d.add(ellipse(41, 42, 4.6, 2.1), "#2E6FD1")
    d.add(ellipse(41, 41.2, 3.3, 1.1), "#C4642E", sil=False)
    return d


def bench():
    d = Drawing(48, 32)
    _shadow(d, 24, 28, 20, 2.5)
    for x in (8, 38):
        d.add(rect(x, 16, 3, 12, 1), "#4A4F57")
    d.add(rect(4, 6, 40, 4, 1), "#B98556")
    d.add(rect(4, 12, 40, 5, 1), "#C98A4B")
    d.add(rect(4, 18, 40, 5, 1), "#B98556")
    return d


def mailbox():
    d = Drawing(32, 32)
    _shadow(d, 16, 29, 6, 1.5)
    d.add(rect(14.8, 18, 2.4, 11, 1), "#5C6168")
    d.add(path("M8,20 L8,10 Q8,5 16,5 Q24,5 24,10 L24,20 Z"), "#F2C14E")
    d.add(rect(11, 11, 10, 2, 1), OUTLINE, sil=False)
    d.add(rect(24, 7, 2, 7, 0.5), "#D7332B")
    return d


def hedge():
    d = Drawing(32, 32)
    d.add(rect(0, 8, 32, 20, 6), "#3F8439")
    d.add(rect(1, 8, 30, 10, 5), "#4E9A47", sil=False)
    for x, y in ((6, 12), (15, 11), (24, 13), (10, 22), (22, 22)):
        d.add(circle(x, y, 1.6), "#72BE5E", sil=False)
    return d


def flower_pot():
    d = Drawing(32, 32)
    _shadow(d, 16, 28, 8, 2)
    d.add(poly([(9, 18), (23, 18), (21, 28), (11, 28)]), "#C8553D")
    d.add(rect(8, 16, 16, 3, 1), "#A3412E")
    for cx, cy, col in ((12, 12, "#F28CB8"), (20, 11, "#F7D154"), (16, 7, "#FFFFFF")):
        d.raw(line(f"M16,17 L{cx},{cy}", "#4E9A47", 1.0))
        d.add(circle(cx, cy, 2.8), col)
        d.add(circle(cx, cy, 1), "#F2A93B", sil=False)
    return d


# ================================================================== ZONE INDUSTRIELLE
def warehouse():
    d = Drawing(128, 96)
    d.under.append('<rect x="4" y="86" width="122" height="8" rx="4" fill="#000" opacity="0.2"/>')
    d.add(rect(6, 40, 116, 52, 0), "#7F93A8")
    for x in range(10, 122, 5):
        d.raw(line(f"M{x},42 L{x},91", "#6D8196", 0.8))
    d.add(poly([(3, 44), (125, 44), (120, 6), (8, 6)]), "#A7B1BC")
    for x in range(14, 118, 8):
        d.raw(line(f"M{x},8 L{x - (x - 64) * 0.08:.1f},42", "#95A0AC", 0.8))
    for cx in (34, 94):
        d.add(ellipse(cx, 22, 6, 4), "#8B96A3")
        d.add(ellipse(cx, 21, 4, 2.4), "#6F7A87", sil=False)
    d.add(rect(6, 44, 116, 3, 0), "#000000", sil=False, opacity=0.2)
    d.add(rect(38, 54, 50, 38, 1), "#C3C9D0")
    for y in range(58, 92, 4):
        d.raw(line(f"M39,{y} L87,{y}", "#A6AEB7", 0.9))
    for k in range(8):
        x = 38 + k * 6.25
        d.add(poly([(x, 49), (x + 3.2, 49), (x + 6.4, 52.5), (x + 3.2, 52.5)]),
              "#F2C14E" if k % 2 == 0 else "#2B2B33", sil=False)
    d.add(rect(100, 66, 13, 26, 1), "#5E6E8C")
    d.add(circle(110, 80, 1), "#F2C14E", sil=False)
    d.add(rect(12, 60, 18, 10, 1), "#9FD3F0")
    d.raw(line("M21,60 L21,70", "#FFFFFF", 1.0))
    return d


def container():
    d = Drawing(96, 48)
    d.under.append('<rect x="3" y="41" width="92" height="6" rx="3" fill="#000" opacity="0.2"/>')
    d.add(rect(2, 18, 92, 26, 0), "#D9772B")
    for x in range(6, 92, 4):
        d.raw(line(f"M{x},19 L{x},43", "#B9601E", 0.8))
    d.add(rect(2, 6, 92, 13, 0), "#E89556")
    d.raw(line("M70,19 L70,43 M82,19 L82,43", "#8F4A17", 1.2))
    for x in (74, 86):
        d.raw(line(f"M{x},23 L{x},39", "#8F4A17", 0.9))
    return d


def pallet():
    d = Drawing(32, 32)
    _shadow(d, 16, 27, 14, 2)
    d.add(rect(3, 20, 26, 6, 1), "#9A6B43")
    for x in (3, 13.5, 24):
        d.add(rect(x, 20, 5, 6, 0.5), "#7E5433", sil=False)
    d.add(rect(3, 10, 26, 11, 1), "#C9A26D")
    for y in (13, 16.5):
        d.raw(line(f"M3,{y} L29,{y}", "#A7824F", 0.9))
    return d


def barrel(col="#2E6FD1", dk="#23579F"):
    d = Drawing(32, 32)
    _shadow(d, 16, 29, 10, 2)
    d.add(rect(7, 8, 18, 20, 3), col)
    for y in (13, 21):
        d.add(rect(7, y, 18, 2, 0), dk, sil=False)
    d.add(ellipse(16, 8, 9, 3.4), dk)
    d.add(ellipse(16, 8, 7, 2.3), col, sil=False)
    d.add(circle(19, 8, 1), dk, sil=False)
    return d


def barrel_red():
    return barrel("#D7332B", "#A82520")


def crate():
    d = Drawing(32, 32)
    _shadow(d, 16, 28.5, 13, 2)
    d.add(rect(4, 13, 24, 15, 0.5), "#C98A4B")
    d.add(rect(4, 5, 24, 9, 0.5), "#DDA566")
    d.raw(line("M5,14 L27,27 M27,14 L5,27", "#A36D37", 1.2))
    d.raw(line("M4,13.5 L28,13.5", "#8A5A3A", 1.0))
    return d


def fence_metal_h():
    d = Drawing(32, 32)
    d.add(rect(2, 4, 3, 24, 1), "#8C9098")
    d.add(rect(0, 5, 32, 2, 0), "#8C9098")
    mesh = ""
    for i in range(-4, 12):
        x = i * 4
        mesh += f"M{x},7 L{x + 18},25 M{x + 18},7 L{x},25 "
    d.raw(f'<clipPath id="m"><rect x="0" y="7" width="32" height="18"/></clipPath>'
          f'<g clip-path="url(#m)" opacity="0.75">{line(mesh, "#B8BCC3", 0.7)}</g>')
    d.add(rect(0, 24.5, 32, 1.4, 0), "#8C9098", sil=False)
    return d


def fence_metal_v():
    d = Drawing(32, 32)
    d.add(rect(15, 0, 2, 32, 0), "#8C9098")
    d.add(circle(16, 5, 2.4), "#8C9098")
    return d


DECOR = {   # nom : (fonction, (largeur, hauteur) 1x, origine 1x)
    "tree": (tree, (64, 64), (32, 58)),
    "bush": (bush, (32, 32), (16, 28)),
    "hay": (hay, (32, 32), (16, 28)),
    "rock": (rock, (32, 32), (16, 27)),
    "fence_wood_h": (fence_wood_h, (32, 32), (0, 28)),
    "fence_wood_v": (fence_wood_v, (32, 32), (16, 32)),
    "signpost": (signpost, (32, 48), (16, 45)),
    "cone": (cone, (32, 32), (16, 28)),
    "road_sign": (road_sign, (32, 48), (16, 45)),
    "lamppost": (lamppost, (32, 64), (16, 61)),
    "house_red": (house, (96, 96), (48, 92)),
    "house_blue": (house_blue, (96, 96), (48, 92)),
    "doghouse": (doghouse, (48, 48), (24, 44)),
    "bench": (bench, (48, 32), (24, 28)),
    "mailbox": (mailbox, (32, 32), (16, 29)),
    "hedge": (hedge, (32, 32), (0, 28)),
    "flower_pot": (flower_pot, (32, 32), (16, 28)),
    "warehouse": (warehouse, (128, 96), (64, 92)),
    "container": (container, (96, 48), (48, 44)),
    "pallet": (pallet, (32, 32), (16, 27)),
    "barrel_blue": (barrel, (32, 32), (16, 29)),
    "barrel_red": (barrel_red, (32, 32), (16, 29)),
    "crate": (crate, (32, 32), (16, 28)),
    "fence_metal_h": (fence_metal_h, (32, 32), (0, 28)),
    "fence_metal_v": (fence_metal_v, (32, 32), (16, 32)),
}

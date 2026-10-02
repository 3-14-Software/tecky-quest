"""
Objets de décor (sprites séparés, triés en profondeur dans GameMaker).
Tailles en 1x ; l'origine conseillée (pied de l'objet) est donnée dans DECOR.
"""
import math

from spritelib import Drawing, circle, ellipse, rect, poly, path, line, leg, OUTLINE


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


CONTAINER_COLORS = {"orange": ("#D9772B", "#B9601E", "#E89556", "#8F4A17"),
                    "blue": ("#2E6FD1", "#23579F", "#5B8FDF", "#1B4378"),
                    "green": ("#3F9A5B", "#2F7A46", "#69B77F", "#245E36")}


def _container_box(d, y, color):
    """Un conteneur de 92 de large : le dessus (13 de haut) à partir de y, la face avant (26) en dessous."""
    col, rib, top, door = CONTAINER_COLORS[color]
    d.add(rect(2, y + 12, 92, 26, 0), col)
    for x in range(6, 92, 4):
        d.raw(line(f"M{x},{y + 13} L{x},{y + 37}", rib, 0.8))
    d.add(rect(2, y, 92, 13, 0), top)
    d.raw(line(f"M70,{y + 13} L70,{y + 37} M82,{y + 13} L82,{y + 37}", door, 1.2))
    for x in (74, 86):
        d.raw(line(f"M{x},{y + 17} L{x},{y + 33}", door, 0.9))


def container(color="orange"):
    d = Drawing(96, 48)
    d.under.append('<rect x="3" y="41" width="92" height="6" rx="3" fill="#000" opacity="0.2"/>')
    _container_box(d, 6, color)
    return d


def container_stack():
    """Deux conteneurs empilés (orange dessous, bleu dessus), au port."""
    d = Drawing(96, 74)
    d.under.append('<rect x="3" y="67" width="92" height="6" rx="3" fill="#000" opacity="0.2"/>')
    _container_box(d, 32, "orange")
    _container_box(d, 6, "blue")
    return d


def truck():
    """Camion de livraison de profil, tourné vers la droite : caisse peinte de ballons, cabine rouge, deux roues."""
    d = Drawing(112, 64)
    d.under.append('<rect x="6" y="55" width="100" height="7" rx="3.5" fill="#000" opacity="0.2"/>')
    d.add(rect(4, 8, 70, 40, 2), "#F3EEE4")
    d.add(rect(4, 8, 70, 5, 2), "#FFFFFF", sil=False)
    for cx, cy, col in ((18, 27, "#E24B4B"), (32, 23, "#F2C14E"), (46, 28, "#4A90D9"), (60, 24, "#5DBB63")):
        d.raw(line(f"M{cx},{cy + 7} Q{cx - 3},{cy + 12} {cx + 1},{cy + 17}", "#8C9098", 0.8))
        d.add(ellipse(cx, cy, 6, 7), col, sil=False, edge=True)
        d.add(ellipse(cx - 2, cy - 3, 1.6, 2.2), "#FFFFFF", sil=False, opacity=0.6)
    d.add(rect(4, 45, 102, 5, 1), "#4A4F57")
    d.add(path("M74,16 L94,16 Q100,16 103,24 L106,32 L106,47 L74,47 Z"), "#D7332B")
    d.add(path("M79,20 L93,20 Q97,20 99,26 L100.5,31 L79,31 Z"), "#9FD3F0", sil=False, edge=True)
    d.raw(line("M83,22 L89,29 M87,21 L93,28", "#FFFFFF", 1.0))
    d.add(rect(74, 36, 32, 2, 0), "#A82520", sil=False)
    d.add(circle(104, 41, 1.6), "#F7D154", sil=False, edge=True)
    for cx in (22, 90):
        d.add(circle(cx, 50, 8), "#3A3A42")
        d.add(circle(cx, 50, 4), "#C9CDD4", sil=False, edge=True)
        d.add(circle(cx, 50, 1.4), "#8C9098", sil=False)
    return d


def forklift():
    """Chariot élévateur jaune de profil, fourche à gauche : mât, toit de protection, siège, contrepoids."""
    d = Drawing(56, 56)
    d.under.append('<rect x="3" y="49" width="50" height="6" rx="3" fill="#000" opacity="0.2"/>')
    d.add(rect(1, 44, 17, 3, 0.8), "#3A3A42")                    # fourche
    d.add(rect(11, 8, 4, 39, 1), "#5C6168")                      # mât
    d.add(rect(15.5, 8, 3, 39, 1), "#4A4F57")
    d.add(rect(9, 30, 4, 17, 0.8), "#3A3A42")                    # tablier de la fourche
    d.add(rect(21, 6, 2.6, 24, 1), "#3A3A42")                    # toit de protection
    d.add(rect(41, 6, 2.6, 24, 1), "#3A3A42")
    d.add(rect(19, 4, 27, 3.5, 1), "#4A4F57")
    d.add(rect(19, 26, 34, 18, 3), "#F2C14E")                    # caisse
    d.add(rect(43, 22, 11, 23, 3), "#D9A92F")                    # contrepoids
    d.add(rect(19, 26, 34, 3, 2), "#FFFFFF", sil=False, opacity=0.3)
    d.add(rect(29, 16, 10, 11, 2.5), "#3A3A42")                  # siège
    d.raw(line("M25,24 L28,15", "#3A3A42", 1.6))                 # volant
    d.add(ellipse(28.5, 14.5, 3, 1.2), "#3A3A42", sil=False)
    for k in range(4):                                           # bandes de sécurité
        d.add(poly([(21 + k * 6, 40), (24 + k * 6, 40), (27 + k * 6, 44), (24 + k * 6, 44)]), "#2B2B33",
              sil=False)
    for cx in (25, 45):
        d.add(circle(cx, 46, 6.5), "#3A3A42")
        d.add(circle(cx, 46, 3), "#C9CDD4", sil=False, edge=True)
    return d


def crane():
    """Portique jaune du port : deux pieds en A, une poutre, un chariot et son crochet (au-dessus des conteneurs).
    Pieds en x 14 et 194 (collisions : RAILS dans game.js)."""
    d = Drawing(208, 128)
    for x in (14, 194):
        d.under.append(f'<ellipse cx="{x}" cy="124" rx="13" ry="3" fill="#000" opacity="0.2"/>')
    for x in (14, 194):
        d.add(path(f"M{x - 3},20 L{x + 3},20 L{x - 5},124 L{x - 11},124 Z"), "#F2C14E")
        d.add(path(f"M{x - 3},20 L{x + 3},20 L{x + 11},124 L{x + 5},124 Z"), "#F2C14E")
        d.add(rect(x - 9, 82, 18, 4, 1), "#D9A92F")
        d.add(rect(x - 13, 119, 26, 6, 1.5), "#5C6168")
    d.add(rect(2, 12, 204, 12, 2), "#F2C14E")                    # poutre
    d.add(rect(2, 20, 204, 4, 0), "#D9A92F", sil=False)
    for x0 in (2, 186):                                          # bouts rayés
        for k in range(4):
            d.add(poly([(x0 + k * 5, 12), (x0 + k * 5 + 2.6, 12), (x0 + k * 5 + 7.6, 24), (x0 + k * 5 + 5, 24)]),
                  "#2B2B33", sil=False)
    d.add(rect(148, 24, 20, 16, 2), "#E8DCC4")                   # cabine du grutier
    d.add(rect(151, 28, 14, 7, 1), "#9FD3F0", sil=False, edge=True)
    d.add(rect(92, 6, 26, 9, 2), "#5C6168")                      # chariot
    d.raw(line("M99,15 L101,64 M111,15 L109,64", "#3A3E45", 1.0))   # câbles
    d.add(rect(97, 62, 16, 7, 1.5), "#D7332B")                   # moufle
    d.add(path("M105,69 L105,74 Q105,79 100.5,78 L100,76 Q102,76.5 102.6,74 L102.6,69 Z"), "#5C6168")
    return d


def guard_hut():
    """Cabane du gardien du port : toit plat qui déborde, fenêtre, porte."""
    d = Drawing(64, 64)
    d.under.append('<rect x="5" y="55" width="54" height="7" rx="3.5" fill="#000" opacity="0.2"/>')
    d.add(rect(9, 22, 46, 36, 1), "#E8DCC4")
    d.add(rect(4, 11, 56, 13, 2), "#5E7FA3")
    d.add(rect(4, 21, 56, 3, 0), "#4A6585", sil=False)
    d.add(rect(36, 31, 13, 27, 1), "#8A5A3A")
    d.add(circle(46, 45, 1), "#F2C14E", sil=False)
    d.add(rect(14, 30, 17, 13, 1), "#9FD3F0")
    d.raw(line("M22.5,30 L22.5,43 M14,36.5 L31,36.5", "#FFFFFF", 1.0))
    return d


def bollard():
    """Bitte d'amarrage en fonte, au bord du quai."""
    d = Drawing(32, 32)
    _shadow(d, 16, 28, 9, 2)
    d.add(rect(10, 14, 12, 14, 3), "#4A4F57")
    d.add(ellipse(16, 13, 9, 4), "#5C6168")
    d.add(ellipse(16, 12.5, 6.5, 2.6), "#6E737B", sil=False)
    d.add(rect(10, 21, 12, 2, 0), "#3A3E45", sil=False)
    return d


def barge():
    """Péniche amarrée (sur l'eau, sans collision) : coque bleue, cale pleine de sable, cabine à l'arrière."""
    d = Drawing(176, 48)
    d.under.append('<ellipse cx="88" cy="42" rx="84" ry="5" fill="#1F5A85" opacity="0.35"/>')
    d.under.append('<path d="M2,45 Q6,43 10,45 M160,46 Q164,44 168,46 M40,47 Q45,45 50,47" fill="none" '
                   'stroke="#9AD6F3" stroke-width="1" stroke-linecap="round"/>')
    d.add(path("M4,26 L172,26 L165,41 Q88,45 11,41 Z"), "#2B4C7E")
    d.add(rect(4, 26, 168, 4, 0), "#D7332B", sil=False)
    d.add(rect(14, 18, 104, 9, 1), "#3A3E45")
    d.add(path("M18,20 Q40,8 64,18 Q86,9 114,20 Z"), "#E3C995")
    d.add(rect(128, 9, 34, 18, 1), "#F3EEE4")
    d.add(rect(126, 5, 38, 5, 1), "#2B4C7E")
    for x in (133, 147):
        d.add(rect(x, 13, 8, 6, 1), "#9FD3F0", sil=False, edge=True)
    d.add(rect(167, 2, 1.8, 24, 0.5), "#5C6168")
    d.add(path("M168.8,3 L176,5.5 L168.8,8 Z"), "#D7332B")
    return d


def goal_net():
    """Le grand filet de Léon (un but, ouverture vers le bas de l'écran) : on y pousse les ballons. Montants avant en
    x 4..8 et 88..92 (pieds en y 60), montants arrière en x 12 et 84 (pieds en y 32). Collisions : RAILS (game.js)."""
    d = Drawing(96, 64)
    d.under.append('<path d="M6,60 L90,60 L84,32 L12,32 Z" fill="#000" opacity="0.1"/>')
    mesh = "".join(f"M{x},2 L{x},62 " for x in range(8, 92, 5)) + "".join(f"M2,{y} L94,{y} " for y in range(6, 62, 5))
    for pts in ([(6, 34), (90, 34), (84, 6), (12, 6)],                      # toit et fond
                [(6, 34), (12, 6), (12, 32), (6, 60)], [(90, 34), (84, 6), (84, 32), (90, 60)]):   # côtés
        cid = f"net{len(d.under)}{pts[0][0]}{pts[1][0]}"
        poly_d = "M" + " L".join(f"{x},{y}" for x, y in pts) + " Z"
        d.raw(f'<clipPath id="{cid}"><path d="{poly_d}"/></clipPath>'
              f'<path d="{poly_d}" fill="#FFFFFF" opacity="0.28"/>'
              f'<g clip-path="url(#{cid})">{line(mesh, "#FFFFFF", 0.6)}</g>')
        d.under.append("")                                                   # (identifiants de clip distincts)
    for x in (12, 84):                                                       # montants arrière, barre du fond
        d.raw(line(f"M{x},6 L{x},32", "#E6EBF0", 1.6))
    d.raw(line("M12,6 L84,6 M12,32 L84,32", "#E6EBF0", 1.4))
    d.raw(line("M6,34 L12,6 M90,34 L84,6", "#E6EBF0", 1.4))
    d.add(rect(4, 32, 4, 28, 1), "#FFFFFF")                                  # cadre avant
    d.add(rect(88, 32, 4, 28, 1), "#FFFFFF")
    d.add(rect(4, 31, 88, 4, 1), "#FFFFFF")
    for x in (4, 88):
        for y in (38, 48):
            d.add(rect(x, y, 4, 4, 0), "#E24B4B", sil=False)
    return d


def leaf_nest():
    """Le nid de Maman Piquette : un tas de feuilles mortes (orange, jaune, brun) avec une petite entrée sombre."""
    d = Drawing(48, 32)
    _shadow(d, 24, 28.5, 20, 2.6)
    d.add(path("M5,28 Q6,14 18,10 Q26,7 33,11 Q43,15 43,28 Z"), "#B9783E")
    for cx, cy, rx, ry, a, col in ((12, 22, 6, 3, -20, "#E08A3A"), (21, 16, 6.5, 3.2, 15, "#F2C14E"),
                                   (31, 18, 6, 3, -25, "#C8642E"), (36, 25, 5.5, 2.8, 20, "#E3A954"),
                                   (17, 25, 5, 2.6, 30, "#D4A23A"), (27, 12.5, 5, 2.4, -10, "#E08A3A")):
        d.add(ellipse(cx, cy, rx, ry, f"rotate({a} {cx} {cy})"), col, sil=False, edge=True)
        d.raw(line(f"M{cx - rx * 0.7:.1f},{cy} L{cx + rx * 0.7:.1f},{cy}", "#8A5A3A", 0.5)
              .replace("/>", f' transform="rotate({a} {cx} {cy})"/>'))
    d.add(path("M20,28 Q20,21.5 24,21.5 Q28,21.5 28,28 Z"), "#4A2E1A", sil=False, edge=True)   # entrée
    return d


def rail():
    """Voie ferrée posée à plat, une tuile qui se répète vers la droite : traverses en bois, deux rails."""
    d = Drawing(32, 32)
    for x in (1, 9, 17, 25):
        d.add(rect(x, 6, 5.5, 20, 1), "#8A5A3A", sil=False, edge=True)
    for y in (9.5, 20.5):
        d.add(rect(0, y, 32, 2.4, 0), "#A9AEB5", sil=False)
        d.raw(line(f"M0,{y + 2.4} L32,{y + 2.4}", "#5C6168", 0.7))
    return d


def buffer_stop():
    """Heurtoir au bout de la voie : butoir rayé rouge et blanc sur deux montants."""
    d = Drawing(32, 40)
    _shadow(d, 16, 36, 12, 2)
    d.add(rect(8, 18, 3, 18, 1), "#5C6168")
    d.add(rect(21, 18, 3, 18, 1), "#5C6168")
    d.add(rect(3, 13, 26, 9, 2), "#FFFFFF")
    for k in range(3):
        d.add(poly([(5 + k * 9, 13), (9 + k * 9, 13), (13 + k * 9, 22), (9 + k * 9, 22)]), "#D7332B", sil=False)
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


# ================================================================== FERME
def barn():
    """Grange rouge, pignon face à nous, toit à la Mansart (deux pans brisés) qui fuit vers le haut."""
    d = Drawing(128, 112)
    d.under.append('<rect x="10" y="100" width="108" height="9" rx="4.5" fill="#000" opacity="0.2"/>')
    # --- toit vu de dessus : le profil du pignon, prolongé vers l'arrière (vers le haut de l'écran)
    front = [(8, 64), (22, 38), (64, 24), (106, 38), (120, 64)]
    back = [(x, y - 20) for x, y in front]
    d.add(poly(front + back[::-1]), "#7A4B33")
    shades = ("#6A3F2A", "#8A5A3A", "#9B6A46", "#7A4B33")      # pan raide, pan doux, pan doux, pan raide
    for k in range(4):
        (x0, y0), (x1, y1) = front[k], front[k + 1]
        d.add(poly([(x0, y0), (x1, y1), (x1, y1 - 20), (x0, y0 - 20)]), shades[k], sil=False)
    # rangs de bardeaux, parallèles au profil
    for t in (5, 10, 15):
        pts = " L".join(f"{x:.1f},{y - t:.1f}" for x, y in front)
        d.raw(line(f"M{pts}", "#5C3522", 0.7))
    d.raw(line("M64,24 L64,4", "#5C3522", 1.0))                 # faîtage
    # --- façade (pignon) rouge
    wall = [(16, 106), (16, 62), (27, 42), (64, 30), (101, 42), (112, 62), (112, 106)]
    d.add(poly(wall), "#D7332B")
    for x in range(22, 110, 6):                                 # planches verticales
        d.raw(line(f"M{x},{max(45, 62 - abs(x - 64) * 0.5):.1f} L{x},105", "#B8281F", 0.8))
    # bordure blanche le long du pignon (rive du toit) et son ombre sur la façade
    rim_o = [(10, 66), (23, 40), (64, 26), (105, 40), (118, 66)]
    rim_i = [(15, 66), (27, 44), (64, 32), (101, 44), (113, 66)]
    d.clip("mur", [poly(wall)])
    d.add(poly(rim_i + [(x, y + 4) for x, y in rim_i[::-1]]), "#000000", sil=False, clip="mur", opacity=0.15)
    d.add(poly(rim_o + rim_i[::-1]), "#FFF7E6")
    # chaînes d'angle blanches
    for x in (16, 107):
        d.add(rect(x, 66, 5, 40, 0), "#FFF7E6", sil=False, edge=True)
    # lucarne de fenil, avec du foin qui dépasse
    d.add(rect(53, 41, 22, 18, 1), "#FFF7E6", sil=False, edge=True)
    d.add(rect(56, 44, 16, 14, 0.5), "#3A2418", sil=False)
    d.add(path("M56,58 L56,52 Q58,49 60,51 Q62,47 64,50 Q66,46 68,50 Q70,48 72,52 L72,58 Z"),
          "#E3B94F", sil=False)
    for x0, x1 in ((58, 55.5), (63, 62.5), (68, 70.5)):
        d.raw(line(f"M{x0},55 L{x1},60.5", "#E3B94F", 1.4))     # brins qui pendent
    d.raw(line("M59,56 L58,59 M66,56 L67,59.5", "#C99B35", 0.7))
    # poutre de levage au-dessus de la lucarne
    d.add(rect(61, 34, 6, 6, 1), "#8A5A3A", sil=False, edge=True)
    # grande porte à deux battants, croisillons en X blancs
    d.add(rect(40, 68, 48, 38, 0.5), "#FFF7E6", sil=False, edge=True)
    for x in (43, 65):
        d.add(rect(x, 71, 20, 35, 0), "#A82520", sil=False)
        d.raw(line(f"M{x + 1.5},72.5 L{x + 18.5},104.5 M{x + 18.5},72.5 L{x + 1.5},104.5", "#FFF7E6", 2.2))
        d.raw(line(f"M{x},88.5 L{x + 20},88.5", "#FFF7E6", 2.2))
    d.raw(line("M64,71 L64,106", "#FFF7E6", 2.0))
    d.add(rect(60.5, 85, 7, 7, 1), "#F2C14E", sil=False, edge=True)     # loquet
    # petites fenêtres latérales
    for x in (24, 94):
        d.add(rect(x, 74, 10, 10, 1), "#9FD3F0", sil=False, edge=True)
        d.raw(line(f"M{x + 5},74.5 L{x + 5},83.5 M{x + 0.5},79 L{x + 9.5},79", "#FFFFFF", 1.0))
    # seuil
    d.add(rect(38, 104, 52, 3, 1), "#B7B2A8")
    return d


def chicken_coop():
    """Poulailler en bois sur pieds : toit rouge, porte ronde, rampe à barreaux, nichoir."""
    d = Drawing(64, 64)
    _shadow(d, 31, 59, 25, 3)
    # pieds
    for x in (16, 44):
        d.add(rect(x - 2, 44, 4, 15, 1), "#8A5A3A")
    # nichoir (sur le côté droit), dessiné avant la cabane
    d.add(rect(46, 34, 12, 11, 1), "#C98A4B")
    d.raw(line("M47,39.5 L57,39.5", "#A36D37", 0.8))
    d.add(poly([(45, 35.5), (59.5, 35.5), (57.5, 30), (47, 30)]), "#A82520")   # couvercle incliné
    d.add(rect(49.5, 37.5, 6, 5, 1), "#3A2418", sil=False)
    d.add(path("M49.5,42.5 Q52.5,39.5 55.5,42.5 Z"), "#F2D27A", sil=False)  # paille au fond
    # cabane
    d.add(rect(12, 24, 36, 23, 1), "#C98A4B")
    for y in (30, 36, 42):
        d.raw(line(f"M13,{y} L47,{y}", "#A36D37", 0.8))
    # toit
    d.add(poly([(6, 27), (54, 27), (46, 8), (14, 8)]), "#D7332B")
    d.add(rect(14, 6, 32, 4, 1.5), "#A82520")
    d.raw(line("M9.5,19.5 L50.5,19.5", "#A82520", 0.9))
    d.add(rect(12, 27, 36, 3, 0), "#000000", sil=False, opacity=0.15)
    # porte ronde
    d.add(circle(24, 38, 5.5), "#FFF7E6", sil=False, edge=True)
    d.add(circle(24, 38, 3.8), "#3A2418", sil=False)
    # petite fenêtre en cœur (motif sur la plaque)
    d.add(rect(32, 13, 12, 7, 1), "#F3E7CF", sil=False, edge=True)
    d.add(path("M38,18.5 L35.4,15.9 Q34.6,14.2 36.4,14 Q37.4,14 38,15 Q38.6,14 39.6,14 Q41.4,14.2 40.6,15.9 Z"),
          "#E24B4B", sil=False)
    # rampe à barreaux, du seuil de la porte jusqu'au sol (vers la gauche)
    d.add(poly([(20, 42), (26, 42), (11, 58), (4, 58)]), "#B98556")
    for k in range(1, 5):
        t = k / 5
        x0, x1 = 20 + (4 - 20) * t, 26 + (11 - 26) * t
        y = 42 + 16 * t
        d.raw(line(f"M{x0 + 0.6:.1f},{y:.1f} L{x1 - 0.6:.1f},{y:.1f}", "#7E5433", 1.2))
    return d


def tractor(body="#D7332B", body_dk="#A82520"):
    """Tracteur de profil, tourné vers la droite : grande roue arrière, petite roue avant, cabine."""
    d = Drawing(64, 48)
    d.under.append('<rect x="4" y="41" width="56" height="6" rx="3" fill="#000" opacity="0.2"/>')
    # pot d'échappement (derrière le capot)
    d.add(rect(40, 8, 3, 16, 1), "#5C6168")
    d.add(rect(39, 6.5, 5, 3, 1), "#4A4F57")
    # cabine : toit + montants + vitres
    d.add(rect(5, 3, 26, 4, 1.5), body_dk)
    d.add(rect(8, 6, 21, 18, 1), "#9FD3F0")
    d.add(rect(8, 6, 3, 18, 0), body, sil=False)
    d.add(rect(26, 6, 3, 18, 0), body, sil=False)
    d.raw(line("M13,10 L18,15 M15,8 L22,15", "#FFFFFF", 1.1))         # reflet
    # capot
    d.add(path("M26,20 L54,20 Q58,20 58,24 L58,34 L26,34 Z"), body)
    d.add(rect(26, 20, 32, 3, 1), "#FFFFFF", sil=False, opacity=0.25)
    for y in (25, 28, 31):                                              # grille avant
        d.raw(line(f"M54,{y} L57.5,{y}", body_dk, 0.9))
    d.add(circle(57.5, 22.8, 1.5), "#F7D154", sil=False, edge=True)    # phare
    # bas de caisse / châssis
    d.add(rect(8, 24, 26, 12, 1), body)
    d.add(rect(8, 33, 50, 3, 0.5), "#4A4F57")
    # garde-boue de la grande roue
    d.add(path("M4,32 Q4,17 18,17 Q32,17 32,32 L28,32 Q28,21 18,21 Q8,21 8,32 Z"), body_dk)
    # grande roue arrière
    d.add(circle(18, 32, 12), "#3A3A42")
    for k in range(12):
        a = k * math.pi / 6
        x0, y0 = 18 + 10.4 * math.cos(a), 32 + 10.4 * math.sin(a)
        x1, y1 = 18 + 12 * math.cos(a), 32 + 12 * math.sin(a)
        d.raw(line(f"M{x0:.2f},{y0:.2f} L{x1:.2f},{y1:.2f}", "#25252B", 1.4))
    d.add(circle(18, 32, 6.5), "#F2C14E", sil=False, edge=True)
    d.add(circle(18, 32, 2.4), "#C99B35", sil=False, edge=True)
    # petite roue avant
    d.add(circle(49, 37, 7), "#3A3A42")
    d.add(circle(49, 37, 3.6), "#F2C14E", sil=False, edge=True)
    d.add(circle(49, 37, 1.3), "#C99B35", sil=False)
    return d


def scarecrow():
    """Épouvantail gentil : piquet, chemise à carreaux, tête en toile de sac souriante, chapeau de paille."""
    d = Drawing(32, 64)
    _shadow(d, 16, 60, 6, 1.6)
    # piquet + traverse (dans les manches)
    d.add(rect(14.6, 40, 2.8, 20, 1), "#8A5A3A")
    # paille qui dépasse des manches et du bas de la chemise
    for x, s in ((3.2, -1), (28.8, 1)):
        d.add(path(f"M{x - s * 1.5},28 L{x + s * 2.5},26.2 L{x + s * 1.5},29 L{x + s * 3},30.6 "
                   f"L{x + s * 1.2},31.4 L{x + s * 2},33.6 L{x - s * 1.5},32.5 Z"), "#F2D27A")
    d.add(path("M11,43 L10,47 L12.5,45.5 L13.5,48.5 L15.5,45 L17,48.5 L18.5,45.5 L21,47 L20,43 Z"), "#F2D27A")
    # chemise : corps + manches
    d.add(path("M4,26.5 L10,24.5 L22,24.5 L28,26.5 L28,32.5 L21.5,32 L21.5,44 L10.5,44 L10.5,32 L4,32.5 Z"),
          "#D7332B")
    d.clip("chemise", [path("M4,26.5 L10,24.5 L22,24.5 L28,26.5 L28,32.5 L21.5,32 L21.5,44 L10.5,44 "
                            "L10.5,32 L4,32.5 Z")])
    grid = "".join(f"M{x},22 L{x},46 " for x in (7, 12.5, 18, 23.5)) + \
           "".join(f"M2,{y} L30,{y} " for y in (28.5, 34, 39.5))
    d.raw(f'<g clip-path="url(#chemise)">{line(grid, "#A82520", 2.2)}'
          f'{line(grid, "#F3E7CF", 0.6)}</g>')
    # pièce rapiécée + boutons
    d.add(rect(17.5, 36.5, 3.6, 3.6, 0.5), "#2E6FD1", sil=False, edge=True)
    d.raw(line("M18.2,37.2 L20.4,39.4 M20.4,37.2 L18.2,39.4", "#FFF7E6", 0.4))
    for y in (30, 34, 38.5):
        d.add(circle(16, y, 0.75), "#F3E7CF", sil=False)
    # tête en sac
    d.add(path("M9.5,17 Q9,9.5 16,9.5 Q23,9.5 22.5,17 Q22,24 16,24 Q10,24 9.5,17 Z"), "#E3C995")
    d.add(path("M12.5,23 L19.5,23 L18.5,26 L13.5,26 Z"), "#E3C995")       # cou noué
    d.raw(line("M13,24.6 L19,24.6", "#8A5A3A", 1.0))                       # ficelle
    # visage souriant
    d.add(circle(13.4, 16, 1.15), OUTLINE, sil=False)
    d.add(circle(18.6, 16, 1.15), OUTLINE, sil=False)
    d.add(circle(13.7, 15.6, 0.4), "#FFFFFF", sil=False)
    d.add(circle(18.9, 15.6, 0.4), "#FFFFFF", sil=False)
    d.add(circle(12, 19, 1.3), "#F28CB8", sil=False, opacity=0.75)
    d.add(circle(20, 19, 1.3), "#F28CB8", sil=False, opacity=0.75)
    d.raw(line("M13.6,19.2 Q16,21.8 18.4,19.2", OUTLINE, 0.9))
    # chapeau de paille
    d.add(ellipse(16, 11, 11.5, 3.2), "#F2C14E")
    d.add(path("M10.5,11 Q10.5,3.5 16,3.5 Q21.5,3.5 21.5,11 Z"), "#E3B94F")
    d.add(rect(10.6, 8, 10.8, 2.2, 0), "#D7332B", sil=False)
    d.raw(line("M7,12 Q16,14.4 25,12", "#C99B35", 0.7))
    d.add(path("M20,9.5 L23.5,6.5 L22.5,10 Z"), "#F7D154", sil=False, edge=True)  # petit épi glissé
    return d


# ================================================================== RIVIÈRE
def bridge():
    """Pont de bois vu de dessus (posé à plat) : il enjambe une rivière horizontale du nord au sud.
    Tablier x 16..80, garde-corps x 8..16 et 80..88, toute la hauteur (160)."""
    d = Drawing(96, 160)
    # ombre portée sur l'eau (un peu décalée vers le bas à droite)
    d.under.append('<rect x="11" y="3" width="81" height="157" rx="2" fill="#000" opacity="0.16"/>')
    # longerons sous les garde-corps
    for x in (8, 80):
        d.add(rect(x, 0, 8, 160, 1), "#8A5A3A")
    # tablier : planches horizontales
    d.add(rect(15, 0, 66, 160, 0), "#C98A4B")
    cols = ("#C98A4B", "#D49A5B", "#BE8045", "#CF9352")
    for k in range(20):
        y = k * 8
        d.add(rect(16, y + 0.6, 64, 6.8, 1), cols[k % 4], sil=False)
        d.raw(line(f"M16,{y + 0.3} L80,{y + 0.3}", "#8A5A3A", 0.9))        # joint entre planches
        # veinage léger, décalé d'une planche à l'autre
        gx = 30 + (k * 17) % 34
        d.raw(line(f"M{gx},{y + 4} L{gx + 10},{y + 4}", "#A36D37", 0.6))
        # clous aux deux extrémités (sur les longerons)
        for nx in (19, 77):
            d.add(circle(nx, y + 4, 0.65), "#6E4428", sil=False)
    # traverses aux deux bouts
    for y in (0, 156):
        d.add(rect(16, y, 64, 4, 0.5), "#A36D37", sil=False, edge=True)
    # garde-corps : lisse + poteaux (vue 3/4 : chapeau clair, face sud plus sombre)
    for x in (8, 80):
        d.add(rect(x + 2.2, 0, 3.6, 160, 1.2), "#B98556", sil=False, edge=True)
        d.raw(line(f"M{x + 3.4},1.5 L{x + 3.4},158.5", "#D9A46A", 0.7))
        for y in (2, 34, 66, 98, 130, 151):
            d.add(rect(x + 0.6, y, 6.8, 7.5, 1.4), "#7E5433", sil=False, edge=True)   # face du poteau
            d.add(rect(x + 0.6, y, 6.8, 4.6, 1.4), "#C98A4B", sil=False, edge=True)   # dessus du poteau
    return d


def reeds():
    """Touffe de roseaux avec quelques massettes, pour le bord de l'eau."""
    d = Drawing(32, 32)
    _shadow(d, 16, 28, 10, 2)

    def blade(x0, x1, tipx, tipy, bend, col, sil=True):
        cx = (x0 + x1) / 2
        d.add(path(f"M{x0},28 Q{cx + bend - 1.5},{(28 + tipy) / 2} {tipx},{tipy} "
                   f"Q{cx + bend + 1.5},{(28 + tipy) / 2} {x1},28 Z"), col, sil=sil)

    cattails = ((11.5, 4), (18.5, 1.5), (24.5, 8))       # (x, haut de l'épi)
    # tiges des massettes (derrière les feuilles)
    for x, top in cattails:
        d.add(rect(x - 0.7, top + 8, 1.4, 20 - top, 0.7), "#5E8F3E")
    # feuilles (de l'arrière vers l'avant)
    blade(9, 12.5, 3.5, 12, -3, "#3F8439")
    blade(19.5, 23, 29, 13, 3, "#3F8439")
    blade(13.5, 17, 15, 9, 0, "#4E9A47")
    blade(16.5, 20, 22.5, 15, 2, "#4E9A47")
    blade(7, 10.5, 2, 19.5, -2, "#4E9A47")
    blade(21.5, 25, 30, 20, 2, "#4E9A47")
    blade(11, 14.5, 8.5, 15.5, -1, "#72BE5E")
    blade(15.5, 19, 18.5, 14.5, 1, "#72BE5E")
    # épis bruns, qui dépassent des feuilles
    for x, top in cattails:
        d.add(rect(x - 0.5, top - 1.5, 1, 3.5, 0.5), "#5E8F3E")           # pointe
        d.add(rect(x - 2, top + 1.5, 4, 7.5, 2), "#7A4B2A")               # épi
        d.add(rect(x - 1.1, top + 2.6, 1, 4, 0.5), "#9B6A46", sil=False)  # reflet
    return d


def boat():
    """Barque en bois amarrée, vue de 3/4 : intérieur visible, bancs, deux rames, corde vers un pieu."""
    d = Drawing(64, 32)
    # reflet sombre sous la coque + rides sur l'eau
    d.under.append('<ellipse cx="29" cy="25" rx="25" ry="3.6" fill="#1F5A85" opacity="0.35"/>')
    d.under.append('<path d="M1,25 Q3.5,23.5 6,25 M50,26 Q53,24.5 56,26 M8,29 Q12,27.5 16,29 '
                   'M40,29.5 Q44,28 48,29.5" fill="none" stroke="#9AD6F3" stroke-width="1" '
                   'stroke-linecap="round"/>')
    # pieu d'amarrage (dans l'eau, à droite)
    d.add(rect(57, 11, 4.5, 15, 1), "#8A5A3A")
    d.add(ellipse(59.25, 11, 2.25, 1.2), "#C98A4B", sil=False, edge=True)
    d.raw(line("M57.5,25.2 Q59.25,24.2 61,25.2", "#9AD6F3", 0.8))
    # coque : flanc (vu de côté) + bordage (vu de dessus)
    hull = "M4,13 Q5,7.5 29,6.5 Q50,7 54,12 Q52,19.5 46,23 Q29,27.5 12,23 Q5,19.5 4,13 Z"
    d.add(path(hull), "#B98556")
    d.add(path("M5,15.5 Q7,21 12,23 Q29,27.5 46,23 Q52,19.5 53.4,14.5 Q50,19 29,19.8 Q8,19.5 5,15.5 Z"),
          "#A36D37", sil=False)
    d.raw(line("M7.5,20 Q29,25 50.5,19.5", "#8A5A3A", 0.7))                # bordé
    d.add(path("M5,15.2 Q8,19.6 29,19.8 Q50,19.4 53.6,14.2 L53.2,16.4 Q49.6,21.2 29,21.8 "
               "Q8.2,21.6 5.2,17.4 Z"), "#2E6FD1", sil=False)              # liseré peint
    # bordage (plat-bord) et intérieur
    d.add(path("M4,13 Q5,7.5 29,6.5 Q50,7 54,12 Q50,19 29,19.8 Q8,19.5 4,13 Z"), "#8A5A3A",
          sil=False, edge=True)
    d.add(path("M7,13 Q8,9.4 29,8.8 Q48,9.2 51,12.4 Q47.5,17.2 29,17.6 Q10,17.4 7,13 Z"), "#DDA566",
          sil=False)
    for y in (11, 13.2, 15.4):
        d.raw(line(f"M10,{y} Q29,{y + 0.6} 48,{y}", "#C9944F", 0.6))
    # bancs (traverses)
    for x in (18, 36):
        d.add(rect(x - 2.4, 8.9, 4.8, 8.7, 0.6), "#A36D37", sil=False, edge=True)
    # rames : manches + pelles, posées sur les bancs (une pelle à chaque bout)
    for (x0, x1, y), (bx0, bx1) in (((10, 38, 11.4), (37, 48)), ((20, 48, 15.1), (21, 10))):
        d.raw(line(f"M{x0},{y} L{x1},{y}", OUTLINE, 2.4))
        d.raw(line(f"M{x0},{y} L{x1},{y}", "#E3B94F", 1.0))
        k = 1 if bx1 > bx0 else -1
        d.add(path(f"M{bx0},{y - 1} Q{bx0 + k * 6},{y - 2.6} {bx1},{y - 1.4} Q{bx1 + k * 1},{y} {bx1},{y + 1.4} "
                   f"Q{bx0 + k * 6},{y + 2.6} {bx0},{y + 1} Z"), "#E3B94F", sil=False, edge=True)
    for x, y in ((10.5, 11.4), (47.5, 15.1)):
        d.add(circle(x, y, 1.1), "#8A5A3A", sil=False, edge=True)          # poignées
    # anneau de proue + corde jusqu'au pieu
    d.add(circle(51.6, 12.4, 1.3), "#5C6168", sil=False)
    d.raw(line("M52.5,13 Q55,19 58.4,16", "#3A1E12", 2.2))
    d.raw(line("M52.5,13 Q55,19 58.4,16", "#E8D39A", 1.1))
    d.raw(line("M56.8,15.4 Q59.25,17.2 61.7,15.4", "#E8D39A", 1.3))         # nœud autour du pieu
    return d


def _ring(cx, cy, rx, ry, color, w=0.8):
    """Ellipse non remplie (cernes du bois, rides de l'eau), jamais dans la silhouette."""
    return (f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="none" '
            f'stroke="{color}" stroke-width="{w}"/>')


def _tube(d, dpath, color, w):
    """Tube fin (garde-corps, jet d'eau) : trait de contour puis trait de couleur par-dessus."""
    d.raw(line(dpath, OUTLINE, w + 1.8))
    d.raw(line(dpath, color, w))


def _amanita(d, x, base, r, h, edge=False, dots=None):
    """Amanite tue-mouches : pied crème, chapeau rouge en dôme à pois blancs.
    (x, base) = pied du champignon au sol ; r = demi-largeur du chapeau ; h = hauteur du pied."""
    sw = r * 0.62
    d.add(rect(x - sw / 2, base - h, sw, h, sw * 0.4), "#F3E7CF", edge=edge)
    cy = base - h + 0.6                          # bas du chapeau
    k = 1.25 * r                                 # dôme : sommet à ~0.94 r au-dessus de cy
    d.add(path(f"M{x - r:.2f},{cy:.2f} C{x - r:.2f},{cy - k:.2f} {x + r:.2f},{cy - k:.2f} {x + r:.2f},{cy:.2f} "
               f"Q{x:.2f},{cy + 1.4:.2f} {x - r:.2f},{cy:.2f} Z"), "#D7332B", edge=edge)
    d.add(ellipse(x - r * 0.38, cy - r * 0.55, r * 0.22, r * 0.14), "#E24B4B", sil=False)   # reflet
    for dx, dy, rr in (dots or ((-0.45, -0.35, 0.17), (0.15, -0.68, 0.15), (0.5, -0.28, 0.13))):
        d.add(circle(x + dx * r, cy + dy * r, max(0.7, rr * r)), "#FFFFFF", sil=False)


def _tuft(d, x, y, col="#3F8439"):
    """Petite touffe d'herbe au pied d'un objet (trois brins)."""
    d.raw(line(f"M{x - 1.6},{y} L{x - 2.4},{y - 2.6} M{x},{y} L{x},{y - 3.4} M{x + 1.6},{y} L{x + 2.4},{y - 2.6}",
               col, 1.0))


# ================================================================== FORÊT
def fir():
    """Sapin : trois étages de branches festonnés, plus sombres que l'arbre rond, petit tronc."""
    d = Drawing(64, 80)
    _shadow(d, 32, 76, 18, 3.5)
    d.add(poly([(28.5, 60), (35.5, 60), (36.5, 76), (27.5, 76)]), "#8A5A3A")
    d.add(rect(31, 67, 2, 7, 1), "#6E4428", sil=False)

    def tier(top, hw, bot, n, dy=0.0):
        """Étage triangulaire : pointe en (32, top), bas festonné de n arrondis vers le bas."""
        top, bot = top + dy, bot + dy
        xl, xr = 32 - hw, 32 + hw
        my = (top + bot) / 2
        s = f"M32,{top:.2f} Q{32 - hw * 0.42:.2f},{my:.2f} {xl:.2f},{bot - 1.5:.2f} "
        step = 2 * hw / n
        for i in range(n):
            x0 = xl + i * step
            s += f"Q{x0 + step / 2:.2f},{bot + 4.2:.2f} {x0 + step:.2f},{bot - 1.5:.2f} "
        s += f"Q{32 + hw * 0.42:.2f},{my:.2f} 32,{top:.2f} Z"
        return path(s)

    tiers = [(36, 27, 64, 5), (19, 22, 47, 4), (3, 16, 30, 3)]   # (pointe, demi-largeur, bas, festons)
    shapes = [tier(*t) for t in tiers]
    for k, (t, s) in enumerate(zip(tiers, shapes)):
        d.clip(f"fir{k}", [s])
        if k:   # ombre portée de l'étage sur celui du dessous
            d.add(tier(*t, dy=3.5), "#24633A", sil=False, clip=f"fir{k - 1}")
        d.add(s, "#2F7A45")
        top, hw, bot, _ = t
        # flanc droit dans l'ombre
        d.add(poly([(33, top + 4), (32 + hw * 0.3, bot + 6), (32 + hw + 3, bot + 6), (32 + hw + 3, top)]),
              "#24633A", sil=False, clip=f"fir{k}", opacity=0.75)
        # reflets sur le flanc gauche
        hy = top + (bot - top) * 0.55
        d.raw(line(f"M{32 - hw * 0.55:.1f},{hy + 3:.1f} Q{32 - hw * 0.35:.1f},{hy + 5.5:.1f} {32 - hw * 0.12:.1f},{hy + 3.5:.1f}",
                   "#4C9A5C", 1.4))
        d.raw(line(f"M{32 - hw * 0.28:.1f},{hy - 3:.1f} Q{32 - hw * 0.15:.1f},{hy - 1:.1f} {32 - hw * 0.02:.1f},{hy - 2.5:.1f}",
                   "#5FAE63", 1.2))
    d.add(circle(29.5, 12, 1.6), "#7CC36B", sil=False)    # petit reflet au sommet
    return d


def stump():
    """Souche : dessus coupé avec cernes, racines qui s'étalent, un peu de mousse."""
    d = Drawing(32, 32)
    _shadow(d, 16, 27, 13, 2.5)
    d.add(path("M8,14 L8,22.5 Q7.2,25.6 3.6,26.8 Q7.5,27.6 10.6,26 Q13,27.6 16,27.4 "
               "Q19,27.6 21.6,26 Q24.6,27.6 28.4,26.8 Q24.8,25.6 24,22.5 L24,14 Z"), "#8A5A3A")
    d.raw(line("M11.5,17.5 L11.5,24.5 M16.5,18.5 L16.5,26 M20.8,16.8 L20.8,23.5", "#6E4428", 0.9))
    d.add(path("M8,18 L8,21 Q10,19.2 12.4,19.4 Q11.2,17.6 8,18 Z"), "#A36D37", sil=False, opacity=0.8)
    # dessus coupé
    d.add(ellipse(16, 14, 8, 3.6), "#E8C48A", edge=True)
    d.raw(_ring(16, 14, 5.4, 2.4, "#C98A4B", 0.8))
    d.raw(_ring(16, 14, 2.8, 1.2, "#C98A4B", 0.8))
    d.add(ellipse(16, 14, 0.8, 0.4), "#A36D37", sil=False)
    d.raw(line("M19.5,12.6 L21.5,14.5", "#A36D37", 0.7))           # fente
    # mousse : petites boules sur le rebord gauche, touffe au pied à droite
    for cx, cy, r in ((8.4, 15.2, 1.7), (10.2, 12.6, 1.9), (12.8, 11.2, 1.4)):
        d.add(circle(cx, cy, r), "#72BE5E")
    d.add(circle(9.8, 12.1, 0.7), "#A6DA8C", sil=False)
    d.add(ellipse(25.2, 25.8, 3, 1.7), "#4E9A47")
    d.add(ellipse(24.7, 25.2, 1.3, 0.7), "#72BE5E", sil=False)
    _tuft(d, 5.8, 27.6)
    return d


def log():
    """Tronc couché : bout coupé (cernes) à gauche, écorce, mousse et un champignon dessus."""
    d = Drawing(64, 32)
    _shadow(d, 33, 26.8, 27, 3)
    d.add(path("M10,9.5 L53,9.5 Q60,9.5 60,18 Q60,26.5 53,26.5 L10,26.5 Z"), "#8A5A3A")
    d.add(path("M12,11.6 L52,11.6 Q56.4,11.8 57.6,15 L12,15 Z"), "#A36D37", sil=False)     # dessus éclairé
    d.raw(line("M18,19 Q24,18 30,19.4 M36,21.8 Q43,20.6 50,22 M22,23.6 L30,23.6 M42,16.8 Q47,16 52,17.4",
               "#6E4428", 0.9))
    d.raw(line("M55,13 Q58.4,18 55,23.5", "#6E4428", 0.8))                                 # bout arrondi
    # petite branche cassée
    d.add(poly([(46, 10.5), (49, 10.5), (51.5, 5.2), (49, 4.4)]), "#8A5A3A")
    d.add(ellipse(50.25, 4.8, 1.5, 0.9, tr="rotate(25 50.25 4.8)"), "#E8C48A", sil=False)
    # bout coupé
    d.add(ellipse(10, 18, 6, 8.6), "#E8C48A", edge=True)
    d.raw(_ring(10, 18, 4.1, 6.0, "#C98A4B", 0.8))
    d.raw(_ring(10, 18, 2.1, 3.1, "#C98A4B", 0.8))
    d.add(ellipse(10, 18, 0.7, 0.9), "#A36D37", sil=False)
    # mousse
    d.add(path("M20,10.4 Q21,7 24.5,7.4 Q27,6 29.5,8 Q32,7.8 32.6,10.4 Z"), "#72BE5E")
    d.add(ellipse(25, 8.6, 1.6, 0.8), "#A6DA8C", sil=False)
    # champignon posé sur le dessus
    _amanita(d, 38.5, 10.2, 4.4, 4.6)
    _tuft(d, 57, 27.2)
    return d


def mushrooms():
    """Petit groupe de trois amanites rouges à pois blancs."""
    d = Drawing(32, 32)
    _shadow(d, 15.5, 27.6, 12.5, 2.2)
    _amanita(d, 13, 26.4, 7.2, 9)
    _amanita(d, 23, 27.2, 5, 6, edge=True,
             dots=((-0.4, -0.4, 0.17), (0.3, -0.62, 0.15)))
    _amanita(d, 6.8, 28, 3.6, 4, edge=True, dots=((-0.1, -0.55, 0.2),))
    _tuft(d, 18.4, 28.2, "#4E9A47")
    _tuft(d, 27.6, 28, "#3F8439")
    return d


def _frond(base, ctrl, tip, w, waves):
    """Fronde de fougère : bande le long d'une courbe de Bézier, effilée, bords festonnés (folioles).
    Retourne (forme, tracé de la nervure)."""
    (bx, by), (cx, cy), (tx, ty) = base, ctrl, tip
    left, right = [], []
    N = 40
    for i in range(N + 1):
        t = i / N
        x = (1 - t) ** 2 * bx + 2 * (1 - t) * t * cx + t * t * tx
        y = (1 - t) ** 2 * by + 2 * (1 - t) * t * cy + t * t * ty
        dx = 2 * (1 - t) * (cx - bx) + 2 * t * (tx - cx)
        dy = 2 * (1 - t) * (cy - by) + 2 * t * (ty - cy)
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        prof = w * math.sin(math.pi * (0.12 + 0.88 * t)) * (0.68 + 0.32 * abs(math.sin(waves * math.pi * t)))
        if t < 0.08:
            prof *= 0.45
        left.append((x + nx * prof, y + ny * prof))
        right.append((x - nx * prof, y - ny * prof))
    shape = poly(left + right[::-1])
    rib = f"M{bx},{by} Q{cx},{cy} {tx},{ty}"
    return shape, rib


def fern():
    """Touffe de fougère : frondes arquées, celles du fond plus sombres."""
    d = Drawing(32, 32)
    _shadow(d, 16, 28, 11, 2.2)
    B = (16, 27.5)
    back = [((6, 15), (2.4, 22.6), 2.6), ((26, 15), (29.6, 22.6), 2.6), ((17, 12), (19.5, 3), 2.6)]
    front = [((8, 8.5), (3.4, 9.4), 3.0), ((24, 8.5), (28.6, 9.4), 3.0), ((12.5, 18), (6.2, 20.4), 2.4),
             ((19.5, 18), (25.8, 20.4), 2.4)]
    for ctrl, tip, w in back:
        s, rib = _frond(B, ctrl, tip, w, 7)
        d.add(s, "#3F8439")
        d.raw(line(rib, "#4E9A47", 0.7))
    for k, (ctrl, tip, w) in enumerate(front):
        s, rib = _frond(B, ctrl, tip, w, 7 if k < 2 else 5)
        d.add(s, "#4E9A47" if k < 2 else "#5BAA4F")
        d.raw(line(rib, "#72BE5E" if k < 2 else "#8ACD70", 0.8))
    d.add(ellipse(16, 27, 3, 1.4), "#3F8439")
    return d


# ================================================================== PARC ET AIRE DE JEUX
def slide():
    """Toboggan vu de profil : échelle à gauche, plateforme avec arceau, glissière jaune qui descend à droite."""
    d = Drawing(64, 64)
    _shadow(d, 33, 60, 28, 3)
    blue, blue_dk = "#2E6FD1", "#23579F"
    # poteau sous la plateforme et pied au bout de la glissière (derrière)
    d.add(rect(25.2, 19, 2.8, 41, 1), blue_dk)
    d.add(rect(52.4, 50, 2.8, 10, 1), blue_dk)
    # garde-corps (arceau) au-dessus de la plateforme
    _tube(d, "M10.8,17 L10.8,9 Q10.8,6 13.8,6 L24,6 Q27,6 27,9 L27,17", "#F7D154", 1.8)
    # glissière : bande le long d'une courbe, surface jaune + flanc rouge
    P = [(26, 17.5), (38, 17.5), (42, 50.5), (58, 50.5)]

    def bez(t):
        return tuple((1 - t) ** 3 * P[0][i] + 3 * (1 - t) ** 2 * t * P[1][i] + 3 * (1 - t) * t * t * P[2][i]
                     + t ** 3 * P[3][i] for i in range(2))

    pts = [bez(i / 30) for i in range(31)]

    def band(o0, o1):
        return poly([(x, y + o0) for x, y in pts] + [(x, y + o1) for x, y in pts[::-1]])

    d.add(band(-3.4, 3.4), "#D7332B")                                  # flanc (silhouette)
    d.add(circle(58, 50.5, 3.4), "#D7332B")                            # bout arrondi
    d.clip("tob", [band(-3.4, 3.4), circle(58, 50.5, 3.4)])
    d.add(band(-3.4, -0.2), "#F2C14E", sil=False)                     # surface de glisse
    d.add(ellipse(58, 48.9, 3.4, 1.6), "#F2C14E", sil=False, clip="tob")
    d.raw(line("M" + " L".join(f"{x:.1f},{y - 2.1:.1f}" for x, y in pts[2:28]), "#FFF0B0", 0.9))
    d.raw(line("M" + " L".join(f"{x:.1f},{y + 1.8:.1f}" for x, y in pts[4:29]), "#A82520", 0.7))
    # plateforme
    d.add(rect(7, 15.5, 22, 4.6, 1.2), "#D7332B")
    d.add(rect(7.6, 16.1, 20.8, 1.4, 0.7), "#E24B4B", sil=False)
    # échelle inclinée : deux montants bleus et barreaux jaunes
    d.add(leg(9.6, 18, 4.6, 60, 2.8), blue)
    d.add(leg(18.2, 18, 13.2, 60, 2.8), blue)
    for k in range(5):
        y = 25 + k * 7.2
        x = 9.6 - (y - 18) * 5 / 42
        d.add(rect(x + 0.6, y, 7.4, 2.1, 0.8), "#F7D154")
    for x0, x1 in ((3.2, 6.0), (11.8, 14.6), (51, 56.6)):            # patins au sol
        d.add(rect(x0, 59, x1 - x0, 1.6, 0.8), blue_dk)
    return d


def swing():
    """Balançoire : portique en A (montants bleus, poutre rouge), deux sièges suspendus par des cordes."""
    d = Drawing(64, 64)
    _shadow(d, 32, 60, 30, 3)
    _shadow(d, 24, 51.5, 6, 1.4)
    _shadow(d, 40, 51.5, 6, 1.4)
    blue = "#2E6FD1"
    # montants en A (pieds écartés), avec traverse
    for cx, s in ((9.5, 1), (54.5, -1)):
        d.add(leg(cx, 9, cx - 6.5 * s, 60, 3.2), blue)
        d.add(leg(cx, 9, cx + 6.5 * s, 60, 3.2), blue)
        d.add(rect(cx - 4.6, 38.5, 9.2, 2.4, 1), blue)
    # poutre
    d.add(rect(4, 6, 56, 5, 1.8), "#D7332B")
    d.add(rect(5, 6.6, 54, 1.4, 0.7), "#E24B4B", sil=False)
    for cx in (9.5, 54.5):
        d.add(circle(cx, 8.5, 1.4), "#F7D154", sil=False)
    # cordes et sièges
    for cx, col, dk in ((24, "#F2C14E", "#D9A43A"), (40, "#2EA3D1", "#2382A8")):
        for rx in (cx - 4.2, cx + 4.2):
            d.add(rect(rx - 0.6, 10.5, 1.2, 32.5, 0.6), "#C9A26D")
            d.add(circle(rx, 11, 1.1), "#A3A8AD")
        d.add(rect(cx - 6, 42.4, 12, 3.4, 1.4), col)
        d.add(rect(cx - 5.4, 44.2, 10.8, 1.2, 0.6), dk, sil=False)
    _tuft(d, 32, 60.4)
    return d


def sandbox():
    """Bac à sable posé à plat : bordure en bois, sable, seau, pelle et petit château."""
    d = Drawing(64, 48)
    d.under.append('<rect x="4" y="40.5" width="58" height="5.5" rx="2.7" fill="#000" opacity="0.18"/>')
    # bordure : dessus des planches + face avant (épaisseur)
    d.add(rect(3, 9, 58, 31, 4), "#C98A4B")
    d.add(rect(3, 37.5, 58, 6.5, 3), "#A36D37", edge=True)
    d.raw(line("M6,40.8 L58,40.8", "#8A5A3A", 0.8))
    d.raw(line("M3.6,9.6 L8.6,13.6 M60.4,9.6 L55.4,13.6 M3.6,36.4 L8.6,33 M60.4,36.4 L55.4,33",
               "#A36D37", 0.9))
    for x, y in ((6, 11.5), (58, 11.5), (6, 35), (58, 35)):
        d.add(circle(x, y, 0.7), "#8A5A3A", sil=False)
    # sable
    d.add(rect(8.5, 13.5, 47, 20, 2.5), "#F3DFA8", sil=False, edge=True)
    d.add(rect(9, 14, 46, 2.6, 1.2), "#D9BE80", sil=False, opacity=0.8)        # ombre de la bordure du fond
    for x, y in ((14, 21), (26, 18.5), (31, 29), (22, 27.5), (51, 30.5), (12, 29.5), (34, 19)):
        d.raw(line(f"M{x - 1.2},{y} Q{x},{y - 0.9} {x + 1.2},{y}", "#DCC07E", 0.8))
    # château de sable (une seule forme : tours crénelées + mur)
    sand, sand_dk = "#E8C873", "#C9A24E"

    def tower(xa, xb, t):
        c = 1.5
        return [(xa, t - c), (xa + c, t - c), (xa + c, t), (xb - c, t), (xb - c, t - c), (xb, t - c)]

    pts = ([(36, 30)] + tower(36, 41, 18.5) + [(41, 22), (42, 22)] + tower(42, 47.5, 15)
           + [(47.5, 22), (48.5, 22)] + tower(48.5, 53.5, 18.5) + [(53.5, 30)])
    d.add(poly(pts), sand, edge=True)
    d.add(path("M42.6,30 L42.6,26.4 Q44.75,24 46.9,26.4 L46.9,30 Z"), sand_dk, sil=False)
    d.raw(line("M37.2,24.5 L40,24.5 M49.6,24.5 L52.4,24.5 M44.75,17.5 L44.75,20", sand_dk, 0.8))
    d.raw(line("M44.75,13.4 L44.75,7.6", OUTLINE, 0.9))
    d.add(poly([(45.1, 7.6), (49.4, 9), (45.1, 10.4)]), "#E24B4B", edge=True)
    # seau
    d.add(poly([(12.8, 20.5), (21.2, 20.5), (20, 29.5), (14, 29.5)]), "#E24B4B", sil=False, edge=True)
    d.add(rect(13.3, 24, 7.4, 1.4, 0.6), "#F7D154", sil=False)
    d.add(ellipse(17, 20.5, 4.2, 1.5), "#A82520", sil=False, edge=True)
    d.raw(line("M12.9,20.8 Q17,14.2 21.1,20.8", OUTLINE, 2.0))
    d.raw(line("M12.9,20.8 Q17,14.2 21.1,20.8", "#2E6FD1", 0.9))
    # pelle couchée sur le sable
    d.add(rect(22.5, 29.3, 9.4, 1.8, 0.9, tr="rotate(-18 27 30.2)"), "#F7D154", sil=False, edge=True)
    d.add(path("M31.4,26.4 Q35.6,24.4 36.8,27.4 Q35.4,30.6 32.6,29.4 Z"), "#2E6FD1", sil=False, edge=True)
    return d


def _bezier(p0, c, p1, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1])


def fountain(phase=0.0):
    """Fontaine : bassin rond en pierre, vasque sur une colonne, jet d'eau qui retombe en gerbe.
    phase (0..1) anime l'eau : le jet monte et descend, des gouttes glissent le long de la gerbe et des filets,
    les éclaboussures palpitent et des ronds s'élargissent dans le bassin (ANIMATED)."""
    d = Drawing(64, 64)
    _shadow(d, 33, 52, 30, 8)
    stone, stone_lt, stone_dk = "#A3A8AD", "#C4C8CC", "#7D8288"
    water, water_dk, water_lt = "#9FD3F0", "#6DB6E3", "#DDF3FC"
    wave = lambda off=0.0: math.sin(2 * math.pi * (phase + off))
    # bassin : paroi avant + margelle
    d.add(path("M5,40 L5,47 A27,11 0 0 0 59,47 L59,40 Z"), stone)
    for x in (12, 22, 32, 42, 52):
        y = 47 + 11 * math.sqrt(max(0, 1 - ((x - 32) / 27) ** 2))
        d.raw(line(f"M{x},{y - 6.5:.1f} L{x},{y - 0.8:.1f}", stone_dk, 0.8))
    d.add(ellipse(32, 40, 27, 11), stone_lt, edge=True)
    # eau du bassin (paroi intérieure du fond visible au-dessus) ; des ronds s'élargissent et s'effacent
    inner = ellipse(32, 40.5, 22.5, 8.2)
    d.clip("fontaine_in", [inner])
    d.add(inner, stone_dk, sil=False, edge=True)
    d.add(ellipse(32, 42.6, 23, 7.6), water, sil=False, clip="fontaine_in")
    for k in range(2):
        f = (phase + k / 2) % 1
        rx = 6 + 15 * f
        d.raw(f'<g clip-path="url(#fontaine_in)" opacity="{1 - f:.2f}">'
              + _ring(32, 44.2, rx, rx * 0.29, water_lt if k == 0 else water_dk, 0.9) + "</g>")
    # colonne et vasque
    d.add(rect(29.6, 26, 4.8, 18, 1), stone, edge=True)
    d.add(rect(30.4, 27, 1.2, 15, 0.6), stone_lt, sil=False)
    d.raw(_ring(32, 43.6, 4.6, 1.4, water_lt, 0.9))
    d.add(path("M22,24 Q22.5,30.5 32,30.5 Q41.5,30.5 42,24 Z"), stone, edge=True)
    d.add(ellipse(32, 24, 10, 3), stone_lt, edge=True)
    d.add(ellipse(32, 24.3, 8, 2), water, sil=False)
    # gerbe : jet central qui retombe dans la vasque, filets qui débordent dans le bassin
    arcs = []
    for s in (-1, 1):
        up = ((32, 8.5), (32 + 8 * s, 6.5), (32 + 9.5 * s, 22.5))
        over = ((32 + 9.6 * s, 26), (32 + 13.5 * s, 27), (32 + 14.2 * s, 37.5))
        arcs += [(up, 3, 1.0), (over, 2, 1.3)]
        _tube(d, f"M{up[0][0]},{up[0][1]} Q{up[1][0]},{up[1][1]} {up[2][0]},{up[2][1]}", water, 1.6)
        _tube(d, f"M{over[0][0]},{over[0][1]} Q{over[1][0]},{over[1][1]} {over[2][0]},{over[2][1]}", water, 1.4)
    top = 6.4 - 0.9 * wave()
    d.add(path(f"M30.4,24 Q30,15 32,{top:.2f} Q34,15 33.6,24 Z"), water)
    d.raw(line(f"M31.9,21 L31.9,{top + 4.6:.2f}", "#FFFFFF", 0.8))
    # gouttes qui glissent le long des filets
    for (p0, c, p1), n, speed in arcs:
        for k in range(n):
            x, y = _bezier(p0, c, p1, (phase * speed + k / n) % 1)
            d.add(circle(x, y, 0.7), "#FFFFFF", sil=False, opacity=0.9)
    # éclaboussures qui palpitent, embruns en haut du jet
    for i, (x, y, r) in enumerate(((22.2, 21.4, 0.9), (41.8, 21.4, 0.9), (17.2, 38.6, 1.0), (46.8, 38.6, 1.0))):
        d.add(circle(x, y, r * (1 + 0.35 * wave(i / 4))), water_lt, sil=False)
    for x in (26, 38):
        d.add(circle(x, 10.5 - 1.2 * wave(0.25), 0.7), water_lt, sil=False)
    return d


def playhouse():
    """Cabane de jeu en bois peint : murs jaunes, toit rouge à pignon, porte ouverte, fenêtre fleurie."""
    d = Drawing(64, 64)
    _shadow(d, 32, 60, 26, 3)
    wall, wall_dk = "#F7D154", "#E3B94F"
    # murs + pignon
    d.add(path("M11,60 L11,33 L32,15 L53,33 L53,60 Z"), wall)
    for y in (38, 44, 50, 56):
        d.raw(line(f"M11.6,{y} L52.4,{y}", wall_dk, 0.8))
    d.add(rect(11, 33, 42, 3, 0), "#000000", sil=False, opacity=0.15)          # ombre sous le toit
    # toit en chevron
    d.add(path("M3.5,34 L32,6 L60.5,34 L55.4,38.4 L32,15.6 L8.6,38.4 Z"), "#D7332B")
    d.raw(line("M8.4,31.6 L32,8.6 L55.6,31.6", "#E24B4B", 1.0))
    for k in range(1, 4):
        t = k / 4
        for s in (-1, 1):
            xo, yo = 32 + s * 28.5 * t, 6 + 28 * t
            xi, yi = 32 + s * 23.4 * t, 15.6 + 22.8 * t
            d.raw(line(f"M{xo:.1f},{yo:.1f} L{xi:.1f},{yi:.1f}", "#A82520", 0.8))
    d.add(circle(32, 7.4, 2), "#F7D154")                                       # boule au faîte
    # coeur sur le pignon
    d.add(path("M32,29.2 C27.6,26 28.4,21.8 30.4,21.8 Q31.6,21.8 32,23.2 Q32.4,21.8 33.6,21.8 "
               "C35.6,21.8 36.4,26 32,29.2 Z"), "#E24B4B", sil=False, edge=True)
    # porte ouverte (intérieur un peu sombre) + battant bleu rabattu à gauche
    d.add(path("M24.5,60 L24.5,43 Q24.5,38.6 30.5,38.6 Q36.5,38.6 36.5,43 L36.5,60 Z"), "#5A3A28",
          sil=False, edge=True)
    d.add(path("M25.4,60 L25.4,43.4 Q25.4,40 30.5,40 Q31.4,40 32,40.1 L32,60 Z"), "#3A2418", sil=False)
    d.add(rect(25.6, 56.4, 10.2, 3.4, 0), "#7A5236", sil=False)               # plancher
    d.add(path("M24.5,43 Q22,40.8 18.8,41.6 L18.8,61 L24.5,60 Z"), "#2E6FD1", edge=True)
    d.add(rect(20.2, 44.6, 2.9, 6, 0.8), "#23579F", sil=False)
    d.add(circle(21, 52.6, 0.9), "#F7D154", sil=False)
    # fenêtre avec volet et jardinière
    d.add(rect(40.5, 40.5, 9.6, 9, 1.2), "#9FD3F0", sil=False, edge=True)
    d.raw(line("M45.3,40.5 L45.3,49.5 M40.5,45 L50.1,45", "#FFFFFF", 1.1))
    d.add(rect(39.6, 49.4, 11.4, 3, 1), "#C98A4B", edge=True)
    for k, col in enumerate(("#E24B4B", "#FFFFFF", "#E24B4B", "#FFFFFF")):
        d.add(circle(41.6 + k * 2.5, 49.2, 1.2), col, sil=False)
    # bas des murs et marche
    d.add(rect(11, 58, 42, 2, 0), wall_dk, sil=False)
    d.add(rect(24, 59.2, 13, 2.6, 1), "#B7B2A8")
    _tuft(d, 12.5, 60.6)
    _tuft(d, 52, 60.6)
    return d


# décors animés : nom -> (nombre d'images, images par seconde) ; la fonction reçoit la phase 0..1
def burrow():
    """Terrier creusé sous un grillage (posé à plat) : monticule de terre, trou sombre, quelques mottes.
    Tecky peut s'y glisser pour passer de l'autre côté."""
    d = Drawing(40, 24)
    d.add(ellipse(20, 14, 17, 7.5), "#B98F58")
    d.add(ellipse(20, 13, 13, 5), "#9C6B3F", sil=False)
    d.add(ellipse(20, 13.6, 9, 3.6), "#3A2418", sil=False)
    d.add(ellipse(20, 12.6, 6.5, 1.8), "#5A3A26", sil=False, opacity=0.8)
    for x, y, r in ((5.5, 17.5, 2.2), (34, 16.5, 2.6), (30, 20, 1.6), (9, 20.4, 1.4), (24, 20.6, 1.8)):
        d.add(ellipse(x, y, r * 1.2, r), "#A97C4A", sil=False, edge=True)
    return d


ANIMATED = {"fountain": (8, 10)}


def frames(name):
    """Images d'un décor (une seule, sauf pour les décors animés)."""
    fn = DECOR[name][0]
    if name in ANIMATED:
        n = ANIMATED[name][0]
        return [fn(i / n) for i in range(n)]
    return [fn()]


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
    "container_blue": (lambda: container("blue"), (96, 48), (48, 44)),
    "container_green": (lambda: container("green"), (96, 48), (48, 44)),
    "container_stack": (container_stack, (96, 74), (48, 70)),
    "truck": (truck, (112, 64), (56, 58)),
    "forklift": (forklift, (56, 56), (28, 52)),
    "crane": (crane, (208, 128), (104, 124)),
    "guard_hut": (guard_hut, (64, 64), (32, 58)),
    "bollard": (bollard, (32, 32), (16, 28)),
    "barge": (barge, (176, 48), (88, 42)),
    "goal_net": (goal_net, (96, 64), (48, 60)),
    "leaf_nest": (leaf_nest, (48, 32), (24, 28)),
    "rail": (rail, (32, 32), (0, 16)),
    "buffer_stop": (buffer_stop, (32, 40), (16, 36)),
    "pallet": (pallet, (32, 32), (16, 27)),
    "barrel_blue": (barrel, (32, 32), (16, 29)),
    "barrel_red": (barrel_red, (32, 32), (16, 29)),
    "crate": (crate, (32, 32), (16, 28)),
    "fence_metal_h": (fence_metal_h, (32, 32), (0, 28)),
    "fence_metal_v": (fence_metal_v, (32, 32), (16, 32)),
    # ferme et rivière
    "barn": (barn, (128, 112), (64, 108)),
    "chicken_coop": (chicken_coop, (64, 64), (32, 60)),
    "tractor": (tractor, (64, 48), (32, 44)),
    "scarecrow": (scarecrow, (32, 64), (16, 60)),
    "bridge": (bridge, (96, 160), (48, 160)),
    "reeds": (reeds, (32, 32), (16, 28)),
    "boat": (boat, (64, 32), (32, 26)),
    # forêt et parc
    "fir": (fir, (64, 80), (32, 76)),
    "stump": (stump, (32, 32), (16, 27)),
    "log": (log, (64, 32), (32, 27)),
    "mushrooms": (mushrooms, (32, 32), (16, 28)),
    "fern": (fern, (32, 32), (16, 28)),
    "slide": (slide, (64, 64), (32, 60)),
    "swing": (swing, (64, 64), (32, 60)),
    "sandbox": (sandbox, (64, 48), (32, 44)),
    "burrow": (burrow, (40, 24), (20, 13)),
    "fountain": (fountain, (64, 64), (32, 58)),
    "playhouse": (playhouse, (64, 64), (32, 60)),
}

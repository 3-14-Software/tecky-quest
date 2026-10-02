"""
Véhicules de la grande route, de profil tournés vers la droite (la vue gauche est le miroir) :
petite voiture (4 couleurs), camionnette de boulangerie, bus. 4 images : les enjoliveurs tournent.
Et Titine, le petit train du port : locomotive à vapeur et trois wagons porte-conteneurs (sur les rails du quai).
Origine au sol, sous les roues (VEHICLES).
"""
import math

from spritelib import Drawing, circle, ellipse, rect, poly, path, line

CAR_COLORS = {   # nom : (carrosserie, ombre)
    "red": ("#D7332B", "#A82520"),
    "blue": ("#2E6FD1", "#23579F"),
    "yellow": ("#F2C14E", "#D4A23A"),
    "green": ("#4E9A47", "#3F8439"),
}
GLASS = "#9FD3F0"
TYRE, HUB = "#3A3A42", "#C9CED6"


def _wheel(d, cx, cy, r, spin):
    d.add(circle(cx, cy, r), TYRE)
    d.add(circle(cx, cy, r * 0.5), HUB, sil=False, edge=True)
    for k in range(3):                                       # rayons de l'enjoliveur : ils tournent
        a = math.radians(spin + k * 120)
        d.raw(line(f"M{cx:.2f},{cy:.2f} L{cx + r * 0.45 * math.cos(a):.2f},{cy + r * 0.45 * math.sin(a):.2f}", "#8C9098", 0.9))


def _shadow(d, x0, x1, y):
    d.under.append(f'<rect x="{x0}" y="{y - 2}" width="{x1 - x0}" height="4" rx="2" fill="#000" opacity="0.22"/>')


def car(color, spin=0):
    """Petite voiture 64x40 : carrosserie arrondie, deux vitres, phare, feu arrière."""
    body, dark = CAR_COLORS[color]
    d = Drawing(64, 40)
    _shadow(d, 6, 59, 38.6)
    d.add(path("M5,31 L5,23.5 Q5,20 9,20 L17,20 L22.5,10.5 Q23.6,8.5 26.5,8.5 L41,8.5 Q44,8.5 45.6,11 "
               "L51,20 L56,20 Q60.5,21 60.5,25.5 L60.5,31 Q60.5,33 58.5,33 L7,33 Q5,33 5,31 Z"), body)
    d.add(path("M5.2,28 L60.3,28 L60.3,31 Q60.3,33 58.5,33 L7,33 Q5.2,33 5.2,31 Z"), dark, sil=False)
    d.add(poly([(24, 11), (32, 11), (32, 19.2), (19.6, 19.2)]), GLASS, sil=False, edge=True)
    d.add(poly([(34.2, 11), (43, 11), (48.2, 19.2), (34.2, 19.2)]), GLASS, sil=False, edge=True)
    d.raw(line("M25.6,17.4 L29.4,12.6 M36.5,17.4 L40.4,12.6", "#FFFFFF", 0.9))      # reflets
    d.raw(line("M33.1,20.5 L33.1,27.5", dark, 0.8))                                  # portière
    d.add(rect(35, 22, 3.4, 1.2, 0.6), dark, sil=False)
    d.add(rect(9, 21.6, 46, 1.4, 0.7), "#FFFFFF", sil=False, opacity=0.3)
    d.add(ellipse(58.6, 23.6, 1.7, 1.3), "#FFF1B8", sil=False, edge=True)           # phare
    d.add(rect(5.2, 21.8, 2, 3.2, 0.8), "#E24B4B", sil=False)                        # feu arrière
    d.add(rect(3, 29, 4.4, 2.8, 1.2), "#B7B2A8")
    d.add(rect(57.8, 29, 4.4, 2.8, 1.2), "#B7B2A8")
    for x in (16, 49):
        _wheel(d, x, 33, 5.6, spin)
    return d


def van(spin=0):
    """Camionnette de boulangerie 80x48 : caisse crème peinte d'une baguette et d'un croissant, cabine à droite."""
    body, dark, accent = "#F3E7CF", "#D9C8A2", "#C8553D"
    d = Drawing(80, 48)
    _shadow(d, 5, 75, 44.4)
    d.add(rect(4, 6, 52, 32, 2.5), body)                                              # caisse
    d.add(path("M55,16 L67,16 Q70,16 71.5,19 L75.5,27 Q76.5,29 76.5,31 L76.5,36 Q76.5,38 74.5,38 L55,38 Z"), body)
    d.add(rect(4, 31, 72.5, 7, 1.5), accent, sil=False)                               # bande rouge
    d.add(poly([(58, 19), (66.5, 19), (71.5, 27.5), (58, 27.5)]), GLASS, sil=False, edge=True)
    d.raw(line("M60.5,25.5 L64.5,20.8", "#FFFFFF", 0.9))
    d.add(rect(7, 9, 46, 19, 2), "#FFF7E6", sil=False, edge=True)                     # panneau peint
    # baguette (en biais) et croissant
    d.add(ellipse(22, 19, 13, 3.4, "rotate(-14 22 19)"), "#D9A55B", sil=False, edge=True)
    for x in (14, 19, 24, 29):
        d.raw(f'<g transform="rotate(-14 22 19)">' + line(f"M{x},17.4 L{x + 2.6},20.2", "#B07A3A", 0.9) + "</g>")
    d.add(path("M38,22.5 Q39,13 46.5,13.5 Q50.5,14.5 50,18.5 Q46,15.8 42.5,18.5 Q41,20.5 41.5,23.5 Z"),
          "#E3A954", sil=False, edge=True)
    d.add(ellipse(73.6, 30.2, 1.6, 1.3), "#FFF1B8", sil=False, edge=True)             # phare
    d.add(rect(4, 26, 1.8, 3.4, 0.8), "#E24B4B", sil=False)
    d.add(rect(2.6, 35, 4.6, 3, 1.2), "#B7B2A8")
    d.add(rect(73.6, 35, 4.6, 3, 1.2), "#B7B2A8")
    for x in (18, 63):
        _wheel(d, x, 38, 6, spin)
    return d


def bus(spin=0):
    """Bus bleu 128x56 : longue rangée de fenêtres, porte à l'avant, girouette au-dessus du pare-brise."""
    body, dark = "#2E6FD1", "#23579F"
    d = Drawing(128, 56)
    _shadow(d, 6, 123, 52.6)
    d.add(path("M4,44 L4,10 Q4,6 8,6 L116,6 Q122,6 123,11 L124.5,40 Q124.5,46 120,46 L8,46 Q4,46 4,44 Z"), body)
    d.add(rect(4.2, 36, 120.2, 3, 0), "#FFFFFF", sil=False, opacity=0.85)            # bande blanche
    d.add(rect(4.2, 39, 120.2, 7, 0), dark, sil=False)
    for k in range(6):                                                                # fenêtres passagers
        x = 9 + k * 15
        d.add(rect(x, 12, 12, 13, 1.5), GLASS, sil=False, edge=True)
        d.raw(line(f"M{x + 2.5},22.5 L{x + 7},14.5", "#FFFFFF", 0.8))
    d.add(rect(100, 12, 9, 24, 1.2), GLASS, sil=False, edge=True)                     # porte
    d.raw(line("M104.5,12.5 L104.5,35.5", dark, 0.9))
    d.add(path("M111.5,12 L119.5,12 Q121.5,12 121.8,14 L122.6,26 L111.5,26 Z"), GLASS, sil=False, edge=True)
    d.add(rect(110, 7.6, 12, 3.2, 1), "#2B2B33", sil=False)                           # girouette
    for x in (111.6, 114.4, 117.2, 120):
        d.add(circle(x, 9.2, 0.6), "#F7D154", sil=False)
    d.add(ellipse(122.4, 33, 1.6, 1.4), "#FFF1B8", sil=False, edge=True)
    d.add(rect(4.2, 29, 2, 4, 0.8), "#E24B4B", sil=False)
    for x in (26, 102):
        _wheel(d, x, 46, 7, spin)
    return d


def loco(spin=0):
    """Titine, petite locomotive à vapeur rouge 64x48, tournée vers la droite : cabine à l'arrière, chaudière, cheminée
    à bord doré, cloche, chasse-pierres, trois roues rouges à rayons."""
    red, dark, gold = "#D7332B", "#A82520", "#F2C14E"
    d = Drawing(64, 48)
    _shadow(d, 4, 60, 44.4)
    d.add(rect(5, 6, 18, 4, 1.5), "#2B2B33")                                          # toit de la cabine
    d.add(rect(7, 9, 15, 26, 1.5), red)                                               # cabine
    d.add(rect(10, 13, 9, 8, 1.5), GLASS, sil=False, edge=True)
    d.raw(line("M12,19 L16.5,14.5", "#FFFFFF", 0.9))
    d.add(rect(21, 18, 33, 15, 7.5), red)                                             # chaudière
    d.add(rect(21, 18, 33, 4, 2), "#FFFFFF", sil=False, opacity=0.25)
    for x in (31, 42):                                                                # cerclages dorés
        d.add(rect(x, 18, 2, 15, 0), gold, sil=False)
    d.add(rect(45, 7, 6.5, 12, 1), "#2B2B33")                                         # cheminée
    d.add(rect(43.6, 5, 9.3, 3.2, 1.2), gold, edge=True)
    d.add(path("M33,18 Q33,12.5 36.5,12.5 Q40,12.5 40,18 Z"), gold)                   # dôme (cloche)
    d.add(circle(54.5, 25.5, 2.4), "#FFF1B8", sil=False, edge=True)                   # phare
    d.add(rect(5, 32, 52, 4, 1), "#2B2B33")                                           # châssis
    d.add(poly([(56, 32), (62, 40), (56, 40)]), "#5C6168")                            # chasse-pierres
    for x, r in ((16, 6.4), (31, 6.4), (45, 5.4)):
        y = 44 - r
        d.add(circle(x, y, r), red)
        d.add(circle(x, y, r * 0.35), gold, sil=False, edge=True)
        for k in range(4):
            a = math.radians(spin * 1.5 + k * 45)
            d.raw(line(f"M{x - r * 0.8 * math.cos(a):.2f},{y - r * 0.8 * math.sin(a):.2f} "
                       f"L{x + r * 0.8 * math.cos(a):.2f},{y + r * 0.8 * math.sin(a):.2f}", dark, 0.9))
    d.raw(line("M16,38 L45,38.6", "#5C6168", 1.6))                                    # bielle
    return d


WAGON_COLORS = {"blue": ("#2E6FD1", "#23579F"), "green": ("#3F9A5B", "#2F7A46"), "orange": ("#D9772B", "#B9601E")}


def wagon(color, spin=0):
    """Wagon plat 48x40 portant un petit conteneur de couleur, attelages de chaque côté."""
    col, rib = WAGON_COLORS[color]
    d = Drawing(48, 40)
    _shadow(d, 4, 44, 36.6)
    d.add(rect(6, 9, 36, 20, 0.5), col)                                               # conteneur
    for x in range(9, 41, 3):
        d.raw(line(f"M{x},10 L{x},28", rib, 0.7))
    d.add(rect(6, 7, 36, 4, 0.5), col)
    d.add(rect(6, 7, 36, 4, 0.5), "#FFFFFF", sil=False, opacity=0.25)
    d.add(rect(3, 28, 42, 3.6, 1), "#4A4F57")                                         # plateau
    d.add(rect(0.6, 28.6, 3, 2.2, 0.8), "#2B2B33")                                    # attelages
    d.add(rect(44.4, 28.6, 3, 2.2, 0.8), "#2B2B33")
    for x in (12, 36):
        _wheel(d, x, 32.4, 4.2, spin)
    return d


SPINS = (0, 30, 60, 90)          # 3 rayons : un tour d'enjoliveur tous les 120°
VEHICLES = {   # nom : (fonction(spin), (largeur, hauteur) 1x, origine 1x)
    **{f"car_{c}": ((lambda c: lambda s: car(c, s))(c), (64, 40), (32, 38.6)) for c in CAR_COLORS},
    "van": (van, (80, 48), (40, 44.4)),
    "bus": (bus, (128, 56), (64, 52.6)),
    "loco": (loco, (64, 48), (32, 44.4)),
    **{f"wagon_{c}": ((lambda c: lambda s: wagon(c, s))(c), (48, 40), (24, 36.6)) for c in WAGON_COLORS},
}


def frames(name):
    fn, _, _ = VEHICLES[name]
    return [fn(s).svg() for s in SPINS]

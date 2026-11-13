"""
Véhicules de la grande route, de profil tournés vers la droite (la vue gauche est le miroir) :
petite voiture (4 couleurs), camionnette de boulangerie, bus. 4 images : les enjoliveurs tournent.
Version 2 (lot 4) : mêmes cadres, mêmes silhouettes, mêmes roues ; la lumière vient d'en haut (dessus clairs, bas de
caisse à l'ombre : elle reste juste quand le véhicule est en miroir), passages de roue, et du monde derrière les
vitres (_tete()).
Et Titine, le petit train du port : locomotive à vapeur et trois wagons porte-conteneurs (sur les rails du quai).
Origine au sol, sous les roues (VEHICLES).
"""
import math

from spritelib import Drawing, circle, ellipse, rect, poly, path, line, OUTLINE_W

CAR_COLORS = {   # nom : (carrosserie, ombre)
    "red": ("#D7332B", "#A82520"),
    "blue": ("#2E6FD1", "#23579F"),
    "yellow": ("#F2C14E", "#D4A23A"),
    "green": ("#4E9A47", "#3F8439"),
}
GLASS = "#9FD3F0"
TYRE, HUB = "#3A3A42", "#C9CED6"


def _clair(couleur, k=0.38):
    """La même couleur, éclaircie (le dessus d'une carrosserie, au soleil)."""
    return "#" + "".join(f"{round(int(couleur[i:i + 2], 16) + (255 - int(couleur[i:i + 2], 16)) * k):02X}" for i in (1, 3, 5))


def _wheel(d, cx, cy, r, spin, jante=HUB):
    """Roue : pneu, jante bordée, trois rayons qui tournent, moyeu ; un reflet sur le haut du pneu."""
    d.add(circle(cx, cy, r), TYRE)
    d.raw(line(f"M{cx - r * 0.62:.2f},{cy - r * 0.62:.2f} A{r * 0.88:.2f},{r * 0.88:.2f} 0 0 1 {cx + r * 0.62:.2f},{cy - r * 0.62:.2f}", "#5E5E68", 0.8))
    d.add(circle(cx, cy, r * 0.56), jante, sil=False, edge=True)
    for k in range(3):                                       # rayons de l'enjoliveur : ils tournent
        a = math.radians(spin + k * 120)
        d.raw(line(f"M{cx:.2f},{cy:.2f} L{cx + r * 0.5 * math.cos(a):.2f},{cy + r * 0.5 * math.sin(a):.2f}", "#8C9098", 1.0))
    d.add(circle(cx, cy, r * 0.17), "#6A6F7A", sil=False)


def _shadow(d, x0, x1, y):
    d.under.append(f'<rect x="{x0}" y="{y - 2}" width="{x1 - x0}" height="4" rx="2" fill="#000" opacity="0.22"/>')


def _passage(d, cx, cy, r, clip):
    """Passage de roue : l'ombre dans laquelle la roue est logée."""
    d.add(circle(cx, cy, r), "#26262C", sil=False, clip=clip)


PEAUX = ("#F2C9A0", "#D9A679", "#F7D9B8", "#B9825A")
CHEVEUX = ("#6E4528", "#2B2B33", "#E0B24A", "#B8562E", "#8C8C96")


def _tete(d, x, y, r, i, clip, casquette=None):
    """Une tête derrière une vitre, de profil vers la droite : visage, cheveux (ou casquette), un œil."""
    d.add(rect(x - r * 1.1, y + r * 0.8, r * 2.2, r * 3, r * 0.8), ("#5C86C4", "#C8553D", "#6DB758", "#F2C14E")[i % 4], sil=False, clip=clip)
    d.add(circle(x, y, r), PEAUX[i % len(PEAUX)], sil=False, clip=clip)
    if casquette:
        d.add(path(f"M{x - r:.2f},{y - r * 0.2:.2f} A{r},{r} 0 0 1 {x + r:.2f},{y - r * 0.2:.2f} L{x + r * 1.6:.2f},{y - r * 0.1:.2f} "
                   f"L{x + r * 1.6:.2f},{y + r * 0.1:.2f} L{x - r:.2f},{y + r * 0.1:.2f} Z"), casquette, sil=False, clip=clip)
    else:
        d.add(path(f"M{x - r:.2f},{y + r * 0.3:.2f} A{r},{r} 0 0 1 {x + r * 0.8:.2f},{y - r * 0.6:.2f} "
                   f"Q{x:.2f},{y - r * 0.5:.2f} {x - r * 0.35:.2f},{y + r * 0.2:.2f} Z"), CHEVEUX[i % len(CHEVEUX)], sil=False, clip=clip)
    d.add(circle(x + r * 0.45, y + r * 0.05, r * 0.14), "#3A1E12", sil=False, clip=clip)


def _vitre(d, cle, forme, reflet):
    """Une vitre : le verre, le haut plus sombre (l'habitacle), un reflet ; rend son clip."""
    d.clip(cle, [forme])
    d.add(forme, GLASS, sil=False)
    return cle


def _bord(d, forme):
    d.raw(forme.replace('fill="%F%"', 'fill="none" stroke="#3A1E12" stroke-width="0.9" stroke-linejoin="round"'))


def car(color, spin=0):
    """Petite voiture 64x40 : carrosserie arrondie éclairée d'en haut (toit, capot et coffre plus clairs, bas de
    caisse à l'ombre), deux vitres et son conducteur, rétroviseur, poignée, phare, feu arrière, pare-chocs."""
    body, dark = CAR_COLORS[color]
    light = _clair(body)
    d = Drawing(64, 40)
    _shadow(d, 6, 59, 38.6)
    caisse = ("M5,31 L5,23.5 Q5,20 9,20 L17,20 L22.5,10.5 Q23.6,8.5 26.5,8.5 L41,8.5 Q44,8.5 45.6,11 "
              "L51,20 L56,20 Q60.5,21 60.5,25.5 L60.5,31 Q60.5,33 58.5,33 L7,33 Q5,33 5,31 Z")
    d.clip("caisse", [path(caisse)])
    d.add(path(caisse), body)
    d.add(rect(20, 8, 28, 2.2), light, sil=False, clip="caisse")                    # le toit
    d.add(rect(49.5, 19.6, 12, 2.1), light, sil=False, clip="caisse")               # le capot
    d.add(rect(4, 19.6, 13.6, 2.1), light, sil=False, clip="caisse")                # le coffre
    d.add(rect(4, 27.4, 58, 6), dark, sil=False, clip="caisse")                     # le bas de caisse
    for x in (16, 49):
        _passage(d, x, 33, 7.3, "caisse")
    v1, v2 = poly([(24, 11), (32, 11), (32, 19.2), (19.6, 19.2)]), poly([(34.2, 11), (43, 11), (48.2, 19.2), (34.2, 19.2)])
    for cle, v in (("v1", v1), ("v2", v2)):
        _vitre(d, cle, v, None)
    _tete(d, 39.6, 15.6, 2.7, list(CAR_COLORS).index(color), "v2")
    d.raw('<g clip-path="url(#v1)">' + line("M25.6,17.8 L29.6,12.2", "#FFFFFF", 1.0) + "</g>")
    d.raw('<g clip-path="url(#v2)">' + line("M44.4,18.6 L41.2,12.6", "#FFFFFF", 0.8) + "</g>")
    _bord(d, v1)
    _bord(d, v2)
    d.raw(line("M33.1,20.5 L33.1,27.2 M18.6,20.4 L49.6,20.4", dark, 0.7))            # portière, ceinture de caisse
    d.add(rect(35.2, 22.2, 3.6, 1.3, 0.6), light, sil=False)                        # poignée
    d.add(rect(47.2, 17.6, 3, 2.2, 0.9), body, sil=False, edge=True)                # rétroviseur
    d.add(ellipse(58.6, 23.8, 1.8, 1.4), "#FFF1B8", sil=False, edge=True)           # phare
    d.add(rect(5.2, 21.9, 2, 3.2, 0.8), "#E24B4B", sil=False)                        # feu arrière
    for x in (3, 57.8):                                                             # pare-chocs
        d.add(rect(x, 29, 4.4, 2.8, 1.2), "#C4C8D0")
        d.add(rect(x + 0.5, 30.6, 3.4, 1.2, 0.6), "#8E949E", sil=False)
    for x in (16, 49):
        _wheel(d, x, 33, 5.6, spin)
    return d


# ------------------------------------------------------------------ la voiture du papa d'Alice
# Une berline sportive rouge à hayon, relevée sur la photo que Christophe a donnée de la sienne (12 novembre 2026 :
# long capot, pavillon en arc qui file jusqu'au petit becquet, grandes roues) ; sans marque ni logo. _PX, _PY
# convertissent les pixels de la photo (nez à gauche, 366 x 220) en unités du dessin (nez à droite, sol en 38,6).
SPORT = dict(body="#C9242E", dark="#8E161F", light="#E8606A", trim="#26262C", glass=GLASS, phare="#F4F7FA",
             feu="#7A0F16", jante="#D5D9E0", jante_dk="#3A3D45", etrier="#E0413A")
# la photo est étirée d'autant en hauteur : une berline basse, mais où l'on voit ses passagers (choix de Christophe
# sur reference/v2/papa_voiture_options.png : « un peu rehaussée » plutôt que les proportions exactes)
SPORT_K = 1.15


def _PX(x):
    return 6 + (334 - x) * 0.246


def _PY(y, k=SPORT_K):
    return 38.6 - (173 - y) * 0.246 * k


def _lisse(pts):
    """Un contour fermé et lisse qui passe entre les points : chaque point tire la courbe, les milieux sont dessus
    (un point répété deux fois fait un angle)."""
    m = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    n = len(pts)
    x0, y0 = m(pts[-1], pts[0])
    out = f"M{x0:.2f},{y0:.2f} "
    for i in range(n):
        mx, my = m(pts[i], pts[(i + 1) % n])
        out += f"Q{pts[i][0]:.2f},{pts[i][1]:.2f} {mx:.2f},{my:.2f} "
    return out + "Z"


def _roue_sport(d, cx, cy, r, spin):
    """Grande roue à pneu fin : jante sombre à cinq branches doubles claires, étrier de frein rouge (qui ne tourne pas)."""
    c = SPORT
    d.add(circle(cx, cy, r), TYRE)
    d.add(circle(cx, cy, r * 0.76), c["jante_dk"], sil=False, edge=True)
    d.raw(f'<path d="M{cx + r * 0.2:.2f},{cy - r * 0.62:.2f} A{r * 0.65:.2f},{r * 0.65:.2f} 0 0 1 {cx + r * 0.64:.2f},{cy - r * 0.1:.2f}" '
          f'fill="none" stroke="{c["etrier"]}" stroke-width="{r * 0.2:.2f}" stroke-linecap="round"/>')
    for i in range(5):                                       # les branches : elles tournent
        for da in (-9, 9):
            a = math.radians(spin * 0.6 + i * 72 + da)
            d.raw(line(f"M{cx + r * 0.16 * math.cos(a):.2f},{cy + r * 0.16 * math.sin(a):.2f} "
                       f"L{cx + r * 0.72 * math.cos(a):.2f},{cy + r * 0.72 * math.sin(a):.2f}", c["jante"], 0.75))
    d.add(circle(cx, cy, r * 0.17), c["jante"], sil=False)


def _passager(d, qui, x, y, r, clip):
    """Une tête derrière une vitre de la voiture, de profil vers la droite : le papa (cheveux ras, bouc, tee-shirt
    rouge), Alice (carré châtain, tee-shirt jaune) ou Tecky (teckel roux, oreille tombante, harnais rouge)."""
    if qui == "tecky":
        d.add(rect(x - r * 1.0, y + r * 0.7, r * 2.0, r * 3, r * 0.7), "#D7332B", sil=False, clip=clip)              # harnais
        d.add(ellipse(x, y, r * 1.05, r * 0.95), "#C56E2E", sil=False, clip=clip)                                   # crâne
        d.add(ellipse(x + r * 1.15, y + r * 0.35, r * 0.9, r * 0.52), "#D98A45", sil=False, clip=clip)              # museau
        d.add(circle(x + r * 1.95, y + r * 0.2, r * 0.26), "#3A1E12", sil=False, clip=clip)                         # truffe
        d.add(ellipse(x - r * 0.55, y + r * 0.75, r * 0.55, r * 1.15, f"rotate(12 {x - r * 0.55:.2f} {y + r * 0.75:.2f})"),
              "#8E4A1E", sil=False, clip=clip)                                                                      # oreille
        d.add(circle(x + r * 0.45, y - r * 0.1, r * 0.2), "#3A1E12", sil=False, clip=clip)
        return
    peau, cheveux, habit = (("#E9B184", "#2B1A14", "#C9242E") if qui == "papa" else ("#FADFCB", "#B9976B", "#F6D360"))
    d.add(rect(x - r * 1.1, y + r * 0.8, r * 2.2, r * 3, r * 0.8), habit, sil=False, clip=clip)
    if qui == "alice":                                                                                              # le carré, derrière
        d.add(rect(x - r * 1.15, y - r * 0.9, r * 1.5, r * 2.5, r * 0.6), cheveux, sil=False, clip=clip)
    d.add(circle(x, y, r), peau, sil=False, clip=clip)
    if qui == "papa":                                       # cheveux ras : une calotte fine ; un bouc le long de la mâchoire
        d.add(path(f"M{x - r:.2f},{y + r * 0.1:.2f} A{r},{r} 0 0 1 {x + r * 0.86:.2f},{y - r * 0.5:.2f} "
                   f"Q{x:.2f},{y - r * 0.62:.2f} {x - r * 0.62:.2f},{y - r * 0.05:.2f} Z"), cheveux, sil=False, clip=clip)
        d.raw(f'<g clip-path="url(#{clip})">' + line(f"M{x - r * 0.1:.2f},{y + r * 0.92:.2f} Q{x + r * 0.62:.2f},{y + r * 0.95:.2f} "
                                                     f"{x + r * 0.78:.2f},{y + r * 0.5:.2f}", cheveux, r * 0.26) + "</g>")
    else:                                                   # la frange et le dessus du carré
        d.add(path(f"M{x - r * 1.05:.2f},{y + r * 0.3:.2f} A{r * 1.05},{r * 1.05} 0 0 1 {x + r * 0.95:.2f},{y - r * 0.35:.2f} "
                   f"Q{x + r * 0.2:.2f},{y - r * 0.3:.2f} {x - r * 0.25:.2f},{y + r * 0.35:.2f} Z"), cheveux, sil=False, clip=clip)
    d.add(circle(x + r * 0.45, y + r * 0.08, r * 0.15), "#3A1E12", sil=False, clip=clip)


def sport(spin=0, k=SPORT_K, passagers=("papa", "alice", "tecky")):
    """La voiture de sport rouge du papa d'Alice, 88x40, de profil vers la droite. passagers : qui l'on voit
    derrière les vitres (le conducteur, puis l'arrière) ; () : garée, vide."""
    c = SPORT
    X, Y = _PX, (lambda y: _PY(y, k))
    r = 5.4 * (1 + (k - 1) * 0.75)
    cy = 38.6 - r
    d = Drawing(88, 40)
    _shadow(d, 8, 82, 38.6)
    haut = [(331, 156), (334, 142), (333, 126), (327, 106), (325, 104), (313, 103), (301, 99), (289, 95), (277, 90),
            (265, 86), (253, 83), (241, 80), (225, 79), (205, 79), (190, 79), (175, 80), (163, 84), (151, 91),
            (139, 98), (127, 105), (112, 108), (85, 110), (61, 113), (43, 118), (31, 124), (25, 130), (24, 142),
            (26, 155), (26, 155), (32, 164)]
    bas = [(60, 166), (140, 166), (220, 166), (300, 166), (322, 163), (331, 156)]
    caisse = _lisse([(X(x), Y(y)) for x, y in haut + bas])
    d.clip("sport", [path(caisse)])
    d.add(path(caisse), c["light"])
    # le dessus au soleil : un liseré clair (la même forme, 1,5 plus bas, dans la couleur de la caisse ; pas de
    # « transform » : la découpe se déplacerait avec elle)
    d.add(path(_lisse([(X(x), Y(y) + 1.5) for x, y in haut + bas])), c["body"], sil=False, clip="sport")
    d.add(rect(0, Y(141), 88, 12), c["dark"], sil=False, clip="sport")               # le bas de caisse, à l'ombre
    d.add(poly([(X(262), Y(139)), (X(118), Y(142)), (X(118), Y(144.5)), (X(262), Y(141.5))]), c["light"], sil=False,
          clip="sport", opacity=0.55)                                                # le pli des portières, qui prend la lumière
    d.add(rect(X(312), Y(159), X(42) - X(312), 10), c["trim"], sil=False, clip="sport")      # bas de caisse noir
    d.add(poly([(X(334), Y(140)), (X(318), Y(143)), (X(316), Y(170)), (X(334), Y(170))]), c["trim"], sil=False, clip="sport")   # diffuseur
    d.add(poly([(X(24), Y(143)), (X(40), Y(147)), (X(43), Y(170)), (X(24), Y(170))]), c["trim"], sil=False, clip="sport")       # entrée d'air
    for x in (X(268), X(72)):
        _passage(d, x, cy, r + 1.1, "sport")
    d.add(poly([(X(108), Y(134)), (X(113), Y(134)), (X(120), Y(156)), (X(115), Y(156))]), c["trim"], sil=False, clip="sport")   # ouïe
    # vitres : la portière avant, puis la longue vitre arrière qui s'effile ; entourage noir
    v1 = poly([(X(149), Y(107)), (X(181), Y(86.5)), (X(197), Y(85.5)), (X(197), Y(107))])
    v2 = path(f"M{X(202):.2f},{Y(85.5):.2f} L{X(244):.2f},{Y(86):.2f} Q{X(268):.2f},{Y(91):.2f} {X(283):.2f},{Y(100.5):.2f} "
              f"L{X(276):.2f},{Y(105.5):.2f} L{X(202):.2f},{Y(107):.2f} Z")
    for cle, v in (("s1", v1), ("s2", v2)):
        _vitre(d, cle, v, None)
    ry = (Y(107) - Y(86)) * 0.47
    for qui, x, cle, m in zip(passagers, (X(183), X(216), X(249)), ("s1", "s2", "s2"), (1, 0.92, 0.8)):
        _passager(d, qui, x, Y(107) - ry * m * 0.95, ry * m, cle)
    d.raw('<g clip-path="url(#s1)">' + line(f"M{X(160):.2f},{Y(105):.2f} L{X(176):.2f},{Y(90):.2f}", "#FFFFFF", 0.8) + "</g>")
    d.raw('<g clip-path="url(#s2)">' + line(f"M{X(262):.2f},{Y(103):.2f} L{X(252):.2f},{Y(90):.2f}", "#FFFFFF", 0.7) + "</g>")
    for v in (v1, v2):
        d.raw(v.replace('fill="%F%"', f'fill="none" stroke="{c["trim"]}" stroke-width="1.0" stroke-linejoin="round"'))
    # portières, poignées affleurantes, rétroviseur, antenne
    d.raw(line(f"M{X(199.5):.2f},{Y(109):.2f} L{X(199.5):.2f},{Y(158):.2f} M{X(263):.2f},{Y(108):.2f} Q{X(266):.2f},{Y(130):.2f} {X(244):.2f},{Y(146):.2f} "
               f"M{X(136):.2f},{Y(110):.2f} L{X(133):.2f},{Y(158):.2f}", c["dark"], 0.6))
    for x in (185, 250):
        d.raw(line(f"M{X(x):.2f},{Y(119):.2f} L{X(x - 12):.2f},{Y(119):.2f}", c["dark"], 0.7))
    d.add(poly([(X(147), Y(99)), (X(138), Y(100)), (X(137), Y(105.5)), (X(147), Y(106))]), c["trim"], sil=False, edge=True)   # rétroviseur
    d.add(poly([(X(250), Y(80.5)), (X(240), Y(78)), (X(237), Y(80.5))]), c["trim"])                                          # antenne
    # phare effilé, feu arrière
    d.add(path(f"M{X(31):.2f},{Y(125):.2f} L{X(52):.2f},{Y(121):.2f} L{X(50):.2f},{Y(126.5):.2f} L{X(33):.2f},{Y(130):.2f} Z"),
          c["phare"], sil=False, edge=True)
    d.add(path(f"M{X(329):.2f},{Y(111):.2f} L{X(304):.2f},{Y(110):.2f} L{X(308):.2f},{Y(116):.2f} L{X(330):.2f},{Y(118):.2f} Z"),
          c["feu"], sil=False, edge=True)
    d.raw(line(f"M{X(326):.2f},{Y(113.5):.2f} L{X(309):.2f},{Y(112.8):.2f}", "#FF8A80", 0.6))
    for x in (X(268), X(72)):
        _roue_sport(d, x, cy, r, spin)
    return d


def van(spin=0):
    """Camionnette de boulangerie 80x48 : caisse crème peinte d'une baguette et d'un croissant, cabine à droite avec
    le boulanger au volant ; le dessus au soleil, le bas à l'ombre."""
    body, dark, accent = "#F3E7CF", "#D9C8A2", "#C8553D"
    d = Drawing(80, 48)
    _shadow(d, 5, 75, 44.4)
    caisse = "M4,8.5 Q4,6 6.5,6 L53.5,6 Q56,6 56,8.5 L56,38 L4,38 Z"
    cabine = "M55,16 L67,16 Q70,16 71.5,19 L75.5,27 Q76.5,29 76.5,31 L76.5,36 Q76.5,38 74.5,38 L55,38 Z"
    d.clip("van", [path(caisse), path(cabine)])
    d.add(path(caisse), body)
    d.add(path(cabine), body)
    d.add(rect(4, 6, 52, 2.4), "#FFFFFF", sil=False, clip="van")                      # le toit de la caisse
    d.add(rect(55, 16, 16, 1.8), "#FFFFFF", sil=False, clip="van")
    d.add(rect(4, 31, 72.5, 7), accent, sil=False, clip="van")                        # bande rouge
    d.add(rect(4, 35.2, 72.5, 3), "#A3412E", sil=False, clip="van")
    for x in (18, 63):
        _passage(d, x, 38, 7.8, "van")
    vitre = poly([(58, 19), (66.5, 19), (71.5, 27.5), (58, 27.5)])
    _vitre(d, "vv", vitre, None)
    _tete(d, 63.4, 23.6, 2.8, 0, "vv", "#FFFFFF")
    d.raw('<g clip-path="url(#vv)">' + line("M68.6,26.6 L65.2,20.6", "#FFFFFF", 0.8) + "</g>")
    _bord(d, vitre)
    d.raw(line("M56.4,17 L56.4,37.6", dark, 0.8))
    d.add(rect(69.8, 25.4, 3, 2.2, 0.9), body, sil=False, edge=True)                  # rétroviseur
    d.add(rect(7, 9, 46, 19, 2), "#FFF7E6", sil=False, edge=True)                     # panneau peint
    d.add(ellipse(22, 19, 13, 3.4, "rotate(-14 22 19)"), "#D9A55B", sil=False, edge=True)
    for x in (14, 19, 24, 29):
        d.raw('<g transform="rotate(-14 22 19)">' + line(f"M{x},17.4 L{x + 2.6},20.2", "#B07A3A", 0.9) + "</g>")
    d.add(path("M38,22.5 Q39,13 46.5,13.5 Q50.5,14.5 50,18.5 Q46,15.8 42.5,18.5 Q41,20.5 41.5,23.5 Z"),
          "#E3A954", sil=False, edge=True)
    d.raw(line("M41,17.4 L43.4,19 M44.4,14.8 L45.6,17", "#B07A3A", 0.8))
    d.add(ellipse(73.6, 30.2, 1.7, 1.4), "#FFF1B8", sil=False, edge=True)             # phare
    d.add(rect(4, 26, 1.8, 3.4, 0.8), "#E24B4B", sil=False)
    for x in (2.6, 73.6):
        d.add(rect(x, 35, 4.6, 3, 1.2), "#C4C8D0")
        d.add(rect(x + 0.5, 36.7, 3.6, 1.2, 0.6), "#8E949E", sil=False)
    for x in (18, 63):
        _wheel(d, x, 38, 6, spin)
    return d


def bus(spin=0):
    """Bus bleu 128x56 : toit clair, longue rangée de fenêtres où l'on voit des passagers, porte à l'avant, le
    chauffeur derrière le pare-brise, girouette, bande blanche, bas de caisse à l'ombre."""
    body, dark = "#2E6FD1", "#23579F"
    d = Drawing(128, 56)
    _shadow(d, 6, 123, 52.6)
    caisse = "M4,44 L4,10 Q4,6 8,6 L116,6 Q122,6 123,11 L124.5,40 Q124.5,46 120,46 L8,46 Q4,46 4,44 Z"
    d.clip("bus", [path(caisse)])
    d.add(path(caisse), body)
    d.add(rect(4, 6, 121, 2.8), _clair(body), sil=False, clip="bus")                  # le toit
    d.add(rect(4.2, 36, 120.4, 3), "#FFFFFF", sil=False, clip="bus")                  # bande blanche
    d.add(rect(4.2, 39, 120.4, 7), dark, sil=False, clip="bus")
    for x in (26, 102):
        _passage(d, x, 46, 9, "bus")
    for k in range(6):                                                                # fenêtres passagers
        x = 9 + k * 15
        f = rect(x, 12, 12, 13, 1.5)
        _vitre(d, f"f{k}", f, None)
        if k in (0, 2, 3, 5):
            _tete(d, x + (5 if k % 2 else 7), 19.4, 3, k + 1, f"f{k}")
        d.raw(f'<g clip-path="url(#f{k})">' + line(f"M{x + 1.5},23 L{x + 5},14", "#FFFFFF", 0.8) + "</g>")
        _bord(d, f)
    d.add(rect(100, 12, 9, 24, 1.2), GLASS, sil=False, edge=True)                     # porte
    d.raw(line("M104.5,12.5 L104.5,35.5", dark, 0.9))
    d.raw(line("M101.6,30 L103,22 M106.2,30 L107.6,22", "#FFFFFF", 0.7))
    pb = path("M111.5,12 L119.5,12 Q121.5,12 121.8,14 L122.6,26 L111.5,26 Z")
    _vitre(d, "pb", pb, None)
    _tete(d, 116, 19.6, 3, 4, "pb", "#23579F")
    _bord(d, pb)
    d.add(rect(110, 7.6, 12, 3.2, 1), "#2B2B33", sil=False)                           # girouette
    for x in (111.6, 114.4, 117.2, 120):
        d.add(circle(x, 9.2, 0.6), "#F7D154", sil=False)
    d.add(ellipse(122.4, 33, 1.7, 1.5), "#FFF1B8", sil=False, edge=True)
    d.add(rect(4.2, 29, 2, 4, 0.8), "#E24B4B", sil=False)
    d.add(rect(122, 41, 4.4, 3.2, 1.2), "#C4C8D0")                                    # pare-chocs
    d.add(rect(1.8, 41, 4.4, 3.2, 1.2), "#C4C8D0")
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
    d.clip("cabine", [rect(7, 9, 15, 26, 1.5)])
    d.add(rect(7, 9, 15, 26, 1.5), red)                                               # cabine
    d.add(rect(7, 28, 15, 8), dark, sil=False, clip="cabine")
    d.add(rect(5.8, 6.6, 16.4, 1.1, 0.5), "#5A5A64", sil=False)                       # (le toit au soleil)
    d.add(rect(10, 13, 9, 8, 1.5), GLASS, sil=False, edge=True)
    d.raw(line("M12,19 L16.5,14.5", "#FFFFFF", 0.9))
    d.clip("chaudiere", [rect(21, 18, 33, 15, 7.5)])
    d.add(rect(21, 18, 33, 15, 7.5), red)                                             # chaudière
    d.add(rect(21, 18, 33, 3.6), _clair(red), sil=False, clip="chaudiere")            # le dessus au soleil
    d.add(rect(21, 28, 33, 6), dark, sil=False, clip="chaudiere")                     # le dessous à l'ombre
    for x in (31, 42):                                                                # cerclages dorés
        d.add(rect(x, 18, 2, 15, 0), gold, sil=False)
    d.add(rect(45, 7, 6.5, 12, 1), "#2B2B33")                                         # cheminée
    d.add(rect(46, 8.6, 1.2, 10, 0.5), "#5A5A64", sil=False)
    d.add(rect(43.6, 5, 9.3, 3.2, 1.2), gold, edge=True)
    d.add(path("M33,18 Q33,12.5 36.5,12.5 Q40,12.5 40,18 Z"), gold)                   # dôme (cloche)
    d.add(circle(54.5, 25.5, 2.4), "#FFF1B8", sil=False, edge=True)                   # phare
    d.add(rect(5, 32, 52, 4, 1), "#2B2B33")                                           # châssis
    d.add(poly([(56, 32), (62, 40), (56, 40)]), "#5C6168")                            # chasse-pierres
    for x, r in ((16, 6.4), (31, 6.4), (45, 5.4)):
        y = 44 - r
        d.add(circle(x, y, r), dark)
        d.add(circle(x, y, r * 0.8), red, sil=False)
        d.raw(line(f"M{x - r * 0.6:.2f},{y - r * 0.62:.2f} A{r * 0.87:.2f},{r * 0.87:.2f} 0 0 1 {x + r * 0.6:.2f},{y - r * 0.62:.2f}", "#F0786E", 0.8))
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
    for x in range(9, 41, 3):
        d.raw(line(f"M{x + 0.9},10 L{x + 0.9},28", _clair(col, 0.3), 0.45))
    d.add(rect(6, 24.6, 36, 4.4), rib, sil=False, opacity=0.6)                        # le bas à l'ombre
    d.add(rect(6, 7, 36, 4, 0.5), col)
    d.add(rect(6, 7, 36, 4, 0.5), "#FFFFFF", sil=False, opacity=0.3)                  # le dessus au soleil
    d.add(rect(8.4, 13.4, 6, 3.6, 0.5), "#F4EFE4", sil=False)                         # la plaque
    d.add(rect(3, 28, 42, 3.6, 1), "#4A4F57")                                         # plateau
    d.add(rect(0.6, 28.6, 3, 2.2, 0.8), "#2B2B33")                                    # attelages
    d.add(rect(44.4, 28.6, 3, 2.2, 0.8), "#2B2B33")
    for x in (12, 36):
        _wheel(d, x, 32.4, 4.2, spin)
    return d


SPINS = (0, 30, 60, 90)          # 3 rayons : un tour d'enjoliveur tous les 120°
VEHICLES = {   # nom : (fonction(spin), (largeur, hauteur) 1x, origine 1x)
    **{f"car_{c}": ((lambda c: lambda s: car(c, s))(c), (64, 40), (32, 38.6)) for c in CAR_COLORS},
    # la voiture de sport du papa d'Alice : avec lui, Alice et Tecky derrière les vitres ; garée, vide
    "sport": (sport, (88, 40), (44, 38.6)),
    "sport_vide": ((lambda s: sport(s, passagers=())), (88, 40), (44, 38.6)),
    "van": (van, (80, 48), (40, 44.4)),
    "bus": (bus, (128, 56), (64, 52.6)),
    "loco": (loco, (64, 48), (32, 44.4)),
    **{f"wagon_{c}": ((lambda c: lambda s: wagon(c, s))(c), (48, 40), (24, 36.6)) for c in WAGON_COLORS},
}


# Taille dans le jeu : les véhicules de la route sont agrandis (Christophe les trouvait trop petits, le 12 novembre
# 2026) ; Titine reste un petit train. game.js : VEHICLE (longueurs).
ECH = {"car": 1.5, "van": 1.5, "bus": 1.5, "sport": 1.5}


def echelle(name):
    return ECH.get(name.split("_")[0], 1)


def cadre(name):
    """(largeur, hauteur, origine x, origine y) d'un véhicule dans le jeu, en unités de l'atlas."""
    _, (w, h), (ox, oy) = VEHICLES[name]
    k = echelle(name)
    return math.ceil(w * k), math.ceil(h * k), ox * k, oy * k


def frames(name):
    """Les images d'un véhicule (les enjoliveurs tournent), en SVG, à sa taille du jeu (contour compensé), sans la
    bande sombre dessinée dessous : le jeu lui donne une ombre portée (game.js : castShadow())."""
    fn, k = VEHICLES[name][0], echelle(name)
    w, h, _, _ = cadre(name)
    out = []
    for s in SPINS:
        d = fn(s)
        d.under, d.w, d.h = [], w, h
        out.append(d.svg(f"scale({k})", outline_w=OUTLINE_W / k) if k != 1 else d.svg())
    return out

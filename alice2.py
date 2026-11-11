"""
Alice, version 2 — celle du jeu web (PLAN_V2.md, lot 3).

D'après reference/alice_tecky.png : cheveux châtains mi-longs et raides, frange en mèches, grands yeux noirs, joues
roses, t-shirt jaune, jupe rose, pieds nus. Grosse tête (un peu plus de deux têtes de haut), comme avant, mais dessinée
plus grand puis réduite de ECH, comme Tecky (tecky2.py) : des traits plus fins, des mains, des orteils, des mèches.
Trois vues : face, dos, profil (tournée vers la droite ; la gauche est son miroir).

alice.py reste celle du kit GameMaker. Mêmes noms d'animations : idle, walk, happy (le saut de joie des retrouvailles).

    python3 alice2.py      # reference/v2/alice_v2.png
"""
import math
import os

from spritelib import Drawing, circle, ellipse, path, poly, line, OUTLINE

SOL = 70                 # ligne du sol
X0 = 30.0                # axe du dessin
ECH = 0.7                # réduction du dessin dans le jeu
TRAIT = 1.8 / ECH
CADRE = (48, 52, 24, 48)     # le jeu : largeur, hauteur, origine (aux pieds), en unités de l'atlas

PAL = dict(skin="#FADFCB", skin_dk="#EDC6AB", hair="#B9976B", hair_hl="#DCC391", hair_dk="#94764C",
           shirt="#FBE36A", shirt_dk="#EBCB4A", skirt="#F6A9C6", skirt_dk="#E288AC",
           eye="#2A1E1A", blush="#F5A3A6", nose="#E9A392", mouth="#B8505A", white="#FFFFFF")


def pose(**kw):
    """pas : avancée du cycle de marche (0..1) ; rebond ; saut : hauteur du saut ; bras : 0 le long du corps, 1 levés ;
    yeux : "fermes" (clignement) ou "rire" ; rire : bouche ouverte ; meche : balancement des cheveux."""
    base = dict(pas=None, rebond=0.0, saut=0.0, bras=0.0, yeux=None, rire=False, meche=0.0)
    base.update(kw)
    return base


def _membre(x1, y1, x2, y2, w1, w2):
    L = math.hypot(x2 - x1, y2 - y1) or 1
    nx, ny = -(y2 - y1) / L, (x2 - x1) / L
    return poly([(x1 + nx * w1 / 2, y1 + ny * w1 / 2), (x2 + nx * w2 / 2, y2 + ny * w2 / 2),
                 (x2 - nx * w2 / 2, y2 - ny * w2 / 2), (x1 - nx * w1 / 2, y1 - ny * w1 / 2)])


def _cerne(d, *formes):
    """Contour de formes posées par-dessus d'autres (le visage devant les cheveux), aussi épais que le contour extérieur."""
    for f in formes:
        d.raw(f.replace('fill="%F%"', f'fill="{OUTLINE}" stroke="{OUTLINE}" stroke-width="{TRAIT:.2f}" stroke-linejoin="round"'))


def _marche(p):
    """(balancement -1..1, levée du pied gauche, levée du pied droit)."""
    if p["pas"] is None:
        return 0.0, 0.0, 0.0
    a = p["pas"] * 2 * math.pi
    return math.sin(a), max(0.0, math.sin(a)) * 2.6, max(0.0, -math.sin(a)) * 2.6


def _pied(d, x, y, s, couleur):
    """Pied nu, vu de face ou de dos : les orteils du côté s."""
    d.add(ellipse(x + s * 0.5, y, 3.5, 2.1), couleur)
    d.raw(line(f"M{x + s * 1.3 - 0.9:.2f},{y + 0.5:.2f} L{x + s * 1.3 - 0.9:.2f},{y + 1.7:.2f} "
               f"M{x + s * 1.3 + 0.7:.2f},{y + 0.6:.2f} L{x + s * 1.3 + 0.7:.2f},{y + 1.7:.2f}", OUTLINE, 0.45))


def _bras(d, sx, sy, mx, my, couleur):
    """Un bras, de l'épaule (sx, sy) à la main (mx, my)."""
    d.add(_membre(sx, sy, mx, my, 4.2, 3.6), couleur)
    d.add(circle(mx, my, 2.5), couleur)


def _habits(d, Y, large=True):
    """Jupe rose (plis, ourlet) et t-shirt jaune : de face et de dos (large), ou de profil."""
    c = PAL
    a, b, e, f = (21.6, 38.4, 17.0, 43.0) if large else (24.6, 35.6, 20.8, 39.6)
    jupe = path(f"M{a:.2f},{Y(44.6):.2f} L{b:.2f},{Y(44.6):.2f} L{f:.2f},{Y(56.0):.2f} Q{X0:.2f},{Y(58.6):.2f} {e:.2f},{Y(56.0):.2f} Z")
    d.clip("jupe", [jupe])
    d.add(jupe, c["skirt"])
    d.add(path(f"M{e - 2:.2f},{Y(54.2):.2f} Q{X0:.2f},{Y(56.8):.2f} {f + 2:.2f},{Y(54.2):.2f} L{f + 2:.2f},{Y(60):.2f} L{e - 2:.2f},{Y(60):.2f} Z"),
          c["skirt_dk"], sil=False, clip="jupe", opacity=0.55)
    plis = ((25.6, 24.2), (30.0, 30.0), (34.4, 35.8)) if large else ((28.4, 27.2), (32.6, 33.8))
    d.raw(f'<g clip-path="url(#jupe)">' + "".join(
        line(f"M{x0:.2f},{Y(47.4):.2f} L{x1:.2f},{Y(57):.2f}", c["skirt_dk"], 0.8) for x0, x1 in plis) + "</g>")
    if large:                # de face, de dos : les deux manches courtes font partie du t-shirt
        haut = path(f"M21.8,{Y(33.2):.2f} Q{X0:.2f},{Y(30.8):.2f} 38.2,{Y(33.2):.2f} L43.6,{Y(37.4):.2f} L41.8,{Y(40.8):.2f} "
                    f"L38.6,{Y(39.4):.2f} L38.8,{Y(46.4):.2f} Q{X0:.2f},{Y(47.6):.2f} 21.2,{Y(46.4):.2f} L21.4,{Y(39.4):.2f} "
                    f"L18.2,{Y(40.8):.2f} L16.4,{Y(37.4):.2f} Z")
    else:
        haut = path(f"M24.8,{Y(33.4):.2f} Q{X0:.2f},{Y(30.8):.2f} 35.2,{Y(33.4):.2f} L35.8,{Y(46.4):.2f} "
                    f"Q{X0:.2f},{Y(47.6):.2f} 24.2,{Y(46.4):.2f} Z")
    d.clip("haut", [haut])
    d.add(haut, c["shirt"])
    d.add(path(f"M14,{Y(44.2):.2f} Q{X0:.2f},{Y(45.6):.2f} 46,{Y(44.2):.2f} L46,{Y(49):.2f} L14,{Y(49):.2f} Z"),
          c["shirt_dk"], sil=False, clip="haut", opacity=0.7)


def _cheveux(hy, dx=0.0, visage=False):
    """Les cheveux : un carré mi-long, coupé droit aux épaules (dx : le bas se balance). visage : la même forme,
    ouverte sur le visage (la frange en mèches en haut, un pan de chaque côté)."""
    dehors = (f"M{15.6 + dx:.2f},{hy + 12.2:.2f} L16.2,{hy:.2f} C16.0,{hy - 17.6:.2f} 44.0,{hy - 17.6:.2f} 43.8,{hy:.2f} "
              f"L{44.4 + dx:.2f},{hy + 12.2:.2f} Q{44.4 + dx:.2f},{hy + 14.8:.2f} {42.0 + dx:.2f},{hy + 14.8:.2f} ")
    fin = f"L{18.0 + dx:.2f},{hy + 14.8:.2f} Q{15.6 + dx:.2f},{hy + 14.8:.2f} {15.6 + dx:.2f},{hy + 12.2:.2f} Z"
    if not visage:
        return path(dehors + fin), None
    bord = (f"{39.9 + dx:.2f},{hy + 14.8:.2f} L39.6,{hy - 2.6:.2f} L37.4,{hy - 0.8:.2f} L36.4,{hy - 3.3:.2f} L33.6,{hy - 0.6:.2f} "
            f"L32.4,{hy - 3.5:.2f} L29.8,{hy - 0.6:.2f} L28.2,{hy - 3.5:.2f} L25.6,{hy - 0.7:.2f} L24.2,{hy - 3.3:.2f} "
            f"L21.8,{hy - 0.8:.2f} L20.4,{hy - 2.6:.2f} L{20.1 + dx:.2f},{hy + 14.8:.2f}")
    return path(dehors + "L" + bord + " " + fin), "M" + bord


def _reflets(d, hy, x=0.0):
    c = PAL
    d.add(ellipse(24.6 + x, hy - 9.4, 4.4, 1.5, f"rotate(-24 {24.6 + x:.2f} {hy - 9.4:.2f})"), c["hair_hl"], sil=False, opacity=0.85)
    d.add(ellipse(35.8 + x, hy - 10.2, 2.6, 1.1, f"rotate(20 {35.8 + x:.2f} {hy - 10.2:.2f})"), c["hair_hl"], sil=False, opacity=0.85)


def devant(p=None):
    """Alice de face."""
    p = p or pose()
    c = PAL
    d = Drawing(60, 76)
    b = p["rebond"] - p["saut"]
    Y = lambda v: v + b
    sw, lA, lB = _marche(p)

    for s, lv in ((-1, lA), (1, lB)):                   # jambes, pieds nus
        x, fy = X0 + s * 4.2, SOL - 1.8 - lv - p["saut"]
        d.add(path(f"M{x - 2.5:.2f},{Y(54):.2f} L{x + 2.5:.2f},{Y(54):.2f} L{x + 2.3:.2f},{fy:.2f} L{x - 2.3:.2f},{fy:.2f} Z"), c["skin"])
        _pied(d, x, fy + 0.3, s, c["skin"])
    ar = p["bras"]
    if ar <= 0.5:                                       # bras le long du corps (levés : plus bas, devant les cheveux)
        for s, ph in ((-1, sw), (1, -sw)):
            sx, sy = X0 + s * 10.6, Y(38.0)
            _bras(d, sx, sy, sx + s * (1.6 + 5 * ar), sy + 10.4 - 8 * ar + ph * 1.6, c["skin"])
    _habits(d, Y)
    d.add(ellipse(X0, Y(32.6), 3.4, 1.7), c["skin"], sil=False)       # l'encolure

    hy = Y(19.0)
    m = p["meche"]
    d.add(_cheveux(hy, m)[0], c["hair"])
    visage = circle(X0, hy + 1.2, 11.2)
    _cerne(d, visage)
    d.add(visage, c["skin"])
    # par-dessus : la frange, en mèches, et les deux pans qui encadrent le visage
    devant_, bord = _cheveux(hy, m, True)
    d.add(devant_, c["hair"])
    d.raw(line(bord, OUTLINE, 0.9))
    d.raw(line(f"M37.4,{hy - 0.8:.2f} L37.0,{hy - 6:.2f} M33.6,{hy - 0.6:.2f} L33.4,{hy - 6.6:.2f} M29.8,{hy - 0.6:.2f} L29.8,{hy - 7:.2f} "
               f"M25.6,{hy - 0.7:.2f} L25.9,{hy - 6.6:.2f} M21.8,{hy - 0.8:.2f} L22.4,{hy - 6:.2f}", c["hair_dk"], 0.6))
    _reflets(d, hy)
    if ar > 0.5:                                        # bras levés : devant les cheveux
        for s in (-1, 1):
            sx, sy = X0 + s * 10.4, Y(36.4)
            bras_, main = _membre(sx, sy, sx + s * 6.6, sy - 21.5 * ar, 4.2, 3.6), circle(sx + s * 6.6, sy - 21.5 * ar, 2.6)
            _cerne(d, bras_, main)
            d.add(bras_, c["skin"])
            d.add(main, c["skin"])
            d.add(path(f"M{sx - s * 2.6:.2f},{sy + 1.8:.2f} L{sx + s * 3.4:.2f},{sy + 2.8:.2f} L{sx + s * 4.8:.2f},{sy - 3.4:.2f} "
                       f"L{sx - s * 0.6:.2f},{sy - 5.0:.2f} Z"), c["shirt"], sil=False, edge=True)

    for s in (-1, 1):
        ex, ey = X0 + s * 5.1, hy + 2.9
        if p["yeux"] == "rire":                         # yeux plissés de joie
            d.raw(line(f"M{ex - 2.1:.2f},{ey + 0.7:.2f} Q{ex:.2f},{ey - 2.4:.2f} {ex + 2.1:.2f},{ey + 0.7:.2f}", c["eye"], 1.1))
        elif p["yeux"] == "fermes":
            d.raw(line(f"M{ex - 1.9:.2f},{ey:.2f} Q{ex:.2f},{ey + 1.5:.2f} {ex + 1.9:.2f},{ey:.2f}", c["eye"], 1.0))
        else:
            d.add(ellipse(ex, ey, 1.95, 2.55), c["eye"], sil=False)
            d.add(circle(ex + 0.6, ey - 0.95, 0.75), c["white"], sil=False)
            d.add(circle(ex - 0.55, ey + 1.05, 0.34), c["white"], sil=False, opacity=0.85)
            d.raw(line(f"M{ex + s * 1.7:.2f},{ey - 1.3:.2f} L{ex + s * 2.8:.2f},{ey - 2.0:.2f} "
                       f"M{ex + s * 1.95:.2f},{ey - 0.2:.2f} L{ex + s * 3.0:.2f},{ey - 0.5:.2f}", c["eye"], 0.5))     # les cils
        d.add(ellipse(X0 + s * 7.6, hy + 7.0, 2.5, 1.6), c["blush"], sil=False, opacity=0.6)
    d.add(ellipse(X0, hy + 5.6, 0.75, 0.5), c["nose"], sil=False)
    if p["rire"]:
        d.add(path(f"M27.0,{hy + 7.6:.2f} Q30,{hy + 13:.2f} 33.0,{hy + 7.6:.2f} Z"), c["mouth"], sil=False, edge=True)
    else:
        d.raw(line(f"M27.6,{hy + 8.1:.2f} Q30,{hy + 10.4:.2f} 32.4,{hy + 8.1:.2f}", c["eye"], 0.85))
    return d


def derriere(p=None):
    """Alice de dos : on ne voit que ses cheveux."""
    p = p or pose()
    c = PAL
    d = Drawing(60, 76)
    b = p["rebond"] - p["saut"]
    Y = lambda v: v + b
    sw, lA, lB = _marche(p)

    for s, lv in ((-1, lB), (1, lA)):
        x, fy = X0 + s * 4.2, SOL - 1.8 - lv - p["saut"]
        d.add(path(f"M{x - 2.5:.2f},{Y(54):.2f} L{x + 2.5:.2f},{Y(54):.2f} L{x + 2.3:.2f},{fy:.2f} L{x - 2.3:.2f},{fy:.2f} Z"), c["skin"])
        d.add(ellipse(x + s * 0.3, fy + 0.3, 3.1, 2.0), c["skin_dk"])            # les talons
    ar = p["bras"]
    for s, ph in ((-1, -sw), (1, sw)):
        sx, sy = X0 + s * 10.6, Y(38.0)
        _bras(d, sx, sy, sx + s * (1.6 + 5 * ar), sy + 10.4 - 20 * ar + ph * 1.6, c["skin"])
    _habits(d, Y)

    hy = Y(19.0)
    m = p["meche"]
    cheveux = _cheveux(hy, m)[0]
    _cerne(d, cheveux)
    d.add(cheveux, c["hair"])
    d.raw(line(f"M30,{hy - 12:.2f} L{30 + m:.2f},{hy + 13.6:.2f} M23.6,{hy - 4:.2f} L{23.0 + m:.2f},{hy + 14:.2f} "
               f"M36.4,{hy - 4:.2f} L{37.0 + m:.2f},{hy + 14:.2f} M19.6,{hy + 4:.2f} L{19.2 + m:.2f},{hy + 13.6:.2f} "
               f"M40.4,{hy + 4:.2f} L{40.8 + m:.2f},{hy + 13.6:.2f}", c["hair_dk"], 0.6))
    _reflets(d, hy)
    return d


def profil(p=None):
    """Alice de profil, tournée vers la droite."""
    p = p or pose()
    c = PAL
    d = Drawing(60, 76)
    b = p["rebond"] - p["saut"]
    Y = lambda v: v + b
    sw = math.sin(p["pas"] * 2 * math.pi) if p["pas"] is not None else 0.0
    ar = p["bras"]

    def jambe(k, lever, couleur):
        fx, fy = X0 + k * 4.6, SOL - 1.8 - lever - p["saut"]
        d.add(_membre(X0, Y(54), fx, fy, 5.0, 4.6), couleur)
        d.add(ellipse(fx + 1.4, fy + 0.3, 3.7, 2.1), couleur)
        return fx, fy

    def bras(k, couleur):
        sx, sy = X0 + 0.2, Y(35.8)
        # (levés : tendus vers l'avant, sous le menton, pour ne pas cacher le visage)
        _bras(d, sx, sy, sx - k * 5.4 * (1 - ar) + ar * 14.5, sy + 12 - 18.6 * ar - abs(k) * 0.8, couleur)

    jambe(-sw, max(0.0, -sw) * 2.4, c["skin_dk"])        # jambe et bras du côté caché
    bras(-sw, c["skin_dk"])
    fx, fy = jambe(sw, max(0.0, sw) * 2.4, c["skin"])
    d.raw(line(f"M{fx + 3.2:.2f},{fy + 0.4:.2f} L{fx + 3.3:.2f},{fy + 1.6:.2f} M{fx + 4.4:.2f},{fy + 0.5:.2f} L{fx + 4.4:.2f},{fy + 1.5:.2f}",
               OUTLINE, 0.45))
    _habits(d, Y, large=False)

    hy = Y(19.0)
    m = p["meche"]
    visage = circle(X0 + 1.2, hy + 1.2, 11.2)
    nez = ellipse(X0 + 12.2, hy + 5.4, 1.0, 0.9)
    d.add(visage, c["skin"])
    d.add(nez, c["skin"])
    # les cheveux : toute la tête derrière le visage, la frange devant, un pan qui cache l'oreille
    cheveux = path(f"M{28.6 + m:.2f},{hy + 14.8:.2f} L{18.6 + m:.2f},{hy + 14.8:.2f} Q{16.2 + m:.2f},{hy + 14.8:.2f} {16.2 + m:.2f},{hy + 12.2:.2f} "
                   f"L16.4,{hy + 1:.2f} C16.2,{hy - 17.6:.2f} 43.4,{hy - 16.8:.2f} 43.2,{hy - 2.8:.2f} "
                   f"L41.6,{hy - 1.0:.2f} L40.4,{hy - 3.4:.2f} L38.0,{hy - 0.8:.2f} L36.6,{hy - 3.4:.2f} L34.0,{hy - 0.8:.2f} "
                   f"L32.6,{hy - 3.2:.2f} L30.2,{hy - 0.6:.2f} L29.4,{hy + 4:.2f} Z")
    d.add(cheveux, c["hair"], edge=True)
    d.raw(line(f"M38.0,{hy - 0.8:.2f} L37.4,{hy - 6.4:.2f} M34.0,{hy - 0.8:.2f} L33.6,{hy - 6.8:.2f} "
               f"M24.6,{hy - 5:.2f} L{24.0 + m:.2f},{hy + 14:.2f} M20.2,{hy + 2:.2f} L{19.8 + m:.2f},{hy + 13.6:.2f}", c["hair_dk"], 0.6))
    _reflets(d, hy, -1.4)

    ex, ey = X0 + 7.8, hy + 2.9
    if p["yeux"] == "rire":
        d.raw(line(f"M{ex - 1.9:.2f},{ey + 0.7:.2f} Q{ex:.2f},{ey - 2.4:.2f} {ex + 1.9:.2f},{ey + 0.7:.2f}", c["eye"], 1.1))
    elif p["yeux"] == "fermes":
        d.raw(line(f"M{ex - 1.7:.2f},{ey:.2f} Q{ex:.2f},{ey + 1.5:.2f} {ex + 1.7:.2f},{ey:.2f}", c["eye"], 1.0))
    else:
        d.add(ellipse(ex, ey, 1.75, 2.55), c["eye"], sil=False)
        d.add(circle(ex + 0.6, ey - 0.95, 0.72), c["white"], sil=False)
        d.add(circle(ex - 0.45, ey + 1.05, 0.32), c["white"], sil=False, opacity=0.85)
        d.raw(line(f"M{ex - 1.5:.2f},{ey - 1.4:.2f} L{ex - 2.5:.2f},{ey - 2.1:.2f}", c["eye"], 0.5))
    d.add(ellipse(X0 + 6.6, hy + 7.0, 2.4, 1.6), c["blush"], sil=False, opacity=0.6)
    if p["rire"]:
        d.add(path(f"M{X0 + 8.4:.2f},{hy + 7.8:.2f} Q{X0 + 10.4:.2f},{hy + 12.4:.2f} {X0 + 12.2:.2f},{hy + 7.6:.2f} Z"), c["mouth"], sil=False, edge=True)
    else:
        d.raw(line(f"M{X0 + 8.8:.2f},{hy + 8.4:.2f} Q{X0 + 10.6:.2f},{hy + 10.0:.2f} {X0 + 12.2:.2f},{hy + 8.0:.2f}", c["eye"], 0.85))

    bras(sw, c["skin"])                                 # le bras de notre côté, et sa manche courte
    mx, my = X0 + 0.2, Y(36.0)
    tr = f"rotate({-sw * 22 * (1 - ar) - ar * 66:.1f} {mx:.2f} {my - 1:.2f})"
    d.add(path(f"M{mx - 3.2:.2f},{my - 1.8:.2f} Q{mx:.2f},{my - 4.2:.2f} {mx + 3.2:.2f},{my - 1.8:.2f} L{mx + 3.4:.2f},{my + 2.6:.2f} "
               f"Q{mx:.2f},{my + 4.4:.2f} {mx - 3.4:.2f},{my + 2.6:.2f} Z", tr), c["shirt"], sil=False)
    d.raw(f'<g transform="{tr}">' + line(f"M{mx - 3.4:.2f},{my + 2.6:.2f} Q{mx:.2f},{my + 4.4:.2f} {mx + 3.4:.2f},{my + 2.6:.2f}", OUTLINE, 0.8)
          + line(f"M{mx - 3.3:.2f},{my - 0.6:.2f} L{mx - 3.4:.2f},{my + 2.6:.2f} M{mx + 3.3:.2f},{my - 0.6:.2f} L{mx + 3.4:.2f},{my + 2.6:.2f}",
                 c["shirt_dk"], 0.7) + "</g>")
    return d


VUES = {"down": devant, "up": derriere, "right": profil}


def image(view, p):
    """SVG d'une image du jeu : la pose p dans la vue donnée, réduite de ECH, les pieds sur l'origine du cadre."""
    w, h, ox, oy = CADRE
    d = VUES[view](p)
    d.w, d.h = w, h
    k = max(0.5, 1 - p["saut"] / 16)                    # l'ombre rétrécit quand elle saute
    d.under.append(f'<ellipse cx="{ox}" cy="{oy + 0.2:.2f}" rx="{7.6 * k:.2f}" ry="{2.0 * k:.2f}" fill="#000" opacity="0.2"/>')
    return d.svg(f"translate({ox - X0 * ECH:.2f} {oy - SOL * ECH:.2f}) scale({ECH})", outline_w=TRAIT)


# ====================================================================== ANIMATIONS
def a_idle(view):
    """Elle attend : elle respire, un clignement."""
    return [pose(rebond=[0, 0.35, 0.55, 0.35][i], yeux="fermes" if i == 3 else None) for i in range(4)]


def a_walk(view):
    """La marche, en 8 images : les bras se balancent, les cheveux suivent."""
    out = []
    for i in range(8):
        a = i / 8 * 2 * math.pi
        out.append(pose(pas=i / 8, rebond=-0.9 * abs(math.sin(a)), meche=0.5 * math.sin(2 * a - 1.2)))
    return out


def a_happy(view):
    """Le saut de joie des retrouvailles : elle s'accroupit, bondit les bras en l'air, retombe."""
    saut = [0, 3.8, 5.6, 2.2]
    bras = [0.3, 1, 1, 0.6]
    return [pose(saut=saut[i], bras=bras[i], yeux="rire", rire=True, rebond=0.9 if i == 0 else 0,
                 meche=[0, -0.4, 0.3, 0.5][i]) for i in range(4)]


ANIMS = {"idle": (a_idle, 6), "walk": (a_walk, 13), "happy": (a_happy, 8)}      # nom : (fonction, images par seconde)


def frames(anim, view):
    return [image(view, p) for p in ANIMS[anim][0](view)]


def portrait(p=None):
    """Le dessin de face, non réduit, pour le portrait (hud.py) : cadre de 60 x 76, le visage autour de (30, 21)."""
    return devant(p or pose())


if __name__ == "__main__":
    from spritelib import render_svg, PAD
    from PIL import Image
    racine = os.path.dirname(os.path.abspath(__file__))
    fond = (126, 200, 100, 255)
    w, h, _, _ = CADRE

    def rangee(images):
        im = Image.new("RGBA", (sum(i.width for i in images), max(i.height for i in images)), fond)
        x = 0
        for i in images:
            im.alpha_composite(i, (x, 0))
            x += i.width
        return im

    grand = rangee([render_svg(image(v, q), w, h, 12, PAD) for v, q in
                    (("down", pose()), ("right", pose()), ("up", pose()), ("down", a_happy("down")[2]),
                     ("right", a_walk("right")[1]))])
    lignes = [grand] + [rangee([render_svg(s, w, h, 4, PAD) for s in frames(a, v)])
                        for a in ANIMS for v in ("down", "up", "right")]
    out = Image.new("RGBA", (max(r.width for r in lignes), sum(r.height for r in lignes)), fond)
    y = 0
    for r in lignes:
        out.alpha_composite(r, ((out.width - r.width) // 2, y))
        y += r.height
    fn = os.path.join(racine, "reference", "v2", "alice_v2.png")
    out.convert("RGB").save(fn)
    print(fn, out.size)

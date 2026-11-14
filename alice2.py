"""
Alice, version 2 — celle du jeu web (PLAN_V2.md, lot 3).

D'après reference/alice_tecky.png : cheveux châtains mi-longs et raides, frange en mèches, grands yeux noirs, joues
roses, t-shirt jaune, jupe rose. Aux pieds, depuis le 11 novembre 2026 (choix de Christophe, qui ne la voulait plus
pieds nus) : de petites chaussures rouges à bride et des socquettes blanches — le rouge du harnais de Tecky, et le
modèle de la chaussure qu'elle perd dans la forêt (items.shoe). Grosse tête (un peu plus de deux têtes de haut),
dessinée plus grand puis réduite de ECH, comme Tecky (tecky2.py) : des traits plus fins, des mains, des mèches.
Trois vues : face, dos, profil (tournée vers la droite ; la gauche est son miroir).

Animations : idle, walk, happy (le saut de joie des retrouvailles).

    python3 alice2.py      # reference/v2/alice_v2.png
"""
import math
import os

from spritelib import Drawing, circle, ellipse, path, poly, line, OUTLINE

SOL = 70                 # ligne du sol
X0 = 30.0                # axe du dessin
ECH = 0.59               # réduction du dessin dans le jeu. Elle a 5 ans : 41 unités de haut, contre 55 à 60 pour les
                         # adultes et 45 pour le petit Lucas. À 0,7 (47 unités), Christophe l'a fait rapetisser.
TRAIT = 1.8 / ECH
CADRE = (48, 52, 24, 48)     # le jeu : largeur, hauteur, origine (aux pieds), en unités de l'atlas
COU = 2.4                # hauteur du cou : la tête est remontée d'autant, les cheveux allongés d'autant
TETE = 19.0 - COU        # hauteur du centre de la tête

PAL = dict(skin="#FADFCB", skin_dk="#EDC6AB", hair="#B9976B", hair_hl="#DCC391", hair_dk="#94764C",
           shirt="#FBE36A", shirt_dk="#EBCB4A", skirt="#F6A9C6", skirt_dk="#E288AC",
           eye="#2A1E1A", blush="#F5A3A6", nose="#E9A392", mouth="#B8505A", white="#FFFFFF",
           sock="#FFFFFF", sock_dk="#DDD6CB", rouge="#DB352C", rouge_dk="#B02620")


ETE = None     # la tenue d'été : None (le printemps), ou dict(tong=couleur des tongs, rayures=couleur des rayures du
#                haut ou None) — les couleurs des habits se changent dans PAL (voir tenue())


def pose(**kw):
    """pas : avancée du cycle de marche (0..1) ; rebond ; saut : hauteur du saut ; bras : 0 le long du corps, 1 levés ;
    yeux : "fermes" (clignement) ou "rire" ; rire : bouche ouverte ; meche : balancement des cheveux ;
    nu : un pied nu (elle a perdu une chaussure dans la forêt : Tecky la retrouve ainsi)."""
    base = dict(pas=None, rebond=0.0, saut=0.0, bras=0.0, yeux=None, rire=False, meche=0.0, nu=False)
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


def _socquette(d, x, fy, haut=3.2, large=2.5):
    """Une socquette blanche, sur le bas de la jambe (haut : sa hauteur), de face et de dos."""
    c = PAL
    if ETE:                              # en tongs : pas de socquettes
        return
    d.add(path(f"M{x - large:.2f},{fy - haut:.2f} L{x + large:.2f},{fy - haut:.2f} L{x + large - 0.2:.2f},{fy + 0.4:.2f} "
               f"L{x - large + 0.2:.2f},{fy + 0.4:.2f} Z"), c["sock"], sil=False)
    d.raw(line(f"M{x - large:.2f},{fy - haut:.2f} L{x + large:.2f},{fy - haut:.2f}", c["sock_dk"], 0.6))


def _pied(d, x, y, s, vue="face", loin=False, nu=False):
    """Un pied dans sa petite chaussure rouge à bride, ou nu. vue : "face" (la pointe du côté s), "dos" (le talon)
    ou "profil" (x, y : le bout de la jambe ; la pointe vers la droite) ; loin : le pied du côté caché, plus sombre."""
    c = PAL
    if vue == "profil":
        cx, cy, rx, ry = x + 1.4, y + 0.3, 3.7, 2.1
    elif vue == "dos":
        cx, cy, rx, ry = x + s * 0.3, y, 3.1, 2.0
    else:
        cx, cy, rx, ry = x + s * 0.5, y, 3.5, 2.1
    if nu or ETE:                        # le pied nu : la peau, et deux petits traits pour les orteils
        if ETE and not nu:               # la tong : une semelle qui dépasse sous le pied
            d.add(ellipse(cx, cy + 0.9, rx + 0.7, ry - 0.2), ETE["tong"])
        d.add(ellipse(cx, cy, rx, ry), c["skin_dk"] if loin or vue == "dos" else c["skin"])
        if ETE and not nu and vue != "dos":      # et sa bride en V, entre les orteils
            bx = x + s * 1.5 if vue == "face" else x + 4.0
            d.raw(line(f"M{cx - rx * 0.75:.2f},{cy - 0.9:.2f} L{bx:.2f},{cy + 0.9:.2f} L{cx + rx * 0.75:.2f},{cy - 0.9:.2f}"
                       if vue == "face" else f"M{cx - 2.2:.2f},{cy - 1.4:.2f} L{bx:.2f},{cy + 0.8:.2f}", ETE["tong"], 0.9))
            return
        if vue != "dos":
            ox = x + s * 1.3 if vue == "face" else x + 4.2
            d.raw(line(f"M{ox - 0.9:.2f},{y + 0.5:.2f} L{ox - 0.9:.2f},{y + 1.7:.2f} M{ox + 0.7:.2f},{y + 0.6:.2f} L{ox + 0.7:.2f},{y + 1.7:.2f}",
                       OUTLINE, 0.45))
        return
    forme = ellipse(cx, cy + 0.1, rx + 0.5, ry + 0.4)
    d.add(forme, c["rouge_dk"] if loin else c["rouge"])
    cid = f"ch{int(cx * 10)}{int(cy * 10)}{vue[0]}"
    d.clip(cid, [forme])
    if vue == "face":                    # le dessus ouvert sur la socquette, et la bride
        d.add(ellipse(cx - s * 0.5, cy - 1.5, 2.3, 1.5), c["sock"], sil=False, clip=cid)
        d.raw(line(f"M{cx - rx + 0.2:.2f},{cy - 0.7:.2f} Q{cx:.2f},{cy - 1.7:.2f} {cx + rx - 0.2:.2f},{cy - 0.7:.2f}", c["rouge_dk"], 1.0))
    elif vue == "profil":
        d.add(ellipse(cx - 1.6, cy - 1.7, 2.3, 1.4), c["sock_dk"] if loin else c["sock"], sil=False, clip=cid)
        d.raw(line(f"M{cx - 1.3:.2f},{cy - 2.3:.2f} L{cx - 0.2:.2f},{cy - 0.4:.2f}", c["rouge_dk"], 1.0))
    if vue != "dos" and not loin:        # un reflet sur le bout
        d.add(ellipse(cx + (s * 1.5 if vue == "face" else 2.0), cy - 0.2, 0.9, 0.5), "#FFFFFF", sil=False, opacity=0.45)


def _bras(d, sx, sy, mx, my, couleur):
    """Un bras, de l'épaule (sx, sy) à la main (mx, my)."""
    d.add(_membre(sx, sy, mx, my, 4.2, 3.6), couleur)
    d.add(circle(mx, my, 2.5), couleur)


def _habits(d, Y, large=True, leves=False, col=True):
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
    if large:                # de face, de dos : l'encolure ronde (de face), et les deux manches courtes, qui font
        # partie du t-shirt ; bras levés (leves), les manches suivent les bras : ici, des épaules arrondies
        encolure = (f"L{X0 - 3.8:.2f},{Y(32.2):.2f} Q{X0:.2f},{Y(36.4):.2f} {X0 + 3.8:.2f},{Y(32.2):.2f} L" if col
                    else f"Q{X0:.2f},{Y(31.6):.2f} ")
        if leves:
            droite = f"C40.8,{Y(33.8):.2f} 41.2,{Y(36.4):.2f} 40.2,{Y(38.6):.2f} L38.6,{Y(39.4):.2f} "
            gauche = f"L19.8,{Y(38.6):.2f} C18.8,{Y(36.4):.2f} 19.2,{Y(33.8):.2f} 21.8,{Y(33.2):.2f} Z"
        else:
            droite = f"L43.6,{Y(37.4):.2f} L41.8,{Y(40.8):.2f} L38.6,{Y(39.4):.2f} "
            gauche = f"L18.2,{Y(40.8):.2f} L16.4,{Y(37.4):.2f} Z"
        haut = path(f"M21.8,{Y(33.2):.2f} {encolure}38.2,{Y(33.2):.2f} {droite}L38.8,{Y(46.4):.2f} "
                    f"Q{X0:.2f},{Y(47.6):.2f} 21.2,{Y(46.4):.2f} L21.4,{Y(39.4):.2f} {gauche}")
    else:
        haut = path(f"M24.8,{Y(33.4):.2f} Q{X0:.2f},{Y(31.6):.2f} 35.2,{Y(33.4):.2f} L35.8,{Y(46.4):.2f} "
                    f"Q{X0:.2f},{Y(47.6):.2f} 24.2,{Y(46.4):.2f} Z")
    d.clip("haut", [haut])
    d.add(haut, c["shirt"])
    d.add(path(f"M14,{Y(44.2):.2f} Q{X0:.2f},{Y(45.6):.2f} 46,{Y(44.2):.2f} L46,{Y(49):.2f} L14,{Y(49):.2f} Z"),
          c["shirt_dk"], sil=False, clip="haut", opacity=0.7)
    if ETE and ETE.get("rayures"):       # la marinière : des rayures en travers du haut
        d.raw('<g clip-path="url(#haut)">' + "".join(
            line(f"M14,{Y(v):.2f} Q{X0:.2f},{Y(v + 1.0):.2f} 46,{Y(v):.2f}", ETE["rayures"], 1.0) for v in (35.6, 38.4, 41.2, 44.0)) + "</g>")
    if large and col:        # le col : le bord de l'encolure, et sa bande un peu plus foncée
        d.raw(f'<g clip-path="url(#haut)">' + line(f"M{X0 - 4.6:.2f},{Y(32.0):.2f} Q{X0:.2f},{Y(38.0):.2f} {X0 + 4.6:.2f},{Y(32.0):.2f}",
                                                    c["shirt_dk"], 1.5) + "</g>")
        d.raw(line(f"M{X0 - 3.8:.2f},{Y(32.2):.2f} Q{X0:.2f},{Y(36.4):.2f} {X0 + 3.8:.2f},{Y(32.2):.2f}", OUTLINE, 0.8))
    elif not large:          # de profil : le col, d'un trait
        d.raw(line(f"M{X0 - 2.2:.2f},{Y(32.9):.2f} Q{X0 + 1.4:.2f},{Y(34.0):.2f} {X0 + 5.0:.2f},{Y(32.7):.2f}", c["shirt_dk"], 1.0))


def _cheveux(hy, dx=0.0, visage=False):
    """Les cheveux : un carré mi-long, coupé droit aux épaules (dx : le bas se balance). visage : la même forme,
    ouverte sur le visage (la frange en mèches en haut, un pan de chaque côté)."""
    dehors = (f"M{15.6 + dx:.2f},{hy + 12.2 + COU:.2f} L16.2,{hy:.2f} C16.0,{hy - 17.6:.2f} 44.0,{hy - 17.6:.2f} 43.8,{hy:.2f} "
              f"L{44.4 + dx:.2f},{hy + 12.2 + COU:.2f} Q{44.4 + dx:.2f},{hy + 14.8 + COU:.2f} {42.0 + dx:.2f},{hy + 14.8 + COU:.2f} ")
    fin = f"L{18.0 + dx:.2f},{hy + 14.8 + COU:.2f} Q{15.6 + dx:.2f},{hy + 14.8 + COU:.2f} {15.6 + dx:.2f},{hy + 12.2 + COU:.2f} Z"
    if not visage:
        return path(dehors + fin), None
    bord = (f"{39.9 + dx:.2f},{hy + 14.8 + COU:.2f} L39.6,{hy - 2.6:.2f} L37.4,{hy - 0.8:.2f} L36.4,{hy - 3.3:.2f} L33.6,{hy - 0.6:.2f} "
            f"L32.4,{hy - 3.5:.2f} L29.8,{hy - 0.6:.2f} L28.2,{hy - 3.5:.2f} L25.6,{hy - 0.7:.2f} L24.2,{hy - 3.3:.2f} "
            f"L21.8,{hy - 0.8:.2f} L20.4,{hy - 2.6:.2f} L{20.1 + dx:.2f},{hy + 14.8 + COU:.2f}")
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

    for s, lv in ((-1, lA), (1, lB)):                   # jambes, socquettes et chaussures
        x, fy = X0 + s * 4.2, SOL - 1.8 - lv - p["saut"]
        d.add(path(f"M{x - 2.5:.2f},{Y(54):.2f} L{x + 2.5:.2f},{Y(54):.2f} L{x + 2.3:.2f},{fy:.2f} L{x - 2.3:.2f},{fy:.2f} Z"), c["skin"])
        nu = p["nu"] and s == -1                        # son pied droit, à gauche de l'image
        if not nu:
            _socquette(d, x, fy)
        _pied(d, x, fy + 0.3, s, nu=nu)
    ar = p["bras"]
    hy = Y(TETE)
    m = p["meche"]
    # les cheveux de derrière, derrière le buste ; sous le menton, ils sont dans l'ombre (sans cou, ils faisaient
    # une barre sous la tête)
    d.add(_cheveux(hy, m)[0], c["hair"])
    d.add(path(f"M20.4,{hy + 9:.2f} L39.6,{hy + 9:.2f} L{39.9 + m:.2f},{hy + 14.8 + COU:.2f} L{20.1 + m:.2f},{hy + 14.8 + COU:.2f} Z"),
          c["hair_dk"], sil=False)
    if ar <= 0.5:                                       # bras le long du corps (levés : plus bas, devant les cheveux)
        for s, ph in ((-1, sw), (1, -sw)):
            sx, sy = X0 + s * 10.6, Y(38.0)
            _bras(d, sx, sy, sx + s * (1.6 + 5 * ar), sy + 10.4 - 8 * ar + ph * 1.6, c["skin"])
    # le cou : il descend de la tête et entre dans l'encolure ronde du t-shirt
    d.add(path(f"M{X0 - 2.7:.2f},{hy + 9:.2f} L{X0 + 2.7:.2f},{hy + 9:.2f} L{X0 + 3.4:.2f},{Y(36.5):.2f} L{X0 - 3.4:.2f},{Y(36.5):.2f} Z"),
          c["skin"], sil=False, edge=True)
    d.add(ellipse(X0, hy + 12.6, 2.7, 1.5), c["skin_dk"], sil=False, opacity=0.7)  # l'ombre du menton
    _habits(d, Y, leves=ar > 0.5)
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
            mx, my = sx + s * 6.6, sy - 21.5 * ar
            bras_, main = _membre(sx, sy, mx, my, 4.2, 3.6), circle(mx, my, 2.6)
            # la manche courte : elle suit le bras sur un tiers de sa longueur et se fond dans l'épaule du t-shirt
            # (deux carrés posés sur les épaules, avant)
            k = 0.36
            manche = _membre(sx - (mx - sx) * 0.12, sy - (my - sy) * 0.12, sx + (mx - sx) * k, sy + (my - sy) * k, 6.0, 5.4)
            epaule = circle(sx - s * 0.6, sy + 1.2, 3.2)
            _cerne(d, bras_, main, manche)
            d.add(bras_, c["skin"])
            d.add(main, c["skin"])
            d.add(manche, c["shirt"])
            d.add(epaule, c["shirt"], sil=False)
            ux, uy = (mx - sx), (my - sy)
            L = math.hypot(ux, uy)
            nx, ny = -uy / L * 2.7, ux / L * 2.7
            ex_, ey_ = sx + ux * k, sy + uy * k
            d.raw(line(f"M{ex_ + nx:.2f},{ey_ + ny:.2f} L{ex_ - nx:.2f},{ey_ - ny:.2f}", c["shirt_dk"], 0.9))   # l'ourlet

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
        nu = p["nu"] and s == 1                         # son pied droit, vu de dos : à droite de l'image
        if not nu:
            _socquette(d, x, fy)
        _pied(d, x, fy + 0.3, s, "dos", nu=nu)          # les talons
    ar = p["bras"]
    for s, ph in ((-1, -sw), (1, sw)):
        sx, sy = X0 + s * 10.6, Y(38.0)
        _bras(d, sx, sy, sx + s * (1.6 + 5 * ar), sy + 10.4 - 20 * ar + ph * 1.6, c["skin"])
    _habits(d, Y, col=False)

    hy = Y(TETE)
    m = p["meche"]
    cheveux = _cheveux(hy, m)[0]
    _cerne(d, cheveux)
    d.add(cheveux, c["hair"])
    d.raw(line(f"M30,{hy - 12:.2f} L{30 + m:.2f},{hy + 13.6 + COU:.2f} M23.6,{hy - 4:.2f} L{23.0 + m:.2f},{hy + 14 + COU:.2f} "
               f"M36.4,{hy - 4:.2f} L{37.0 + m:.2f},{hy + 14 + COU:.2f} M19.6,{hy + 4:.2f} L{19.2 + m:.2f},{hy + 13.6 + COU:.2f} "
               f"M40.4,{hy + 4:.2f} L{40.8 + m:.2f},{hy + 13.6 + COU:.2f}", c["hair_dk"], 0.6))
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

    def jambe(k, lever, couleur, loin=False):
        fx, fy = X0 + k * 4.6, SOL - 1.8 - lever - p["saut"]
        d.add(_membre(X0, Y(54), fx, fy, 5.0, 4.6), couleur)
        nu = p["nu"] and not loin                        # de profil : le pied nu est celui qu'on voit le mieux
        if not nu and not ETE:                           # la socquette, sur le bas de la jambe
            h = 0.22
            d.add(_membre(fx + (X0 - fx) * h, fy + (Y(54) - fy) * h, fx, fy + 0.3, 4.7, 4.6), c["sock_dk"] if loin else c["sock"], sil=False)
        _pied(d, fx, fy, 1, "profil", loin, nu)
        return fx, fy

    def bras(k, couleur):
        sx, sy = X0 + 0.2, Y(35.8)
        # (levés : tendus vers l'avant, sous le menton, pour ne pas cacher le visage)
        _bras(d, sx, sy, sx - k * 5.4 * (1 - ar) + ar * 14.5, sy + 12 - 18.6 * ar - abs(k) * 0.8, couleur)

    jambe(-sw, max(0.0, -sw) * 2.4, c["skin_dk"], True)  # jambe et bras du côté caché
    bras(-sw, c["skin_dk"])
    jambe(sw, max(0.0, sw) * 2.4, c["skin"])
    hy = Y(TETE)
    m = p["meche"]
    d.add(path(f"M{X0 - 1.0:.2f},{hy + 9:.2f} L{X0 + 4.6:.2f},{hy + 9:.2f} L{X0 + 3.8:.2f},{Y(35):.2f} L{X0 - 1.8:.2f},{Y(35):.2f} Z"),
          c["skin"])                                     # le cou, qui entre dans le col
    _habits(d, Y, large=False)

    visage = circle(X0 + 1.2, hy + 1.2, 11.2)
    nez = ellipse(X0 + 12.2, hy + 5.4, 1.0, 0.9)
    d.add(visage, c["skin"])
    d.add(nez, c["skin"])
    # les cheveux : toute la tête derrière le visage, la frange devant, un pan qui cache l'oreille
    cheveux = path(f"M{28.6 + m:.2f},{hy + 14.8 + COU:.2f} L{18.6 + m:.2f},{hy + 14.8 + COU:.2f} Q{16.2 + m:.2f},{hy + 14.8 + COU:.2f} {16.2 + m:.2f},{hy + 12.2 + COU:.2f} "
                   f"L16.4,{hy + 1:.2f} C16.2,{hy - 17.6:.2f} 43.4,{hy - 16.8:.2f} 43.2,{hy - 2.8:.2f} "
                   f"L41.6,{hy - 1.0:.2f} L40.4,{hy - 3.4:.2f} L38.0,{hy - 0.8:.2f} L36.6,{hy - 3.4:.2f} L34.0,{hy - 0.8:.2f} "
                   f"L32.6,{hy - 3.2:.2f} L30.2,{hy - 0.6:.2f} L29.4,{hy + 4:.2f} Z")
    d.add(cheveux, c["hair"], edge=True)
    d.raw(line(f"M38.0,{hy - 0.8:.2f} L37.4,{hy - 6.4:.2f} M34.0,{hy - 0.8:.2f} L33.6,{hy - 6.8:.2f} "
               f"M24.6,{hy - 5:.2f} L{24.0 + m:.2f},{hy + 14 + COU:.2f} M20.2,{hy + 2:.2f} L{19.8 + m:.2f},{hy + 13.6 + COU:.2f}", c["hair_dk"], 0.6))
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
    saut = [0, 5.2, 7.6, 3.0]
    bras = [0.3, 1, 1, 0.6]
    return [pose(saut=saut[i], bras=bras[i], yeux="rire", rire=True, rebond=0.9 if i == 0 else 0,
                 meche=[0, -0.4, 0.3, 0.5][i]) for i in range(4)]


ANIMS = {"idle": (a_idle, 6), "walk": (a_walk, 13), "happy": (a_happy, 8)}      # nom : (fonction, images par seconde)


# Les tenues des autres saisons : (ETE, couleurs de PAL qui changent). L'été, choisi par Christophe sur
# reference/v2/ete_options_alice.png (13 novembre 2026) : marinière, jupe rouge, tongs bleues, sans socquettes.
TENUES = {"ete": (dict(tong="#2F6FC0", rayures="#2B4C8C"), dict(shirt="#FFFFFF", shirt_dk="#DDE3EC", skirt="#E0483C", skirt_dk="#B8322A"))}


def _vetue(tenue, dessine):
    """Appelle dessine() avec Alice dans cette tenue (None : celle du printemps), puis rend ses habits du printemps."""
    global ETE
    if not tenue:
        return dessine()
    garde = dict(PAL)
    ETE = TENUES[tenue][0]
    PAL.update(TENUES[tenue][1])
    try:
        return dessine()
    finally:
        ETE = None
        PAL.clear()
        PAL.update(garde)


def frames(anim, view, nu=False, tenue=None):
    """SVG des images d'une animation. nu : Alice a un pied nu (les sprites « alice1 » du jeu : c'est ainsi que
    Tecky la retrouve, avant qu'elle remette la chaussure qu'il lui rapporte)."""
    return _vetue(tenue, lambda: [image(view, dict(p, nu=nu)) for p in ANIMS[anim][0](view)])


def portrait(p=None, tenue=None):
    """Le dessin de face, non réduit, pour le portrait (hud.py) : cadre de 60 x 76, le visage autour de (30, 21)."""
    return _vetue(tenue, lambda: devant(p or pose()))


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

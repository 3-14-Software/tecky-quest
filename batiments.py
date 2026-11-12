"""
Bâtiments, version 2 (PLAN_V2.md, lot 4) : maisons du village, boulangerie, grange, entrepôts, cabanes.

Comme la niche de nature.py : un volume vu de trois quarts, éclairé d'en haut à gauche. La façade est en pleine
lumière, le mur de droite fuit vers l'arrière dans l'ombre, le toit a une épaisseur et des rangs de tuiles ; pas
d'ombre ovale, l'ombre portée se calcule sur la silhouette (nature.ombre(), à partir de la ligne où les murs
touchent le sol : Sprite.sol).

Un bâtiment est un nature.Sprite à sa taille du jeu (pas de réduction). Les formes sont écrites en unités de
l'atlas ; la profondeur fuit vers la droite et vers le haut : un point à la profondeur p est décalé de
(p * FUITE[0], -p * FUITE[1]).

    python3 batiments.py      # reference/v2/batiments_v2.png
"""
import os

from PIL import Image

import nature
from nature import Sprite
from spritelib import Drawing, circle, ellipse, rect, path, poly, line, OUTLINE

FUITE = (0.5, 0.36)              # une unité de profondeur, à l'écran
CONTACT = 0.7                    # la ligne où un mur touche le sol (Sprite.sol) passe un peu au-dessus de son bord du
#                                  bas : l'ombre portée part de dessous le contour. Posée juste sous le mur, elle
#                                  laissait un liseré clair entre le bâtiment et son ombre (vu par Christophe).
TRAIT = 1.7
VITRE = "#A9D8F2"


def _fonce(couleur, k=0.8):
    """La même couleur, plus sombre."""
    return "#" + "".join(f"{int(int(couleur[i:i + 2], 16) * k):02X}" for i in (1, 3, 5))


def _p(x, y, prof=0.0):
    """Point de l'écran : x le long de la façade, y la hauteur à l'écran, reculé de `prof`."""
    return (x + prof * FUITE[0], y - prof * FUITE[1])


def _pts(pts):
    return poly([(round(x, 2), round(y, 2)) for x, y in pts])


def _dessin(w, h):
    d = Drawing(w, h)
    d.vitres = []            # (forme, croisillons) : ce qui s'allume le soir (lumieres())
    return d


def _fenetre(d, x, y, w, h, volets=None, jardiniere=True, croisillons=True):
    """Fenêtre de la façade : vitre (un reflet en biais), croisillons blancs, appui ; volets ; jardinière fleurie."""
    barres = f"M{x + w / 2},{y + 0.6} L{x + w / 2},{y + h - 0.6} M{x + 0.6},{y + h / 2} L{x + w - 0.6},{y + h / 2}"
    d.vitres.append((rect(x, y, w, h, 1.2), barres if croisillons else ""))
    if volets:
        for sx in (x - 5.2, x + w + 0.7):
            d.add(rect(sx, y - 0.5, 4.5, h + 1, 0.8), volets, sil=False, edge=True)
            d.raw(line(f"M{sx + 0.9},{y + h * 0.33:.1f} L{sx + 3.6},{y + h * 0.33:.1f} M{sx + 0.9},{y + h * 0.66:.1f} "
                       f"L{sx + 3.6},{y + h * 0.66:.1f}", OUTLINE, 0.5))
    cid = f"vitre{x:.0f}_{y:.0f}"
    d.clip(cid, [rect(x, y, w, h, 1.2)])
    d.add(rect(x, y, w, h, 1.2), VITRE, sil=False, edge=True)
    d.add(_pts([(x + w * 0.1, y + h), (x + w * 0.55, y), (x + w * 0.85, y), (x + w * 0.4, y + h)]), "#D4EEFB", sil=False, clip=cid)
    d.add(rect(x, y, w, 1.6), "#6FA9CC", sil=False, clip=cid, opacity=0.55)                   # ombre du linteau
    if croisillons:
        d.raw(line(barres, "#FFFFFF", 1.2))
    if jardiniere:
        d.add(rect(x - 1.2, y + h - 0.4, w + 2.4, 3.8, 1), "#9A6B43", sil=False, edge=True)
        for k in range(int((w + 1) / 3.6)):
            d.add(circle(x + 1.2 + k * 3.6, y + h - 0.9, 1.5), ("#E24B4B", "#F7D154", "#F28CB8")[k % 3], sil=False)
    else:
        d.add(rect(x - 1, y + h - 0.2, w + 2, 1.8, 0.6), "#E9DFC9", sil=False, edge=True)


def _fenetre_cote(d, x1, y, p0, pw, h):
    """Fenêtre du mur de droite, qui fuit (de la profondeur p0 à p0 + pw) : un parallélogramme, la vitre dans l'ombre."""
    a, b, c, e = _p(x1, y, p0), _p(x1, y, p0 + pw), _p(x1, y + h, p0 + pw), _p(x1, y + h, p0)
    d.add(_pts([a, b, c, e]), "#7FB4D2", sil=False, edge=True)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    barre = f"M{mx:.2f},{my:.2f} L{mx:.2f},{my + h:.2f}"
    d.raw(line(barre, "#E9E3D4", 0.9))
    d.vitres.append((_pts([a, b, c, e]), barre))


def _porte(d, x, y, w, h, couleur, ronde=False):
    """Porte de la façade, son encadrement, sa poignée, une marche de pierre."""
    forme = (path(f"M{x},{y + h} L{x},{y + w * 0.45:.2f} Q{x + w / 2},{y - w * 0.12:.2f} {x + w},{y + w * 0.45:.2f} L{x + w},{y + h} Z")
             if ronde else rect(x, y, w, h, 1.6))
    d.add(forme, couleur, sil=False, edge=True)
    d.raw(line(f"M{x + w / 2},{y + (w * 0.2 if ronde else 1.5):.2f} L{x + w / 2},{y + h}", OUTLINE, 0.5))
    d.add(rect(x + w * 0.56, y + 1.2 + (w * 0.3 if ronde else 0), w * 0.38, h - 1.2 - (w * 0.3 if ronde else 0), 1), "#000000", sil=False, opacity=0.12)
    d.add(circle(x + w * 0.8, y + h * 0.58, 1.1), "#F2C14E", sil=False)
    d.add(rect(x - 2, y + h - 0.8, w + 4, 3, 1), "#C4BEB2", sil=False, edge=True)


def _cheminee(d, x, y, h, brique="#B26A50"):
    """Cheminée de brique sur le toit : face éclairée, flanc droit dans l'ombre, chapeau de pierre."""
    d.add(rect(x, y, 9, h), brique)
    d.add(_pts([(x + 9, y), (x + 12, y - 2.2), (x + 12, y + h - 2.2), (x + 9, y + h)]), "#8C4E3A")
    d.add(_pts([(x - 1, y), (x + 10, y), (x + 13.4, y - 2.6), (x + 2.4, y - 2.6)]), "#D9D2C5", edge=True)
    for k in range(1, int(h / 4)):
        d.raw(line(f"M{x + 0.6},{y + k * 4} L{x + 8.4},{y + k * 4}", "#8C4E3A", 0.5))


def _tuiles(d, cid, coins, rangs, sombre, clair, biais, pas=8.0):
    """Rangs de tuiles d'un pan de toit (un parallélogramme : coins bas gauche, bas droit, haut droit, haut gauche,
    déjà dans le clip `cid`) : lignes parallèles à la rive, joints décalés d'un rang sur l'autre (ils penchent comme
    le pan : `biais` = décalage en x par unité de y), une bande claire sous le faîtage."""
    (x0, y0), (x1, _), (x2, y2), (x3, _) = coins
    h = y0 - y2
    d.add(_pts([(x3, y2), (x2, y2), (x2 - biais * h * 0.2, y2 + h * 0.2), (x3 - biais * h * 0.2, y2 + h * 0.2)]), clair, sil=False,
          clip=cid, opacity=0.5)
    for i in range(1, rangs):
        y = y0 - h * i / rangs
        dx = biais * (y0 - y)
        d.raw(f'<g clip-path="url(#{cid})">' + line(f"M{x0 + dx:.2f},{y:.2f} L{x1 + dx:.2f},{y:.2f}", sombre, 0.9) + "</g>")
    for i in range(rangs):
        ya, yb = y0 - h * i / rangs, y0 - h * (i + 1) / rangs
        x = x0 + (pas / 2 if i % 2 else 0) + 3
        while x < x1 + 2:
            d.raw(f'<g clip-path="url(#{cid})">' + line(f"M{x + biais * (y0 - ya):.2f},{ya:.2f} L{x + biais * (y0 - yb):.2f},{yb:.2f}", sombre, 0.6) + "</g>")
            x += pas


# ====================================================================== LES DEUX VOLUMES
TUILE = ("#D4563F", "#A9402E", "#EE8A72")         # toit : base, ombre, lumière
BRUNE = ("#A9603F", "#7E4229", "#C98562")
ARDOISE = ("#6F7C92", "#515D72", "#94A1B5")
TOLE = ("#A7B1BC", "#8792A0", "#C6CFD9")
CREME = ("#F4E6C8", "#CDB790")                    # murs : au soleil, à l'ombre
PIERRE = ("#C9C2B4", "#9E9588")                   # soubassement : au soleil, à l'ombre


def _murs_facade(d, x0, x1, yb, yt, prof, mur, pignon_haut=None, plinthe=True):
    """Le mur de droite, qui fuit dans l'ombre (un pignon s'il monte jusqu'au faîte `pignon_haut`), puis la façade,
    son soubassement de pierre et l'ombre du débord de toit. Rend la ligne où les murs touchent le sol."""
    cote = [_p(x1, yb), _p(x1, yb, prof), _p(x1, yt, prof)] + ([pignon_haut] if pignon_haut else []) + [_p(x1, yt)]
    d.clip("cote", [_pts(cote)])
    d.add(_pts(cote), mur[1])
    d.clip("face", [rect(x0, yt, x1 - x0, yb - yt)])
    d.add(rect(x0, yt, x1 - x0, yb - yt), mur[0])
    if plinthe:
        d.add(_pts([_p(x1, yb - 3.5), _p(x1, yb - 3.5, prof), _p(x1, yb, prof), _p(x1, yb)]), PIERRE[1], sil=False, clip="cote")
        d.add(rect(x0, yb - 3.5, x1 - x0, 3.5), PIERRE[0], sil=False, clip="face")
        d.raw(line(f"M{x0},{yb - 3.5} L{x1},{yb - 3.5}", PIERRE[1], 0.6))
    return [(x0, yb - CONTACT), (x1, yb - CONTACT), _p(x1, yb - CONTACT, prof)]


def _toit_long(d, x0, x1, yt, prof, comble, toit, rangs=4, couverture="tuiles", avant=None):
    """Toit d'une maison vue par sa façade longue : la rive du pan arrière le long du pignon de droite, le pan de
    devant (rangs de tuiles ou d'ardoises, ou nervures de tôle), l'épaisseur de sa rive, la faîtière.
    avant(faîte y) : dessiné avant le pan (la cheminée, dont le pied passe derrière). Rend (biais, e0, faîte y)."""
    faite = _p(x1, yt - comble, prof / 2)
    biais = (prof / 2 * FUITE[0]) / (comble + prof / 2 * FUITE[1] + 2.5)
    e0, e1 = (x0 - 3.5, yt + 2.5), (x1 + 1.5, yt + 2.5)
    hp = e0[1] - faite[1]
    r0, r1 = (e0[0] + biais * hp, faite[1]), (e1[0] + biais * hp, faite[1])
    if avant:
        avant(faite[1])
    arriere = _p(x1 + 1.5, yt + 2.5, prof)
    d.add(_pts([r1, (r1[0] + 2.4, r1[1]), (arriere[0] + 2.4, arriere[1]), arriere]), toit[1])       # rive du pan arrière
    pan = [e0, e1, r1, r0]
    d.clip("pan", [_pts(pan)])
    d.add(_pts(pan), toit[0])
    if couverture == "tole":
        d.add(_pts([r0, r1, (r1[0] - biais * hp * 0.25, r1[1] + hp * 0.25), (r0[0] - biais * hp * 0.25, r0[1] + hp * 0.25)]), toit[2],
              sil=False, clip="pan", opacity=0.5)
        x = e0[0] + 5
        while x < e1[0]:
            d.raw('<g clip-path="url(#pan)">' + line(f"M{x:.2f},{e0[1]:.2f} L{x + biais * hp:.2f},{faite[1]:.2f}", toit[1], 0.8) + "</g>")
            x += 7
    else:
        _tuiles(d, "pan", pan, rangs, toit[1], toit[2], biais, 8.0 if couverture == "tuiles" else 6.0)
    d.add(_pts([e0, e1, (e1[0], e1[1] + 2.6), (e0[0], e0[1] + 2.6)]), toit[1])                     # rive du bas : l'épaisseur
    d.add(_pts([e1, (e1[0] + 2.4, e1[1]), (r1[0] + 2.4, r1[1]), r1]), toit[1])                     # rive du pignon
    d.add(_pts([(r0[0] - 1, r0[1] - 1.6), (r1[0] + 2.6, r1[1] - 1.6), (r1[0] + 2.6, r1[1] + 1.4), (r0[0] - 1, r0[1] + 1.4)]), toit[2])
    return biais, e0, faite[1]


def _toit_pignon(d, profil, prof, toit, lignes=3, avant=None, debord=4.5):
    """Toit d'une maison vue par son pignon. profil : la ligne du toit sur le pignon, de la rive gauche à la rive
    droite en passant par le faîte (3 points, ou 5 pour un toit brisé). Les pans de droite fuient vers l'arrière,
    dans l'ombre ; ceux de gauche se voient par la tranche, éclairée. avant() : dessiné après les pans de droite
    (la cheminée, plantée dedans)."""
    n, a = len(profil), len(profil) // 2

    def bout(p, q):                                    # la rive dépasse le mur, dans l'axe du pan
        L = ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5
        return (p[0] + (p[0] - q[0]) / L * debord, p[1] + (p[1] - q[1]) / L * debord)
    haut = [(x, y - 3) for x, y in profil]
    haut[0], haut[-1] = bout(haut[0], haut[1]), bout(haut[-1], haut[-2])
    P = prof + 3
    for i in range(n - 1, a, -1):                      # pans de droite, du bas vers le faîte
        p, q = haut[i], haut[i - 1]
        quad = [p, _p(p[0], p[1], P), _p(q[0], q[1], P), q]
        cid = f"pan{i}"
        d.clip(cid, [_pts(quad)])
        d.add(_pts(quad), toit[1])
        if i < n - 1:                                  # (toit brisé : le pan du haut, plus couché, prend un peu de lumière)
            d.add(_pts(quad), toit[0], sil=False, clip=cid, opacity=0.45)
        for k in range(1, lignes + 1):
            t = k / (lignes + 1)
            u, v = (q[0] + (p[0] - q[0]) * t, q[1] + (p[1] - q[1]) * t), None
            v = _p(u[0], u[1], P)
            d.raw(f'<g clip-path="url(#{cid})">' + line(f"M{u[0]:.2f},{u[1]:.2f} L{v[0]:.2f},{v[1]:.2f}", _fonce(toit[1]), 0.8) + "</g>")
    if avant:
        avant()
    bas = [(x, y + 0.6) for x, y in profil]
    bas[0], bas[-1] = (haut[0][0] + 2.6, haut[0][1] + 3.2), (haut[-1][0] - 2.6, haut[-1][1] + 3.2)
    d.add(_pts(haut + bas[::-1]), toit[0])                                                  # la tranche du toit, devant
    d.add(_pts(haut[:a + 1] + [(x + 1.4, y + 1.5) for x, y in haut[a::-1]]), toit[2], sil=False)   # lumière sur les pans de gauche
    f0, f1 = haut[a], _p(haut[a][0], haut[a][1], P)
    d.add(_pts([f0, f1, (f1[0] + 1.6, f1[1] + 1.6), (f0[0] + 1.6, f0[1] + 1.6)]), toit[0], sil=False)        # faîtage


def _ombre_pignon(d, profil, clip):
    """Ombre de la rive du toit sur le haut du pignon."""
    d.add(_pts(profil + [(x, y + 5) for x, y in profil[::-1]]), "#000000", sil=False, clip=clip, opacity=0.16)


# ====================================================================== MAISONS DU VILLAGE
def maison(toit=TUILE, mur=CREME, porte="#8A5A3A", volets=None):
    """Maison de trois quarts, la façade longue devant : mur de face en pleine lumière, pignon de droite dans
    l'ombre, pan de toit tourné vers nous."""
    w, h, px, py = 100, 100, 48, 92
    x0, larg, haut, prof, comble = 8, 62, 36, 30, 26
    x1, yb, yt = x0 + larg, py, py - haut
    d = _dessin(w, h)
    sol = _murs_facade(d, x0, x1, yb, yt, prof, mur, _p(x1, yt - comble, prof / 2))
    _fenetre_cote(d, x1, yt + 13, prof * 0.3, prof * 0.4, 11)
    d.add(rect(x0, yt, larg, 5), "#000000", sil=False, clip="face", opacity=0.16)
    _fenetre(d, x0 + 6.5, yt + 10, 13, 14, volets)
    _fenetre(d, x1 - 19.5, yt + 10, 13, 14, volets)
    _porte(d, x0 + larg / 2 - 7, yb - 27, 14, 26.4, porte)
    _toit_long(d, x0, x1, yt, prof, comble, toit, avant=lambda y: _cheminee(d, x0 + larg * 0.66, y - 9, 16))
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


def maison_pignon(toit=TUILE, mur=CREME, porte="#8A5A3A", volets=None, oeil=False):
    """Maison de trois quarts, le pignon devant, comme la niche : la porte dans le pignon, le pan de toit de droite
    qui fuit vers l'arrière dans l'ombre, celui de gauche vu par la tranche. oeil : un œil-de-bœuf au grenier."""
    w, h, px, py = 100, 106, 47, 98
    x0, larg, haut, prof, comble = 12, 50, 36, 40, 27
    x1, yb, yt, xm = x0 + larg, py, py - haut, x0 + larg / 2
    d = _dessin(w, h)
    cote = [_p(x1, yb), _p(x1, yb, prof), _p(x1, yt, prof), _p(x1, yt)]
    d.clip("cote", [_pts(cote)])
    d.add(_pts(cote), mur[1])
    d.add(_pts([_p(x1, yb - 3.5), _p(x1, yb - 3.5, prof), _p(x1, yb, prof), _p(x1, yb)]), PIERRE[1], sil=False, clip="cote")
    _fenetre_cote(d, x1, yt + 13, prof * 0.32, prof * 0.36, 11)
    profil = [(x0, yt), (xm, yt - comble), (x1, yt)]
    pignon = [(x0, yb)] + profil + [(x1, yb)]
    d.clip("pignon", [_pts(pignon)])
    d.add(_pts(pignon), mur[0])
    d.add(rect(x0, yb - 3.5, larg, 3.5), PIERRE[0], sil=False, clip="pignon")
    d.raw(line(f"M{x0},{yb - 3.5} L{x1},{yb - 3.5}", PIERRE[1], 0.6))
    _ombre_pignon(d, profil, "pignon")
    if oeil:
        d.vitres.append((circle(xm, yt - 7.5, 5), f"M{xm},{yt - 12} L{xm},{yt - 3} M{xm - 4.5},{yt - 7.5} L{xm + 4.5},{yt - 7.5}"))
        d.add(circle(xm, yt - 7.5, 6.2), "#E9DFC9", sil=False, edge=True)
        d.add(circle(xm, yt - 7.5, 4.6), VITRE, sil=False, edge=True)
        d.raw(line(d.vitres[-1][1], "#FFFFFF", 1.1))
    else:
        _fenetre(d, xm - 5.5, yt - 13, 11, 11, None, jardiniere=False)
    _fenetre(d, x0 + 5, yt + 10, 12, 14, volets)
    _porte(d, x1 - 21.5, yb - 27, 14, 26.4, porte)
    _toit_pignon(d, profil, prof, toit, avant=lambda: _cheminee(d, xm + 19, yt - comble - 1, 15))
    sol = [(x0, yb - CONTACT), (x1, yb - CONTACT), _p(x1, yb - CONTACT, prof)]
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


def maison_colombages():
    """Maison à colombages, pignon devant : murs crème, poutres brunes (croix de Saint-André), toit pentu de tuiles
    brunes, volets rouges, porte ronde."""
    w, h, px, py = 100, 108, 47, 100
    x0, larg, haut, prof, comble = 13, 48, 36, 38, 30
    x1, yb, yt, xm = x0 + larg, py, py - haut, x0 + larg / 2
    mur, bois, bois_o = ("#F7EDD6", "#D5C6A6"), "#7A4B2C", "#5F3920"
    d = _dessin(w, h)
    cote = [_p(x1, yb), _p(x1, yb, prof), _p(x1, yt, prof), _p(x1, yt)]
    d.clip("cote", [_pts(cote)])
    d.add(_pts(cote), mur[1])
    d.add(_pts([_p(x1, yb - 3.5), _p(x1, yb - 3.5, prof), _p(x1, yb, prof), _p(x1, yb)]), PIERRE[1], sil=False, clip="cote")
    for p in (prof * 0.34, prof * 0.68):                                        # poteaux et sablière du mur qui fuit
        a, b = _p(x1, yb - 3.5, p), _p(x1, yt, p)
        d.raw('<g clip-path="url(#cote)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", bois_o, 2.0) + "</g>")
    a, b = _p(x1, yt + 16), _p(x1, yt + 16, prof)
    d.raw('<g clip-path="url(#cote)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", bois_o, 2.0) + "</g>")
    _fenetre_cote(d, x1, yt + 3.5, prof * 0.4, prof * 0.22, 9)
    profil = [(x0, yt), (xm, yt - comble), (x1, yt)]
    pignon = [(x0, yb)] + profil + [(x1, yb)]
    d.clip("pignon", [_pts(pignon)])
    d.add(_pts(pignon), mur[0])
    d.add(rect(x0, yb - 3.5, larg, 3.5), PIERRE[0], sil=False, clip="pignon")
    _ombre_pignon(d, profil, "pignon")

    def poutre(x_a, y_a, x_b, y_b, ep=2.4):
        d.raw('<g clip-path="url(#pignon)">' + line(f"M{x_a:.2f},{y_a:.2f} L{x_b:.2f},{y_b:.2f}", bois, ep) + "</g>")
    for x in (x0 + 1.2, x0 + 15, x1 - 15, x1 - 1.2):                            # poteaux
        poutre(x, yt, x, yb - 3.5)
    poutre(x0, yt, x1, yt)                                                      # entrait, au pied du pignon
    poutre(x0, yt + 17, x0 + 15, yt + 17)
    poutre(x1 - 15, yt + 17, x1, yt + 17)
    poutre(xm, yt, xm, yt - comble + 3)                                         # poinçon
    poutre(x0 + 10, yt, xm - 9, yt - 17)                                        # décharges du grenier
    poutre(x1 - 10, yt, xm + 9, yt - 17)
    poutre(x1 - 13.6, yt + 2, x1 - 2.6, yt + 15.6, 2.0)                         # croix de Saint-André
    poutre(x1 - 2.6, yt + 2, x1 - 13.6, yt + 15.6, 2.0)
    poutre(x0 + 2.6, yt + 19, x0 + 13.6, yb - 5, 2.0)
    poutre(x0 + 13.6, yt + 19, x0 + 2.6, yb - 5, 2.0)
    _fenetre(d, xm - 4.5, yt - 15, 9, 10, "#C8453A", jardiniere=False)
    _fenetre(d, x0 + 3.6, yt + 4, 9, 10, None)
    _fenetre(d, x1 - 12.6, yt + 21, 9, 9, None, jardiniere=False)
    _porte(d, xm - 7, yb - 26, 14, 25.4, "#7E4A2A", ronde=True)
    _toit_pignon(d, profil, prof, BRUNE, avant=lambda: _cheminee(d, xm + 18, yt - comble - 2, 15))
    sol = [(x0, yb - CONTACT), (x1, yb - CONTACT), _p(x1, yb - CONTACT, prof)]
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


def maison_haute():
    """Maison de ville à étage, façade devant : murs ocre jaune, volets verts, toit d'ardoises avec une lucarne,
    petit balcon en fer forgé, porte sous un auvent."""
    w, h, px, py = 100, 126, 48, 118
    x0, larg, haut, prof, comble = 9, 60, 62, 30, 24
    x1, yb, yt = x0 + larg, py, py - haut
    mur, vert = ("#F2D58A", "#CBAA5E"), "#4F8F5A"
    d = _dessin(w, h)
    sol = _murs_facade(d, x0, x1, yb, yt, prof, mur, _p(x1, yt - comble, prof / 2))
    a, b = _p(x1, yt + 31), _p(x1, yt + 31, prof)
    d.raw('<g clip-path="url(#cote)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#A88B48", 2.4) + "</g>")
    _fenetre_cote(d, x1, yt + 13, prof * 0.3, prof * 0.4, 12)
    _fenetre_cote(d, x1, yt + 43, prof * 0.3, prof * 0.4, 12)
    d.add(rect(x0, yt, larg, 5), "#000000", sil=False, clip="face", opacity=0.16)
    d.add(rect(x0, yt + 29.6, larg, 2.8), "#E3C06E", sil=False, edge=True)                 # bandeau entre les étages
    for x in (x0 + 6.6, x0 + 43.4):
        _fenetre(d, x, yt + 9, 10, 15, vert)
    bx = x0 + 25
    _fenetre(d, bx, yt + 8, 10, 19, None, jardiniere=False)                                # porte-fenêtre du balcon
    d.add(rect(bx - 4, yt + 26.6, 18, 2.2, 0.6), "#3A3A44", sil=False)                     # balcon en fer forgé
    for x in range(int(bx) - 3, int(bx) + 14, 3):
        d.raw(line(f"M{x},{yt + 20} L{x},{yt + 27.4}", "#3A3A44", 0.7))
    d.raw(line(f"M{bx - 4},{yt + 20} L{bx + 14},{yt + 20}", "#3A3A44", 1.0))
    for x in (x0 + 6.6, x0 + 43.4):
        _fenetre(d, x, yt + 39, 10, 14, vert)
    _porte(d, x0 + 23, yb - 28, 14, 27.4, "#3F7D5A")
    d.add(_pts([(x0 + 19, yb - 28), (x0 + 41, yb - 28), (x0 + 38, yb - 33), (x0 + 22, yb - 33)]), ARDOISE[1], sil=False, edge=True)   # auvent
    biais, e0, fy = _toit_long(d, x0, x1, yt, prof, comble, ARDOISE, couverture="ardoises",
                               avant=lambda y: _cheminee(d, x0 + larg * 0.7, y - 10, 17))
    # lucarne, plantée dans le pan de devant : sa joue de droite et son petit pan à l'ombre, son pignon, sa rive claire
    lx, ly = x0 + 21 + biais * 10, yt - 6
    d.add(_pts([(lx + 14, ly + 7), (lx + 14, ly - 3), (lx + 19, ly - 6), (lx + 19, ly + 3.4)]), mur[1])
    d.add(_pts([(lx + 7, ly - 11.5), (lx + 16.6, ly - 2.6), (lx + 22, ly - 6), (lx + 12.4, ly - 14.8)]), ARDOISE[1])
    d.add(_pts([(lx, ly + 7), (lx, ly - 3), (lx + 7, ly - 9.4), (lx + 14, ly - 3), (lx + 14, ly + 7)]), mur[0])
    d.vitres.append((rect(lx + 3, ly - 2.4, 8, 8, 1), f"M{lx + 7},{ly - 2.4} L{lx + 7},{ly + 5.6}"))
    d.add(rect(lx + 3, ly - 2.4, 8, 8, 1), VITRE, sil=False, edge=True)
    d.raw(line(d.vitres[-1][1], "#FFFFFF", 1.0))
    d.add(_pts([(lx - 2.6, ly - 2), (lx + 7, ly - 11.5), (lx + 16.6, ly - 2.6), (lx + 14.6, ly - 0.6), (lx + 7, ly - 7.6), (lx - 0.6, ly - 0.2)]), ARDOISE[2])
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


def boulangerie():
    """La boulangerie du village, façade devant : vitrine pleine de pains, store rayé bleu et blanc festonné,
    enseigne avec une baguette et un croissant dorés, porte vitrée, ardoise des prix sur le trottoir."""
    w, h, px, py = 122, 100, 54, 92
    x0, larg, haut, prof, comble = 8, 76, 38, 30, 24
    x1, yb, yt = x0 + larg, py, py - haut
    mur = ("#F7E7D0", "#D2BE9E")
    d = _dessin(w, h)
    sol = _murs_facade(d, x0, x1, yb, yt, prof, mur, _p(x1, yt - comble, prof / 2))
    _fenetre_cote(d, x1, yt + 14, prof * 0.3, prof * 0.4, 12)
    d.add(rect(x0, yt, larg, 5), "#000000", sil=False, clip="face", opacity=0.16)
    # enseigne : baguette et croissant
    ex, ey = x0 + 14, yt + 3.2
    d.add(rect(ex, ey, 48, 10, 2), "#5B3A22", sil=False, edge=True)
    d.add(path(f"M{ex + 6},{ey + 7.4} Q{ex + 20},{ey + 0.6} {ex + 32},{ey + 3.4} Q{ex + 34},{ey + 4.9} {ex + 32},{ey + 6.4} "
               f"Q{ex + 20},{ey + 4.4} {ex + 7},{ey + 9.2} Q{ex + 4},{ey + 9.2} {ex + 6},{ey + 7.4} Z"), "#E8B55A", sil=False, edge=True)
    for x in (13, 19, 25):
        d.raw(line(f"M{ex + x},{ey + 5 - (x - 13) * 0.12:.1f} L{ex + x + 2.4},{ey + 6.6 - (x - 13) * 0.12:.1f}", "#B97A30", 0.8))
    d.add(path(f"M{ex + 35},{ey + 7.9} Q{ex + 36},{ey + 1.9} {ex + 41},{ey + 1.9} Q{ex + 46},{ey + 1.9} {ex + 47},{ey + 7.9} "
               f"Q{ex + 44},{ey + 5.4} {ex + 41},{ey + 6} Q{ex + 38},{ey + 5.4} {ex + 35},{ey + 7.9} Z"), "#E8B55A", sil=False, edge=True)
    # vitrine pleine de pains, porte vitrée (sous le store)
    vy = yt + 25
    d.vitres.append((rect(x0 + 4, vy, 39, 11.5, 1), ""))
    d.add(rect(x0 + 4, vy, 39, 11.5, 1), "#CFE9F5", sil=False, edge=True)
    for x in (x0 + 10, x0 + 19, x0 + 28, x0 + 37):
        d.add(ellipse(x, vy + 7.6, 3.9, 2.5), "#D99A4E", sil=False, edge=True)
        d.raw(line(f"M{x - 1.7},{vy + 7.1} L{x - 0.5},{vy + 8.5} M{x + 0.7},{vy + 6.7} L{x + 1.9},{vy + 8.1}", "#A86A2C", 0.6))
    d.raw(line(f"M{x0 + 8},{vy + 4.4} L{x0 + 21},{vy + 1.2} M{x0 + 14},{vy + 4.9} L{x0 + 27},{vy + 1.7}", "#D99A4E", 2.0))
    d.add(rect(x0 + 4, yb - 1.4, 39, 1.4), PIERRE[0], sil=False)
    d.vitres.append((rect(x0 + 47, vy - 1, 15, yb - vy + 0.4, 1), f"M{x0 + 54.5},{vy - 1} L{x0 + 54.5},{yb - 0.6}"))
    d.add(rect(x0 + 47, vy - 1, 15, yb - vy + 0.4, 1), "#CFE9F5", sil=False, edge=True)
    d.raw(line(d.vitres[-1][1], "#8A5A3A", 1.0))
    d.add(rect(x0 + 45, yb - 0.8, 19, 3, 1), "#C4BEB2", sil=False, edge=True)
    # store rayé festonné, par-dessus
    sy = yt + 15
    for i, x in enumerate(range(x0 + 2, x1 - 4, 7)):
        d.add(rect(x, sy, 7, 7.5, 0), ("#3E7BC4", "#FFFFFF")[i % 2], sil=False)
        d.add(circle(x + 3.5, sy + 7.5, 3.5), ("#3E7BC4", "#FFFFFF")[i % 2], sil=False)
    fin = x0 + 2 + 7 * len(range(x0 + 2, x1 - 4, 7))
    d.raw(line(f"M{x0 + 2},{sy} L{fin},{sy} M{x0 + 2},{sy} L{x0 + 2},{sy + 7.5} M{fin},{sy} L{fin},{sy + 7.5}", OUTLINE, 0.9))
    d.raw(path(f"M{x0 + 2},{sy + 7.5} " + " ".join(f"A3.5,3.5 0 0 0 {x + 7},{sy + 7.5}" for x in range(x0 + 2, x1 - 4, 7)))
          .replace('fill="%F%"', 'fill="none"').replace("/>", f' stroke="{OUTLINE}" stroke-width="0.9"/>'))
    _toit_long(d, x0, x1, yt, prof, comble, TUILE, avant=lambda y: _cheminee(d, x0 + larg * 0.72, y - 9, 16))
    # ardoise des prix, posée devant
    ax = x1 - 6
    d.add(_pts([(ax - 6, yb + 1.6), (ax - 3, yb - 13), (ax + 3, yb - 13), (ax + 6, yb + 1.6)]), "#3A3A44")
    d.add(rect(ax - 3.6, yb - 11, 7.2, 8, 0.6), "#2E3A33", sil=False)
    for y in (yb - 8.6, yb - 6.1, yb - 3.6):
        d.raw(line(f"M{ax - 2.2},{y} L{ax + 2.2},{y}", "#F3F0E8", 0.6))
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


# ====================================================================== FERME, PORT, PARC
def grange():
    """Grange rouge, pignon devant, toit brisé (à la Mansart) : grande porte à deux battants et croisillons blancs,
    fenil d'où dépasse le foin, rives et chaînes d'angle blanches."""
    w, h, px, py = 132, 120, 62, 112
    x0, larg, haut, prof = 14, 72, 44, 48
    x1, yb, yt, xm = x0 + larg, py, py - haut, x0 + larg / 2
    rouge, rouge_o, blanc = "#D7332B", "#A3261F", "#FFF7E6"
    d = _dessin(w, h)
    cote = [_p(x1, yb), _p(x1, yb, prof), _p(x1, yt, prof), _p(x1, yt)]
    d.clip("cote", [_pts(cote)])
    d.add(_pts(cote), rouge_o)
    for k in range(1, 9):                                                       # planches du mur qui fuit
        a, b = _p(x1, yb, prof * k / 9), _p(x1, yt, prof * k / 9)
        d.raw('<g clip-path="url(#cote)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#8A1F19", 0.7) + "</g>")
    _fenetre_cote(d, x1, yt + 14, prof * 0.36, prof * 0.28, 11)
    profil = [(x0, yt), (x0 + 11, yt - 21), (xm, yt - 33), (x1 - 11, yt - 21), (x1, yt)]
    pignon = [(x0, yb)] + profil + [(x1, yb)]
    d.clip("pignon", [_pts(pignon)])
    d.add(_pts(pignon), rouge)
    for x in range(int(x0) + 6, int(x1), 6):                                    # planches verticales
        d.raw('<g clip-path="url(#pignon)">' + line(f"M{x},{yt - 34} L{x},{yb}", "#B8281F", 0.8) + "</g>")
    _ombre_pignon(d, profil, "pignon")
    for x in (x0, x1 - 5):                                                      # chaînes d'angle blanches
        d.add(rect(x, yt + 2, 5, haut - 2, 0), blanc, sil=False, edge=True)
    # fenil, avec du foin qui dépasse, et sa poutre de levage
    d.add(rect(xm - 11, yt - 23, 22, 18, 1), blanc, sil=False, edge=True)
    d.add(rect(xm - 8, yt - 20, 16, 14, 0.5), "#3A2418", sil=False)
    d.add(path(f"M{xm - 8},{yt - 6} L{xm - 8},{yt - 12} Q{xm - 6},{yt - 15} {xm - 4},{yt - 13} Q{xm - 2},{yt - 17} {xm},{yt - 14} "
               f"Q{xm + 2},{yt - 18} {xm + 4},{yt - 14} Q{xm + 6},{yt - 16} {xm + 8},{yt - 12} L{xm + 8},{yt - 6} Z"), "#E3B94F", sil=False)
    for xa, xb in ((-6, -8.5), (-1, -1.5), (4, 6.5)):
        d.raw(line(f"M{xm + xa},{yt - 9} L{xm + xb},{yt - 3.5}", "#E3B94F", 1.4))
    d.add(rect(xm - 3, yt - 30, 6, 6, 1), "#8A5A3A", sil=False, edge=True)
    # grande porte à deux battants, croisillons en X blancs
    d.add(rect(xm - 24, yb - 38, 48, 38, 0.5), blanc, sil=False, edge=True)
    for x in (xm - 21, xm + 1):
        d.add(rect(x, yb - 35, 20, 35, 0), "#A82520", sil=False)
        d.raw(line(f"M{x + 1.5},{yb - 33.5} L{x + 18.5},{yb - 1.5} M{x + 18.5},{yb - 33.5} L{x + 1.5},{yb - 1.5}", blanc, 2.2))
        d.raw(line(f"M{x},{yb - 17.5} L{x + 20},{yb - 17.5}", blanc, 2.2))
    d.raw(line(f"M{xm},{yb - 35} L{xm},{yb}", blanc, 2.0))
    d.add(rect(xm - 3.5, yb - 21, 7, 7, 1), "#F2C14E", sil=False, edge=True)
    for x in (x0 + 7.5, x1 - 17.5):                                             # petites fenêtres
        _fenetre(d, x, yb - 32, 10, 10, None, jardiniere=False)
    d.add(rect(xm - 26, yb - 1.4, 52, 3, 1), "#C4BEB2", sil=False, edge=True)
    _toit_pignon(d, profil, prof, ("#8A5A3A", "#5F3A27", "#B07E55"), lignes=2, debord=5)
    # rive blanche le long du pignon
    rive = [(x + (2.2 if i < 2 else -2.2 if i > 2 else 0), y + 1.6) for i, (x, y) in enumerate(profil)]
    d.raw(line("M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in rive), blanc, 1.8))
    sol = [(x0, yb - CONTACT), (x1, yb - CONTACT), _p(x1, yb - CONTACT, prof)]
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


def entrepot():
    """Entrepôt du port, façade devant : murs de tôle ondulée, toit de tôle à faible pente et ses deux aérateurs,
    grand rideau de fer sous une bande jaune et noire, porte de service, fenêtre."""
    w, h, px, py = 134, 100, 64, 92
    x0, larg, haut, prof, comble = 6, 98, 44, 36, 12
    x1, yb, yt = x0 + larg, py, py - haut
    mur = ("#7F93A8", "#5F7388")
    d = _dessin(w, h)
    sol = _murs_facade(d, x0, x1, yb, yt, prof, mur, _p(x1, yt - comble, prof / 2), plinthe=False)
    for x in range(int(x0) + 4, int(x1), 5):                                    # ondulations
        d.raw(line(f"M{x},{yt + 1} L{x},{yb - 0.6}", "#6D8196", 0.8))
    for k in range(1, 8):
        a, b = _p(x1, yb, prof * k / 8), _p(x1, yt, prof * k / 8)
        d.raw('<g clip-path="url(#cote)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#526679", 0.8) + "</g>")
    d.add(rect(x0, yt, larg, 4.5), "#000000", sil=False, clip="face", opacity=0.2)
    rx = x0 + 28                                                                 # rideau de fer
    d.add(rect(rx, yb - 38, 48, 38, 1), "#C3C9D0", sil=False, edge=True)
    for y in range(int(yb) - 34, int(yb), 4):
        d.raw(line(f"M{rx + 1},{y} L{rx + 47},{y}", "#A6AEB7", 0.9))
    for k in range(8):
        x = rx + k * 6
        d.add(_pts([(x, yb - 43), (x + 3, yb - 43), (x + 6, yb - 39.5), (x + 3, yb - 39.5)]), "#F2C14E" if k % 2 == 0 else "#2B2B33", sil=False)
    d.add(rect(x1 - 17, yb - 26, 12, 26, 1), "#5E6E8C", sil=False, edge=True)   # porte de service
    d.add(circle(x1 - 8, yb - 12, 1), "#F2C14E", sil=False)
    _fenetre(d, x0 + 6, yb - 32, 16, 10, None, jardiniere=False)
    biais, e0, fy = _toit_long(d, x0, x1, yt, prof, comble, TOLE, couverture="tole")
    for cx in (x0 + 30, x0 + 78):                                               # aérateurs
        d.add(ellipse(cx, fy + 1.5, 6, 3.6), "#8B96A3")
        d.add(ellipse(cx, fy + 0.6, 4, 2.2), "#6F7A87", sil=False)
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


def guerite():
    """Cabane du gardien du port : un cube clair sous un toit plat bleu qui déborde, fenêtre, porte."""
    w, h, px, py = 68, 66, 32, 58
    x0, larg, haut, prof = 7, 38, 32, 24
    x1, yb, yt = x0 + larg, py, py - haut
    d = _dessin(w, h)
    sol = _murs_facade(d, x0, x1, yb, yt, prof, ("#E8DCC4", "#C2B496"))
    _fenetre_cote(d, x1, yt + 8, prof * 0.28, prof * 0.44, 10)
    d.add(rect(x0, yt, larg, 4), "#000000", sil=False, clip="face", opacity=0.16)
    _fenetre(d, x0 + 4.5, yt + 8, 15, 12, None, jardiniere=False)
    _porte(d, x1 - 15.5, yb - 25, 12, 24.4, "#8A5A3A")
    # dalle du toit : le dessus (au soleil), le chant de devant, le chant de droite (à l'ombre)
    a, b = (x0 - 3.5, yt - 1), (x1 + 3, yt - 1)
    c, e = _p(b[0], b[1], prof + 6), _p(a[0], a[1], prof + 6)
    d.add(_pts([a, b, c, e]), "#86A6C8")
    d.add(_pts([a, b, (b[0], b[1] + 4), (a[0], a[1] + 4)]), "#5E7FA3")
    d.add(_pts([b, c, (c[0], c[1] + 4), (b[0], b[1] + 4)]), "#4A6585")
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


def cabane():
    """La cabane d'Alice, au parc : bois peint en jaune, toit rouge, pignon devant avec un cœur, porte ouverte (un
    battant bleu rabattu), fenêtre fleurie."""
    w, h, px, py = 68, 72, 32, 64
    x0, larg, haut, prof, comble = 10, 34, 27, 20, 18
    x1, yb, yt, xm = x0 + larg, py, py - haut, x0 + larg / 2
    mur, mur_o = "#F7D154", "#D4AC3E"
    d = _dessin(w, h)
    cote = [_p(x1, yb), _p(x1, yb, prof), _p(x1, yt, prof), _p(x1, yt)]
    d.clip("cote", [_pts(cote)])
    d.add(_pts(cote), mur_o)
    for y in (yt + 5.5, yt + 11.5, yt + 17.5, yt + 23.5):
        a, b = _p(x1, y), _p(x1, y, prof)
        d.raw('<g clip-path="url(#cote)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#B8922F", 0.7) + "</g>")
    profil = [(x0, yt), (xm, yt - comble), (x1, yt)]
    pignon = [(x0, yb)] + profil + [(x1, yb)]
    d.clip("pignon", [_pts(pignon)])
    d.add(_pts(pignon), mur)
    for y in (yt + 5.5, yt + 11.5, yt + 17.5, yt + 23.5):
        d.raw(line(f"M{x0 + 0.6},{y} L{x1 - 0.6},{y}", "#E3B94F", 0.8))
    _ombre_pignon(d, profil, "pignon")
    d.add(path(f"M{xm},{yt - 2.8} C{xm - 4.4},{yt - 6} {xm - 3.6},{yt - 10.2} {xm - 1.6},{yt - 10.2} Q{xm - 0.4},{yt - 10.2} {xm},{yt - 8.8} "
               f"Q{xm + 0.4},{yt - 10.2} {xm + 1.6},{yt - 10.2} C{xm + 3.6},{yt - 10.2} {xm + 4.4},{yt - 6} {xm},{yt - 2.8} Z"), "#E24B4B", sil=False, edge=True)
    # porte ouverte (l'intérieur, un peu sombre) et son battant bleu rabattu à gauche
    px0 = x0 + 10.5
    d.add(path(f"M{px0},{yb} L{px0},{yb - 17} Q{px0},{yb - 21.4} {px0 + 6},{yb - 21.4} Q{px0 + 12},{yb - 21.4} {px0 + 12},{yb - 17} L{px0 + 12},{yb} Z"),
          "#5A3A28", sil=False, edge=True)
    d.add(path(f"M{px0 + 0.9},{yb} L{px0 + 0.9},{yb - 16.6} Q{px0 + 0.9},{yb - 20} {px0 + 6},{yb - 20} Q{px0 + 6.9},{yb - 20} {px0 + 7.5},{yb - 19.9} "
               f"L{px0 + 7.5},{yb} Z"), "#3A2418", sil=False)
    d.add(rect(px0 + 1.1, yb - 3.6, 10.2, 3.4, 0), "#7A5236", sil=False)
    d.add(path(f"M{px0},{yb - 17} Q{px0 - 2.5},{yb - 19.2} {px0 - 5.7},{yb - 18.4} L{px0 - 5.7},{yb + 1} L{px0},{yb} Z"), "#2E6FD1", edge=True)
    d.add(rect(px0 - 4.3, yb - 15.4, 2.9, 6, 0.8), "#23579F", sil=False)
    d.add(circle(px0 - 3.5, yb - 7.4, 0.9), "#F7D154", sil=False)
    _fenetre(d, x1 - 10.4, yt + 5, 8, 8, None)
    d.add(rect(px0 - 0.5, yb - 0.8, 13, 2.6, 1), "#C4BEB2", sil=False, edge=True)
    _toit_pignon(d, profil, prof, ("#D7332B", "#A82520", "#EE7A70"), lignes=2, debord=4)
    d.add(circle(xm, yt - comble - 3.4, 2), "#F7D154")                         # boule au faîte
    sol = [(x0, yb - CONTACT), (x1, yb - CONTACT), _p(x1, yb - CONTACT, prof)]
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


# ====================================================================== MARCHÉ, BASSE-COUR
STORES = {"fruits": ("#D7332B", "#FFFFFF"), "legumes": ("#3F9A4A", "#FFFFFF"), "fleurs": ("#E06BA8", "#FFFFFF")}


def _marchandises(d, genre, i, x, y):
    """Ce que porte la cagette numéro i (son bord du haut à la hauteur y) : fruits, légumes ou bouquets."""
    if genre == "fruits" or (genre == "legumes" and i == 2):
        col = ("#E0413A", "#F29A2E", "#B7D45A")[i] if genre == "fruits" else "#E0413A"
        for dx, dy in ((3, -0.5), (7.5, -1), (12, -0.5), (5.2, -3.5), (9.8, -3.5)):
            d.add(circle(x + dx, y + dy, 2.3), col, sil=False, edge=True)
            if genre == "legumes":
                d.add(circle(x + dx, y + dy - 2, 0.8), "#4E9A47", sil=False)
    elif genre == "legumes" and i == 0:                                         # carottes
        for k in range(4):
            d.add(_pts([(x + 2 + k * 3.4, y - 0.5), (x + 5.2 + k * 3.4, y - 0.5), (x + 3.6 + k * 3.4, y - 8)]), "#F08A2E", sil=False, edge=True)
            d.raw(line(f"M{x + 3.6 + k * 3.4},{y - 0.5} L{x + 3 + k * 3.4},{y + 2}", "#4E9A47", 1.2))
    elif genre == "legumes":                                                    # salades
        for dx in (4, 11):
            d.add(circle(x + dx, y - 2.5, 4.2), "#7CC45A", sil=False, edge=True)
            d.add(circle(x + dx, y - 2.5, 2), "#A8DC7E", sil=False)
    else:                                                                       # bouquets
        col = ("#F28CB8", "#F7D154", "#B48ED8")[i]
        for dx in (3.5, 7.5, 11.5):
            d.raw(line(f"M{x + dx},{y} L{x + dx},{y - 6}", "#4E9A47", 1.0))
            d.add(circle(x + dx, y - 7, 2.3), col, sil=False, edge=True)
            d.add(circle(x + dx, y - 7, 0.8), "#FFF7E6", sil=False)


def etal(genre):
    """Un étal du marché, de trois quarts : comptoir de bois (le dessus au soleil, le flanc droit à l'ombre),
    trois cagettes de marchandises, quatre poteaux et un store rayé qui fuit vers l'arrière, frangé de festons."""
    c1, c2 = STORES[genre]
    w, h, px, py = 76, 80, 33, 71
    x0, x1, yb, prof = 8, 58, py, 16
    haut, toit = yb - 23, 12                               # dessus du comptoir, bord avant du store
    bois, bois_o, bois_c = "#B98556", "#8F6238", "#DDA566"
    d = _dessin(w, h)
    for x in (x0 + 1.2, x1 - 3.8):                         # poteaux du fond
        a = _p(x, yb, prof)
        d.add(rect(a[0], toit - prof * FUITE[1], 2.6, a[1] - toit + prof * FUITE[1], 1), "#7A4E30")
    d.add(_pts([_p(x1, yb), _p(x1, yb, prof), _p(x1, haut, prof), _p(x1, haut)]), bois_o)      # flanc du comptoir
    d.add(rect(x0, haut, x1 - x0, yb - haut), bois)                                         # sa face
    for y in (haut + 9, haut + 16):
        d.raw(line(f"M{x0 + 0.8},{y} L{x1 - 0.8},{y}", "#9A6B43", 0.9))
    plateau = [(x0 - 1.5, haut), (x1 + 1.5, haut), _p(x1 + 1.5, haut, prof), _p(x0 - 1.5, haut, prof)]
    d.add(_pts(plateau), bois_c)                                                             # son dessus
    d.add(rect(x0 - 1.5, haut, x1 - x0 + 3, 3.4, 1), "#C98A4B")                             # et son chant
    for i, x in enumerate((x0 + 5.5, x0 + 21, x0 + 36.5)):                                  # cagettes, posées sur le dessus
        cy = haut - 4
        d.add(_pts([(x + 15, cy), (x + 18, cy - 2.2), (x + 18, cy - 9.2), (x + 15, cy - 7)]), "#B07A45", edge=True)
        d.add(rect(x, cy - 7, 15, 7, 0.6), bois_c, edge=True)
        d.raw(line(f"M{x + 0.6},{cy - 3.5} L{x + 14.4},{cy - 3.5}", "#B07A45", 0.7))
        _marchandises(d, genre, i, x, cy - 7)
    for x in (x0 + 0.4, x1 - 3):                           # poteaux de devant, plantés aux coins du comptoir
        d.add(rect(x, toit, 2.6, haut - toit + 1, 1), "#8A5A3A")
    # store : la toile qui fuit vers l'arrière, sa retombée de droite (à l'ombre), puis celle de devant, festonnée
    a0, a1 = (x0 - 4, toit), (x1 + 4, toit)
    b0, b1 = _p(a0[0], toit - 2, prof), _p(a1[0], toit - 2, prof)
    n = 8
    for i in range(n):
        u0, u1 = i / n, (i + 1) / n
        d.add(_pts([(a0[0] + (a1[0] - a0[0]) * u0, a0[1]), (a0[0] + (a1[0] - a0[0]) * u1, a0[1]),
                    (b0[0] + (b1[0] - b0[0]) * u1, b0[1]), (b0[0] + (b1[0] - b0[0]) * u0, b0[1])]), (c1, c2)[i % 2])
    d.add(_pts([a1, b1, (b1[0], b1[1] + 6), (a1[0], a1[1] + 7)]), _fonce(c1, 0.78))
    pas = (a1[0] - a0[0]) / n
    for i in range(n):
        x = a0[0] + i * pas
        d.add(rect(x, toit, pas, 6.5, 0), (c1, c2)[i % 2], sil=False)
        d.add(circle(x + pas / 2, toit + 6.5, pas / 2), (c1, c2)[i % 2], sil=False)
    d.raw(line(f"M{a0[0]},{toit} L{a1[0]},{toit} M{a0[0]},{toit} L{a0[0]},{toit + 6.5} M{a1[0]},{toit} L{a1[0]},{toit + 6.5}", OUTLINE, 0.9))
    d.raw(path(f"M{a0[0]},{toit + 6.5} " + " ".join(f"A{pas / 2:.2f},{pas / 2:.2f} 0 0 0 {a0[0] + (i + 1) * pas:.2f},{toit + 6.5}" for i in range(n)))
          .replace('fill="%F%"', 'fill="none"').replace("/>", f' stroke="{OUTLINE}" stroke-width="0.9"/>'))
    sol = [(x0, yb - CONTACT), (x1, yb - CONTACT), _p(x1, yb - CONTACT, prof)]
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


def poulailler():
    """Poulailler en bois sur pieds, pignon devant : toit rouge, porte ronde, plaque au cœur, rampe à barreaux, et
    son nichoir accroché au mur de droite."""
    w, h, px, py = 72, 76, 32, 68
    x0, larg, haut, prof, comble = 14, 30, 17, 22, 15
    x1, sol_y, xm = x0 + larg, py, x0 + larg / 2
    yb = sol_y - 15                                        # le plancher, sur ses pieds
    yt = yb - haut
    bois, bois_o, trait = "#C98A4B", "#9C6835", "#A36D37"
    d = _dessin(w, h)
    for x, p in ((x0 + 2, prof - 2), (x1 - 2, prof - 2), (x0 + 2, 0), (x1 - 2, 0)):           # pieds : le fond, puis devant
        a = _p(x, yb, p)
        d.add(rect(a[0] - 2, a[1] - 1, 4, sol_y - yb + 1 - (0 if p == 0 else 0), 1), "#8A5A3A" if p == 0 else "#6E4628")
    cote = [_p(x1, yb), _p(x1, yb, prof), _p(x1, yt, prof), _p(x1, yt)]
    d.clip("cote", [_pts(cote)])
    d.add(_pts(cote), bois_o)
    for y in (yt + 5.5, yt + 11):
        a, b = _p(x1, y), _p(x1, y, prof)
        d.raw('<g clip-path="url(#cote)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#7E5229", 0.7) + "</g>")
    # nichoir, accroché au mur de droite : sa face, son flanc, son couvercle incliné, la paille au fond
    nx, ny = _p(x1, yb - 1, prof * 0.3)
    d.add(_pts([(nx, ny), (nx + 9, ny - 6.5), (nx + 9, ny - 15.5), (nx, ny - 9)]), bois)
    d.add(_pts([(nx + 9, ny - 6.5), (nx + 13, ny - 6.5), (nx + 13, ny - 14), (nx + 9, ny - 15.5)]), bois_o)
    d.add(_pts([(nx + 1.6, ny - 2.4), (nx + 7.2, ny - 6.4), (nx + 7.2, ny - 11.4), (nx + 1.6, ny - 7.4)]), "#3A2418", sil=False)
    d.add(_pts([(nx + 1.6, ny - 2.4), (nx + 7.2, ny - 6.4), (nx + 7.2, ny - 8), (nx + 1.6, ny - 4)]), "#F2D27A", sil=False)
    d.add(_pts([(nx - 1.2, ny - 8.6), (nx + 9.6, ny - 16.4), (nx + 14.6, ny - 15), (nx + 4, ny - 7.4)]), "#A82520")
    # pignon
    profil = [(x0, yt), (xm, yt - comble), (x1, yt)]
    pignon = [(x0, yb)] + profil + [(x1, yb)]
    d.clip("pignon", [_pts(pignon)])
    d.add(_pts(pignon), bois)
    for y in (yt + 5.5, yt + 11):
        d.raw(line(f"M{x0 + 0.6},{y} L{x1 - 0.6},{y}", trait, 0.8))
    _ombre_pignon(d, profil, "pignon")
    d.add(rect(xm - 6, yt - 9.5, 12, 7, 1), "#F3E7CF", sil=False, edge=True)                   # plaque au cœur
    d.add(path(f"M{xm},{yt - 3.9} L{xm - 2.6},{yt - 6.5} Q{xm - 3.4},{yt - 8.2} {xm - 1.6},{yt - 8.4} Q{xm - 0.6},{yt - 8.4} {xm},{yt - 7.4} "
               f"Q{xm + 0.6},{yt - 8.4} {xm + 1.6},{yt - 8.4} Q{xm + 3.4},{yt - 8.2} {xm + 2.6},{yt - 6.5} Z"), "#E24B4B", sil=False)
    d.add(circle(xm - 4, yb - 8, 5.5), "#FFF7E6", sil=False, edge=True)                       # porte ronde
    d.add(circle(xm - 4, yb - 8, 3.8), "#3A2418", sil=False)
    # rampe à barreaux, du seuil de la porte jusqu'au sol, vers la gauche
    r0, r1 = (xm - 7, yb - 3.4), (xm - 1, yb - 3.4)
    g0, g1 = (x0 - 9, sol_y), (x0 - 2, sol_y)
    d.add(_pts([r0, r1, g1, g0]), "#B98556")
    for k in range(1, 5):
        t = k / 5
        a = (r0[0] + (g0[0] - r0[0]) * t + 0.6, r0[1] + (g0[1] - r0[1]) * t)
        b = (r1[0] + (g1[0] - r1[0]) * t - 0.6, a[1])
        d.raw(line(f"M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f}", "#7E5433", 1.2))
    _toit_pignon(d, profil, prof, ("#D7332B", "#A82520", "#EE7A70"), lignes=2, debord=4)
    sol = [(x0, sol_y - CONTACT), (x1, sol_y - CONTACT), _p(x1, sol_y - CONTACT, prof)]
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), sol)


BLEU = ("#5E6E8C", "#48556F", "#8A99B5")
CATALOGUE = {
    "maison_rouge": maison,
    "maison_rouge_pignon": lambda: maison_pignon(volets="#7A8FB0"),
    "maison_bleue": lambda: maison_pignon(BLEU, ("#E8EEF2", "#BCC7D1"), "#3F7D5A", "#5E6E8C", oeil=True),
    "maison_colombages": maison_colombages,
    "maison_haute": maison_haute,
    "boulangerie": boulangerie,
    "grange": grange,
    "entrepot": entrepot,
    "guerite": guerite,
    "cabane": cabane,
    "etal_fruits": lambda: etal("fruits"), "etal_legumes": lambda: etal("legumes"), "etal_fleurs": lambda: etal("fleurs"),
    "poulailler": poulailler,
}
# Décor de carte.json -> ses dessins (un par position, comme la nature) ; `n` reste le nom du décor : l'obstacle
# (FOOT dans game.js) ne change pas, chaque bâtiment tient dans l'emprise de celui qu'il remplace.
VARIANTES = {
    "house_red": (["maison_rouge", "maison_rouge_pignon"], [0, 1]),
    "house_blue": (["maison_bleue"], [0]),
    "house_timber": (["maison_colombages"], [0]),
    "house_tall": (["maison_haute"], [0]),
    "bakery": (["boulangerie"], [0]),
    "barn": (["grange"], [0]),
    "warehouse": (["entrepot"], [0]),
    "guard_hut": (["guerite"], [0]),
    "playhouse": (["cabane"], [0]),
    "stall_fruit": (["etal_fruits"], [0]), "stall_veg": (["etal_legumes"], [0]), "stall_flower": (["etal_fleurs"], [0]),
    "chicken_coop": (["poulailler"], [0]),
}
# Où un chat se réfugie sur chaque toit : points du cadre (game.js : REFUGES, MAP.perches)
PERCHOIRS = {
    "maison_rouge": [(24, 40), (58, 36)],
    "maison_rouge_pignon": [(46, 25.5), (74, 41)],
    "maison_bleue": [(46, 25.5), (74, 41)],
    "maison_colombages": [(46, 24.5), (73, 42)],
    "maison_haute": [(26, 44), (56, 38)],
    "boulangerie": [(26, 42), (66, 38)],
}


def perchoirs(echelle=2):
    """nom -> [[dx, dy]…] : les perchoirs, en pixels du jeu à partir du pied du bâtiment."""
    out = {}
    for nom, pts in PERCHOIRS.items():
        px, py = CATALOGUE[nom]().pied
        out[nom] = [[round((x - px) * echelle * ECH[nom]), round((y - py) * echelle * ECH[nom])] for x, y in pts]
    return out


# Taille dans le jeu : les dessins sont agrandis (Christophe les trouvait trop petits à côté des villageois, le
# 12 novembre 2026). L'obstacle du décor grandit d'autant : MAP.grow, appliqué à FOOT par game.js.
ECH = {"maison_rouge": 1.3, "maison_rouge_pignon": 1.3, "maison_bleue": 1.3, "maison_colombages": 1.3, "maison_haute": 1.3,
       "boulangerie": 1.3, "grange": 1.25, "entrepot": 1.2, "guerite": 1.25, "cabane": 1.2,
       "etal_fruits": 1.25, "etal_legumes": 1.25, "etal_fleurs": 1.25, "poulailler": 1.25}


def agrandis():
    """décor de carte.json -> son agrandissement (celui de ses dessins)."""
    return {decor: ECH[noms[0]] for decor, (noms, _) in VARIANTES.items()}


def lumieres(nom):
    """Les fenêtres d'un bâtiment, allumées : un Sprite du même cadre, que le jeu pose par-dessus le soir
    (sprite « nuit/… » ; dans le catalogue de la nature sous le nom nuit_<nom>, à la même échelle)."""
    sp = CATALOGUE[nom]()
    src = sp.calques[0][0]
    d = Drawing(sp.w, sp.h)
    for forme, barres in src.vitres:
        d.add(forme, "#FFD98A", sil=False)
        d.add(forme, "#FFF3C4", sil=False, opacity=0.5)
        if barres:
            d.raw(line(barres, "#B5823A", 1.0))
    return Sprite([(d, OUTLINE, TRAIT)], sp.w, sp.h, sp.pied)


ECLAIRES = [n for n, f in CATALOGUE.items() if f().calques[0][0].vitres]      # ceux qui ont des fenêtres
for _n, _f in CATALOGUE.items():                # ils se dessinent, se mettent à l'échelle et s'ombrent comme la nature
    nature.CATALOGUE[_n] = _f
    nature.ECHELLES[_n] = ECH[_n]
    if _n in ECLAIRES:
        nature.CATALOGUE["nuit_" + _n] = (lambda n: lambda: lumieres(n))(_n)
        nature.ECHELLES["nuit_" + _n] = ECH[_n]
nature.VARIANTES.update(VARIANTES)



if __name__ == "__main__":
    noms = list(CATALOGUE)
    ims = [nature.image(n, 6) for n in noms]
    rangs = [ims[i:i + 5] for i in range(0, len(ims), 5)]
    H = max(i.height for i in ims)
    planche = Image.new("RGBA", (max(sum(i.width for i in r) for r in rangs) + 20, len(rangs) * H + 20), (126, 196, 100, 255))
    for j, r in enumerate(rangs):
        x = 10
        for im in r:
            planche.alpha_composite(im, (x, 10 + j * H + H - im.height))
            x += im.width
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference", "v2", "batiments_v2.png")
    planche.convert("RGB").save(fn)
    print(fn, planche.size)

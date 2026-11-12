"""
Petit mobilier, version 2 (PLAN_V2.md, lot 4) : ce qui est posé dans le décor, redessiné dans la famille des
bâtiments de batiments.py et de la nature de nature.py.

- Les volumes (conteneurs, caisses, cagette, palettes, bottes de foin, tonneaux, haie, banc, boîte aux lettres) sont
  vus de trois quarts comme les étals : la face de devant en pleine lumière, le dessus plus clair, le flanc droit
  qui fuit dans l'ombre (batiments.FUITE). De face et à plat, ils juraient à côté des maisons.
- Le mobilier de la forêt (souche, tronc couché, champignons, fougère) prend le contour doux de la nature (brun du
  bois, vert foncé du feuillage) et sa lumière d'en haut à gauche.

Ce sont des nature.Sprite à leur taille du jeu, inscrits dans nature.CATALOGUE / VARIANTES : atlas, ombre portée
et choix du modèle par position comme la nature. `d.n` reste le décor de carte.json et son obstacle (FOOT dans
game.js), dans l'emprise duquel chaque dessin tient. decor.py garde les anciens dessins (éditeur de carte).

    python3 mobilier.py      # reference/v2/mobilier_v2.png
"""
import math
import os

from PIL import Image

import nature
from batiments import CONTACT, FUITE, TRAIT, _fonce, _p, _pts
from nature import BOIS, FEUILLAGES, Sprite
from spritelib import Drawing, circle, ellipse, rect, path, line, OUTLINE


def _boite(d, cle, x0, x1, yb, haut, prof, face, cote, dessus):
    """Un pavé de trois quarts : le flanc droit, la face, le dessus (clips « c », « f », « t » + cle). Rend la
    hauteur du dessus à l'écran."""
    yt = yb - haut
    formes = (("c", _pts([_p(x1, yb), _p(x1, yb, prof), _p(x1, yt, prof), _p(x1, yt)]), cote),
              ("f", rect(x0, yt, x1 - x0, haut), face),
              ("t", _pts([(x0, yt), (x1, yt), _p(x1, yt, prof), _p(x0, yt, prof)]), dessus))
    for nom, forme, couleur in formes:
        d.clip(nom + cle, [forme])
        d.add(forme, couleur)
    return yt


def _dans(d, cle, xml):
    """Un trait (ou un groupe) borné à une face de la boîte."""
    d.raw(f'<g clip-path="url(#{cle})">{xml}</g>')


def _sol_boite(x0, x1, yb, prof):
    """Ligne de contact d'un pavé : le bas de la face, puis du flanc qui fuit."""
    return [(x0, yb - CONTACT), (x1, yb - CONTACT), _p(x1, yb - CONTACT, prof)]


# ====================================================================== LE PORT
CONTENEURS = {                   # face, nervures et flanc, dessus, ferrures
    "orange": ("#DD7A2D", "#B9601E", "#EDA064", "#8F4A17"),
    "bleu": ("#3273D4", "#23579F", "#6B9BE6", "#1B4378"),
    "vert": ("#42A05F", "#2F7A46", "#74C08A", "#245E36"),
}
CONT = (80, 30, 24)              # un conteneur : longueur, hauteur, profondeur


def _conteneur(d, cle, x0, yb, couleur):
    """Un conteneur : la longue face ondulée devant, ses longerons, une plaque ; les portes au bout, dans l'ombre,
    avec leurs barres de fermeture ; le dessus nervuré."""
    face, sombre, clair, fer = CONTENEURS[couleur]
    L, H, P = CONT
    x1 = x0 + L
    yt = _boite(d, cle, x0, x1, yb, H, P, face, sombre, clair)
    for x in range(int(x0) + 5, int(x1) - 3, 3):                       # tôle ondulée : un creux, une crête
        _dans(d, "f" + cle, line(f"M{x},{yt + 3} L{x},{yb - 3}", sombre, 0.7) + line(f"M{x + 0.9},{yt + 3} L{x + 0.9},{yb - 3}", clair, 0.45))
    for y, h in ((yt, 2.6), (yb - 2.6, 2.6)):                           # longerons du haut et du bas
        d.add(rect(x0, y, L, h), _fonce(face, 0.9), sil=False)
    for x in (x0, x1 - 2.6):                                           # montants d'angle
        d.add(rect(x, yt, 2.6, H), _fonce(face, 0.9), sil=False)
    d.raw(line(f"M{x0},{yt + 2.6} L{x1},{yt + 2.6} M{x0},{yb - 2.6} L{x1},{yb - 2.6}", fer, 0.6))
    d.add(rect(x0 + 6, yt + 6, 9, 5.5, 0.6), "#F4EFE4", sil=False)     # la plaque
    d.raw(line(f"M{x0 + 7.4},{yt + 7.8} L{x0 + 13.6},{yt + 7.8} M{x0 + 7.4},{yt + 9.7} L{x0 + 11.6},{yt + 9.7}", fer, 0.7))
    for p in range(4, P, 5):                                           # dessus : nervures qui fuient
        a, b = _p(x0, yt, p), _p(x1, yt, p)
        _dans(d, "t" + cle, line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", face, 0.6))
    d.raw(line(f"M{x0},{yt} L{x1},{yt}", "#FFFFFF", 0.5).replace("/>", ' opacity="0.45"/>'))     # arête au soleil
    for p in (P / 2,):                                                 # les deux portes
        a, b = _p(x1, yb - 1.5, p), _p(x1, yt + 1.5, p)
        d.raw(line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", fer, 0.9))
    for p in (P * 0.2, P * 0.36, P * 0.64, P * 0.8):                   # leurs barres, et les poignées
        a, b = _p(x1, yb - 2.5, p), _p(x1, yt + 2.5, p)
        d.raw(line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", clair, 0.7))
        m = _p(x1, yb - H * 0.42, p)
        d.raw(line(f"M{m[0] - 0.9:.2f},{m[1] + 0.65:.2f} L{m[0] + 0.9:.2f},{m[1] - 0.65:.2f}", fer, 1.3))
    return x1


def conteneur(couleur="orange"):
    w, h, px, py = 100, 50, 50, 44
    d = Drawing(w, h)
    x1 = _conteneur(d, "a", 4, py, couleur)
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), _sol_boite(4, x1, py, CONT[2]))


def conteneurs_empiles():
    """Deux conteneurs l'un sur l'autre (orange dessous, bleu dessus)."""
    w, h, px, py = 100, 80, 50, 74
    d = Drawing(w, h)
    x1 = _conteneur(d, "a", 4, py, "orange")
    _conteneur(d, "b", 4, py - CONT[1], "bleu")
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), _sol_boite(4, x1, py, CONT[2]))


def caisse(croix=True):
    """Caisse de bois : un cadre de planches, une écharpe en croix (ou des planches et deux flèches « haut »)."""
    w, h, px, py = 32, 32, 16, 28
    x0, x1, H, P = 5, 23, 16, 10
    bois, sombre, clair, trait = "#D9A566", "#A87643", "#EFC98E", "#9A6B3C"
    d = Drawing(w, h)
    yt = _boite(d, "a", x0, x1, py, H, P, bois, sombre, clair)
    if croix:
        _dans(d, "fa", line(f"M{x0 + 1},{yt + 1} L{x1 - 1},{py - 1} M{x1 - 1},{yt + 1} L{x0 + 1},{py - 1}", "#C08B50", 2.6))
        _dans(d, "fa", line(f"M{x0 + 2.4},{yt + 1} L{x1 - 1},{py - 2.4} M{x1 - 2.4},{yt + 1} L{x0 + 1},{py - 2.4}", trait, 0.5))
    else:
        for y in (yt + 5.4, yt + 10.6):
            d.raw(line(f"M{x0 + 2.4},{y} L{x1 - 2.4},{y}", trait, 0.6))
        for x in (x0 + 6.2, x0 + 11.8):                                # « haut » : deux flèches au pochoir
            d.raw(line(f"M{x},{yt + 11.6} L{x},{yt + 5.2} M{x - 1.7},{yt + 7} L{x},{yt + 5} L{x + 1.7},{yt + 7}", "#8A5A33", 0.9))
    for forme in (rect(x0, yt, x1 - x0, 2.4), rect(x0, py - 2.4, x1 - x0, 2.4), rect(x0, yt, 2.4, H), rect(x1 - 2.4, yt, 2.4, H)):
        d.add(forme, "#E6B878", sil=False)                             # le cadre
    d.raw(line(f"M{x0 + 2.4},{yt + 2.4} L{x1 - 2.4},{yt + 2.4} L{x1 - 2.4},{py - 2.4} L{x0 + 2.4},{py - 2.4} Z", trait, 0.5))
    for x in (x0 + 1.2, x1 - 1.2):                                     # clous
        for y in (yt + 1.2, py - 1.2):
            d.add(circle(x, y, 0.45), "#7A5230", sil=False)
    for k in (1, 2):                                                   # planches du dessus et du flanc
        a, b = _p(x0, yt, P * k / 3), _p(x1, yt, P * k / 3)
        d.raw(line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#D2A268", 0.55))
        y = yt + H * k / 3
        a, b = _p(x1, y, 0), _p(x1, y, P)
        d.raw(line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#8E6236", 0.55))
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), _sol_boite(x0, x1, py, P))


def palettes():
    """Deux palettes empilées : planches du dessus, dés, et le jour entre eux."""
    w, h, px, py = 32, 24, 16, 20
    x0, x1, H, P = 3, 23, 4.6, 12
    bois, sombre, clair = "#D2A56C", "#9C7040", "#E9C690"
    d = Drawing(w, h)
    for i, cle in enumerate("ab"):
        yb = py - i * H
        yt = _boite(d, cle, x0, x1, yb, H, P, "#5E4126", "#4A321D", clair)        # le jour, sombre
        d.add(rect(x0, yt, x1 - x0, 1.5), bois, sil=False)                         # planche du dessus, de chant
        d.add(rect(x0, yb - 1.1, x1 - x0, 1.1), _fonce(bois, 0.9), sil=False)      # semelle
        for x in (x0, (x0 + x1) / 2 - 1.6, x1 - 3.2):                              # trois dés
            d.add(rect(x, yt + 1.5, 3.2, H - 2.6), _fonce(bois, 0.84), sil=False)
        for p in (0, P - 2.6):                                                    # deux dés du flanc
            d.add(_pts([_p(x1, yb - 1.1, p), _p(x1, yb - 1.1, p + 2.6), _p(x1, yt + 1.5, p + 2.6), _p(x1, yt + 1.5, p)]), sombre, sil=False)
        d.add(_pts([_p(x1, yt), _p(x1, yt, P), _p(x1, yt + 1.5, P), _p(x1, yt + 1.5)]), sombre, sil=False)
    yt = py - 2 * H
    for k in range(1, 5):                                                         # planches du dessus
        a, b = _p(x0, yt, P * k / 5), _p(x1, yt, P * k / 5)
        d.raw(line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#B98B55", 0.6))
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), _sol_boite(x0, x1, py, P))


TONNEAUX = {"bleu": ("#3273D4", "#23579F", "#74A3EC"), "rouge": ("#D9382F", "#A82520", "#F0786E")}


def tonneau(couleur="bleu"):
    """Fût de tôle : éclairé à gauche, deux cercles, le couvercle et sa bonde."""
    base, sombre, clair = TONNEAUX[couleur]
    w, h, px, py = 24, 28, 12, 25
    rx, ry, yt, yb = 8, 2.9, 7.5, 22
    d = Drawing(w, h)
    corps = f"M{px - rx},{yt} L{px - rx},{yb} A{rx},{ry} 0 0 0 {px + rx},{yb} L{px + rx},{yt} Z"
    d.clip("fut", [path(corps)])
    d.add(path(corps), base)
    d.add(rect(px + rx * 0.3, yt, rx, yb - yt + 4), sombre, sil=False, clip="fut")
    d.add(rect(px - rx * 0.78, yt, rx * 0.3, yb - yt + 4), clair, sil=False, clip="fut", opacity=0.85)
    for y in (yt + 5, yb - 4.4):                                       # les cercles
        _dans(d, "fut", line(f"M{px - rx},{y} A{rx},{ry} 0 0 0 {px + rx},{y}", _fonce(sombre, 0.82), 1.3)
              + line(f"M{px - rx},{y - 0.9} A{rx},{ry} 0 0 0 {px + rx},{y - 0.9}", clair, 0.4))
    d.add(ellipse(px, yt, rx, ry), clair)
    d.add(ellipse(px, yt + 0.25, rx - 1.5, ry - 0.75), base, sil=False)
    d.add(ellipse(px + 3, yt + 0.2, 1.1, 0.6), sombre, sil=False)
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), "contour")


# ====================================================================== LA FERME
def foin():
    """Botte de paille carrée, liée de deux ficelles rouges ; des brins dépassent."""
    w, h, px, py = 32, 32, 16, 28
    x0, x1, H, P = 3, 23, 13, 12
    face, sombre, clair = "#EEC660", "#C99A3C", "#F8DD8A"
    d = Drawing(w, h)
    for x, y, dx, dy in ((x0, py - 9, -1.6, -1.1), (x0, py - 4, -1.8, 0.5), (x1 + 6, py - 12, 1.7, -1.0), (x0 + 9, py - H - 4.3, -0.6, -1.8),
                         (x1 + 2, py - H - 4.3, 0.9, -1.7)):           # brins qui dépassent
        d.raw(line(f"M{x},{y} l{dx},{dy}", "#D9AE4A", 0.8))
    yt = _boite(d, "a", x0, x1, py, H, P, face, sombre, clair)
    for i in range(22):                                                # brins de la face
        x = x0 + 1.2 + (i * 7.3) % (x1 - x0 - 5)
        y = yt + 1.6 + (i * 4.7) % (H - 3)
        _dans(d, "fa", line(f"M{x:.1f},{y:.1f} l{2.6 + i % 3},{(i % 2) * 0.5 - 0.25}", ("#D4A944", "#FBE9A8")[i % 3 == 0], 0.6))
    for i in range(9):                                                 # ceux du dessus, qui fuient
        a = _p(x0 + 1.5 + (i * 5.3) % (x1 - x0 - 3), yt, 1.5 + (i * 3.7) % (P - 4))
        _dans(d, "ta", line(f"M{a[0]:.2f},{a[1]:.2f} l1.6,-1.1", "#E2B955", 0.6))
    for i in range(6):                                                 # et du flanc
        a = _p(x1, yt + 2 + i * 2, 1 + (i * 4.1) % (P - 3))
        _dans(d, "ca", line(f"M{a[0]:.2f},{a[1]:.2f} l1.4,-1.0", "#B0832F", 0.6))
    for x in (x0 + 5.5, x1 - 5.5):                                     # les ficelles : sur la face, puis sur le dessus
        b = _p(x, yt, P)
        d.raw(line(f"M{x},{py} L{x},{yt} L{b[0]:.2f},{b[1]:.2f}", "#D0483A", 1.0))
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), _sol_boite(x0, x1, py, P))


def foin_rond():
    """Balle de foin ronde, couchée : le rouleau éclairé d'en haut, le bout en spirale à droite, dans l'ombre."""
    w, h, px, py = 32, 32, 16, 28
    x0, x1, r, e = 3.5, 22.5, 9.2, 4.6
    cy = py - r
    d = Drawing(w, h)
    corps = (f"M{x0 + e},{cy - r} L{x1},{cy - r} A{e},{r} 0 0 1 {x1},{cy + r} L{x0 + e},{cy + r} "
             f"A{e},{r} 0 0 1 {x0 + e},{cy - r} Z")
    d.clip("balle", [path(corps)])
    d.add(path(corps), "#EDC45C")
    d.add(rect(0, cy - r, w, r * 0.62), "#F8DD8A", sil=False, clip="balle")              # le haut au soleil
    d.add(rect(0, cy + r * 0.45, w, r), "#D2A440", sil=False, clip="balle")              # le bas à l'ombre
    for i in range(16):                                                # brins couchés, le long du rouleau
        x = x0 + 1 + (i * 6.1) % (x1 - x0 - 5)
        y = cy - r + 1.5 + (i * 4.3) % (2 * r - 3)
        _dans(d, "balle", line(f"M{x:.1f},{y:.1f} l{3 + i % 3},0", ("#C9983A", "#FBEBB0")[i % 4 == 0], 0.55))
    for x in (x0 + 6.5, x0 + 13.5):                                    # le filet qui la tient
        _dans(d, "balle", line(f"M{x},{cy - r} A{e},{r} 0 0 1 {x},{cy + r}", "#D0483A", 0.9))
    d.add(ellipse(x1, cy, e, r), "#C0902F")                           # le bout
    for k in (0.72, 0.44, 0.18):
        d.raw(line(f"M{x1 - e * k:.2f},{cy} A{e * k:.2f},{r * k:.2f} 0 1 1 {x1 + e * k:.2f},{cy} "
                   f"A{e * k:.2f},{r * k:.2f} 0 0 1 {x1 - e * k * 0.6:.2f},{cy + r * k * 0.5:.2f}", "#9A6F22", 0.6))
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), "contour")


def _pomme(d, x, y, r=2.8, couleur="#E2463F"):
    d.add(circle(x, y, r), couleur, edge=True)
    d.add(circle(x - r * 0.35, y - r * 0.38, r * 0.3), "#FFFFFF", sil=False, opacity=0.7)


def cagette():
    """Cagette de pommes : des lattes, et un tas de pommes rouges."""
    w, h, px, py = 32, 32, 16, 28
    x0, x1, H, P = 4, 24, 9, 12
    bois, sombre, clair = "#D9A566", "#A87643", "#EFC98E"
    d = Drawing(w, h)
    yt = _boite(d, "a", x0, x1, py, H, P, bois, sombre, "#7A4E2A")
    d.raw(line(f"M{x0},{yt + H / 2} L{x1},{yt + H / 2}", "#6E4526", 1.1))               # le jour entre deux lattes
    a, b = _p(x1, yt + H / 2, 0), _p(x1, yt + H / 2, P)
    d.raw(line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#6E4526", 1.0))
    for x in (x0, x1 - 2.2):
        d.add(rect(x, yt, 2.2, H), clair, sil=False)
    for x, y in ((11, yt - 4.6), (16.2, yt - 4.9), (21.4, yt - 4.6), (26.2, yt - 4.2)):                 # rang du fond
        _pomme(d, x, y, 2.7, "#D23C36")
    for x, y in ((13.6, yt - 7.2), (19, yt - 7.6), (23.6, yt - 6.8)):                                    # le tas
        _pomme(d, x, y, 2.8)
    for x, y in ((7.4, yt - 1.9), (12.6, yt - 2.4), (17.8, yt - 2.2), (22.8, yt - 1.9)):               # rang de devant
        _pomme(d, x, y, 2.8)
    d.raw(line(f"M19,{yt - 10.3} q0.6,-1.6 1.9,-1.9", "#6E4526", 0.7))                  # une queue, une feuille
    d.add(path(f"M20.6,{yt - 12.1} q2.4,-1.5 3.8,0.2 q-2.2,1.3 -3.8,-0.2 Z"), "#5CB84A", sil=False)
    d.add(rect(x0, yt, x1 - x0, 2.1), clair, sil=False)                                 # le bord de devant, par-dessus
    d.raw(line(f"M{x0},{yt + 2.1} L{x1},{yt + 2.1}", "#9A6B3C", 0.5))
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), _sol_boite(x0, x1, py, P))


# ====================================================================== LE VILLAGE
FER = ("#3F6A5C", "#2C4F44")     # fonte verte du mobilier de rue : au soleil, à l'ombre


def banc():
    """Banc public, tourné vers nous : assise et dossier de lattes, flasques de fonte verte aux deux bouts."""
    w, h, px, py = 48, 32, 24, 28
    x0, x1, P, hs = 4, 39.5, 9, 8                          # l'assise : de x0 à x1, profonde de P, à hs du sol
    bois, sombre, clair = "#D9A566", "#B07A45", "#EFC98E"
    d = Drawing(w, h)

    def flasque(x, teinte):                                # le montant d'un bout, dans le plan qui fuit
        for p0, p1, h0, h1 in ((0, 1.7, 0, 13.4), (P - 1.7, P, 0, 19), (0, P, 6.2, 8), (0, P, 12, 13.4)):
            d.add(_pts([_p(x, py - h0, p0), _p(x, py - h0, p1), _p(x, py - h1, p1), _p(x, py - h1, p0)]), teinte)

    flasque(x0, FER[1])
    for h0, h1 in ((10.4, 13.8), (14.8, 18.4)):            # les deux lattes du dossier
        a = _p(x0, py - h1, P)
        d.add(rect(a[0], a[1], x1 - x0, h1 - h0, 0.8), bois)
        d.add(rect(a[0], a[1], x1 - x0, 1.1, 0.5), clair, sil=False)
    ys = py - hs
    d.add(_pts([(x0, ys), (x1, ys), _p(x1, ys, P), _p(x0, ys, P)]), clair)             # l'assise
    for k in (1, 2):
        a, b = _p(x0, ys, P * k / 3), _p(x1, ys, P * k / 3)
        d.raw(line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#C9995C", 0.6))
    d.add(rect(x0, ys, x1 - x0, 2), sombre)                                             # son chant
    flasque(x1, FER[0])
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), "pied")


def boite_aux_lettres():
    """Boîte aux lettres jaune sur son poteau : la fente, une étiquette, le flanc dans l'ombre."""
    w, h, px, py = 24, 32, 12, 29
    x0, x1, yb, H, P = 6, 16, 19, 10, 6
    d = Drawing(w, h)
    d.add(rect(px - 1.2, yb - 1, 2.4, py - yb + 1, 0.8), "#6A6F7A")
    d.add(rect(px + 0.2, yb, 1, py - yb, 0), "#4E535D", sil=False)
    yt = _boite(d, "a", x0, x1, yb, H, P, "#F4C542", "#C99A2B", "#FBE08A")
    d.add(rect(x0 + 1.6, yt + 2.2, x1 - x0 - 3.2, 1.5, 0.6), "#5A3E12", sil=False)     # la fente
    d.add(rect(x0 + 2.4, yt + 5.2, x1 - x0 - 4.8, 3, 0.4), "#FFF8E2", sil=False)       # l'étiquette
    d.raw(line(f"M{x0 + 3.2},{yt + 6.2} L{x1 - 3.2},{yt + 6.2} M{x0 + 3.2},{yt + 7.3} L{x1 - 4.4},{yt + 7.3}", "#B58A2A", 0.5))
    d.raw(line(f"M{x0},{yt} L{x1},{yt}", "#FFFFFF", 0.5).replace("/>", ' opacity="0.5"/>'))
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), "pied")


def _fleur(d, x, y, r, couleur, coeur="#F6C945"):
    for k in range(5):
        a = k * 2 * math.pi / 5 - math.pi / 2
        d.add(circle(x + r * 0.62 * math.cos(a), y + r * 0.62 * math.sin(a), r * 0.52), couleur)
    d.add(circle(x, y, r * 0.38), coeur, sil=False)


POTS = {"mele": ("#F28CB8", "#F7D154", "#FFFFFF"), "geranium": ("#E24B4B", "#F0605A", "#F28CB8"),
        "bleu": ("#8FB8F2", "#FFFFFF", "#C7A6F0")}


def pot_de_fleurs(genre="mele"):
    """Pot de terre cuite, éclairé à gauche, et son bouquet : feuilles, tiges, cinq fleurs."""
    c1, c2, c3 = POTS[genre]
    w, h, px, py = 24, 32, 12, 28
    d = Drawing(w, h)
    for x0, y0, cx, cy, x1, y1 in ((12, 19, 6, 17, 4.6, 12.5), (12, 19, 18, 17, 19.6, 12.8), (12, 19, 9, 13, 8, 9.4), (12, 19, 15.4, 13, 16.6, 10)):
        d.add(path(f"M{x0},{y0} Q{cx},{cy} {x1},{y1} Q{cx + (1.6 if x1 < 12 else -1.6)},{cy - 2.6} {x0},{y0} Z"), "#4FA04A")   # feuilles
    d.raw(line("M12,19 Q11.4,13 12,8.6 M12,19 Q9.4,15 7.4,13.4 M12,19 Q14.6,15 16.8,13.6", "#3B8240", 0.8))
    corps = "M6.4,20.4 L7.8,26.6 A4.2,1.5 0 0 0 16.2,26.6 L17.6,20.4 Z"
    d.clip("pot", [path(corps)])
    d.add(path(corps), "#C8603F")
    d.add(rect(13.2, 19, 6, 10), "#A04A30", sil=False, clip="pot")
    d.add(rect(7.4, 19, 1.9, 10), "#E58E6E", sil=False, clip="pot")
    d.add(rect(5.4, 18.4, 13.2, 2.8, 1.3), "#D97452")                                  # le rebord
    d.add(rect(13.4, 18.4, 5.2, 2.8, 1.3), "#B5583A", sil=False)
    d.raw(line("M6.2,21.2 L17.8,21.2", "#8E3F28", 0.5))
    for x, y, r, c in ((7.2, 12.6, 2.5, c2), (16.8, 12.8, 2.5, c3), (9.2, 8.8, 2.5, c1), (15, 9.2, 2.4, c2), (12, 6.6, 2.8, c1 if genre != "bleu" else c2),
                       (12, 12.2, 2.6, c3 if genre != "geranium" else c1)):
        _fleur(d, x, y, r, c, "#F6C945" if c != "#F7D154" else "#E8932E")
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), "contour")


def table_de_terrasse():
    """Table ronde de café sous son parasol rayé, vu d'un peu au-dessus (les fuseaux de droite dans l'ombre), une
    tasse et un verre, deux chaises de bistrot."""
    w, h, px, py = 48, 64, 24, 58
    rouge, blanc = "#D8362E", "#FFF8EC"
    d = Drawing(w, h)
    # chaises : pieds et dossier de fer, assise ronde
    for cx, sens in ((8.5, -1), (39.5, 1)):
        d.raw(line(f"M{cx - 3},{py - 8} L{cx - 3.6},{py - 0.6} M{cx + 3},{py - 8} L{cx + 3.6},{py - 0.6} "
                   f"M{cx + sens * 3.4},{py - 9} L{cx + sens * 3.9},{py - 19} "
                   f"Q{cx + sens * 2},{py - 21.4} {cx + sens * 0.2},{py - 19.4} L{cx + sens * 0.6},{py - 9.6}", "#3A3F4A", 1.3))
        d.add(ellipse(cx, py - 9, 4.6, 1.9), "#C8553D")
        d.add(ellipse(cx - 0.8, py - 9.5, 2.6, 0.9), "#E07A62", sil=False)
    # table : pied, plateau
    d.add(ellipse(px, py - 1.2, 5.2, 1.7), "#4A4F5A")
    d.add(rect(px - 1.1, py - 13, 2.2, 12, 0.6), "#6A6F7A")
    ty = py - 14
    d.add(ellipse(px, ty + 1.6, 10.5, 3.7), "#CDBFA6")
    d.add(ellipse(px, ty, 10.5, 3.7), "#FBF4E6")
    d.add(path(f"M{px + 2},{ty - 3.6} A10.5,3.7 0 0 1 {px + 2},{ty + 3.6} Q{px + 6},{ty} {px + 2},{ty - 3.6} Z"), "#E9DEC8", sil=False)
    d.add(rect(px - 6.4, ty - 2.6, 3, 2.4, 0.6), "#FFFFFF", sil=False, edge=True)      # la tasse
    d.add(ellipse(px - 4.9, ty - 2.5, 1.2, 0.5), "#7A4E2A", sil=False)
    d.add(rect(px + 3.2, ty - 3.6, 2.2, 3.6, 0.5), "#F2A83B", sil=False, edge=True)    # le verre
    # mât et parasol
    d.add(rect(px - 0.9, 18, 1.8, ty - 19, 0), "#B9BCC4")
    cy, rx, ry, top = 21, 21, 6.4, 5
    rim = lambda t: (px + rx * math.cos(math.radians(t)), cy + ry * math.sin(math.radians(t)))
    n = 6
    for i in range(n):
        (ax, ay), (bx, by) = rim(180 - i * 180 / n), rim(180 - (i + 1) * 180 / n)
        mx, my = rim(180 - (i + 0.5) * 180 / n)
        fuseau = (f"M{px},{top} Q{(px + ax) / 2 - (px - ax) * 0.08:.2f},{(top + ay) / 2 - 3.4:.2f} {ax:.2f},{ay:.2f} "
                  f"Q{mx:.2f},{my + 3.2:.2f} {bx:.2f},{by:.2f} "
                  f"Q{(px + bx) / 2 - (px - bx) * 0.08:.2f},{(top + by) / 2 - 3.4:.2f} {px},{top} Z")
        teinte = (rouge, blanc)[i % 2]
        d.add(path(fuseau), teinte if i < n / 2 else _fonce(teinte, 0.84))
        if i:
            d.raw(line(f"M{px},{top} Q{(px + ax) / 2 - (px - ax) * 0.08:.2f},{(top + ay) / 2 - 3.4:.2f} {ax:.2f},{ay:.2f}", "#8E2A22", 0.5))
    d.add(circle(px, top - 0.6, 1.5), "#F2C14E")
    return Sprite([(d, OUTLINE, TRAIT)], w, h, (px, py), "pied")


def haie():
    """Un tronçon de haie taillée : la face au soleil, le dessus plus clair, le flanc droit à l'ombre ; des feuilles
    festonnent les arêtes. Contour vert, comme la nature."""
    ombre, base, clair, contour = FEUILLAGES["buisson"]
    w, h, px, py = 38, 32, 3, 27
    x0, x1, H, P = 4, 30, 15, 10
    d = Drawing(w, h)
    yt = py - H
    for i in range(9):                                     # festons : le haut du fond, le flanc, le bas
        a = _p(x0 + 1.5 + i * 3.1, yt, P)
        d.add(circle(a[0], a[1] + 0.4, 1.9), clair)
    for i in range(5):
        a = _p(x1, yt + 2 + i * 3, P)
        d.add(circle(a[0] - 0.4, a[1], 1.8), ombre)
    for i in range(8):
        d.add(circle(x0 + 1.8 + i * 3.4, py - 1.5, 1.9), base if i % 3 else ombre)
    _boite(d, "a", x0, x1, py - 0.6, H - 0.6, P, base, ombre, clair)
    for i in range(8):                                     # festons de l'arête de devant
        d.add(circle(x0 + 1.6 + i * 3.3, yt + 0.5, 1.9), clair, sil=False)
    d.add(rect(x0, py - 5, x1 - x0, 5), ombre, sil=False, clip="fa", opacity=0.45)     # le bas dans l'ombre
    for i in range(12):                                    # feuilles de la face
        x, y = x0 + 2 + (i * 7.9) % (x1 - x0 - 5), yt + 4 + (i * 5.3) % (H - 8)
        d.raw(line(f"M{x:.1f},{y + 0.8:.1f} q1.2,-1.8 2.8,-1.1", (ombre, clair)[i % 3 == 0], 0.8))
    for i in range(5):                                     # et du dessus
        a = _p(x0 + 3 + i * 5.2, yt, 3 + (i * 3.1) % 5)
        _dans(d, "ta", line(f"M{a[0]:.2f},{a[1]:.2f} q1.2,-1.4 2.6,-0.8", base, 0.7))
    return Sprite([(d, contour, nature.TRAIT)], w, h, (px, py), _sol_boite(x0, x1, py, P))


# ====================================================================== LA FORÊT
ECORCE = ("#9C6B43", "#7B4F2F", "#B88558", "#6E4528")    # écorce : base, ombre, lumière, fentes
AUBIER = ("#EBCB9B", "#C99A62")                           # le bois coupé, ses cernes
MOUSSE = ("#6DB758", "#93D271")


def _cernes(cx, cy, rx, ry):
    return "".join(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * k:.2f}" ry="{ry * k:.2f}" fill="none" stroke="{AUBIER[1]}" stroke-width="0.7"/>'
                   for k in (0.7, 0.36))


def _amanite(d, x, pied, r, haut, pois, chapeau=("#D9382F", "#B02A24", "#EF6F62"), cle="a"):
    """Champignon : pied crème (le côté droit à l'ombre), chapeau en dôme éclairé à gauche ; `pois` : ses points
    blancs (dx, dy, rayon, en fractions de r), aucun pour un bolet."""
    base, sombre, clair = chapeau
    lp = r * 0.6
    d.add(rect(x - lp / 2, pied - haut, lp, haut, lp * 0.4), "#F6EDDA")
    d.add(rect(x + lp * 0.08, pied - haut, lp * 0.42, haut - 0.4, lp * 0.3), "#D9CBB0", sil=False)
    cy, k = pied - haut + 0.6, 1.25 * r
    dome = (f"M{x - r:.2f},{cy:.2f} C{x - r:.2f},{cy - k:.2f} {x + r:.2f},{cy - k:.2f} {x + r:.2f},{cy:.2f} "
            f"Q{x:.2f},{cy + 1.5:.2f} {x - r:.2f},{cy:.2f} Z")
    d.clip("ch" + cle, [path(dome)])
    d.add(path(dome), base)
    d.add(circle(x + r * 0.55, cy - r * 0.1, r * 0.75), sombre, sil=False, clip="ch" + cle, opacity=0.8)
    d.add(ellipse(x - r * 0.38, cy - r * 0.56, r * 0.3, r * 0.17), clair, sil=False, clip="ch" + cle)
    for dx, dy, rr in pois:
        d.add(circle(x + dx * r, cy + dy * r, max(0.65, rr * r)), "#FFFFFF", sil=False, clip="ch" + cle)


def champignons(bolets=False):
    """Trois champignons : des amanites rouges à pois blancs, ou des bolets bruns."""
    w, h, px, py = 32, 32, 16, 28
    d = Drawing(w, h)
    if bolets:
        brun = ("#B8713F", "#8C5129", "#DB9A62")
        _amanite(d, 20.5, 27, 5.6, 6.5, (), brun, "a")
        _amanite(d, 10.5, 27.4, 6.8, 8.6, (), brun, "b")
        _amanite(d, 26.4, 27.8, 3.2, 3.6, (), brun, "c")
    else:
        _amanite(d, 23, 27.2, 5, 6, ((-0.4, -0.4, 0.17), (0.3, -0.62, 0.15)), cle="a")
        _amanite(d, 13, 26.6, 7.2, 9.2, ((-0.45, -0.35, 0.17), (0.15, -0.68, 0.15), (0.5, -0.28, 0.13), (-0.05, -0.2, 0.1)), cle="b")
        _amanite(d, 6.6, 27.8, 3.6, 4, ((-0.1, -0.55, 0.2),), cle="c")
    return Sprite([(d, BOIS, nature.TRAIT)], w, h, (px, py), "contour")


def souche():
    """Souche : la coupe et ses cernes, l'écorce éclairée à gauche, des racines, de la mousse, un petit champignon."""
    base, ombre, clair, fente = ECORCE
    w, h, px, py = 32, 32, 16, 27
    d = Drawing(w, h)
    corps = ("M8.4,14.5 L8.4,21.5 Q7.6,25.2 3.8,26.6 Q7.6,27.6 10.6,26.2 Q13,27.8 16,27.4 Q19,27.8 21.6,26.2 "
             "Q24.6,27.6 28.2,26.6 Q24.6,25.2 23.6,21.5 L23.6,14.5 Z")
    d.clip("souche", [path(corps)])
    d.add(path(corps), base)
    d.add(path("M17.6,13 L24,13 L24,22 Q25,25.4 29,27.4 L19.4,28 Q18.6,21 17.6,13 Z"), ombre, sil=False, clip="souche")
    d.add(path("M8,13 L10.6,13 Q10.2,21 9.6,25.8 L3,27.6 Q7.6,25 8,21 Z"), clair, sil=False, clip="souche", opacity=0.85)
    d.raw(line("M12.4,18.4 L12.2,24.6 M15.6,19.6 L15.8,26 M20.4,18.2 L20.8,23.8", fente, 0.8))
    d.add(ellipse(16, 14.5, 7.6, 3.4), AUBIER[0])
    d.raw(_cernes(16, 14.5, 7.6, 3.4))
    d.raw(line("M19.6,13.2 L21.6,15", fente, 0.6))
    for cx, cy, r in ((8.6, 15.6, 1.8), (10.4, 12.9, 2.0), (13.2, 11.6, 1.5)):          # mousse sur le rebord
        d.add(circle(cx, cy, r), MOUSSE[0])
    d.add(circle(10, 12.3, 0.8), MOUSSE[1], sil=False)
    _amanite(d, 26, 27.4, 2.6, 3, (), ("#B8713F", "#8C5129", "#DB9A62"), "s")
    return Sprite([(d, BOIS, nature.TRAIT)], w, h, (px, py), "contour")


def tronc_couche():
    """Tronc couché : le bout coupé à gauche, l'écorce éclairée d'en haut, un chicot de branche, de la mousse et
    un champignon posés dessus."""
    base, ombre, clair, fente = ECORCE
    w, h, px, py = 64, 32, 32, 27
    d = Drawing(w, h)
    d.add(_pts([(45.6, 11.5), (48.8, 11.5), (51.6, 5.6), (49, 4.6)]), base)             # le chicot
    d.add(ellipse(50.3, 5.1, 1.5, 0.9, tr="rotate(25 50.3 5.1)"), AUBIER[0], sil=False)
    corps = "M10,10 L53,10 Q60,10 60,18.5 Q60,27 53,27 L10,27 Z"
    d.clip("tronc", [path(corps)])
    d.add(path(corps), base)
    d.add(rect(8, 10, 54, 4.4), clair, sil=False, clip="tronc")
    d.add(rect(8, 21.4, 54, 6), ombre, sil=False, clip="tronc")
    d.raw(line("M18,17.6 Q24,16.6 30,18 M36,19.6 Q43,18.4 50,19.8 M22,24.4 L30,24.4 M41,15.6 Q46,14.8 52,16.2", fente, 0.8))
    d.raw(line("M55.4,12.8 Q58.6,18.5 55.4,24.4", fente, 0.7))
    d.add(ellipse(10, 18.5, 5.8, 8.5), AUBIER[0])
    d.raw(_cernes(10, 18.5, 5.8, 8.5))
    d.add(path("M19.6,10.8 Q20.6,7.2 24.2,7.6 Q26.8,6.2 29.4,8.2 Q32,8 32.8,10.8 Z"), MOUSSE[0])
    d.add(ellipse(25, 8.8, 1.7, 0.8), MOUSSE[1], sil=False)
    _amanite(d, 38.6, 10.6, 4.2, 4.6, ((-0.45, -0.35, 0.17), (0.15, -0.68, 0.15), (0.5, -0.28, 0.13)), cle="t")
    return Sprite([(d, BOIS, nature.TRAIT)], w, h, (px, py), "contour")


def _fronde(pied, ctrl, pointe, larg, n):
    """Fronde de fougère : une bande effilée le long d'une courbe, aux bords découpés en folioles ; rend la forme
    et le tracé de sa nervure."""
    (bx, by), (cx, cy), (tx, ty) = pied, ctrl, pointe
    gauche, droite = [], []
    N = 44
    for i in range(N + 1):
        t = i / N
        x = (1 - t) ** 2 * bx + 2 * (1 - t) * t * cx + t * t * tx
        y = (1 - t) ** 2 * by + 2 * (1 - t) * t * cy + t * t * ty
        dx = 2 * (1 - t) * (cx - bx) + 2 * t * (tx - cx)
        dy = 2 * (1 - t) * (cy - by) + 2 * t * (ty - cy)
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        e = larg * math.sin(math.pi * (0.12 + 0.88 * t)) * (0.62 + 0.38 * abs(math.sin(n * math.pi * t)))
        if t < 0.08:
            e *= 0.45
        gauche.append((x + nx * e, y + ny * e))
        droite.append((x - nx * e, y - ny * e))
    return _pts(gauche + droite[::-1]), f"M{bx},{by} Q{cx},{cy} {tx},{ty}"


def fougere(grande=False):
    """Touffe de fougère : des frondes arquées, celles du fond et de droite dans l'ombre, une nervure claire ; la
    grande a deux crosses qui se déroulent."""
    ombre, base, clair, contour = FEUILLAGES["jeune"] if grande else FEUILLAGES["buisson"]
    w, h, px, py = 36, 34, 18, 30
    B = (18, 29.5)
    k = 1.0 if grande else 0.86
    P = lambda x, y: (18 + (x - 18) * k, 29.5 + (y - 29.5) * k)
    d = Drawing(w, h)
    fond = [((7, 16), (2.6, 24), 2.7), ((29, 16), (33.4, 24), 2.7), ((19, 12), (21.6, 2.6), 2.8)]
    devant = [((9, 8.5), (3.6, 9.6), 3.1), ((27, 8.5), (32.4, 9.6), 3.1), ((14, 19), (7, 21.6), 2.5), ((22, 19), (29, 21.6), 2.5)]
    for c, p, e in fond:
        f, nervure = _fronde(B, P(*c), P(*p), e * k, 7)
        d.add(f, ombre)
        d.raw(line(nervure, base, 0.7))
    for i, (c, p, e) in enumerate(devant):
        f, nervure = _fronde(B, P(*c), P(*p), e * k, 7 if i < 2 else 5)
        d.add(f, ombre if i % 2 else base)                # celles de droite, à l'ombre
        d.raw(line(nervure, base if i % 2 else clair, 0.8))
    if grande:
        for x, s in ((14.6, -1), (21.4, 1)):              # crosses
            d.raw(line(f"M18,29 Q{x},22 {x + s * 0.4},16.4 q{s * 0.4},-2.6 {-s * 1.6},-2.4 q{-s * 1.5},0.6 {-s * 0.6},1.9", contour, 1.9))
            d.raw(line(f"M18,29 Q{x},22 {x + s * 0.4},16.4 q{s * 0.4},-2.6 {-s * 1.6},-2.4 q{-s * 1.5},0.6 {-s * 0.6},1.9", clair, 0.9))
    d.add(ellipse(18, 29, 3, 1.4), ombre)
    return Sprite([(d, contour, nature.TRAIT)], w, h, (px, py), "contour")


CATALOGUE = {
    "conteneur": conteneur, "conteneur_bleu": lambda: conteneur("bleu"), "conteneur_vert": lambda: conteneur("vert"),
    "conteneurs_empiles": conteneurs_empiles,
    "caisse": caisse, "caisse_fleches": lambda: caisse(False), "palettes": palettes,
    "tonneau_bleu": tonneau, "tonneau_rouge": lambda: tonneau("rouge"),
    "foin": foin, "foin_rond": foin_rond, "cagette": cagette,
    "banc": banc, "boite_aux_lettres": boite_aux_lettres, "table_de_terrasse": table_de_terrasse, "haie": haie,
    "pot_de_fleurs": pot_de_fleurs, "pot_de_geraniums": lambda: pot_de_fleurs("geranium"), "pot_de_fleurs_bleues": lambda: pot_de_fleurs("bleu"),
    "souche": souche, "tronc_couche": tronc_couche, "champignons": champignons, "bolets": lambda: champignons(True),
    "fougere": fougere, "grande_fougere": lambda: fougere(True),
}
# Décor de carte.json -> ses dessins (un par position, comme la nature) ; `n` reste le nom du décor et son obstacle.
VARIANTES = {
    "container": (["conteneur"], [0]), "container_blue": (["conteneur_bleu"], [0]), "container_green": (["conteneur_vert"], [0]),
    "container_stack": (["conteneurs_empiles"], [0]),
    "crate": (["caisse", "caisse_fleches"], [0, 1]), "pallet": (["palettes"], [0]),
    "barrel_blue": (["tonneau_bleu"], [0]), "barrel_red": (["tonneau_rouge"], [0]),
    "hay": (["foin", "foin_rond"], [0, 0, 1]), "apple_crate": (["cagette"], [0]),
    "bench": (["banc"], [0]), "mailbox": (["boite_aux_lettres"], [0]), "cafe_table": (["table_de_terrasse"], [0]), "hedge": (["haie"], [0]),
    "flower_pot": (["pot_de_fleurs", "pot_de_geraniums", "pot_de_fleurs_bleues"], [0, 1, 2]),
    "stump": (["souche"], [0]), "log": (["tronc_couche"], [0]), "mushrooms": (["champignons", "bolets"], [0, 0, 1]),
    "fern": (["fougere", "grande_fougere"], [0, 1]),
}
# Où un chat se réfugie sur un conteneur : points du cadre (game.js : REFUGES, MAP.perches)
PERCHOIRS = {
    "conteneur": [(28, 9.5), (70, 9.5)], "conteneur_bleu": [(28, 9.5), (70, 9.5)], "conteneur_vert": [(28, 9.5), (70, 9.5)],
    "conteneurs_empiles": [(28, 9.5), (70, 9.5)],
}


# Taille dans le jeu. Les conteneurs sont agrandis : à côté des maisons, des véhicules et des personnages agrandis,
# Christophe les a trouvés « très petits » (12 novembre 2026). L'obstacle du décor grandit d'autant (MAP.grow).
ECH = {"conteneur": 1.5, "conteneur_bleu": 1.5, "conteneur_vert": 1.5, "conteneurs_empiles": 1.5,
       "table_de_terrasse": 1.35, "banc": 1.2,            # (un parasol plus haut qu'un villageois, un banc où s'asseoir)
       "foin": 1.3, "foin_rond": 1.3, "tonneau_bleu": 1.35, "tonneau_rouge": 1.35}


def agrandis():
    """décor de carte.json -> son agrandissement (celui de ses dessins)."""
    return {decor: ECH[noms[0]] for decor, (noms, _) in VARIANTES.items() if noms[0] in ECH}


def perchoirs(echelle=2):
    """nom -> [[dx, dy]…] : les perchoirs, en pixels du jeu à partir du pied du sprite."""
    out = {}
    for nom, pts in PERCHOIRS.items():
        px, py = CATALOGUE[nom]().pied
        k = echelle * ECH.get(nom, 1)
        out[nom] = [[round((x - px) * k), round((y - py) * k)] for x, y in pts]
    return out


for _n, _f in CATALOGUE.items():                # ils se dessinent, se mettent à l'échelle et s'ombrent comme la nature
    nature.CATALOGUE[_n] = _f
    nature.ECHELLES[_n] = ECH.get(_n, 1)
nature.VARIANTES.update(VARIANTES)


if __name__ == "__main__":
    noms = list(CATALOGUE)
    ims = [nature.image(n, 6) for n in noms]
    rangs, rang, larg = [], [], 0
    for im in ims:
        if rang and larg + im.width > 1880:
            rangs.append(rang)
            rang, larg = [], 0
        rang.append(im)
        larg += im.width
    rangs.append(rang)
    hauts = [max(i.height for i in r) for r in rangs]
    planche = Image.new("RGBA", (1900, sum(hauts) + 20), (126, 196, 100, 255))
    y = 10
    for r, H in zip(rangs, hauts):
        x = 10
        for im in r:
            planche.alpha_composite(im, (x, y + H - im.height))
            x += im.width
        y += H
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference", "v2", "mobilier_v2.png")
    planche.convert("RGB").save(fn)
    print(fn, planche.size)

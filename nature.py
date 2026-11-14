"""
Nature et niche, version 2 — le décor naturel du jeu web (PLAN_V2.md, lot 4), né de l'écran témoin (lot 1).

Ce qui change par rapport à decor.py :
- plusieurs modèles par espèce (chêne, bouleau, cerisier en fleurs, jeune arbre ; buissons ronds ou fleuris) ;
- un feuillage en touffes, chacune avec son ombre et sa lumière : le soleil vient d'en haut à gauche ;
- un contour de la teinte du décor (vert foncé pour le feuillage, brun doux pour le bois) : le brun #3A1E12 reste aux
  personnages et à ce qu'on peut toucher, qui se détachent ainsi du paysage ;
- pas d'ombre ovale dessinée dans le sprite : l'ombre portée se calcule à partir de la silhouette.

Chaque fonction rend un Sprite : des calques (dessin, couleur et épaisseur du contour), la taille du cadre, le pied
(le point posé au sol) et `sol`, la ligne où l'objet touche le sol, d'où part son ombre portée :
- "pied" : une horizontale à la hauteur du pied (arbres, roseaux, personnages : ils ne touchent le sol qu'au pied) ;
- "contour" : une horizontale au point le plus bas de la silhouette (buissons, rocher : posés au sol) ;
- une liste de points (x, y) du cadre, de gauche à droite (la niche : le bas du pignon, puis du mur qui fuit).

Dans le jeu (pack_web.py) : VARIANTES dit, pour un décor de carte.json (« tree », « bush », « fir »…), quels sprites
le remplacent ; le jeu en choisit un d'après la position du décor (hash3, comme les tuiles) : rien à changer dans la
carte. Les sprites, dessinés pour le premier témoin, sont réduits de ECH : la taille des décors qu'ils remplacent,
dont les obstacles ne bougent pas. Le jeu calcule leur ombre portée (game.js : groundShadows()) à partir de leur
silhouette et de la ligne où ils touchent le sol (bandes()).

    python3 nature.py      # reference/v2/nature_v2.png
"""
import math
import random
import os
import sys
from collections import namedtuple


from PIL import Image  # noqa: E402

from spritelib import Drawing, circle, ellipse, rect, path, poly, line, render_svg, OUTLINE, PAD  # noqa: E402

Sprite = namedtuple("Sprite", "calques w h pied sol", defaults=("pied",))
TRAIT = 1.6                      # épaisseur du contour du décor (1.8 pour les personnages)
BOIS = "#4E3220"                 # contour du bois

ECH = 0.62                       # réduction des sprites dans le jeu

FEUILLAGES = {                   # ombre, base, clair, contour
    "sapin":    ("#1F6B45", "#2F8A55", "#5DB06C", "#17432C"),
    "sapin_bleu": ("#1E6660", "#2C857A", "#59AC9C", "#143F3C"),
    "chene":    ("#37913D", "#56B345", "#93D557", "#235A2B"),
    "sombre":   ("#2A7B40", "#3F9745", "#63B34F", "#1B4A2A"),
    "bouleau":  ("#74B441", "#9BD052", "#CBE877", "#3F6C2C"),
    "jeune":    ("#2B8C5E", "#45AA74", "#83D09A", "#1D5640"),
    "cerisier": ("#E27FA8", "#F6B0CA", "#FFDDE9", "#8C4160"),
    "buisson":  ("#3A9642", "#5CB84A", "#98DA5E", "#235A2B"),
    "fond":     ("#185A3A", "#23734A", "#3F935B", "#123824"),      # le fond d'un fourré de la forêt
}


def rendre(sp, echelle):
    """Image RGBA d'un Sprite (ses calques superposés), marge PAD comprise."""
    out = None
    for d, contour, ep, *_ in sp.calques:
        im = render_svg(d.svg(outline=contour, outline_w=ep), sp.w, sp.h, echelle, PAD)
        out = im if out is None else Image.alpha_composite(out, im)
    return out


def _touffes(d, touffes, teinte, cle):
    """Feuillage, de la touffe la plus lointaine à la plus proche. Chaque touffe : un bord festonné (de petites
    bosses, pour que la silhouette soit celle d'un feuillage et non d'un ballon), un disque sombre, un disque décalé
    vers la lumière (il laisse un croissant d'ombre en bas à droite), une plage claire en haut à gauche et deux
    feuilles dessinées dedans."""
    ombre, base, clair, contour = FEUILLAGES[teinte]
    for i, (cx, cy, r) in enumerate(touffes):
        cid = f"{cle}{i}"
        n = max(6, round(r * 0.62))
        for k in range(n):                                   # bosses du bord, un peu irrégulières
            a = (k + 0.5 * math.sin(i * 1.7 + k * 2.3)) * 2 * math.pi / n + i
            rb = r * (0.24 + 0.07 * math.sin(k * 3.1 + i))
            d.add(circle(cx + (r - rb * 0.45) * math.cos(a), cy + (r - rb * 0.45) * math.sin(a), rb), ombre)
        disque = circle(cx, cy, r)
        d.clip(cid, [disque])
        d.add(disque, ombre)
        d.add(circle(cx - r * 0.16, cy - r * 0.2, r * 0.92), base, sil=False, clip=cid)
        d.add(circle(cx - r * 0.36, cy - r * 0.42, r * 0.56), clair, sil=False, clip=cid)
        for fx, fy, ang in ((0.2, 0.05, -35), (-0.15, 0.42, -20)):          # deux feuilles, dans la partie moyenne
            x, y = cx + r * fx, cy + r * fy
            d.raw(line(f"M{x - r * 0.13:.2f},{y + r * 0.05:.2f} q{r * 0.12:.2f},{-r * 0.16:.2f} {r * 0.27:.2f},{-r * 0.1:.2f}",
                       ombre, max(0.7, r * 0.07)))


def _tronc(w, h, x, bas, haut, larg, couleur=("#9C6B43", "#7B4F2F", "#B88558"), racines=True):
    """Tronc légèrement évasé au pied : face éclairée à gauche, ombre à droite, ombre du feuillage en haut."""
    base, sombre, clair = couleur
    d = Drawing(w, h)
    L, e = larg / 2, larg * (0.95 if racines else 0.3)
    corps = (f"M{x - L - e:.2f},{bas + 0.6:.2f} C{x - L - 1.5:.2f},{bas - 2:.2f} {x - L:.2f},{bas - 8:.2f} {x - L + 0.4:.2f},{bas - 18:.2f} "
             f"L{x - L + 0.8:.2f},{haut:.2f} L{x + L - 0.8:.2f},{haut:.2f} L{x + L - 0.4:.2f},{bas - 18:.2f} "
             f"C{x + L:.2f},{bas - 8:.2f} {x + L + 1.5:.2f},{bas - 2:.2f} {x + L + e:.2f},{bas + 0.6:.2f} "
             f"C{x + L * 0.6:.2f},{bas + 2.2:.2f} {x + 1:.2f},{bas + 0.8:.2f} {x:.2f},{bas + 1.8:.2f} "
             f"C{x - 1:.2f},{bas + 0.8:.2f} {x - L * 0.6:.2f},{bas + 2.2:.2f} {x - L - e:.2f},{bas + 0.6:.2f} Z")
    d.clip("tronc", [path(corps)])
    d.add(path(corps), base)
    d.add(rect(x + L * 0.15, haut, larg, bas - haut + 4), sombre, sil=False, clip="tronc")
    d.add(rect(x - L - e, haut, L * 0.55 + e, bas - haut + 4), clair, sil=False, clip="tronc", opacity=0.75)
    d.add(rect(x - larg, haut, larg * 2, 9), "#4B2E1B", sil=False, clip="tronc", opacity=0.45)      # ombre du feuillage
    return d


# ====================================================================== ARBRES
def chene(teinte="chene"):
    """Grand chêne : large feuillage en dôme, tronc trapu."""
    w, h, px, py = 100, 116, 50, 108
    tr = _tronc(w, h, px, py, 68, 12)
    tr.raw(line(f"M{px - 1.5},84 L{px - 1.2},97 M{px + 2.6},78 L{px + 2.8},88", "#6E4528", 0.9))
    f = Drawing(w, h)
    _touffes(f, [(50, 22, 17), (32, 29, 15), (69, 29, 15), (20, 45, 13.5), (80, 45, 13.5), (50, 41, 22),
                 (29, 59, 13), (71, 59, 13), (62, 53, 14), (40, 55, 14), (50, 64, 13)], teinte, "c")
    return Sprite([(tr, BOIS, TRAIT), (f, FEUILLAGES[teinte][3], TRAIT)], w, h, (px, py))


def bouleau():
    """Bouleau : tronc blanc élancé, marques sombres, feuillage clair tout en hauteur."""
    w, h, px, py = 64, 124, 32, 116
    tr = _tronc(w, h, px, py, 58, 7.5, ("#EFEADF", "#CFC8BA", "#FFFFFF"), racines=False)
    for y, x0, x1 in ((74, -3, 0.5), (84, 0, 3.2), (93, -3.2, -0.4), (103, -0.5, 3.4)):
        tr.raw(line(f"M{px + x0},{y} L{px + x1},{y + 0.6}", "#5A534A", 1.3))
    f = Drawing(w, h)
    _touffes(f, [(32, 20, 12.5), (22, 33, 11.5), (42, 33, 11.5), (32, 42, 14), (22.5, 53, 10.5), (42, 54, 10.5),
                 (32, 62, 10.5)], "bouleau", "b")
    return Sprite([(tr, "#6B6558", TRAIT), (f, FEUILLAGES["bouleau"][3], TRAIT)], w, h, (px, py))


def cerisier():
    """Cerisier en fleurs : feuillage rose, quelques touffes vertes, tronc sombre."""
    w, h, px, py = 96, 104, 48, 96
    tr = _tronc(w, h, px, py, 60, 9.5, ("#7E5238", "#5F3B27", "#9A6A4A"))
    v = Drawing(w, h)
    _touffes(v, [(30, 44, 11), (68, 46, 11)], "chene", "v")
    f = Drawing(w, h)
    _touffes(f, [(48, 22, 15.5), (30, 29, 13.5), (66, 29, 13.5), (20, 43, 11), (77, 43, 11), (48, 39, 19),
                 (33, 54, 11.5), (64, 54, 11.5), (49, 58, 11.5)], "cerisier", "r")
    for x, y in ((40, 30), (58, 35), (27, 40), (70, 41), (47, 50), (36, 20), (61, 22)):      # cœurs de fleurs
        f.add(circle(x, y, 1.15), "#FFF6C9", sil=False)
        f.add(circle(x, y, 0.5), "#E8A93A", sil=False)
    return Sprite([(tr, BOIS, TRAIT), (v, FEUILLAGES["chene"][3], TRAIT), (f, FEUILLAGES["cerisier"][3], TRAIT)],
                  w, h, (px, py))


def jeune_arbre():
    """Petit arbre rond, d'un vert plus bleu."""
    w, h, px, py = 60, 80, 30, 72
    tr = _tronc(w, h, px, py, 44, 7, racines=False)
    f = Drawing(w, h)
    _touffes(f, [(30, 16, 11.5), (19, 27, 11), (41, 27, 11), (30, 31, 14), (22, 41, 9.5), (38, 41, 9.5)], "jeune", "j")
    return Sprite([(tr, BOIS, TRAIT), (f, FEUILLAGES["jeune"][3], TRAIT)], w, h, (px, py))


def pommier(jeune=False):
    """Pommier du verger : le feuillage d'un chêne (ou d'un jeune arbre), des pommes rouges."""
    sp = jeune_arbre() if jeune else chene()
    f = sp.calques[-1][0]
    pommes = (((22, 22), (36, 30), (27, 38), (19, 30)) if jeune else
              ((34, 26), (62, 24), (22, 44), (50, 38), (76, 46), (38, 56), (64, 58), (50, 18)))
    for x, y in pommes:
        f.add(circle(x, y, 2.5), "#E2463F", sil=False, edge=True)
        f.add(circle(x - 0.8, y - 0.9, 0.75), "#FFFFFF", sil=False, opacity=0.8)
    return sp


def sapin(haut=96, large=66, etages=4, teinte="sapin"):
    """Sapin : des étages de branches au bord festonné, plus larges vers le bas, chacun éclairé à gauche et dans
    l'ombre à droite, sur un tronc court."""
    w, h = 80, haut + 22
    px, py = w / 2, h - 8
    tr = _tronc(w, h, px, py, py - 20, 7, ("#7E5238", "#5F3B27", "#9A6A4A"), racines=False)
    ombre, base, clair, contour = FEUILLAGES[teinte]
    f = Drawing(w, h)
    sommet, bas = py - haut, py - 11
    for i in range(etages - 1, -1, -1):                       # du bas (le plus large) vers le haut
        t0, t1 = i / etages, (i + 1) / etages
        y0 = sommet + (bas - sommet) * max(0.0, t0 - 0.2)     # la pointe de l'étage, cachée sous celui du dessus
        y1 = sommet + (bas - sommet) * t1
        L = large / 2 * (0.34 + 0.66 * t1)
        n = 4 + i                                             # festons du bord du bas
        pas = 2 * L / n
        dessin = f"M{px:.2f},{y0:.2f} C{px + L * 0.25:.2f},{y0 + (y1 - y0) * 0.45:.2f} {px + L * 0.7:.2f},{y1 - 7:.2f} {px + L:.2f},{y1 - 3:.2f} "
        for k in range(n):
            x0, x1 = px + L - k * pas, px + L - (k + 1) * pas
            creux = 3.0 * (1 - abs((x0 + x1) / 2 - px) / L) ** 0.5
            dessin += f"Q{(x0 + x1) / 2:.2f},{y1 + 4.5 - creux * 0.4:.2f} {x1:.2f},{y1 - 3 + (creux if k < n - 1 else 0):.2f} "
        dessin += f"C{px - L * 0.7:.2f},{y1 - 7:.2f} {px - L * 0.25:.2f},{y0 + (y1 - y0) * 0.45:.2f} {px:.2f},{y0:.2f} Z"
        forme = path(dessin)
        cid = f"sap{i}"
        f.clip(cid, [forme])
        f.add(forme, base)
        f.add(path(f"M{px + L * 0.18:.2f},{y0:.2f} C{px + L * 0.3:.2f},{y0 + (y1 - y0) * 0.5:.2f} {px + L * 0.34:.2f},{y1 - 4:.2f} "
                   f"{px + L * 0.2:.2f},{y1 + 6:.2f} L{px + L + 3:.2f},{y1 + 6:.2f} L{px + L + 3:.2f},{y0:.2f} Z"), ombre, sil=False, clip=cid)
        f.add(path(f"M{px - L * 0.1:.2f},{y0 + (y1 - y0) * 0.42:.2f} C{px - L * 0.3:.2f},{y0 + (y1 - y0) * 0.6:.2f} "
                   f"{px - L * 0.55:.2f},{y1 - 5:.2f} {px - L * 0.78:.2f},{y1 - 3.5:.2f} C{px - L * 0.5:.2f},{y1 - 8:.2f} "
                   f"{px - L * 0.3:.2f},{y0 + (y1 - y0) * 0.55:.2f} {px - L * 0.1:.2f},{y0 + (y1 - y0) * 0.42:.2f} Z"),
              clair, sil=False, clip=cid, opacity=0.85)
    return Sprite([(tr, BOIS, TRAIT), (f, contour, TRAIT)], w, h, (px, py))


# ====================================================================== BUISSONS, ROSEAUX, ROCHER
def buisson(fleurs=None, baies=False, teinte="buisson"):
    """Buisson en touffes ; fleurs : couleur des petites fleurs, baies : des baies rouges."""
    w, h, px, py = 48, 40, 24, 34
    d = Drawing(w, h)
    _touffes(d, [(24, 15, 10.5), (13, 21, 9), (35, 21, 9), (19, 26, 8.5), (30, 26, 8.5)], teinte, "u")
    if fleurs:
        for x, y in ((16, 14), (27, 10), (34, 18), (22, 22), (11, 22), (30, 27), (38, 24), (18, 29)):
            for k in range(5):
                a = k * 2 * math.pi / 5 + x
                d.add(circle(x + 1.3 * math.cos(a), y + 1.3 * math.sin(a), 1.05), fleurs, sil=False)
            d.add(circle(x, y, 0.85), "#F6C945", sil=False)
    if baies:
        for x, y in ((17, 15), (29, 13), (33, 23), (21, 25), (12, 22), (26, 20)):
            d.add(circle(x, y, 1.45), "#E2463F", sil=False)
            d.add(circle(x - 0.45, y - 0.5, 0.45), "#FFFFFF", sil=False, opacity=0.8)
    return Sprite([(d, FEUILLAGES[teinte][3], TRAIT)], w, h, (px, py), "contour")


def fourre(teinte="buisson", fond="sombre", fleurs=None):
    """Fourré de la lisière (lisiere.py) : un gros massif touffu, large comme deux buissons ; les touffes du fond,
    à l'ombre, sont d'un vert plus sombre que celles de devant."""
    w, h, px, py = 84, 60, 42, 52
    d = Drawing(w, h)
    _touffes(d, [(41, 17, 12.5), (25, 23, 13.5), (58, 22, 14), (12, 32, 9.5), (72, 31, 10)], fond, "g")
    _touffes(d, [(16, 41, 10), (68, 42, 9.5), (33, 38, 12.5), (53, 39, 12)], teinte, "h")
    if fleurs:
        for x, y in ((28, 32), (40, 40), (56, 34), (14, 40), (66, 40), (48, 44), (22, 46)):
            for k in range(5):
                a = k * 2 * math.pi / 5 + x
                d.add(circle(x + 1.4 * math.cos(a), y + 1.4 * math.sin(a), 1.15), fleurs, sil=False)
            d.add(circle(x, y, 0.9), "#F6C945", sil=False)
    return Sprite([(d, FEUILLAGES[fond][3], TRAIT)], w, h, (px, py), "contour")


def roseaux():
    """Touffe de roseaux et de massettes, au bord de l'eau."""
    w, h, px, py = 32, 48, 16, 43
    d = Drawing(w, h)
    for x0, x1, y1, col in ((12, 5, 16, "#4E9A47"), (14, 11, 8, "#62B054"), (17, 20, 10, "#4E9A47"), (19, 27, 18, "#62B054"),
                            (15, 15.5, 5, "#74BD5E"), (10, 2.5, 26, "#62B054"), (21, 29.5, 28, "#4E9A47")):
        d.add(path(f"M{x0 - 1.2},{py} Q{(x0 + x1) / 2 - 1.5:.2f},{(py + y1) / 2:.2f} {x1},{y1} "
                   f"Q{(x0 + x1) / 2 + 1.5:.2f},{(py + y1) / 2:.2f} {x0 + 1.2},{py} Z"), col)
    for x, y in ((11, 9), (20, 6), (16, 13)):
        d.raw(line(f"M{x},{y + 7} L{x + 0.3},{py - 3}", "#3F7A3A", 0.9))
        d.add(rect(x - 1.5, y, 3, 8, 1.5), "#7A4A2B", edge=False)
        d.add(rect(x - 1.5, y, 1.2, 8, 0.6), "#9A6238", sil=False)
    return Sprite([(d, "#28592F", TRAIT)], w, h, (px, py))


def rocher():
    """Rocher à facettes : dessus éclairé, flanc droit dans l'ombre, un coussin de mousse, un caillou à côté."""
    w, h, px, py = 48, 38, 24, 31.5
    d = Drawing(w, h)
    corps = "M7,31 C5,22 9,13 18,9.5 C27,6 37,9 41,17 C44,23 43,28 41,31 Z"
    d.clip("roc", [path(corps)])
    d.add(path(corps), "#A7ADB3")
    d.add(path("M27,7 C36,9 43,17 43,31 L30,31 C32,24 31,15 27,7 Z"), "#858C94", sil=False, clip="roc")
    d.add(path("M9,22 C10,15 15,11 22,10 C19,14 17,19 17,24 Z"), "#C9CED3", sil=False, clip="roc")
    d.raw(line("M22,17 L27,22 L26,28", "#757C84", 0.9))
    d.add(path("M12,13.5 C15,8.5 24,6 30,8.5 C31.5,11 27,13 22,13.2 C18,13.4 15,15 12,13.5 Z"), "#6DB758", sil=False, clip="roc")
    d.add(path("M14,12.4 C17,9.4 22,8.2 26,8.8 C22,10 18,11 14,12.4 Z"), "#93D271", sil=False, clip="roc")
    d.add(path("M2,32 C1.5,28.5 4,26.5 7,27 C9.5,27.5 10.5,30 10,32 Z"), "#B4BAC0")
    d.add(path("M6,27.2 C8.6,27.8 10.4,29.8 10,32 L7,32 Z"), "#8E959D", sil=False)
    return Sprite([(d, "#4A5058", TRAIT)], w, h, (px, py), "contour")


# ====================================================================== NICHE
def niche():
    """La niche de Tecky, de trois quarts : pignon en planches, pan de toit et mur de droite dans l'ombre,
    plaque à l'os au-dessus de l'entrée. Elle touche le sol le long du pignon, puis du mur de droite qui fuit."""
    w, h, px, py = 88, 84, 36, 73
    d = Drawing(w, h)
    # mur de droite (dans l'ombre) et pignon
    d.add(poly([(54, 72), (54, 42), (72, 33), (72, 62)]), "#B5763C")
    for y in (50, 58, 66):
        d.raw(line(f"M54,{y} L72,{y - 9.6}", "#96602E", 0.8))
    pignon = poly([(10, 72), (10, 42), (32, 20), (54, 42), (54, 72)])
    d.clip("pignon", [pignon])
    d.add(pignon, "#DDA35C")
    for y in (36, 44, 52, 60, 68):
        d.raw(f'<g clip-path="url(#pignon)">' + line(f"M8,{y} L56,{y}", "#BE8644", 0.8) + "</g>")
    d.add(poly([(10, 42), (32, 20), (54, 42), (54, 47), (32, 25), (10, 47)]), "#A9692F", sil=False, clip="pignon", opacity=0.55)
    # entrée : une arche sombre, le bout d'une couverture rouge
    arche = path("M21,72 L21,56 C21,46.5 43,46.5 43,56 L43,72 Z")
    d.clip("arche", [arche])
    d.add(arche, "#3A2418", sil=False, edge=True)
    d.add(path("M21,72 L21,56 C21,50 28,47.6 32,47.6 L32,72 Z"), "#2A1810", sil=False, clip="arche")
    d.add(ellipse(33, 73, 10, 4), "#D64A40", sil=False, clip="arche")
    d.add(ellipse(31, 72, 5, 1.6), "#E8695E", sil=False, clip="arche")
    # toit : le pan de droite fuit vers l'arrière (dans l'ombre), le pan de gauche se voit par la tranche
    d.add(poly([(32, 14), (59, 41), (77, 32), (50, 5)]), "#B9291F")
    for t in (0.25, 0.5, 0.75):
        d.raw(line(f"M{32 + 27 * t:.1f},{14 + 27 * t:.1f} L{50 + 27 * t:.1f},{5 + 27 * t:.1f}", "#931F18", 0.8))
    d.add(poly([(4, 44), (32, 14), (60, 42), (56.5, 46), (32, 21.5), (7.5, 46)]), "#E2453B")
    d.add(poly([(4, 44), (32, 14), (33.5, 15.5), (6, 45.5)]), "#F47A6C", sil=False)
    d.add(poly([(32, 14), (50, 5), (51.5, 6.5), (33.5, 15.5)]), "#D63A31", sil=False)
    # plaque crème et son os
    d.add(rect(24.5, 31.5, 15, 8.5, 2), "#F6EBD2", sil=False, edge=True)
    d.add(rect(28.4, 35, 7.2, 1.7, 0.8), "#C98A4B", sil=False)
    for x, y in ((28.2, 34.6), (28.2, 37), (35.8, 34.6), (35.8, 37)):
        d.add(circle(x, y, 1.25), "#C98A4B", sil=False)
    return Sprite([(d, OUTLINE, 1.8)], w, h, (px, py), [(10, 71.3), (54, 71.3), (72, 61.3)])


def gamelle():
    """La gamelle bleue de Tecky, à côté de la niche."""
    w, h, px, py = 24, 20, 12, 15.5
    d = Drawing(w, h)
    d.add(path("M4,8 C4,3.5 20,3.5 20,8 L18.5,14 C18.5,16.5 5.5,16.5 5.5,14 Z"), "#2F74D6")
    d.add(ellipse(12, 7.6, 8, 2.9), "#5B9BEA", sil=False, edge=True)
    d.add(ellipse(12, 8, 6, 1.9), "#B8642C", sil=False)
    d.add(path("M5.5,12 C8,14.6 16,14.6 18.5,12 L18.5,14 C18.5,16.5 5.5,16.5 5.5,14 Z"), "#2259AE", sil=False)
    return Sprite([(d, OUTLINE, 1.8)], w, h, (px, py), "contour")


def niche_gamelle():
    """La niche et, posée devant son mur de droite, la gamelle : le décor « doghouse » du jeu."""
    n, g = niche(), gamelle()
    return Sprite(n.calques + [(g.calques[0][0], OUTLINE, 1.8, (63, 63))], n.w, n.h, n.pied, n.sol)


CATALOGUE = {
    "pommier": pommier, "pommier_jeune": lambda: pommier(True), "sapin": sapin,
    "sapin_haut": lambda: sapin(112, 60, 5), "sapin_petit": lambda: sapin(76, 58, 3, "sapin_bleu"),
    "niche_gamelle": niche_gamelle,
    "chene": chene, "chene_sombre": lambda: chene("sombre"), "bouleau": bouleau, "cerisier": cerisier,
    "jeune_arbre": jeune_arbre, "buisson": buisson, "buisson_fleuri": lambda: buisson(fleurs="#FFFFFF"),
    "buisson_rose": lambda: buisson(fleurs="#F9A8C4"), "buisson_baies": lambda: buisson(baies=True),
    "buisson_sombre": lambda: buisson(teinte="sombre"),
    "fourre": fourre, "fourre_fleuri": lambda: fourre(fleurs="#FFFFFF"), "fourre_clair": lambda: fourre("bouleau", "buisson"),
    "fourre_sombre": lambda: fourre("sombre", "sapin"), "fourre_foret": lambda: fourre("sapin", "fond"),
    "roseaux": roseaux, "rocher": rocher, "niche": niche, "gamelle": gamelle,
}


# Décor de carte.json -> (sprites qui le remplacent, tirage : le rang du sprite choisi, d'après la position du décor)
VARIANTES = {
    "tree": (["chene", "chene_sombre", "bouleau", "jeune_arbre", "cerisier"], [0, 0, 0, 1, 1, 2, 2, 3, 3, 4]),
    "bush": (["buisson", "buisson_fleuri", "buisson_baies", "buisson_sombre", "buisson_rose"], [0, 0, 1, 2, 3, 3, 4]),
    "fir": (["sapin", "sapin_haut", "sapin_petit"], [0, 0, 1, 1, 2]),
    "apple_tree": (["pommier"], [0]),
    "apple_tree_young": (["pommier_jeune"], [0]),
    "rock": (["rocher"], [0]),
    "reeds": (["roseaux"], [0]),
    "doghouse": (["niche_gamelle"], [0]),
    # la lisière (lisiere.py) : fourrés du bord de la carte, plus sombres le long de la forêt
    "thicket": (["fourre", "fourre_fleuri", "fourre_clair"], [0, 0, 0, 1, 2]),
    "thicket_dark": (["fourre_sombre", "fourre_foret"], [0, 0, 1]),
}


ECHELLES = {"roseaux": 0.9, "sapin": 0.75, "sapin_haut": 0.75, "sapin_petit": 0.75}      # ceux qui ne sont pas réduits de ECH
OMBRE = (0.45, 0.23)             # ombre portée à midi : décalage vers la droite et vers le bas, par unité de hauteur
#                                  (pack_web.py le donne au jeu : MAP.shadow ; il l'allonge le soir)


def cadre(nom):
    """(sprite, largeur, hauteur, origine x, origine y) d'un sprite du catalogue dans le jeu, en unités de l'atlas."""
    sp, k = CATALOGUE[nom](), ECHELLES.get(nom, ECH)
    return sp, math.ceil(sp.w * k), math.ceil(sp.h * k), sp.pied[0] * k, sp.pied[1] * k


def image(nom, echelle):
    """Image RGBA d'un sprite du catalogue à sa taille du jeu (réduit, contours compensés), marge PAD comprise."""
    sp, w, h, _, _ = cadre(nom)
    k = ECHELLES.get(nom, ECH)
    out = None
    for d, contour, ep, *reste in sp.calques:
        dx, dy = reste[0] if reste else (0, 0)
        d.w, d.h = w, h
        im = render_svg(d.svg(f"scale({k}) translate({dx} {dy})", outline=contour, outline_w=ep / k), w, h, echelle, PAD)
        out = im if out is None else Image.alpha_composite(out, im)
    return out


# ====================================================================== LE SOL
SOL_T = 12                       # cadre des détails du sol (origine au centre)


def sol_fleurs():
    """Petites fleurs semées dans l'herbe (game.js : groundDetails()) : pâquerette, bouton d'or, rose, bleue."""
    out = []
    for petales, coeur, n in (("#FFFFFF", "#F6C945", 6), ("#FBD84A", "#E8932E", 5), ("#F9A8C4", "#FFF1B8", 5), ("#A9C8F2", "#FFF1B8", 5)):
        d = Drawing(SOL_T, SOL_T)
        for k in range(n):
            a = k * 2 * math.pi / n + 0.4
            d.add(circle(6 + 1.5 * math.cos(a), 6 + 1.5 * math.sin(a), 1.15), petales)
        d.add(circle(6, 6, 1.0), coeur, sil=False)
        out.append(d.svg(outline="#5E7F3C", outline_w=1.0))
    return out


def sol_brins():
    """Touffes de brins d'herbe, plus sombres ou plus claires que le pré."""
    out = []
    for teinte, brins in (("#4FA04A", ((-2.6, 1.2, -4.0), (0, 0, -5.4), (2.4, 1.0, -3.6))), ("#5DAE50", ((-1.6, 0.6, -4.4), (1.6, -0.4, -4.8))),
                          ("#9BD86A", ((-2.2, 1.0, -3.6), (0.4, 0, -4.8), (2.6, 0.6, -3.2))), ("#4FA04A", ((-3.0, 2.0, -3.4), (-0.6, 0.4, -5.0), (1.6, -0.6, -5.6), (3.4, 1.4, -3.0)))):
        d = Drawing(SOL_T, SOL_T)
        d.raw(line(" ".join(f"M{6 + x},{9.5} Q{6 + x + c * 0.4:.2f},{9.5 + h * 0.6:.2f} {6 + x + c:.2f},{9.5 + h:.2f}" for x, c, h in brins),
                   teinte, 1.15))
        out.append(d.svg())
    return out


EAU_T = 16                       # cadre des nénuphars (origine au centre)


def _svg(t, corps):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {t} {t}" width="{t}" height="{t}">{corps}</svg>')


def sol_nenuphars():
    """Nénuphars posés sur l'eau, près des rives (game.js : waterDetails()) : une feuille ronde entaillée, son ombre
    dans l'eau, une nervure claire ; le premier porte une fleur rose."""
    out = []
    for r, fleur, tourne in ((4.6, True, 0), (3.2, False, 140), (3.8, False, 250), (2.8, False, 40)):
        x = y = EAU_T / 2
        s = [f'<ellipse cx="{x + 1:.2f}" cy="{y + 1.4:.2f}" rx="{r:.2f}" ry="{r * 0.78:.2f}" fill="#2F7DAE" opacity="0.35"/>',
             f'<g transform="rotate({tourne} {x} {y})">'
             f'<path d="M{x:.2f},{y:.2f} L{x + r:.2f},{y - r * 0.28:.2f} A{r:.2f},{r * 0.78:.2f} 0 1 0 {x + r * 0.86:.2f},{y + r * 0.4:.2f} Z" '
             f'fill="#5DB257" stroke="#2C6E3C" stroke-width="0.6" stroke-linejoin="round"/></g>',
             f'<path d="M{x - r * 0.7:.2f},{y - r * 0.2:.2f} Q{x - r * 0.3:.2f},{y - r * 0.6:.2f} {x + r * 0.3:.2f},{y - r * 0.55:.2f}" '
             f'stroke="#8ED278" stroke-width="0.8" fill="none" stroke-linecap="round"/>']
        if fleur:
            for i in range(6):
                a = i * math.pi / 3
                px, py = x - 1.2 + 1.5 * math.cos(a), y - 0.4 + 1.1 * math.sin(a)
                s.append(f'<ellipse cx="{px:.2f}" cy="{py:.2f}" rx="1.3" ry="0.9" fill="#FFC7DB" stroke="#C9698F" '
                         f'stroke-width="0.35" transform="rotate({math.degrees(a):.0f} {px:.2f} {py:.2f})"/>')
            s.append(f'<circle cx="{x - 1.2:.2f}" cy="{y - 0.4:.2f}" r="0.9" fill="#F6C945"/>')
        out.append(_svg(EAU_T, "".join(s)))
    return out


def sol_galets():
    """Galets posés sur le sable de la berge."""
    out = []
    for rx, ry, teinte, bord in ((2.4, 1.6, "#C9CDD1", "#7F868E"), (1.8, 1.3, "#D8D2C6", "#8D8577"), (2.9, 1.7, "#B9BEC4", "#727981")):
        x = y = SOL_T / 2
        out.append(_svg(SOL_T, f'<ellipse cx="{x + 0.5}" cy="{y + 0.9}" rx="{rx + 0.2}" ry="{ry - 0.1}" fill="#B9A46F" opacity="0.8"/>'
                               f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{teinte}" stroke="{bord}" stroke-width="0.55"/>'
                               f'<ellipse cx="{x - rx * 0.25:.2f}" cy="{y - ry * 0.3:.2f}" rx="{rx * 0.42:.2f}" ry="{ry * 0.3:.2f}" fill="#FFFFFF" opacity="0.7"/>'))
    return out


CAILLOUX = ((0, 2), (2, 3), (5, 3))      # gros, moyens, graviers : (première image, nombre d'images) de « sol/caillou »


def sol_cailloux():
    """Cailloux de craie semés sur la lande du plateau (game.js : heathDetails()), dans l'ordre de CAILLOUX : deux
    gros, trois moyens, trois graviers. Des pierres aux pans inégaux, pas des ovales : la face d'en haut à gauche au
    soleil, celle d'en bas à droite à l'ombre, et leur ombre couchée sur l'herbe."""
    out = []
    c = SOL_T / 2
    formes = ((4.3, 2.8, "#EFE9D8", 9), (3.8, 3.0, "#E2DAC4", 8),
              (2.9, 2.0, "#F1ECDD", 7), (2.6, 1.7, "#D6CCB2", 7), (2.3, 2.0, "#E6DFCB", 6),
              (1.5, 1.1, "#EFE9D8", 5), (1.2, 0.9, "#D9D0B8", 5), (1.6, 0.9, "#E3DCC6", 5))
    for i, (rx, ry, teinte, n) in enumerate(formes):
        rnd = random.Random(40 + i)
        pts = []
        for j in range(n):
            a = 2 * math.pi * (j + rnd.uniform(-0.28, 0.28)) / n
            k = rnd.uniform(0.78, 1.0)
            pts.append((c + rx * k * math.cos(a), c + ry * k * math.sin(a)))
        contour = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        haut = [(x, y) for x, y in pts if (x - c) / rx + (y - c) / ry < 0.15]            # les sommets tournés vers la lumière
        s = (f'<polygon points="{" ".join(f"{x + 0.7:.2f},{y + 0.9:.2f}" for x, y in pts)}" fill="#6F7A2C" opacity="0.5" '
             f'stroke="#6F7A2C" stroke-width="0.5" stroke-linejoin="round"/>'
             f'<polygon points="{contour}" fill="{teinte}" stroke="#857D66" stroke-width="{0.55 if rx > 2 else 0.45}" stroke-linejoin="round"/>')
        if rx > 2:                                                                       # le pan à l'ombre, le pan au soleil
            bas = [(x, y) for x, y in pts if (x - c) / rx + (y - c) / ry > 0.35]
            if len(bas) >= 2:
                s += (f'<polygon points="{" ".join(f"{c + (x - c) * 0.86:.2f},{c + (y - c) * 0.86:.2f}" for x, y in bas)} '
                      f'{c + rx * 0.15:.2f},{c + ry * 0.1:.2f}" fill="#B9AE92" opacity="0.75"/>')
            if len(haut) >= 2:
                s += (f'<polygon points="{" ".join(f"{c + (x - c) * 0.72:.2f},{c + (y - c) * 0.72:.2f}" for x, y in haut[:3])} '
                      f'{c - rx * 0.1:.2f},{c - ry * 0.05:.2f}" fill="#FFFFFF" opacity="0.65"/>')
        out.append(_svg(SOL_T, s))
    return out


def _feuille(x, y, a, L, w, fond, bord, nervure=None, ep=0.45):
    """Une feuille effilée qui part de (x, y) dans la direction a (degrés, 0 = vers la droite, -90 = vers le haut),
    longue de L et large de 2 w, avec sa nervure."""
    a = math.radians(a)
    c, s = math.cos(a), math.sin(a)
    tx, ty, mx, my = x + L * c, y + L * s, x + 0.42 * L * c, y + 0.42 * L * s
    out = (f'<path d="M{x:.2f},{y:.2f} Q{mx - s * w:.2f},{my + c * w:.2f} {tx:.2f},{ty:.2f} Q{mx + s * w:.2f},{my - c * w:.2f} {x:.2f},{y:.2f} Z" '
           f'fill="{fond}" stroke="{bord}" stroke-width="{ep}" stroke-linejoin="round"/>')
    if nervure:
        out += (f'<path d="M{x + 0.12 * L * c:.2f},{y + 0.12 * L * s:.2f} L{x + 0.8 * L * c:.2f},{y + 0.8 * L * s:.2f}" stroke="{nervure}" '
                f'stroke-width="{ep * 0.6:.2f}" fill="none" stroke-linecap="round"/>')
    return out


BOIS_T = 16                      # cadre des détails du sous-bois (origine au centre)
SOUS_BOIS = {"fougere": (0, 2), "mousse": (2, 2), "champignon": (4, 2), "pomme_de_pin": (6, 1), "brindille": (7, 2),
             "feuilles": (9, 2)}          # détail -> (première image, nombre d'images) de « sol/sousbois »


def sol_sousbois():
    """Détails semés dans le sous-bois (game.js : woodDetails()), dans l'ordre de SOUS_BOIS : petites fougères,
    coussins de mousse, champignons bruns, pomme de pin, brindilles, feuilles mortes."""
    c = BOIS_T / 2
    bord = "#2F6B3A"
    out = []
    for frondes in (((-158, 5.6), (-124, 6.6), (-92, 7.0), (-58, 6.4), (-24, 5.4)), ((-146, 5.0), (-106, 6.2), (-70, 6.0), (-34, 4.8))):
        s = f'<ellipse cx="{c + 0.8}" cy="{c + 4.4}" rx="4.4" ry="1.3" fill="#2E6B3C" opacity="0.45"/>'
        for i, (a, L) in enumerate(frondes):
            s += _feuille(c, c + 4, a, L, 1.5, "#63B659" if i % 2 else "#74C563", bord, "#A9E08A")
        out.append(_svg(BOIS_T, s))
    for bosses in (((-2.4, 0.6, 2.6), (1.6, 0.2, 3.0), (0, -1.0, 2.4)), ((-1.2, 0.2, 2.6), (1.8, 0.6, 2.0))):
        s = "".join(f'<ellipse cx="{c + x:.2f}" cy="{c + y + 0.7:.2f}" rx="{r:.2f}" ry="{r * 0.62:.2f}" fill="#3E7F3F"/>' for x, y, r in bosses)
        s += "".join(f'<ellipse cx="{c + x:.2f}" cy="{c + y:.2f}" rx="{r:.2f}" ry="{r * 0.62:.2f}" fill="#7DBE55"/>' for x, y, r in bosses)
        s += "".join(f'<ellipse cx="{c + x - r * 0.25:.2f}" cy="{c + y - r * 0.2:.2f}" rx="{r * 0.5:.2f}" ry="{r * 0.26:.2f}" fill="#A6DA6F"/>'
                     for x, y, r in bosses)
        out.append(_svg(BOIS_T, s))
    for pieds in (((-1.8, 1.2, 2.4), (2.0, 1.8, 1.7)), ((0, 1.4, 2.2),)):
        s = ""
        for x, y, r in pieds:
            px, py = c + x, c + y
            s += (f'<ellipse cx="{px + 0.7:.2f}" cy="{py + 0.5:.2f}" rx="{r * 0.9:.2f}" ry="{r * 0.3:.2f}" fill="#2E6B3C" opacity="0.45"/>'
                  f'<rect x="{px - r * 0.3:.2f}" y="{py - r * 1.0:.2f}" width="{r * 0.6:.2f}" height="{r * 1.1:.2f}" rx="{r * 0.25:.2f}" '
                  f'fill="#F3E6C8" stroke="#6A4628" stroke-width="0.4"/>'
                  f'<path d="M{px - r:.2f},{py - r * 0.85:.2f} A{r:.2f},{r * 0.95:.2f} 0 0 1 {px + r:.2f},{py - r * 0.85:.2f} Z" '
                  f'fill="#C8854C" stroke="#6A4628" stroke-width="0.45" stroke-linejoin="round"/>'
                  f'<ellipse cx="{px - r * 0.35:.2f}" cy="{py - r * 1.4:.2f}" rx="{r * 0.32:.2f}" ry="{r * 0.17:.2f}" fill="#E7B27C"/>')
        out.append(_svg(BOIS_T, s))
    s = (f'<ellipse cx="{c + 0.8}" cy="{c + 1.6}" rx="3.2" ry="1.3" fill="#2E6B3C" opacity="0.45"/>'
         f'<g transform="rotate(-24 {c} {c})"><ellipse cx="{c}" cy="{c}" rx="3.1" ry="1.9" fill="#9A6A3E" stroke="#4E3220" stroke-width="0.5"/>'
         + "".join(f'<path d="M{c + x},{c - 1.5} Q{c + x + 1.1},{c} {c + x},{c + 1.5}" stroke="#5E3E24" stroke-width="0.45" fill="none"/>'
                   for x in (-1.6, -0.2, 1.2))
         + f'<ellipse cx="{c - 0.8}" cy="{c - 0.9}" rx="1.3" ry="0.4" fill="#C08E5A"/></g>')
    out.append(_svg(BOIS_T, s))
    for trace in ("M-4.6,1.6 L0.4,-0.2 L4.4,-1.6 M0.4,-0.2 L2.2,2.2", "M-4.0,-1.8 L-0.6,0.4 L3.8,1.0 M-0.6,0.4 L-1.6,2.8"):
        s = "".join(f'<g transform="translate({c} {c})"><path d="{trace}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linecap="round" '
                    f'stroke-linejoin="round"/></g>' for col, w in (("#4E3220", 1.7), ("#9A6E42", 0.8)))
        out.append(_svg(BOIS_T, s))
    for feuilles in (((-2.6, 1.0, -30, "#D9A441"), (1.4, -1.2, 40, "#D9803A"), (2.2, 2.2, 160, "#C9B24A")), ((-1.6, -0.8, 200, "#D9803A"), (1.8, 1.0, 20, "#D9A441"))):
        s = "".join(_feuille(c + x, c + y, a, 3.4, 1.15, col, "#7A5226", "#7A5226", 0.35) for x, y, a, col in feuilles)
        out.append(_svg(BOIS_T, s))
    return out


CULTURES = ("pousses", "salades", "carottes", "poireaux")        # deux images chacune dans « sol/culture »


def sol_cultures():
    """Les cultures du champ, plantées en rangs sur les buttes (game.js : fieldDetails()), deux plants par culture,
    dans l'ordre de CULTURES. Vues d'un peu au-dessus, le pied au milieu du cadre, une ombre sur la terre."""
    c = SOL_T / 2
    bord = "#3A7434"
    ombre = lambda rx: f'<ellipse cx="{c + 0.7}" cy="{c + 0.7}" rx="{rx}" ry="{rx * 0.42:.2f}" fill="#7A5230" opacity="0.55"/>'
    out = []
    for feuilles in (((-150, 3.4), (-30, 3.4), (-90, 2.6)), ((-160, 3.0), (-20, 3.6), (-84, 3.0))):          # jeunes pousses
        out.append(_svg(SOL_T, ombre(2.6) + "".join(_feuille(c, c + 0.4, a, L, 1.2, "#86CF62", bord, "#C4EE9A") for a, L in feuilles)))
    for n, r in ((7, 3.5), (6, 3.1)):                                                                       # salades
        s = ombre(r + 0.5)
        for i in range(n):
            a = i * 2 * math.pi / n + 0.3
            s += (f'<ellipse cx="{c + r * 0.5 * math.cos(a):.2f}" cy="{c - 0.6 + r * 0.38 * math.sin(a):.2f}" rx="{r * 0.6:.2f}" ry="{r * 0.44:.2f}" '
                  f'fill="{"#7CC65A" if i % 2 else "#8FD46A"}" stroke="{bord}" stroke-width="0.45"/>')
        s += (f'<ellipse cx="{c}" cy="{c - 0.6}" rx="{r * 0.56:.2f}" ry="{r * 0.4:.2f}" fill="#A9E27C" stroke="{bord}" stroke-width="0.4"/>'
              f'<ellipse cx="{c - 0.3}" cy="{c - 0.8}" rx="{r * 0.24:.2f}" ry="{r * 0.16:.2f}" fill="#D6F5A8"/>')
        out.append(_svg(SOL_T, s))
    for fanes in (((-128, 4.2), (-96, 5.0), (-62, 4.4)), ((-140, 3.8), (-104, 4.6), (-74, 4.8), (-42, 3.8))):  # carottes
        s = ombre(2.4) + f'<ellipse cx="{c}" cy="{c + 0.5}" rx="1.5" ry="0.95" fill="#F08A32" stroke="#9A4E1A" stroke-width="0.4"/>'
        s += "".join(_feuille(c, c + 0.2, a, L, 0.85, "#4FA84C", "#2F6B3A", "#8ED278", 0.4) for a, L in fanes)
        out.append(_svg(SOL_T, s))
    for brins in (((-112, 5.0), (-90, 5.6), (-66, 4.8)), ((-120, 4.4), (-96, 5.4), (-74, 5.2), (-52, 4.2))):   # poireaux
        s = ombre(2.2) + f'<rect x="{c - 0.9}" y="{c - 1.0}" width="1.8" height="1.8" rx="0.7" fill="#EEF3D8" stroke="#6E8F5A" stroke-width="0.4"/>'
        s += "".join(_feuille(c, c - 0.6, a, L, 0.7, "#6FB78C", "#33705A", None, 0.4) for a, L in brins)
        out.append(_svg(SOL_T, s))
    return out


CULTURES_ETE = ("ble", "tournesols", "mais", "tomates")          # les cultures de l'été, deux images chacune


def sol_cultures_ete():
    """Les cultures de l'été, dans l'ordre de CULTURES_ETE : blé mûr, tournesols, maïs, tomates. Mêmes cadres et même
    pied que sol_cultures()."""
    c = SOL_T / 2
    ombre = lambda rx: f'<ellipse cx="{c + 0.7}" cy="{c + 0.7}" rx="{rx}" ry="{rx * 0.42:.2f}" fill="#7A5230" opacity="0.55"/>'
    out = []
    for tiges in (((-112, 4.6), (-90, 5.2), (-68, 4.4)), ((-120, 4.0), (-98, 5.0), (-78, 5.2), (-56, 4.0))):      # blé mûr
        t = ombre(2.4)
        for a, L in tiges:
            r = math.radians(a)
            x, y = c + L * math.cos(r), c + 0.4 + L * math.sin(r)
            t += f'<path d="M{c:.2f},{c + 0.4:.2f} L{x:.2f},{y:.2f}" stroke="#C9972E" stroke-width="0.55" stroke-linecap="round"/>'
            t += (f'<ellipse cx="{x:.2f}" cy="{y - 0.5:.2f}" rx="0.75" ry="1.5" transform="rotate({a + 90:.0f} {x:.2f} {y - 0.5:.2f})" '
                  f'fill="#F2CB5A" stroke="#A8761E" stroke-width="0.4"/>')
        out.append(_svg(SOL_T, t))
    for r0, tourne in ((2.5, 0), (2.1, 25)):                                                                # tournesols
        t = ombre(2.6) + _feuille(c, c + 0.8, -165, 3.0, 1.1, "#5DAE4E", "#2F6B3A", "#9BD680", 0.4) + _feuille(c, c + 0.8, -15, 3.0, 1.1, "#5DAE4E", "#2F6B3A", "#9BD680", 0.4)
        y = c - 1.6
        for i in range(9):
            a = math.radians(i * 40 + tourne)
            t += (f'<ellipse cx="{c + r0 * 0.78 * math.cos(a):.2f}" cy="{y + r0 * 0.78 * math.sin(a):.2f}" rx="{r0 * 0.5:.2f}" ry="{r0 * 0.28:.2f}" '
                  f'transform="rotate({i * 40 + tourne} {c + r0 * 0.78 * math.cos(a):.2f} {y + r0 * 0.78 * math.sin(a):.2f})" fill="#F7C933" stroke="#B5801A" stroke-width="0.35"/>')
        t += f'<circle cx="{c}" cy="{y}" r="{r0 * 0.5:.2f}" fill="#7A4A22" stroke="#4E2C12" stroke-width="0.4"/><circle cx="{c - 0.3}" cy="{y - 0.3}" r="{r0 * 0.2:.2f}" fill="#A06A38"/>'
        out.append(_svg(SOL_T, t))
    for feuilles in (((-150, 4.2), (-30, 4.2), (-118, 4.8), (-62, 4.8)), ((-160, 3.8), (-24, 4.4), (-110, 5.0), (-70, 4.4))):   # maïs
        t = ombre(2.6) + "".join(_feuille(c, c + 0.4, a, L, 0.9, "#6DBB52", "#2F6B3A", "#B4E48C", 0.4) for a, L in feuilles)
        t += (f'<ellipse cx="{c + 0.2}" cy="{c - 2.2}" rx="1.0" ry="2.1" fill="#F4D24A" stroke="#A8761E" stroke-width="0.4"/>'
              f'<path d="M{c - 0.5},{c - 0.6} Q{c + 0.2},{c - 2.6} {c + 1.0},{c - 0.6} Z" fill="#8FD46A" stroke="#2F6B3A" stroke-width="0.35"/>')
        out.append(_svg(SOL_T, t))
    for fruits in (((-1.9, -1.0), (1.6, -1.9), (0.3, 0.3)), ((-1.4, -2.0), (1.9, -0.6), (-0.4, 0.2), (0.6, -3.0))):  # tomates
        t = ombre(3.0) + "".join(_feuille(c, c + 0.4, a, 3.8, 1.5, "#4FA84C", "#2F6B3A", "#8ED278", 0.4) for a in (-155, -90, -25))
        for dx, dy in fruits:
            t += (f'<circle cx="{c + dx}" cy="{c + dy}" r="1.15" fill="#E2412E" stroke="#8E2018" stroke-width="0.4"/>'
                  f'<circle cx="{c + dx - 0.35}" cy="{c + dy - 0.4}" r="0.35" fill="#FFFFFF" opacity="0.7"/>')
        out.append(_svg(SOL_T, t))
    return out


SABLE = ("etoile", "coquille", "coquille2", "algue", "galet", "galet2", "bois", "rides", "rides2", "trou")


def sol_sable():
    """Ce que la mer a laissé sur le sable (le jeu le sème une fois dans le sol, comme les cailloux de la lande), dans
    l'ordre de SABLE : une étoile de mer, deux éclats de coquille, une algue, deux galets, un bois flotté, deux rides
    de sable, un petit trou de crabe."""
    c = SOL_T / 2
    om = "#C9A860"
    out = []
    pts = []
    for i in range(10):                                                                                     # étoile de mer
        a, r = math.radians(i * 36 - 90), (3.6 if i % 2 == 0 else 1.5)
        pts.append(f"{c + r * math.cos(a):.2f},{c + r * math.sin(a) * 0.8:.2f}")
    out.append(_svg(SOL_T, f'<polygon points="{" ".join(pts)}" transform="translate(0.5 0.6)" fill="{om}"/>'
                           f'<polygon points="{" ".join(pts)}" fill="#F08A5A" stroke="#B4552E" stroke-width="0.5" stroke-linejoin="round"/>'
                           f'<circle cx="{c}" cy="{c}" r="0.6" fill="#F9B48C"/>'))
    for teinte, bord, rot in (("#FBF3E4", "#B9A48A", -20), ("#F6C9C0", "#B8847A", 35)):                      # éclats de coquille
        out.append(_svg(SOL_T, f'<g transform="rotate({rot} {c} {c})"><path d="M{c - 2.6},{c + 1} Q{c},{c - 3.6} {c + 2.6},{c + 1} Q{c},{c + 2} {c - 2.6},{c + 1} Z" '
                               f'fill="{om}" transform="translate(0.5 0.6)"/><path d="M{c - 2.6},{c + 1} Q{c},{c - 3.6} {c + 2.6},{c + 1} Q{c},{c + 2} {c - 2.6},{c + 1} Z" '
                               f'fill="{teinte}" stroke="{bord}" stroke-width="0.45"/>'
                               f'<path d="M{c},{c + 1.2} L{c},{c - 1.6} M{c},{c + 1.2} L{c - 1.3},{c - 0.9} M{c},{c + 1.2} L{c + 1.3},{c - 0.9}" stroke="{bord}" stroke-width="0.3" fill="none"/></g>'))
    out.append(_svg(SOL_T, "".join(_feuille(c - 0.6, c + 1.4, a, L, 0.8, "#5E9A5A", "#35663A", None, 0.4) for a, L in ((-150, 3.6), (-100, 4.6), (-48, 4.0), (-10, 3.0)))))
    for rx, ry, teinte, bord in ((2.2, 1.4, "#D9D4CA", "#8D8577"), (1.5, 1.0, "#BFC4CA", "#727981")):          # galets
        out.append(_svg(SOL_T, f'<ellipse cx="{c + 0.5}" cy="{c + 0.7}" rx="{rx}" ry="{ry}" fill="{om}"/>'
                               f'<ellipse cx="{c}" cy="{c}" rx="{rx}" ry="{ry}" fill="{teinte}" stroke="{bord}" stroke-width="0.5"/>'
                               f'<ellipse cx="{c - rx * 0.25:.2f}" cy="{c - ry * 0.3:.2f}" rx="{rx * 0.4:.2f}" ry="{ry * 0.28:.2f}" fill="#FFFFFF" opacity="0.7"/>'))
    out.append(_svg(SOL_T, f'<path d="M{c - 4},{c + 1.2} Q{c - 1},{c - 0.6} {c + 4},{c - 0.8}" stroke="{om}" stroke-width="2" stroke-linecap="round" fill="none" transform="translate(0.4 0.7)"/>'
                           f'<path d="M{c - 4},{c + 1.2} Q{c - 1},{c - 0.6} {c + 4},{c - 0.8}" stroke="#8A6A48" stroke-width="2.3" stroke-linecap="round" fill="none"/>'
                           f'<path d="M{c - 4},{c + 1.2} Q{c - 1},{c - 0.6} {c + 4},{c - 0.8}" stroke="#C4A27A" stroke-width="1.4" stroke-linecap="round" fill="none"/>'
                           f'<path d="M{c + 0.6},{c - 0.4} l1.6,-1.8" stroke="#8A6A48" stroke-width="0.9" stroke-linecap="round"/>'))
    for dy in (0.0, 0.6):                                                                                   # rides de sable
        out.append(_svg(SOL_T, "".join(
            f'<path d="M{c - 4.4 + k * 0.6},{c - 2 + k * 2 + dy} q2.2,-1.1 4.4,0 t4.4,0" stroke="{"#D9B870" if k % 2 else "#FBE7B0"}" stroke-width="0.55" '
            f'stroke-linecap="round" fill="none" opacity="0.9"/>' for k in range(3))))
    out.append(_svg(SOL_T, f'<ellipse cx="{c}" cy="{c}" rx="1.5" ry="0.9" fill="#8E7240"/><ellipse cx="{c - 0.2}" cy="{c - 0.2}" rx="0.9" ry="0.5" fill="#5E4A28"/>'
                           + "".join(f'<circle cx="{c + dx}" cy="{c + dy}" r="0.45" fill="#F7E2A6" stroke="{om}" stroke-width="0.25"/>'
                                     for dx, dy in ((2.2, 0.6), (2.9, -0.4), (-2.3, 0.9), (1.4, 1.5), (-1.6, -1.2)))))
    return out


def assise(plein):
    """La rangée où une silhouette (tableau de booléens) est assise sur le sol, vue du côté où tombe son ombre : en
    remontant depuis son point le plus bas, la première rangée où son bord droit cesse de s'écarter (il devient un
    flanc). Pour un bas droit, c'est la dernière rangée. Pour un bas arrondi (le socle d'une bitte, le fond d'un pot
    ou d'un tonneau, un buisson), c'est plus haut, au bout du socle : couchée à partir du point le plus bas, l'ombre
    laissait un coin de sol éclairé entre elle et l'objet, à droite (vu par Christophe : « des ombres qui ont un
    espace avant leur objet »). Ce qui est sous cette rangée se couche sous l'objet, caché. Jamais plus haut que
    20 % de la hauteur."""
    import numpy as np
    rangs = np.where(plein.any(axis=1))[0]
    haut, bas = int(rangs[0]), int(rangs[-1])
    droite = lambda y: int(np.where(plein[y])[0][-1]) if plein[y].any() else -1
    fin = bas - max(2, int((bas - haut) * 0.2))
    for y in range(bas, fin, -1):
        if droite(y - 2) <= droite(y):
            return y + 1
    return fin + 1


def bandes_image(im, ox, oy, sol, echelle):
    """Ligne de contact d'une image (RGBA, marge PAD comprise, à `echelle` pixels par unité, origine en (ox, oy)
    unités) : là où elle touche le sol. Liste de points [u, b] en pixels de l'image à partir de son origine, de
    gauche à droite, d'un bord de la silhouette à l'autre : à la colonne u, le sol est b pixels sous l'origine.
    Le jeu couche la silhouette à partir de cette ligne pour dessiner l'ombre portée (game.js : groundShadows()) :
    un point à la hauteur h au-dessus du sol tombe h * SHADOW plus loin, à droite et vers le bas.
    sol : "pied" (une horizontale à l'origine), "contour" (une horizontale au point le plus bas de la silhouette :
    un buisson, une botte de foin ; suivre le bas de la silhouette colonne par colonne effilochait l'ombre aux coins
    arrondis) ou une liste de points (x, y) en unités, de gauche à droite (les murs d'un bâtiment)."""
    import numpy as np
    A = np.asarray(im.getchannel("A"), dtype=np.float32) / 255.0
    m = PAD * echelle
    x0, y0 = ox * echelle + m, oy * echelle + m
    plein = A > 0.5
    cols = np.where(plein.any(axis=0))[0]
    if not len(cols):
        return []
    c0, c1 = int(cols[0]) - x0, int(cols[-1]) + 1 - x0
    if sol == "pied":
        return [[round(c0), 0], [round(c1), 0]]
    if sol == "contour":
        return [[round(c0), round(assise(plein) - y0)], [round(c1), round(assise(plein) - y0)]]
    pts = [[x * echelle + m - x0, y * echelle + m - y0] for x, y in sol]
    pts[0][0], pts[-1][0] = min(pts[0][0], c0), max(pts[-1][0], c1)         # (à plat au-delà des bouts)
    return [[round(u, 1), round(v, 1)] for u, v in pts]


def bandes(nom, echelle):
    """Ligne de contact d'un sprite du catalogue (voir bandes_image), à sa taille du jeu."""
    sp, w, h, ox, oy = cadre(nom)
    k = ECHELLES.get(nom, ECH)
    sol = sp.sol if isinstance(sp.sol, str) else [(x * k, y * k) for x, y in sp.sol]
    return bandes_image(image(nom, echelle), ox, oy, sol, echelle)


if __name__ == "__main__":
    noms = [n for n in CATALOGUE if n != "gamelle"]
    ims = [image(n, 6) for n in noms]
    rangs = [ims[i:i + 7] for i in range(0, len(ims), 7)]
    H = max(i.height for i in ims)
    planche = Image.new("RGBA", (max(sum(i.width for i in r) for r in rangs) + 20, len(rangs) * H + 20), (126, 196, 100, 255))
    for j, r in enumerate(rangs):
        x = 10
        for im in r:
            planche.alpha_composite(im, (x, 10 + j * H + H - im.height))
            x += im.width
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference", "v2", "nature_v2.png")
    planche.convert("RGB").save(fn)
    print(fn, planche.size)

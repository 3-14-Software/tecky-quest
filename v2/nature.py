"""
Nature et niche, version 2 — étude pour l'écran témoin (PLAN_V2.md, lots 1 et 4).

Ce qui change par rapport à decor.py :
- plusieurs modèles par espèce (chêne, bouleau, cerisier en fleurs, jeune arbre ; buissons ronds ou fleuris) ;
- un feuillage en touffes, chacune avec son ombre et sa lumière : le soleil vient d'en haut à gauche ;
- un contour de la teinte du décor (vert foncé pour le feuillage, brun doux pour le bois) : le brun #3A1E12 reste aux
  personnages et à ce qu'on peut toucher, qui se détachent ainsi du paysage ;
- pas d'ombre ovale dessinée dans le sprite : l'ombre portée se calcule à partir de la silhouette (temoin.py).

Chaque fonction rend un Sprite : des calques (dessin, couleur et épaisseur du contour), la taille du cadre, le pied
(le point posé au sol) et `sol`, la ligne où l'objet touche le sol, d'où part son ombre portée :
- "pied" : une horizontale à la hauteur du pied (arbres, roseaux, personnages : ils ne touchent le sol qu'au pied) ;
- "contour" : le bas de la silhouette (buissons, rocher : ils sont posés au sol sur toute leur largeur) ;
- une liste de points (x, y) du cadre, de gauche à droite (la niche : le bas du pignon, puis du mur qui fuit).
Le jeu ne s'en sert pas encore.
"""
import math
import os
import sys
from collections import namedtuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image  # noqa: E402

from spritelib import Drawing, circle, ellipse, rect, path, poly, line, render_svg, OUTLINE, PAD  # noqa: E402

Sprite = namedtuple("Sprite", "calques w h pied sol", defaults=("pied",))
TRAIT = 1.6                      # épaisseur du contour du décor (1.8 pour les personnages)
BOIS = "#4E3220"                 # contour du bois

FEUILLAGES = {                   # ombre, base, clair, contour
    "chene":    ("#37913D", "#56B345", "#93D557", "#235A2B"),
    "sombre":   ("#2A7B40", "#3F9745", "#63B34F", "#1B4A2A"),
    "bouleau":  ("#74B441", "#9BD052", "#CBE877", "#3F6C2C"),
    "jeune":    ("#2B8C5E", "#45AA74", "#83D09A", "#1D5640"),
    "cerisier": ("#E27FA8", "#F6B0CA", "#FFDDE9", "#8C4160"),
    "buisson":  ("#3A9642", "#5CB84A", "#98DA5E", "#235A2B"),
}


def rendre(sp, echelle):
    """Image RGBA d'un Sprite (ses calques superposés), marge PAD comprise."""
    out = None
    for d, contour, ep in sp.calques:
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
    return Sprite([(d, OUTLINE, 1.8)], w, h, (px, py), [(10, 72.9), (54, 72.9), (72, 62.9)])


def gamelle():
    """La gamelle bleue de Tecky, à côté de la niche."""
    w, h, px, py = 24, 20, 12, 15.5
    d = Drawing(w, h)
    d.add(path("M4,8 C4,3.5 20,3.5 20,8 L18.5,14 C18.5,16.5 5.5,16.5 5.5,14 Z"), "#2F74D6")
    d.add(ellipse(12, 7.6, 8, 2.9), "#5B9BEA", sil=False, edge=True)
    d.add(ellipse(12, 8, 6, 1.9), "#B8642C", sil=False)
    d.add(path("M5.5,12 C8,14.6 16,14.6 18.5,12 L18.5,14 C18.5,16.5 5.5,16.5 5.5,14 Z"), "#2259AE", sil=False)
    return Sprite([(d, OUTLINE, 1.8)], w, h, (px, py), "contour")


CATALOGUE = {
    "chene": chene, "chene_sombre": lambda: chene("sombre"), "bouleau": bouleau, "cerisier": cerisier,
    "jeune_arbre": jeune_arbre, "buisson": buisson, "buisson_fleuri": lambda: buisson(fleurs="#FFFFFF"),
    "buisson_rose": lambda: buisson(fleurs="#F9A8C4"), "buisson_baies": lambda: buisson(baies=True),
    "buisson_sombre": lambda: buisson(teinte="sombre"), "roseaux": roseaux, "rocher": rocher, "niche": niche, "gamelle": gamelle,
}


if __name__ == "__main__":
    noms = list(CATALOGUE)
    ims = [rendre(CATALOGUE[n](), 4) for n in noms]
    H = max(i.height for i in ims)
    planche = Image.new("RGBA", (sum(i.width for i in ims[:7]) + 40, 2 * H + 20), (126, 196, 100, 255))
    x = y = 10
    for k, im in enumerate(ims):
        if k == 7:
            x, y = 10, H + 10
        planche.alpha_composite(im, (x, y + H - im.height))
        x += im.width
    fn = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reference", "v2", "nature_v2.png")
    planche.convert("RGB").save(fn)
    print(fn, planche.size)

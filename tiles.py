"""
Tuiles de sol 32x32 (1x) avec transitions "coins" (Wang / marching squares).

Chaque "paire" (terrain du dessus / terrain du dessous) a 16 tuiles : la tuile
n°k a le terrain du dessus dans les coins dont le bit est à 1 :  NO=1, NE=2, SO=4, SE=8.
  ex. 15 = tout terrain, 3 = moitié haute, 1 = coin haut-gauche seulement.
Le contour est calculé à partir d'un champ bilinéaire des 4 coins : les bords
droits sont droits, les coins sont arrondis, et tout raccorde d'une tuile à l'autre.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw

T = 32          # taille de tuile en 1x
SS = 4          # sur-échantillonnage (anti-crénelage)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


GRASS = dict(fill="#7CC36B", blade="#5FA852", flower=("#FFFFFF", "#F7D154", "#F28CB8"))

TERRAINS = {
    # nom : fond, liseré (bordure), trait extérieur, largeurs (px 1x)
    "dirt":     dict(fill="#D9B47A", edge="#C29A62", out="#8A6A3E", edge_w=1.6, out_w=0.9),
    "road":     dict(fill="#5B5E68", edge="#C6C9D1", out="#3E4048", edge_w=2.6, out_w=0.9),
    "paving":   dict(fill="#D4CBB8", edge="#B3A88F", out="#7E735E", edge_w=1.6, out_w=0.9),
    "concrete": dict(fill="#A9ACB2", edge="#8E9197", out="#5F6268", edge_w=1.6, out_w=0.9),
    "sidewalk": dict(fill="#CDD0D5", edge="#B3B7BE", out="#6E727A", edge_w=1.4, out_w=0.9),
    "water":    dict(fill="#5FB5E5", out="#2F7DAE", out_w=0.85, shore=True),      # berge et hauts-fonds : _shore()
    "field":    dict(fill="#B07A45", edge="#9A6638", out="#6E4628", edge_w=1.6, out_w=0.9),   # champ labouré
    "forest":   dict(fill="#5A9A4E", edge="#4F8C45", out="#3F7537", edge_w=1.2, out_w=0.7),   # sous-bois
    # La côte (l'épisode de l'été ; teintes choisies par Christophe sur reference/v2/cote_terrains_options.png : le
    # sable doré et les planches brunes ; la mer, turquoise, est l'eau aux couleurs de l'été : saisons.py). Ces
    # bords naturels (sable / herbe, eau / sable, falaise) ont leur rangée dans le tileset : PAIRS.
    "sand":     dict(fill="#F2DFA8", edge="#E3CB8C", out="#B79A5C", edge_w=1.6, out_w=0.8),   # le sable de la plage
    "planks":   dict(fill="#B98A5C", edge="#9C7046", out="#5E4630", edge_w=1.4, out_w=0.9),   # les planches, la jetée
    # La mer : un terrain à part de l'eau douce (Christophe, 13 novembre 2026 : la rivière « doit avoir une couleur
    # moins prononcée que la mer »). La mer garde le turquoise choisi sur cote_terrains_options.png, la rivière et
    # les mares le bleu doux de « water ». Pour les collisions, les deux sont de l'eau (pack_web : MAP.water).
    "sea":      dict(fill="#2F9CCB", out="#1C6A96", out_w=0.85, shore=True, mer=True),
    # La falaise, façon RPG Maker XP (demande de Christophe, d'après une carte de RPG Maker, validée sur
    # reference/v2/falaise_rpg.png) : le plateau est un bloc surélevé aux bords arrondis. « heath », la lande du
    # plateau (herbe jaunie, caillouteuse), cernée d'un liséré de pierres ; « chalk », la paroi de roche peinte sous
    # ses bords du bas (hauteur : le nombre de rangées de coins) ; « stairs », l'escalier qui la franchit.
    "chalk":    dict(fill="#EAE3CF", out="#6E6650", out_w=1.3, cliff=True),
    "heath":    dict(fill="#C4C658", out="#7A725B", out_w=1.3, lisere=True),
    "stairs":   dict(fill="#DCD3BC", edge="#B5AD96", out="#6E6650", edge_w=1.0, out_w=1.3),
}

# Paires disponibles (dessus, dessous), dans l'ordre des lignes de la planche.
# Les 4 premières gardent les index de la version précédente.
PAIRS = [("dirt", "grass"), ("road", "grass"), ("paving", "grass"), ("concrete", "grass"),
         ("sidewalk", "grass"), ("road", "sidewalk"), ("water", "grass"), ("paving", "sidewalk"),
         ("road", "dirt"), ("road", "concrete"), ("concrete", "sidewalk"), ("field", "grass"),
         ("forest", "grass"), ("dirt", "forest"),
         # la côte : ses bords naturels ont une rangée (et donc leurs variantes froissées, ALTERNEES) ; les planches,
         # la falaise et les autres mélanges restent des tuiles composées
         ("sand", "grass"), ("sea", "sand")]

# Retouches de style pour certaines paires (sinon : style du terrain du dessus)
PAIR_STYLE = {
    ("road", "dirt"): dict(edge="#74777F", edge_w=1.2),
    ("road", "concrete"): dict(edge="#74777F", edge_w=1.2),
}

# Priorité d'empilement (utile pour la génération automatique) : l'eau recouvre le sable, la falaise a le pied dans
# l'eau ou sur le sable, les planches (la jetée) passent sur l'eau
PRIORITY = ["grass", "forest", "field", "dirt", "sand", "water", "sea", "chalk", "heath", "stairs", "sidewalk",
            "concrete", "paving", "planks", "road"]
# (l'ordre d'avant la côte, les nouveaux terrains à la suite : la graine des tuiles composées, qui ne doit pas
# changer pour celles qui existaient — composite_seed())
_GRAINES = ["grass", "forest", "field", "dirt", "water", "sidewalk", "concrete", "paving", "road", "sand", "chalk", "planks",
            "heath", "stairs", "sea"]
# Le bloc de la falaise : le plateau, sa paroi, son escalier. Il a les bords arrondis de tous les terrains, sans
# froissement, et jette une ombre sur le sol d'en bas (_ombre_bloc).
BLOC = ("chalk", "heath", "stairs")
# Terrain dont la texture se suit d'une tuile à l'autre (les grandes masses de roche de la paroi) : elle est découpée
# dans une grande image qui ne se répète que toutes les PHASES tuiles — plus large qu'un écran : on ne voit jamais
# deux fois la même roche —, d'après la place de la tuile dans la carte. Une tuile qui en contient est donc
# toujours une tuile composée, propre à sa place (phase()). La lande, elle, est unie : c'est le jeu qui y sème ses
# cailloux, d'après la position (game.js : heathDetails()) ; dessinés dans la texture, ils revenaient toutes les
# six tuiles, et cela se voyait autour du phare.
SUIVIES = ("chalk",)
PHASES = (24, 4)


def phase(corners, tx, ty):
    """La place d'une tuile dans les grandes textures (None si elle n'en a pas besoin)."""
    return (tx % PHASES[0], ty % PHASES[1]) if any(c in SUIVIES for c in corners) else None


# ------------------------------------------------------------------ textures (sur-échantillonnées)
def _canvas(scale, color):
    n = T * scale * SS
    return Image.new("RGBA", (n, n), hexrgb(color) + (255,))


def tex_grass(scale, variant=0, seed=0):
    im = _canvas(scale, GRASS["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    rnd = random.Random(1000 + seed * 7 + variant)
    if variant in (1, 2):
        for _ in range(7):
            x, y = rnd.uniform(4, 28), rnd.uniform(5, 28)
            w = 1.1 * k
            d.line([(x * k - 1.5 * k, y * k - 2.2 * k), (x * k, y * k)], fill=hexrgb(GRASS["blade"]), width=int(w))
            d.line([(x * k + 1.5 * k, y * k - 2.2 * k), (x * k, y * k)], fill=hexrgb(GRASS["blade"]), width=int(w))
    if variant == 2:
        for _ in range(3):
            x, y = rnd.uniform(6, 26), rnd.uniform(6, 26)
            col = hexrgb(rnd.choice(GRASS["flower"]))
            for dx, dy in ((-1.2, 0), (1.2, 0), (0, -1.2), (0, 1.2)):
                d.ellipse([(x + dx - 1) * k, (y + dy - 1) * k, (x + dx + 1) * k, (y + dy + 1) * k], fill=col)
            d.ellipse([(x - 0.8) * k, (y - 0.8) * k, (x + 0.8) * k, (y + 0.8) * k], fill=hexrgb("#F2A93B"))
    if variant == 3:
        for _ in range(3):
            x, y, r = rnd.uniform(7, 25), rnd.uniform(7, 25), rnd.uniform(1.4, 2.4)
            d.ellipse([(x - r) * k, (y - r * 0.75) * k, (x + r) * k, (y + r * 0.75) * k],
                      fill=hexrgb("#A8ADB0"), outline=hexrgb("#5F6268"), width=int(0.7 * k))
    return im


def tex_dirt(scale, seed=0):
    im = _canvas(scale, TERRAINS["dirt"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    rnd = random.Random(2000 + seed)
    for _ in range(6):
        x, y, r = rnd.uniform(4, 28), rnd.uniform(4, 28), rnd.uniform(0.7, 1.4)
        d.ellipse([(x - r) * k, (y - r * 0.7) * k, (x + r) * k, (y + r * 0.7) * k], fill=hexrgb("#BF9960"))
    return im


def tex_road(scale, seed=0, marking=None):
    im = _canvas(scale, TERRAINS["road"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    rnd = random.Random(3000 + seed)
    for _ in range(5):
        x, y, r = rnd.uniform(4, 28), rnd.uniform(4, 28), rnd.uniform(0.4, 0.8)
        d.ellipse([(x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k], fill=hexrgb("#6A6D77"))
    w = hexrgb("#F2F2EE")
    if marking == "dash_h":
        d.rectangle([4 * k, 15 * k, 20 * k, 17 * k], fill=w)
    elif marking == "dash_v":
        d.rectangle([15 * k, 4 * k, 17 * k, 20 * k], fill=w)
    elif marking == "zebra_h":      # passage piéton sur une route horizontale : bandes verticales
        for x in (2, 10, 18, 26):
            d.rectangle([x * k, 0, (x + 4) * k, T * k], fill=w)
    elif marking == "zebra_v":
        for y in (2, 10, 18, 26):
            d.rectangle([0, y * k, T * k, (y + 4) * k], fill=w)
    return im


def tex_paving(scale, seed=0):
    im = _canvas(scale, TERRAINS["paving"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    c = hexrgb("#B7AC95")
    for row in range(8):
        y = row * 4
        d.line([(0, y * k), (T * k, y * k)], fill=c, width=int(0.6 * k))
        off = 4 if row % 2 else 0
        for x in range(off, T + 1, 8):
            d.line([(x * k, y * k), (x * k, (y + 4) * k)], fill=c, width=int(0.6 * k))
    return im


def tex_concrete(scale, seed=0):
    im = _canvas(scale, TERRAINS["concrete"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    c = hexrgb("#95989E")
    for v in (0, 16):
        d.line([(v * k, 0), (v * k, T * k)], fill=c, width=int(0.7 * k))
        d.line([(0, v * k), (T * k, v * k)], fill=c, width=int(0.7 * k))
    rnd = random.Random(4000 + seed)
    if seed % 3 == 1:     # fissure
        x, y = rnd.uniform(4, 10), rnd.uniform(4, 10)
        pts = [(x * k, y * k)]
        for _ in range(4):
            x += rnd.uniform(1.5, 3.5)
            y += rnd.uniform(-1.5, 3)
            pts.append((min(x, 28) * k, min(max(y, 3), 28) * k))
        d.line(pts, fill=hexrgb("#6F7278"), width=int(0.6 * k))
    if seed % 3 == 2:     # tache d'huile
        x, y = rnd.uniform(10, 22), rnd.uniform(10, 22)
        d.ellipse([(x - 4) * k, (y - 2.5) * k, (x + 4) * k, (y + 2.5) * k], fill=hexrgb("#8B8E95"))
        d.ellipse([(x - 2) * k, (y - 1.2) * k, (x + 2.5) * k, (y + 1.5) * k], fill=hexrgb("#7F828A"))
    return im


def tex_sidewalk(scale, seed=0):
    im = _canvas(scale, TERRAINS["sidewalk"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    c = hexrgb("#B8BCC3")
    for v in (0, 16):
        d.line([(v * k, 0), (v * k, T * k)], fill=c, width=int(0.8 * k))
        d.line([(0, v * k), (T * k, v * k)], fill=c, width=int(0.8 * k))
    rnd = random.Random(5000 + seed)
    for _ in range(3):
        x, y = rnd.uniform(3, 29), rnd.uniform(3, 29)
        d.ellipse([(x - 0.5) * k, (y - 0.5) * k, (x + 0.5) * k, (y + 0.5) * k], fill=hexrgb("#BFC3C9"))
    return im


def tex_water(scale, seed=0):
    """Eau unie : le jeu anime ses vaguelettes à part (fx_ripple)."""
    return _canvas(scale, TERRAINS["water"]["fill"])


def tex_sea(scale, seed=0):
    """La mer, unie elle aussi."""
    return _canvas(scale, TERRAINS["sea"]["fill"])


SILLONS = (8, 24)            # crêtes des buttes du champ, en px 1x dans la tuile : le jeu y plante ses rangs


def tex_field(scale, seed=0):
    """Champ labouré : deux buttes par tuile, à plat. La lumière vient d'en haut : le haut d'une butte est clair, la
    raie qui la sépare de la suivante est sombre, plus sombre encore au pied de la butte du dessus (son ombre). Le
    dessin est le même dans toutes les tuiles (les raies se raccordent, bords de champ compris) ; ce qui change d'un
    endroit à l'autre, ce sont les rangs de cultures, plantés par le jeu sur les crêtes (game.js : fieldDetails())."""
    im = _canvas(scale, TERRAINS["field"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    for crete in SILLONS:
        for y in (crete + 8, crete + 8 - T):               # la raie, sous la butte (32 = 0 : elle se referme)
            d.rectangle([0, (y - 1.8) * k, T * k, (y + 1.8) * k], fill=hexrgb("#9D6B3C"))
            d.rectangle([0, (y - 1.8) * k, T * k, (y - 0.7) * k], fill=hexrgb("#8A5A33"))
            d.rectangle([0, (y + 1.8) * k, T * k, (y + 2.9) * k], fill=hexrgb("#C08B55"))
    return im


def tex_forest(scale, seed=0):
    """Sous-bois : un vert sombre uni. Les taches de soleil, les fougères, la mousse, les brindilles… sont semées par
    le jeu (game.js : woodDetails()), comme les brins et les fleurs de l'herbe."""
    return _canvas(scale, TERRAINS["forest"]["fill"])


def tex_sand(scale, seed=0):
    """Sable : uni, à quelques grains près (les mêmes dans chaque tuile : il y en a peu). Coquillages, rides et
    traces sont l'affaire du jeu, comme les brins de l'herbe."""
    im = _canvas(scale, TERRAINS["sand"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    rnd = random.Random(7000)
    for i in range(5):
        x, y, r = rnd.uniform(3, 29), rnd.uniform(3, 29), rnd.uniform(0.35, 0.6)
        d.ellipse([(x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k], fill=hexrgb(("#E6CE90", "#FBEFC8")[i % 2]))
    return im


def tex_planks(scale, seed=0):
    """Planches : des lames de 4 px posées en travers de la promenade (leurs joints se raccordent d'une tuile à
    l'autre), de trois tons, avec ici et là un about de lame."""
    im = _canvas(scale, TERRAINS["planks"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    a, b, joint = hexrgb("#C4966A"), hexrgb("#AC7E52"), hexrgb("#7E5A3A")
    for i, x in enumerate(range(0, T, 4)):
        if (i * 5 + seed) % 3 == 0:
            d.rectangle([x * k, 0, (x + 4) * k, T * k], fill=a)
        elif (i * 3 + seed) % 4 == 0:
            d.rectangle([x * k, 0, (x + 4) * k, T * k], fill=b)
        d.line([(x * k, 0), (x * k, T * k)], fill=joint, width=int(0.55 * k))
        y = (i * 13 + 5 + seed * 7) % 28 + 2
        d.line([(x * k, y * k), ((x + 4) * k, y * k)], fill=joint, width=int(0.5 * k))
    return im


def _cellules(W, H, pas, seed, etire=1.0):
    """Des cellules irrégulières qui se répètent d'un bord à l'autre (W x H) : pour chaque pixel, la distance au
    germe le plus proche d'une grille bousculée et au suivant, leurs numéros, et l'écart au plus proche (dx, dy)."""
    rnd = np.random.RandomState(seed)
    gx, gy = max(1, round(W / pas[0])), max(1, round(H / pas[1]))
    px, py = W / gx, H / gy
    sx = (np.arange(gx)[None, :] + rnd.uniform(0.05, 0.95, (gy, gx))) * px
    sy = (np.arange(gy)[:, None] + rnd.uniform(0.05, 0.95, (gy, gx))) * py
    yy, xx = np.mgrid[0:H, 0:W]
    cj, ci = (yy // py).astype(int), (xx // px).astype(int)
    d1, d2 = np.full((H, W), 1e9), np.full((H, W), 1e9)
    n1, n2 = np.full((H, W), -1), np.full((H, W), -1)
    ox, oy = np.zeros((H, W)), np.zeros((H, W))
    for dj in range(-2, 3):
        for di in range(-2, 3):
            j, i = (cj + dj) % gy, (ci + di) % gx
            dx = (xx - sx[j, i] + W / 2) % W - W / 2
            dy = (yy - sy[j, i] + H / 2) % H - H / 2
            d, n = np.hypot(dx, dy * etire), j * gx + i
            pres = (d < d1) & (n != n1)
            second = ~pres & (d < d2) & (n != n1)
            d2, n2 = np.where(pres, d1, np.where(second, d, d2)), np.where(pres, n1, np.where(second, n, n2))
            ox, oy = np.where(pres, dx, ox), np.where(pres, dy, oy)
            d1, n1 = np.where(pres, d, d1), np.where(pres, n, n1)
    return d1, d2, n1, n2, ox, oy


_GRANDES = {}        # les grandes textures déjà dessinées : (nom, échelle, couleurs) -> image sur-échantillonnée


def _grande(nom, scale, dessin, *cle):
    """La grande texture `nom` (PHASES tuiles), dessinée une fois à demi-résolution du sur-échantillonnage (r pixels
    par unité) puis agrandie : dessin(W, H, r) -> image."""
    k = (nom, scale) + cle
    if k not in _GRANDES:
        r = scale * SS // 2
        im = dessin(PHASES[0] * T * r, PHASES[1] * T * r, r)
        _GRANDES[k] = im.resize((im.width * 2, im.height * 2), Image.BILINEAR).convert("RGBA")
    return _GRANDES[k]


def _decoupe(grande, scale, ph):
    n = T * scale * SS
    x, y = (ph or (0, 0))[0] * n, (ph or (0, 0))[1] * n
    return grande.crop((x, y, x + n, y + n))


def _dessin_roche(W, H, r):
    """La paroi : de grandes masses de roche inégales (leurs tons, leur face éclairée, en haut à gauche), fendues de
    failles ici et là seulement ; dedans, de petites facettes à peine marquées ; des coulures d'érosion debout ;
    quelques corniches (un trait clair dessus, de l'ombre dessous). Teintes de craie."""
    tons = np.array([hexrgb(t) for t in ("#F6F2E6", "#EAE3CF", "#DCD3BB", "#F0EBDB", "#CDC3A8", "#E3DCC6", "#D5CCB3")], dtype=float)
    d1, d2, n1, n2, ox, oy = _cellules(W, H, (37 * r, 25 * r), 3, 0.8)            # les grandes masses, plutôt debout
    a = tons[(n1 * 7 + 3) % len(tons)].copy()
    a += np.clip((-ox * 0.7 - oy * 0.7) / (15 * r), -1, 1)[..., None] * 16
    paire = (np.minimum(n1, n2) * 13 + np.maximum(n1, n2) * 7) % 10
    bord = (d2 - d1) / r
    a[(bord < 3.5) & (paire < 7)] *= 0.9                                        # le creux de la faille
    a[(bord < 1.1 + paire * 0.17) & (paire < 6)] = hexrgb("#7A725B")           # la faille : pas partout, plus ou moins large
    e1, e2, m1, m2, px, py = _cellules(W, H, (12 * r, 10 * r), 8)                 # les facettes
    a += (((m1 * 5) % 7) - 3)[..., None] * 2.2
    a += np.clip((-px * 0.6 - py * 0.8) / (6 * r), -1, 1)[..., None] * 5
    f = (np.minimum(m1, m2) * 11 + np.maximum(m1, m2) * 5) % 10
    a[((e2 - e1) / r < 0.8) & (f < 3)] *= 0.86
    t = 2 * np.pi * np.arange(W)[None, :] / W                                   # (des coulures qui se referment)
    coulure = np.sin(9 * t + 1.3) + 0.6 * np.sin(23 * t + 0.4) + 0.5 * np.sin(4 * t)
    a *= (1 - np.clip(coulure - 1.0, 0, 1) * 0.1)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    rnd = random.Random(3)
    for _ in range(PHASES[0] * PHASES[1] // 3 * 4):                             # corniches (loin des bords de l'image)
        w = rnd.uniform(11, 30) * r
        x, y = rnd.uniform(3 * r, W - w - 3 * r), rnd.uniform(3 * r, H - 5 * r)
        pts = [(x + w * i / 4, y + rnd.uniform(-1.2, 1.2) * r) for i in range(5)]
        d.line(pts, fill="#FFFFFF", width=max(1, round(1.5 * r)))
        d.line([(px + r, py + 2 * r) for px, py in pts], fill="#857D66", width=max(1, round(1.5 * r)))
    return im


def tex_chalk(scale, seed=0, ph=None):
    """La paroi de roche de la falaise : un morceau de la grande texture, d'après la place de la tuile."""
    return _decoupe(_grande("roche", scale, _dessin_roche), scale, ph)


LANDE = "#E2C24E"            # l'herbe du plateau : celle de la saison, jaunie de moitié par cette couleur


def _teinte_lande():
    g, j = hexrgb(GRASS["fill"]), hexrgb(LANDE)
    return "#" + "".join(f"{round((a + b) / 2):02X}" for a, b in zip(g, j))


def tex_heath(scale, seed=0):
    """La lande du plateau : l'herbe de la saison, jaunie, unie (le jeu y sème les cailloux : heathDetails())."""
    return _canvas(scale, _teinte_lande())


def tex_stairs(scale, seed=0):
    """L'escalier : quatre marches de pierre par tuile (elles se raccordent), le nez de marche à l'ombre."""
    im = _canvas(scale, TERRAINS["stairs"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    for y in range(0, T, 8):
        d.rectangle([0, y * k, T * k, (y + 1.6) * k], fill=hexrgb("#9C9480"))
        d.rectangle([0, (y + 1.6) * k, T * k, (y + 3.2) * k], fill=hexrgb("#F2ECDC"))
    return im


def _pierres(scale):
    """Les petites pierres du liséré : une texture de la taille d'une tuile, qui se répète."""
    def dessin(W, H, r):
        e1, e2, m1, _, px, py = _cellules(W, H, (7.5 * r, 6.5 * r), 11)
        a = np.array([hexrgb(t) for t in ("#F4EFE1", "#E3DCC6", "#D5CCB3")], dtype=float)[m1 % 3]
        a = a + np.clip((-px - py) / (4 * r), -1, 1)[..., None] * 10
        a[(e2 - e1) / r < 1.1] = hexrgb("#7A725B")
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    k = ("pierres", scale)
    if k not in _GRANDES:
        r = scale * SS // 2
        im = dessin(T * r, T * r, r)
        _GRANDES[k] = np.array(im.resize((im.width * 2, im.height * 2), Image.BILINEAR).convert("RGBA"))
    return _GRANDES[k]


def tex_lower_grass(scale, seed=0):
    return tex_grass(scale, seed % 4 if seed % 4 != 3 else 0, seed)


TEX = {"dirt": tex_dirt, "road": tex_road, "paving": tex_paving, "concrete": tex_concrete,
       "sidewalk": tex_sidewalk, "water": tex_water, "grass": tex_lower_grass, "field": tex_field,
       "forest": tex_forest, "sand": tex_sand, "planks": tex_planks, "chalk": tex_chalk, "heath": tex_heath,
       "stairs": tex_stairs, "sea": tex_sea}


def _tex(terrain, scale, seed=0, marking=None, ph=None):
    """La texture d'un terrain : celle de la route prend un marquage, celles qui se suivent une place (phase())."""
    if terrain == "road":
        return TEX[terrain](scale, seed, marking)
    return TEX[terrain](scale, seed, ph) if terrain in SUIVIES else TEX[terrain](scale, seed)


# ------------------------------------------------------------------ transitions
SUN = (0.6, 0.8)             # sens de la lumière au sol : elle vient d'en haut à gauche

# L'eau (lot 4 de la v2, d'après l'écran témoin). Distances au bord en px 1x : négatives sur la rive, positives
# dans l'eau. Sur la rive (seulement là où elle est de terre : BANKS), une lèvre d'herbe jaunie, du sable, du sable
# mouillé ; dans l'eau, des hauts-fonds clairs, une eau moyenne, puis le fond (la couleur des tuiles pleines). La
# berge du haut et de gauche jette une ombre sur les hauts-fonds ; celle du bas et de droite a un peu d'écume.
# Les limites des hauts-fonds et de l'eau moyenne suivent le champ des coins plutôt que la distance (qui n'est
# qu'approchée loin du bord, et saute d'une tuile à l'autre) : elles se raccordent, et s'arrêtent avant le bord
# de la tuile, à une demi-tuile du rivage.
BANKS = ("grass", "forest", "field", "dirt")
SHORE = dict(lip=("#93B35A", -4.4, -3.2), sand=("#EDDFAE", -3.6), wet=("#D9C68C", -1.2),
             shallow="#9FDFF0", mid="#78C9EC", mid_at=4.6, deep=9.5,
             shade=("#69B4D8", 0.85), foam=("#FFFFFF", 1.5, 2.5, 0.8))
# Le bord de mer, là où l'eau recouvre le sable : pas de lèvre d'herbe ; du sable mouillé (deux bandes : couleur,
# distance), des hauts-fonds, de l'écume tout le long du bord et une vague un peu plus loin (distances en px 1x).
PLAGE = dict(wet=("#E2CC8E", -5.5), wet2=("#CDB273", -2.2), shallow="#9FE3E0", mid="#5FC3DA", mid_at=5.0, deep=10.5,
             ecume=(-0.6, 1.4, -0.9, 0.95), vague=(5.2, 6.4, 0.35, 0.7))
# La falaise (BLOC). ombre : celle du bloc sur le sol d'en bas, le long de ses bords du bas et de droite (couleur,
# longueur en px 1x, opacité) ; pied : la paroi s'assombrit vers son pied ; lisere : la largeur du liséré de pierres
# du plateau, et son trait du dedans, côté herbe.
FALAISE = dict(ombre=("#22402E", 11, 0.36), pied=("#6E6650", 14, 0.5), lisere=6.5, dedans=("#8C8556", 1.0))


def _ease(t):
    """Interpolation adoucie entre deux coins (3t² - 2t³) : le champ arrive à plat sur les bords de la tuile, donc un
    contour les traverse toujours d'équerre. Une courbe d'angle repart ainsi dans l'axe du bord droit de la tuile
    voisine, sans cassure (avec une interpolation linéaire, elle le quittait de biais : un coude à chaque angle de
    mare ou de chemin). game.js fait le même calcul pour l'eau (waterVal())."""
    return t * t * (3 - 2 * t)


TREMBLE = 0.06               # bords naturels : de combien le champ est froissé (0 : des bords tirés à la règle)
NATURELS = ("dirt", "water", "sea", "forest", "field", "sand")   # chemins de terre, rives, sous-bois, champ, plage ; pas la voirie ni la falaise
EAUX = ("water", "sea")      # l'eau douce et la mer
RIVES = BANKS + ("sand",)    # là où le bord de l'eau est froissé (pas le long d'un quai)


FROISSES = 3                 # nombre de froissements différents : la tuile de base et FROISSES - 1 variantes


def _froisse(n, variante=0):
    """Le froissement des bords naturels (chemins, rives) : une ondulation du champ, nulle et à plat sur les quatre
    bords de la tuile, pour que le contour s'y raccorde toujours à celui de la tuile voisine, d'équerre. Sans lui,
    rives et chemins étaient lisses mais droits comme des règles. Plusieurs variantes, que le jeu tire de la position
    de la tuile (game.js : tileLook()) : la même ondulation répétée à chaque tuile faisait une dentelle."""
    x = (np.arange(n) + 0.5) / n
    X, Y = np.meshgrid(x, x)
    onde = (np.sin(2 * np.pi * X + 0.6) + np.sin(2 * np.pi * Y + 2.1) + 0.2 * np.sin(4 * np.pi * (X + Y)),
            -np.sin(2 * np.pi * X + 2.0) - np.sin(2 * np.pi * Y + 0.3) + 0.2 * np.sin(4 * np.pi * (X - Y) + 1.0),
            0.9 * np.sin(2 * np.pi * X + 4.4) + 0.9 * np.sin(2 * np.pi * Y + 3.6) + 0.5 * np.cos(2 * np.pi * (X + Y)))[variante]
    return np.sin(np.pi * X) ** 2 * np.sin(np.pi * Y) ** 2 * onde


# Les bords debout de la falaise (les côtés du plateau et de sa paroi) ne sont pas tirés au cordeau (Christophe :
# « rendre moins droite et rigide la bordure verticale ») : une ondulation du champ qui ne dépend que de la hauteur
# dans la tuile. Elle est nulle et à plat en haut et en bas de la tuile (les contours se raccordent en douceur), et
# nulle à mi-hauteur : un bord couché, qui passe là, ne bouge pas. Une paire d'amplitudes par variante.
ONDES = ((0.14, 0.07), (-0.12, 0.09), (0.09, -0.10))
ONDULES = ("chalk", "heath")


def _ondule(n, variante=0):
    y = (np.arange(n) + 0.5) / n
    a, b = ONDES[variante % len(ONDES)]
    f = np.sin(np.pi * y) ** 2 * (a * np.sin(2 * np.pi * y) + b * np.sin(4 * np.pi * y))
    return np.repeat(f[:, None], n, axis=1)


def _field(bits, n, light=False, tremble=0.0, variante=0, ondule=False):
    """Champ des 4 coins (interpolation adoucie : _ease) et distance signée approx. au contour 0.5 (en px
    sur-échantillonnés). tremble : froissement du champ (_froisse), pour un bord naturel ; ondule : l'ondulation des
    bords debout de la falaise (_ondule).
    light : rend aussi l'éclairage du bord (-1..1 : positif là où l'intérieur est à l'ombre du bord, c'est-à-dire
    le long des bords du haut et de gauche) et le champ lui-même (0..1, continu d'une tuile à sa voisine)."""
    nw, ne, sw, se = [(bits >> i) & 1 for i in range(4)]
    u = _ease((np.arange(n) + 0.5) / n)
    U, V = np.meshgrid(u, u)
    v = nw * (1 - U) * (1 - V) + ne * U * (1 - V) + sw * (1 - U) * V + se * U * V
    if tremble and bits not in (0, 15):
        v = v + tremble * _froisse(n, variante)
    if ondule and bits not in (0, 15):
        # seulement près du contour (loin de lui, le champ reste à plat : sinon la distance approchée s'affole), et
        # seulement là où le bord est debout (un bord couché ondulé se dédoublait)
        gy0, gx0 = np.gradient(v)
        v = v + _ondule(n, variante) * 4 * v * (1 - v) * gx0 ** 2 / (gx0 ** 2 + gy0 ** 2 + 1e-12)
    gy, gx = np.gradient(v)
    g = np.sqrt(gx ** 2 + gy ** 2)
    dist = (v - 0.5) / np.maximum(g, 1e-6)
    dist[g < 1e-6] = np.where(v[g < 1e-6] > 0.5, 1e6, -1e6)
    if light:
        return dist, (gx * SUN[0] + gy * SUN[1]) / np.maximum(g, 1e-6), v
    return dist


def _blend(out, color, alpha):
    """Pose `color` sur `out` avec l'opacité `alpha` (tableau 0..1)."""
    a = np.clip(alpha, 0, 1)[..., None]
    out[..., :3] = out[..., :3] * (1 - a) + np.array(hexrgb(color)) * a


def _part_mer(corners, n):
    """Dans une tuile où la mer et l'eau douce se rejoignent : la part de mer en chaque point (0 l'eau douce, 1 la
    mer), d'après les seuls coins d'eau, chacun pesé comme dans le champ des coins. Le long d'un bord de la tuile,
    elle ne dépend que des deux coins de ce bord (un seul coin d'eau : sa valeur, d'un bout à l'autre) : elle se
    raccorde donc à la tuile voisine, qu'elle soit mêlée elle aussi, toute de mer ou toute d'eau douce."""
    u = (np.arange(n) + 0.5) / n                      # (en ligne droite, sans _ease : la pente la plus douce d'un bord
    U, V = np.meshgrid(u, u)                          # à l'autre — adoucie, la jonction faisait une tache)
    poids = ((1 - U) * (1 - V), U * (1 - V), (1 - U) * V, U * V)
    num = sum(w for w, c in zip(poids, corners) if c == "sea")
    den = sum(w for w, c in zip(poids, corners) if c in EAUX)
    return num / np.maximum(den, 1e-9)


def _teinte(out, masque, a, b, m):
    """Dans `masque`, la couleur a (l'eau douce) fondue vers b (la mer) selon la part de mer m."""
    a, b = np.array(hexrgb(a), dtype=float), np.array(hexrgb(b), dtype=float)
    out[..., :3][masque] = a + (b - a) * m[masque][:, None]
    out[..., 3][masque] = 255


def _shore(out, bits, below, scale, tremble=0.0, variante=0, mer=False, vrai=None):
    """Rive et hauts-fonds de l'eau (SHORE) autour des coins `bits`, par-dessus `out` où l'eau est déjà posée.
    mer : la mer (ses hauts-fonds sont ceux de PLAGE ; sur le sable, le bord de mer) — vrai, faux, ou la part de
    mer en chaque point (_part_mer) là où la mer et l'eau douce se rejoignent : tout ce qui les distingue (largeur
    du sable mouillé, couleurs et largeurs des hauts-fonds, écume) passe alors de l'une à l'autre en continu.
    vrai : dans une tuile composée, les seuls coins qui sont vraiment de l'eau (`bits` compte aussi ceux des
    terrains posés par-dessus : un quai, les planches). Entre la rive et ce terrain, l'eau finit en pointe au bord
    de la tuile : la rive (sable mouillé, lèvre, écume) s'amincit avec elle au lieu d'être coupée net."""
    n, k = T * scale * SS, scale * SS
    dist, lum, v = _field(bits, n, light=True, tremble=tremble, variante=variante)
    d = dist / k                                      # en px 1x
    m = mer if isinstance(mer, np.ndarray) else np.full((n, n), 1.0 if mer else 0.0)
    band = lambda a, b: (d >= a) & (d < b)
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    motif = (np.sin(2 * np.pi * (3 * U + V)) + 0.7 * np.sin(2 * np.pi * (2 * V - 5 * U) + 1.0)
             + 0.5 * np.sin(2 * np.pi * (7 * U + 4 * V) + 2.0))
    plage = below == "sand"
    f = 1.0                                           # la part de vraie eau : 1 le long d'une rive libre
    if vrai is not None and vrai != bits:
        vb, vt = (_field(b, n, light=True)[2] for b in (bits, vrai))
        f = _ease(np.clip(vt / np.maximum(vb, 1e-6) / 0.6, 0, 1))
    if below in BANKS:
        col, a, b = SHORE["lip"]
        out[band(a * f, b * f)] = hexrgb(col) + (255,)
        for key in ("sand", "wet"):
            col, a = SHORE[key]
            out[band(a * f, 0)] = hexrgb(col) + (255,)
    elif plage:                                       # du sable mouillé : large au bord de mer (PLAGE), étroit là où
        for key in ("wet", "wet2"):                   # la rivière traverse la plage
            col, a = PLAGE[key]
            out[band(a * (0.6 + 0.4 * m) * f, 0)] = hexrgb(col) + (255,)
    # les hauts-fonds : ceux de la mer (PLAGE, le long d'un quai ou de l'herbe aussi) ou de l'eau douce (SHORE)
    niveau = lambda fonds, key: float(_ease(0.5 + fonds[key] / T))                 # niveaux du champ, en ligne droite
    v1, v2 = (niveau(SHORE, key) + (niveau(PLAGE, key) - niveau(SHORE, key)) * m for key in ("mid_at", "deep"))
    shallow = (v >= 0.5) & (v < v1)
    _teinte(out, shallow, SHORE["shallow"], PLAGE["shallow"], m)
    _teinte(out, (v >= v1) & (v < v2), SHORE["mid"], PLAGE["mid"], m)
    douce = 1 - m if plage else 1.0                   # (au bord de mer, sur le sable : ni ombre de berge ni tirets)
    col, a = SHORE["shade"]
    _blend(out, col, shallow * (d >= a) * (lum * 6 - 0.6) * douce)
    # écume : des tirets inégaux, tirés d'un motif qui se répète d'une tuile à l'autre (ils se raccordent)
    col, a, b, op = SHORE["foam"]
    _blend(out, col, band(a, b) * np.clip(-lum * 6 - 0.6, 0, 1) * (motif > 0.55) * op * douce * f)
    if plage:                                         # le bord de mer : de l'écume tout le long, une vague plus loin
        for key in ("ecume", "vague"):
            a, b, seuil, op = PLAGE[key]
            _blend(out, "#FFFFFF", band(a, b) * (motif > seuil) * op * m * f)


def _ombre_bloc(out, bloc, scale, variante=0):
    """L'ombre du bloc de la falaise (coins `bloc`) sur le sol d'en bas, le long de ses bords du bas et de droite."""
    n, k = T * scale * SS, scale * SS
    dist, lum, _ = _field(bloc, n, light=True, variante=variante, ondule=True)
    d = dist / k
    col, L, op = FALAISE["ombre"]
    _blend(out, col, (d > -L) * (d < 0) * np.clip(-lum * 3, 0, 1) * np.clip((L + d) / 2.5, 0, 1) * op)


def _layer(out, terrain, bits, below, scale, seed=0, marking=None, variante=0, propres=None, ph=None, bloc=None, mer=None):
    """Pose `terrain` sur `out` (tableau sur-échantillonné) dans les coins `bits`, avec le style de la paire
    (terrain, below) : liseré et contour ; pour l'eau, la rive et les hauts-fonds (_shore). Dans une tuile composée :
    propres, les seuls coins qui sont vraiment de ce terrain (`bits` compte aussi ceux des terrains posés par-dessus,
    sous lesquels il passe) ; ph, la place de la tuile dans les grandes textures ; bloc, les coins du bloc de la
    falaise, donnés à son premier terrain posé : il en dessine l'ombre et, pour la paroi, le pied ; mer, pour l'eau
    d'une tuile où la mer et l'eau douce se rejoignent : la part de mer en chaque point (_part_mer)."""
    n = T * scale * SS
    k = scale * SS
    spec = dict(TERRAINS[terrain])
    spec.update(PAIR_STYLE.get((terrain, below), {}))
    ter = np.array(_tex(terrain, scale, seed, marking, ph))
    if mer is not None:                               # l'eau douce et la mer, fondues l'une dans l'autre
        ter = _eaux(scale, mer)
    tremble = TREMBLE if terrain in NATURELS and (terrain not in EAUX or below in RIVES) else 0     # (pas le long d'un quai)
    onde = terrain in ONDULES
    dist = _field(bits, n, tremble=tremble, variante=variante, ondule=onde)
    if bloc is not None:
        _ombre_bloc(out, bloc, scale, variante)
    inside = dist >= 0
    out[inside] = ter[inside]
    if spec.get("cliff"):                             # la paroi : plus sombre vers son pied (le bord du bas du bloc)
        db, _, v = _field(bits if bloc is None else bloc, n, light=True, variante=variante, ondule=True)
        gy, gx = np.gradient(v)
        ny = gy / np.maximum(np.sqrt(gx ** 2 + gy ** 2), 1e-6)
        col, L, op = FALAISE["pied"]
        d = db / k
        _blend(out, col, inside * (d >= 0) * (d < L) * np.clip((-ny - 0.35) * 2.5, 0, 1) * np.clip(1 - d / L, 0, 1) * op)
    elif spec.get("lisere"):                          # le plateau : son liséré de pierres, le long de ses seuls bords
        d = _field(bits if propres is None else propres, n, variante=variante, ondule=True) / k
        L = FALAISE["lisere"]
        bande = (d >= 0) & (d < L)
        out[bande] = _pierres(scale)[bande]
        col, w = FALAISE["dedans"]
        out[(d >= L - w) & (d < L)] = hexrgb(col) + (255,)
        out[(d >= 0) & (d < spec["out_w"])] = hexrgb(spec["out"]) + (255,)
        return
    elif spec.get("shore"):
        _shore(out, bits, below, scale, tremble, variante, mer=bool(spec.get("mer")) if mer is None else mer, vrai=propres)
    else:
        edge = (dist >= spec["out_w"] * k) & (dist < (spec["out_w"] + spec["edge_w"]) * k)
        out[edge] = hexrgb(spec["edge"]) + (255,)
    outline = (dist >= 0) & (dist < spec["out_w"] * k)
    if mer is not None:
        _teinte(out, outline, TERRAINS["water"]["out"], TERRAINS["sea"]["out"], mer)
    else:
        out[outline] = hexrgb(spec["out"]) + (255,)


def _eaux(scale, m):
    """L'eau d'une tuile où la mer et l'eau douce se rejoignent : chacune sa couleur, fondues selon la part de mer."""
    a, b = (np.array(_tex(t, scale), dtype=float) for t in EAUX)
    return a + (b - a) * m[..., None]


def _finish(out, scale):
    return Image.fromarray(out.astype(np.uint8)).resize((T * scale, T * scale), Image.LANCZOS)


def transition(terrain, bits, scale, seed=0, marking=None, lower="grass", variante=0):
    """Tuile de transition : `terrain` (dessus) dans les coins `bits`, `lower` ailleurs. variante : un autre
    froissement de son bord, s'il est naturel (_froisse)."""
    out = np.array(_tex(lower, scale, seed))
    _layer(out, terrain, bits, lower, scale, seed, marking, variante)
    return _finish(out, scale)


def needs_composite(corners):
    """Vrai si la tuile mêle trois terrains, ou deux qui n'ont pas de paire dans PAIRS : `resolve()` ne saurait pas
    la dessiner sans remplacer un terrain par un autre (encoches carrées au bout des chemins, des trottoirs…). Vrai
    aussi pour la tuile pleine d'un terrain sans rangée dans le tileset (les planches, l'escalier), et pour toute
    tuile dont la texture dépend de sa place (SUIVIES : la paroi, la lande)."""
    kinds = sorted(set(corners), key=PRIORITY.index)
    if any(c in SUIVIES for c in kinds):
        return True
    if len(kinds) == 1:
        return kinds[0] != "grass" and (kinds[0], "grass") not in PAIRS
    return len(kinds) >= 3 or (kinds[1], kinds[0]) not in PAIRS


def composite_seed(corners):
    """Graine de la texture d'une tuile composée : la même pour les mêmes coins, où que la tuile soit dans la carte
    (l'éditeur de carte la redessine à la demande, comme dans le jeu)."""
    return sum(_GRAINES.index(c) * 9 ** i for i, c in enumerate(corners[:4])) % 97


def composite(corners, scale, seed=0, ph=None, variante=0):
    """Tuile composée (voir needs_composite) : le terrain le plus bas en fond, puis chaque terrain par-dessus le
    précédent, dans l'ordre de PRIORITY, sur les coins où il est ou bien un terrain plus haut (il passe ainsi sous les
    suivants). Les contours viennent du même champ de coins que les tuiles voisines : ils s'y raccordent. corners :
    les quatre coins, suivis de la place de la tuile (phase()) si sa texture en dépend ; ph : cette place."""
    if len(corners) > 4:
        corners, ph = corners[:4], tuple(corners[4:])
    if ph:                                            # (une ondulation des bords debout par place : tuiles voisines différentes)
        variante = (ph[0] * 3 + ph[1] * 5) % len(ONDES)
    kinds = sorted(set(corners), key=PRIORITY.index)
    # L'embouchure : là où la mer et l'eau douce se rejoignent, elles ne font qu'une seule eau, posée d'un coup —
    # une seule rive, dont les couleurs passent de l'une à l'autre (_part_mer). Posées l'une après l'autre (la rive
    # d'eau douce, puis un voile de mer), la tuile ne se raccordait à aucune de ses voisines.
    mer = None
    if all(e in kinds for e in EAUX):
        mer = _part_mer(corners, T * scale * SS)
        kinds.remove("sea")
    out = np.array(_tex(kinds[0], scale, seed, None, ph)) if not (mer is not None and kinds[0] == "water") else _eaux(scale, mer)
    vu = kinds[0] in BLOC                             # le bloc de la falaise a-t-il déjà un terrain posé ?
    for below, t in zip(kinds, kinds[1:]):
        bits = sum(1 << i for i, c in enumerate(corners) if PRIORITY.index(c) >= PRIORITY.index(t))
        bloc = None
        if t in BLOC and not vu:
            bloc, vu = sum(1 << i for i, c in enumerate(corners) if c in BLOC), True
        _layer(out, t, bits, below, scale, seed, variante=variante, ph=ph, bloc=bloc,
               propres=sum(1 << i for i, c in enumerate(corners) if c == t or (mer is not None and c in EAUX and t == "water")),
               mer=mer if t == "water" else None)
    return _finish(out, scale)


def full_tile(terrain, scale, seed=0):
    if terrain == "grass":
        return grass_tile(scale, 0)
    return transition(terrain, 15, scale, seed=seed)


def grass_tile(scale, variant):
    return tex_grass(scale, variant, variant).resize((T * scale, T * scale), Image.LANCZOS)


def road_marking(scale, marking):
    return tex_road(scale, 0, marking).resize((T * scale, T * scale), Image.LANCZOS)


# ------------------------------------------------------------------ détails (tuiles transparentes)
def _overlay(scale, draw_fn):
    n = T * scale * SS
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(im), scale * SS)
    return im.resize((T * scale, T * scale), Image.LANCZOS)


def _ov_arrow(d, k):
    w = hexrgb("#F2F2EE")
    d.rectangle([14.5 * k, 12 * k, 17.5 * k, 28 * k], fill=w)
    d.polygon([(9 * k, 13 * k), (16 * k, 4 * k), (23 * k, 13 * k)], fill=w)


def _ov_manhole(d, k):
    d.ellipse([7 * k, 7 * k, 25 * k, 25 * k], fill=hexrgb("#4A4D55"), outline=hexrgb("#2F3137"), width=int(1 * k))
    for y in (11, 14, 17, 20):
        d.line([(10 * k, y * k), (22 * k, y * k)], fill=hexrgb("#3A3D44"), width=int(0.9 * k))


def _ov_grate(d, k):
    d.rectangle([8 * k, 11 * k, 24 * k, 21 * k], fill=hexrgb("#3A3D44"), outline=hexrgb("#2A2C31"), width=int(1 * k))
    for x in range(10, 24, 3):
        d.line([(x * k, 12 * k), (x * k, 20 * k)], fill=hexrgb("#7C808A"), width=int(1 * k))


def _ov_puddle(d, k):
    d.ellipse([5 * k, 10 * k, 27 * k, 23 * k], fill=hexrgb("#7FA8C4") + (200,))
    d.ellipse([9 * k, 12 * k, 17 * k, 15 * k], fill=hexrgb("#B9D8EA") + (200,))


def _ov_oil(d, k):
    d.ellipse([7 * k, 10 * k, 25 * k, 22 * k], fill=(40, 40, 50, 90))
    d.ellipse([12 * k, 13 * k, 20 * k, 18 * k], fill=(40, 40, 50, 70))


def _ov_cracks(d, k):
    c = (40, 40, 45, 150)
    d.line([(6 * k, 8 * k), (12 * k, 13 * k), (11 * k, 19 * k), (17 * k, 24 * k), (25 * k, 25 * k)], fill=c, width=int(0.8 * k))
    d.line([(12 * k, 13 * k), (19 * k, 11 * k), (24 * k, 6 * k)], fill=c, width=int(0.7 * k))


def _ov_leaves(d, k):
    rnd = random.Random(77)
    for _ in range(7):
        x, y = rnd.uniform(5, 27), rnd.uniform(5, 27)
        col = hexrgb(rnd.choice(("#E2A13B", "#C8553D", "#E8C547")))
        d.ellipse([(x - 1.8) * k, (y - 1) * k, (x + 1.8) * k, (y + 1) * k], fill=col, outline=hexrgb("#8A5A3A"), width=int(0.4 * k))


def _ov_flowers(d, k):
    rnd = random.Random(12)
    for _ in range(5):
        x, y = rnd.uniform(6, 26), rnd.uniform(6, 26)
        col = hexrgb(rnd.choice(GRASS["flower"]))
        for dx, dy in ((-1.2, 0), (1.2, 0), (0, -1.2), (0, 1.2)):
            d.ellipse([(x + dx - 1) * k, (y + dy - 1) * k, (x + dx + 1) * k, (y + dy + 1) * k], fill=col)
        d.ellipse([(x - 0.8) * k, (y - 0.8) * k, (x + 0.8) * k, (y + 0.8) * k], fill=hexrgb("#F2A93B"))


def _ov_tuft(d, k):
    c = hexrgb("#4E9A47")
    for x0, h in ((11, 9), (14, 12), (17, 10), (20, 8), (15.5, 7)):
        d.polygon([((x0 - 1.3) * k, 24 * k), ((x0 + 1.3) * k, 24 * k), ((x0 + 0.6) * k, (24 - h) * k)], fill=c)
    d.ellipse([9 * k, 22.5 * k, 23 * k, 25.5 * k], fill=hexrgb("#5FA852"))


def _ov_pebbles(d, k):
    rnd = random.Random(5)
    for _ in range(5):
        x, y, r = rnd.uniform(6, 26), rnd.uniform(6, 26), rnd.uniform(1, 2)
        d.ellipse([(x - r) * k, (y - r * 0.75) * k, (x + r) * k, (y + r * 0.75) * k],
                  fill=hexrgb("#A8ADB0"), outline=hexrgb("#5F6268"), width=int(0.6 * k))


def _ov_park_line(d, k):
    d.rectangle([0, 0, 1.6 * k, T * k], fill=hexrgb("#F2F2EE"))


def _ov_hazard(d, k):
    d.rectangle([0, 12 * k, T * k, 20 * k], fill=hexrgb("#F2C14E"))
    for x in range(-8, 32, 8):
        d.polygon([(x * k, 20 * k), ((x + 4) * k, 20 * k), ((x + 12) * k, 12 * k), ((x + 8) * k, 12 * k)],
                  fill=hexrgb("#2B2B33"))


def _ov_paws(d, k):
    c = (90, 60, 40, 150)
    for x, y in ((10, 24), (20, 16), (11, 8)):
        d.ellipse([(x - 2) * k, (y - 1.5) * k, (x + 2) * k, (y + 2) * k], fill=c)
        for dx, dy in ((-2.2, -2.6), (-0.7, -3.4), (0.9, -3.4), (2.3, -2.6)):
            d.ellipse([(x + dx - 0.7) * k, (y + dy - 0.8) * k, (x + dx + 0.7) * k, (y + dy + 0.8) * k], fill=c)


def _ov_dig(d, k):
    d.ellipse([7 * k, 13 * k, 25 * k, 25 * k], fill=hexrgb("#B98F58"), outline=hexrgb("#8A6A3E"), width=int(0.8 * k))
    d.ellipse([11 * k, 16 * k, 21 * k, 22 * k], fill=hexrgb("#6B4E2C"))
    for x, y in ((6, 11), (25, 12), (23, 26)):
        d.ellipse([(x - 1.5) * k, (y - 1) * k, (x + 1.5) * k, (y + 1) * k], fill=hexrgb("#B98F58"))


def _ov_stop_h(d, k):
    d.rectangle([0, 26 * k, T * k, 30 * k], fill=hexrgb("#F2F2EE"))


def _ov_stop_v(d, k):
    d.rectangle([2 * k, 0, 6 * k, T * k], fill=hexrgb("#F2F2EE"))


OVERLAYS = [("ligne d'arrêt H", _ov_stop_h), ("ligne d'arrêt V", _ov_stop_v), ("flèche au sol", _ov_arrow),
            ("plaque d'égout", _ov_manhole), ("grille d'évacuation", _ov_grate), ("flaque", _ov_puddle),
            ("tache d'huile", _ov_oil), ("fissures", _ov_cracks), ("feuilles mortes", _ov_leaves),
            ("fleurs", _ov_flowers), ("touffe d'herbe", _ov_tuft), ("cailloux", _ov_pebbles),
            ("ligne de parking", _ov_park_line), ("bande de danger", _ov_hazard),
            ("traces de pattes", _ov_paws), ("trou creusé (trésor)", _ov_dig)]


def overlay(scale, i):
    return _overlay(scale, OVERLAYS[i][1])


# ------------------------------------------------------------------ planche
# La tuile 0 est toujours vide. Disposition, 16 colonnes :
#   ligne 0      : [vide] herbe x4, marquages x4, variantes pleines x7
#   lignes 1..   : une paire (dessus/dessous) par ligne (PAIRS), colonne = bits de coins (0..15)
#   ligne suivante (OVERLAY_ROW) : détails transparents à poser sur un 2e calque de tuiles
COLS = 16
# L'image du tileset, elle, a deux fois plus de colonnes (la tuile n° i est en (i % LARGEUR, i // LARGEUR)) : deux
# fois moins haute, elle reste sous les 4096 px en x4 quand les tuiles composées de la côte s'ajoutent.
LARGEUR = 32
ROW0 = ["(vide)", "herbe", "herbe + brins", "herbe + fleurs", "herbe + cailloux",
        "route ligne H", "route ligne V", "passage piéton (route H)", "passage piéton (route V)",
        "terre var. 1", "terre var. 2", "route var. 1", "route var. 2",
        "pavés var. 1", "béton var. 1", "béton var. 2"]
OVERLAY_ROW = 1 + len(PAIRS)
# Variantes des transitions à bord naturel (un autre froissement, mêmes coins) : FROISSES - 1 rangées par paire,
# après la ligne des détails. La carte ne les connaît pas : le jeu les choisit en peignant le sol (MAP.tileAlt).
ALTERNEES = [p for p in PAIRS if p[0] in NATURELS and (p[0] not in EAUX or p[1] in RIVES)]
ALT_ROW = OVERLAY_ROW + 1
COMPOSITE_BASE = (ALT_ROW + len(ALTERNEES) * (FROISSES - 1)) * COLS      # tuiles composées, après les variantes


def alternees():
    """rangée d'une paire dans le tileset -> les rangées de ses variantes."""
    return {1 + PAIRS.index(p): [ALT_ROW + i * (FROISSES - 1) + v for v in range(FROISSES - 1)] for i, p in enumerate(ALTERNEES)}


def tileset(scale, composites=()):
    """composites : coins (NO, NE, SO, SE) des tuiles composées, ajoutées à partir de l'index COMPOSITE_BASE."""
    ts = T * scale
    total = COMPOSITE_BASE + len(composites)
    sheet = Image.new("RGBA", (LARGEUR * ts, -(-total // LARGEUR) * ts), (0, 0, 0, 0))
    place = lambda i: ((i % LARGEUR) * ts, (i // LARGEUR) * ts)       # où va la tuile n° i
    row0 = [None] + [grass_tile(scale, v) for v in range(4)]
    row0 += [road_marking(scale, m) for m in ("dash_h", "dash_v", "zebra_h", "zebra_v")]
    row0 += [transition(t, 15, scale, seed=s_) for t, s_ in
             (("dirt", 1), ("dirt", 2), ("road", 1), ("road", 2), ("paving", 1), ("concrete", 1), ("concrete", 2))]
    for i, im in enumerate(row0):
        if im is not None:
            sheet.paste(im, place(i))
    for r, (up, lo) in enumerate(PAIRS):
        for bits in range(16):
            sheet.paste(transition(up, bits, scale, seed=bits, lower=lo), place((1 + r) * COLS + bits))
    for i in range(len(OVERLAYS)):
        sheet.paste(overlay(scale, i), place(OVERLAY_ROW * COLS + i))
    for r, alts in alternees().items():
        up, lo = PAIRS[r - 1]
        for v, row in enumerate(alts):
            for bits in range(1, 15):
                sheet.paste(transition(up, bits, scale, seed=bits, lower=lo, variante=v + 1), place(row * COLS + bits))
    for i, cs in enumerate(composites):
        j = COMPOSITE_BASE + i
        sheet.paste(composite(cs, scale, seed=composite_seed(cs)), place(j))
    return sheet


def tile_index(upper, bits, lower="grass"):
    """Index d'une tuile de transition dans le tileset."""
    return (1 + PAIRS.index((upper, lower))) * COLS + bits


def resolve(corners):
    """
    corners : 4 terrains (NO, NE, SO, SE) -> (dessus, dessous, bits) pour la tuile.
    Le terrain le plus haut passe dessus ; le dessous est le terrain le plus fréquent parmi
    les autres coins (à égalité, le plus bas). Un éventuel 3e terrain est remplacé par le dessous.
    """
    kinds = sorted(set(corners), key=PRIORITY.index)
    if len(kinds) == 1:
        return kinds[0], kinds[0], 15
    up = kinds[-1]
    others = [c for c in corners if c != up]
    lo = min(set(others), key=lambda c: (-others.count(c), PRIORITY.index(c)))
    if (up, lo) not in PAIRS:
        lo = "grass"
    bits = sum(1 << i for i, c in enumerate(corners) if c == up)
    return up, lo, bits

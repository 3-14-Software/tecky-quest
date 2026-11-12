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
}

# Paires disponibles (dessus, dessous), dans l'ordre des lignes de la planche.
# Les 4 premières gardent les index de la version précédente.
PAIRS = [("dirt", "grass"), ("road", "grass"), ("paving", "grass"), ("concrete", "grass"),
         ("sidewalk", "grass"), ("road", "sidewalk"), ("water", "grass"), ("paving", "sidewalk"),
         ("road", "dirt"), ("road", "concrete"), ("concrete", "sidewalk"), ("field", "grass"),
         ("forest", "grass"), ("dirt", "forest")]

# Retouches de style pour certaines paires (sinon : style du terrain du dessus)
PAIR_STYLE = {
    ("road", "dirt"): dict(edge="#74777F", edge_w=1.2),
    ("road", "concrete"): dict(edge="#74777F", edge_w=1.2),
}

# Priorité d'empilement (utile pour la génération automatique)
PRIORITY = ["grass", "forest", "field", "dirt", "water", "sidewalk", "concrete", "paving", "road"]


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


def tex_lower_grass(scale, seed=0):
    return tex_grass(scale, seed % 4 if seed % 4 != 3 else 0, seed)


TEX = {"dirt": tex_dirt, "road": tex_road, "paving": tex_paving, "concrete": tex_concrete,
       "sidewalk": tex_sidewalk, "water": tex_water, "grass": tex_lower_grass, "field": tex_field,
       "forest": tex_forest}


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


def _ease(t):
    """Interpolation adoucie entre deux coins (3t² - 2t³) : le champ arrive à plat sur les bords de la tuile, donc un
    contour les traverse toujours d'équerre. Une courbe d'angle repart ainsi dans l'axe du bord droit de la tuile
    voisine, sans cassure (avec une interpolation linéaire, elle le quittait de biais : un coude à chaque angle de
    mare ou de chemin). game.js fait le même calcul pour l'eau (waterVal())."""
    return t * t * (3 - 2 * t)


TREMBLE = 0.06               # bords naturels : de combien le champ est froissé (0 : des bords tirés à la règle)
NATURELS = ("dirt", "water", "forest", "field")       # chemins de terre, rives, sous-bois, champ ; pas la voirie


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


def _field(bits, n, light=False, tremble=0.0, variante=0):
    """Champ des 4 coins (interpolation adoucie : _ease) et distance signée approx. au contour 0.5 (en px
    sur-échantillonnés). tremble : froissement du champ (_froisse), pour un bord naturel.
    light : rend aussi l'éclairage du bord (-1..1 : positif là où l'intérieur est à l'ombre du bord, c'est-à-dire
    le long des bords du haut et de gauche) et le champ lui-même (0..1, continu d'une tuile à sa voisine)."""
    nw, ne, sw, se = [(bits >> i) & 1 for i in range(4)]
    u = _ease((np.arange(n) + 0.5) / n)
    U, V = np.meshgrid(u, u)
    v = nw * (1 - U) * (1 - V) + ne * U * (1 - V) + sw * (1 - U) * V + se * U * V
    if tremble and bits not in (0, 15):
        v = v + tremble * _froisse(n, variante)
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


def _shore(out, bits, below, scale, tremble=0.0, variante=0):
    """Rive et hauts-fonds de l'eau (SHORE) autour des coins `bits`, par-dessus `out` où l'eau est déjà posée."""
    n, k = T * scale * SS, scale * SS
    dist, lum, v = _field(bits, n, light=True, tremble=tremble, variante=variante)
    d = dist / k                                      # en px 1x
    band = lambda a, b: (d >= a) & (d < b)
    if below in BANKS:
        col, a, b = SHORE["lip"]
        out[band(a, b)] = hexrgb(col) + (255,)
        for key in ("sand", "wet"):
            col, a = SHORE[key]
            out[band(a, 0)] = hexrgb(col) + (255,)
    v1, v2 = (float(_ease(0.5 + SHORE[key] / T)) for key in ("mid_at", "deep"))    # niveaux du champ, en ligne droite
    shallow = (v >= 0.5) & (v < v1)
    out[shallow] = hexrgb(SHORE["shallow"]) + (255,)
    out[(v >= v1) & (v < v2)] = hexrgb(SHORE["mid"]) + (255,)
    col, a = SHORE["shade"]
    _blend(out, col, shallow * (d >= a) * (lum * 6 - 0.6))
    # écume : des tirets inégaux, tirés d'un motif qui se répète d'une tuile à l'autre (ils se raccordent)
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    motif = (np.sin(2 * np.pi * (3 * U + V)) + 0.7 * np.sin(2 * np.pi * (2 * V - 5 * U) + 1.0)
             + 0.5 * np.sin(2 * np.pi * (7 * U + 4 * V) + 2.0))
    col, a, b, op = SHORE["foam"]
    _blend(out, col, band(a, b) * np.clip(-lum * 6 - 0.6, 0, 1) * (motif > 0.55) * op)


def _layer(out, terrain, bits, below, scale, seed=0, marking=None, variante=0):
    """Pose `terrain` sur `out` (tableau sur-échantillonné) dans les coins `bits`, avec le style de la paire
    (terrain, below) : liseré et contour ; pour l'eau, la rive et les hauts-fonds (_shore)."""
    n = T * scale * SS
    k = scale * SS
    spec = dict(TERRAINS[terrain])
    spec.update(PAIR_STYLE.get((terrain, below), {}))
    ter = np.array(TEX[terrain](scale, seed, marking) if terrain == "road" else TEX[terrain](scale, seed))
    tremble = TREMBLE if terrain in NATURELS and (terrain != "water" or below in BANKS) else 0     # (pas le long d'un quai)
    dist = _field(bits, n, tremble=tremble, variante=variante)
    inside = dist >= 0
    out[inside] = ter[inside]
    if spec.get("shore"):
        _shore(out, bits, below, scale, tremble, variante)
    else:
        edge = (dist >= spec["out_w"] * k) & (dist < (spec["out_w"] + spec["edge_w"]) * k)
        out[edge] = hexrgb(spec["edge"]) + (255,)
    outline = (dist >= 0) & (dist < spec["out_w"] * k)
    out[outline] = hexrgb(spec["out"]) + (255,)


def _finish(out, scale):
    return Image.fromarray(out.astype(np.uint8)).resize((T * scale, T * scale), Image.LANCZOS)


def transition(terrain, bits, scale, seed=0, marking=None, lower="grass", variante=0):
    """Tuile de transition : `terrain` (dessus) dans les coins `bits`, `lower` ailleurs. variante : un autre
    froissement de son bord, s'il est naturel (_froisse)."""
    out = np.array(TEX[lower](scale, seed))
    _layer(out, terrain, bits, lower, scale, seed, marking, variante)
    return _finish(out, scale)


def needs_composite(corners):
    """Vrai si la tuile mêle trois terrains, ou deux qui n'ont pas de paire dans PAIRS : `resolve()` ne saurait pas
    la dessiner sans remplacer un terrain par un autre (encoches carrées au bout des chemins, des trottoirs…)."""
    kinds = sorted(set(corners), key=PRIORITY.index)
    return len(kinds) >= 3 or (len(kinds) == 2 and (kinds[1], kinds[0]) not in PAIRS)


def composite_seed(corners):
    """Graine de la texture d'une tuile composée : la même pour les mêmes coins, où que la tuile soit dans la carte
    (l'éditeur de carte la redessine à la demande, comme dans le jeu)."""
    return sum(PRIORITY.index(c) * 9 ** i for i, c in enumerate(corners)) % 97


def composite(corners, scale, seed=0):
    """Tuile composée (voir needs_composite) : le terrain le plus bas en fond, puis chaque terrain par-dessus le
    précédent, dans l'ordre de PRIORITY, sur les coins où il est ou bien un terrain plus haut (il passe ainsi sous les
    suivants). Les contours viennent du même champ de coins que les tuiles voisines : ils s'y raccordent."""
    kinds = sorted(set(corners), key=PRIORITY.index)
    out = np.array(TEX[kinds[0]](scale, seed))
    for below, t in zip(kinds, kinds[1:]):
        bits = sum(1 << i for i, c in enumerate(corners) if PRIORITY.index(c) >= PRIORITY.index(t))
        _layer(out, t, bits, below, scale, seed)
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
#   lignes 1..14 : une paire (dessus/dessous) par ligne, colonne = bits de coins (0..15)
#   ligne 15     : détails transparents à poser sur un 2e calque de tuiles
COLS = 16
ROW0 = ["(vide)", "herbe", "herbe + brins", "herbe + fleurs", "herbe + cailloux",
        "route ligne H", "route ligne V", "passage piéton (route H)", "passage piéton (route V)",
        "terre var. 1", "terre var. 2", "route var. 1", "route var. 2",
        "pavés var. 1", "béton var. 1", "béton var. 2"]
OVERLAY_ROW = 1 + len(PAIRS)
# Variantes des transitions à bord naturel (un autre froissement, mêmes coins) : FROISSES - 1 rangées par paire,
# après la ligne des détails. La carte ne les connaît pas : le jeu les choisit en peignant le sol (MAP.tileAlt).
ALTERNEES = [p for p in PAIRS if p[0] in NATURELS and (p[0] != "water" or p[1] in BANKS)]
ALT_ROW = OVERLAY_ROW + 1
COMPOSITE_BASE = (ALT_ROW + len(ALTERNEES) * (FROISSES - 1)) * COLS      # tuiles composées, après les variantes


def alternees():
    """rangée d'une paire dans le tileset -> les rangées de ses variantes."""
    return {1 + PAIRS.index(p): [ALT_ROW + i * (FROISSES - 1) + v for v in range(FROISSES - 1)] for i, p in enumerate(ALTERNEES)}


def tileset(scale, composites=()):
    """composites : coins (NO, NE, SO, SE) des tuiles composées, ajoutées à partir de l'index COMPOSITE_BASE."""
    ts = T * scale
    rows = COMPOSITE_BASE // COLS + (len(composites) + COLS - 1) // COLS
    sheet = Image.new("RGBA", (COLS * ts, rows * ts), (0, 0, 0, 0))
    row0 = [None] + [grass_tile(scale, v) for v in range(4)]
    row0 += [road_marking(scale, m) for m in ("dash_h", "dash_v", "zebra_h", "zebra_v")]
    row0 += [transition(t, 15, scale, seed=s_) for t, s_ in
             (("dirt", 1), ("dirt", 2), ("road", 1), ("road", 2), ("paving", 1), ("concrete", 1), ("concrete", 2))]
    for i, im in enumerate(row0):
        if im is not None:
            sheet.paste(im, (i * ts, 0))
    for r, (up, lo) in enumerate(PAIRS):
        for bits in range(16):
            sheet.paste(transition(up, bits, scale, seed=bits, lower=lo), (bits * ts, (1 + r) * ts))
    for i in range(len(OVERLAYS)):
        sheet.paste(overlay(scale, i), (i * ts, OVERLAY_ROW * ts))
    for r, alts in alternees().items():
        up, lo = PAIRS[r - 1]
        for v, row in enumerate(alts):
            for bits in range(1, 15):
                sheet.paste(transition(up, bits, scale, seed=bits, lower=lo, variante=v + 1), (bits * ts, row * ts))
    for i, cs in enumerate(composites):
        j = COMPOSITE_BASE + i
        sheet.paste(composite(cs, scale, seed=composite_seed(cs)), ((j % COLS) * ts, (j // COLS) * ts))
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

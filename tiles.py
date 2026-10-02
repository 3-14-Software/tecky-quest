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
    "water":    dict(fill="#5DADE2", edge="#8FD0F0", out="#2F6F9A", edge_w=2.6, out_w=1.0,
                     halo=("#E8D39A", 2.2)),          # berge sableuse côté herbe
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


WATER_MARKS = True        # vaguelettes fixes dans la texture (la version web les anime à part : fx_ripple)


def tex_water(scale, seed=0):
    im = _canvas(scale, TERRAINS["water"]["fill"])
    if not WATER_MARKS:
        return im
    d = ImageDraw.Draw(im)
    k = scale * SS
    rnd = random.Random(6000 + seed)
    for _ in range(3):
        x, y = rnd.uniform(7, 23), rnd.uniform(7, 25)
        w = rnd.uniform(3, 5)
        d.arc([(x - w) * k, (y - 1.5) * k, (x + w) * k, (y + 1.5) * k], 200, 340,
              fill=hexrgb("#9AD6F3"), width=int(0.9 * k))
    return im


def tex_field(scale, seed=0):
    """Champ labouré : sillons horizontaux et rangs de jeunes pousses."""
    im = _canvas(scale, TERRAINS["field"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    rnd = random.Random(4000 + seed)
    for y in range(4, 32, 8):
        d.rectangle([0, (y + 2.2) * k, T * k, (y + 4.4) * k], fill=hexrgb("#8E5F33"))
        d.rectangle([0, y * k, T * k, (y + 1.1) * k], fill=hexrgb("#C68F58"))
        for x in range(3, 32, 6):
            xx = x + rnd.uniform(-0.8, 0.8)
            for dx in (-1.1, 1.1):
                d.ellipse([(xx + dx - 0.9) * k, (y - 0.5) * k, (xx + dx + 0.9) * k, (y + 0.9) * k], fill=hexrgb("#6FB25E"))
    return im


def tex_forest(scale, seed=0):
    """Sous-bois : herbe sombre, aiguilles de pin, quelques brindilles."""
    im = _canvas(scale, TERRAINS["forest"]["fill"])
    d = ImageDraw.Draw(im)
    k = scale * SS
    rnd = random.Random(5000 + seed)
    for _ in range(26):
        x, y, a = rnd.uniform(1, 31), rnd.uniform(1, 31), rnd.uniform(0, math.pi)
        dx, dy = math.cos(a) * 1.4, math.sin(a) * 1.4
        d.line([((x - dx) * k, (y - dy) * k), ((x + dx) * k, (y + dy) * k)],
               fill=hexrgb(rnd.choice(("#4A8240", "#4A8240", "#6AAA5C", "#8A6A3E"))), width=int(0.55 * k))
    for _ in range(3):
        x, y, r = rnd.uniform(5, 27), rnd.uniform(5, 27), rnd.uniform(1.6, 2.6)
        d.ellipse([(x - r) * k, (y - r * 0.6) * k, (x + r) * k, (y + r * 0.6) * k], fill=hexrgb("#4F8F46"))
    return im


def tex_lower_grass(scale, seed=0):
    return tex_grass(scale, seed % 4 if seed % 4 != 3 else 0, seed)


TEX = {"dirt": tex_dirt, "road": tex_road, "paving": tex_paving, "concrete": tex_concrete,
       "sidewalk": tex_sidewalk, "water": tex_water, "grass": tex_lower_grass, "field": tex_field,
       "forest": tex_forest}


# ------------------------------------------------------------------ transitions
def _field(bits, n):
    """Champ bilinéaire des 4 coins et distance signée approx. au contour 0.5 (en px sur-échantillonnés)."""
    nw, ne, sw, se = [(bits >> i) & 1 for i in range(4)]
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    v = nw * (1 - U) * (1 - V) + ne * U * (1 - V) + sw * (1 - U) * V + se * U * V
    gy, gx = np.gradient(v)
    g = np.sqrt(gx ** 2 + gy ** 2)
    dist = (v - 0.5) / np.maximum(g, 1e-6)
    dist[g < 1e-6] = np.where(v[g < 1e-6] > 0.5, 1e6, -1e6)
    return dist


def _layer(out, terrain, bits, below, scale, seed=0, marking=None):
    """Pose `terrain` sur `out` (tableau sur-échantillonné) dans les coins `bits`, avec le style de la paire
    (terrain, below) : berge côté herbe, liseré, contour."""
    n = T * scale * SS
    k = scale * SS
    spec = dict(TERRAINS[terrain])
    spec.update(PAIR_STYLE.get((terrain, below), {}))
    ter = np.array(TEX[terrain](scale, seed, marking) if terrain == "road" else TEX[terrain](scale, seed))
    dist = _field(bits, n)
    if "halo" in spec and below == "grass":
        col, w = spec["halo"]
        out[(dist < 0) & (dist >= -w * k)] = hexrgb(col) + (255,)
    inside = dist >= 0
    out[inside] = ter[inside]
    edge = (dist >= spec["out_w"] * k) & (dist < (spec["out_w"] + spec["edge_w"]) * k)
    out[edge] = hexrgb(spec["edge"]) + (255,)
    outline = (dist >= 0) & (dist < spec["out_w"] * k)
    out[outline] = hexrgb(spec["out"]) + (255,)


def _finish(out, scale):
    return Image.fromarray(out.astype(np.uint8)).resize((T * scale, T * scale), Image.LANCZOS)


def transition(terrain, bits, scale, seed=0, marking=None, lower="grass"):
    """Tuile de transition : `terrain` (dessus) dans les coins `bits`, `lower` ailleurs."""
    out = np.array(TEX[lower](scale, seed))
    _layer(out, terrain, bits, lower, scale, seed, marking)
    return _finish(out, scale)


def needs_composite(corners):
    """Vrai si la tuile mêle trois terrains, ou deux qui n'ont pas de paire dans PAIRS : `resolve()` ne saurait pas
    la dessiner sans remplacer un terrain par un autre (encoches carrées au bout des chemins, des trottoirs…)."""
    kinds = sorted(set(corners), key=PRIORITY.index)
    return len(kinds) >= 3 or (len(kinds) == 2 and (kinds[1], kinds[0]) not in PAIRS)


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
# GameMaker réserve la tuile 0 (toujours vide). Disposition, 16 colonnes :
#   ligne 0      : [vide] herbe x4, marquages x4, variantes pleines x7
#   lignes 1..14 : une paire (dessus/dessous) par ligne, colonne = bits de coins (0..15)
#   ligne 15     : détails transparents à poser sur un 2e calque de tuiles
COLS = 16
ROW0 = ["(vide)", "herbe", "herbe + brins", "herbe + fleurs", "herbe + cailloux",
        "route ligne H", "route ligne V", "passage piéton (route H)", "passage piéton (route V)",
        "terre var. 1", "terre var. 2", "route var. 1", "route var. 2",
        "pavés var. 1", "béton var. 1", "béton var. 2"]
OVERLAY_ROW = 1 + len(PAIRS)
COMPOSITE_BASE = (OVERLAY_ROW + 1) * COLS      # tuiles composées (version web), après la ligne des détails


def tileset(scale, water_marks=True, composites=()):
    """water_marks=False : eau unie, pour la version web qui anime ses vaguelettes.
    composites : coins (NO, NE, SO, SE) des tuiles composées, ajoutées à partir de l'index COMPOSITE_BASE."""
    global WATER_MARKS
    WATER_MARKS, before = water_marks, WATER_MARKS
    try:
        return _tileset(scale, composites)
    finally:
        WATER_MARKS = before


def _tileset(scale, composites=()):
    ts = T * scale
    rows = 2 + len(PAIRS) + (len(composites) + COLS - 1) // COLS
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
    for i, cs in enumerate(composites):
        j = COMPOSITE_BASE + i
        sheet.paste(composite(cs, scale, seed=i), ((j % COLS) * ts, (j // COLS) * ts))
    return sheet


def tile_index(upper, bits, lower="grass"):
    """Index GameMaker d'une tuile de transition."""
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

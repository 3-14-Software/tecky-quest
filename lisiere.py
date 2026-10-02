"""
Lisière : ce qui borde la carte (version web), dessiné dans la marge que la caméra montre au-delà des bords
(EDGE.cam dans game.js) : des fourrés devant une rangée d'arbres (des sapins le long de la forêt) et, aux deux bouts de
la grande route, l'entrée d'un tunnel où les voitures disparaissent. Ce ne sont pas des obstacles : Tecky s'arrête au
bord de la carte (BOUND dans game.js), juste devant. Le sol de la marge (RING tuiles autour de la carte) prolonge celui
du bord : pack_web.build_map.
"""
import math
import random

from spritelib import Drawing, circle, path, rect, line

RING = 2                      # tuiles de sol autour de la carte (la caméra en montre une)


def _shadow(d, cx, cy, rx, ry):
    d.under.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" opacity="0.2"/>')


def thicket(dark=False):
    """Fourré de la lisière : un gros buisson touffu, sans baies, plus sombre au fond (dark : celui de la forêt)."""
    back, front, light = ("#24633A", "#2F7A45", "#4C9A5C") if dark else ("#3F8439", "#4E9A47", "#72BE5E")
    d = Drawing(48, 32)
    _shadow(d, 24, 28, 21, 3.5)
    for cx, cy, r in ((15, 14, 9), (31, 12, 10), (24, 9, 7.5), (40, 17, 6.5)):     # touffes du fond, à l'ombre
        d.add(circle(cx, cy, r), back)
    for cx, cy, r in ((9, 21, 7), (21, 19.5, 8.5), (33, 20, 8), (41, 23, 5.5)):
        d.add(circle(cx, cy, r), front)
    for cx, cy, r in ((18, 15.5, 3.2), (31, 16, 2.6), (8, 18, 2), (24, 7, 2.2)):   # reflets
        d.add(circle(cx, cy, r), light, sil=False)
    return d


def _clump(d, cx, cy, k=1.0):
    """Touffe de fourré (trois boules et un reflet), pour habiller la butte du tunnel."""
    for dx, dy, r in ((-7, 2, 6.5), (6, 1.5, 7), (0, -4, 6.5)):
        d.add(circle(cx + dx * k, cy + dy * k, r * k), "#4E9A47")
    d.add(circle(cx - 3 * k, cy - 6 * k, 2.4 * k), "#72BE5E", sil=False)


def tunnel():
    """Entrée du tunnel de la grande route au bord ouest de la carte (en miroir au bord est) : une butte boisée que la
    route traverse ; la bouche, cerclée de pierres, s'ouvre vers la carte et la route s'y enfonce dans le noir.
    Origine (56, 208) : pied de la butte, sur le bord de la carte ; la route passe entre v 64 et v 192 (ligne du
    milieu en v 128). On n'en voit que la partie droite (u > 24) : la caméra ne déborde que d'une tuile."""
    d = Drawing(72, 216)
    d.under.append('<path d="M60,58 L68,62 Q73,128 68,194 L60,198 Z" fill="#000" opacity="0.2"/>')   # ombre
    d.under.append('<ellipse cx="40" cy="211" rx="30" ry="4" fill="#000" opacity="0.2"/>')
    # la butte : herbe un peu plus sombre que le pré, flanc tourné vers la carte encore plus sombre
    hill = path("M0,12 C10,4 26,2 40,6 C54,10 64,18 66,32 C67,40 64,46 62,50 L62,206 C66,207 68,211 64,214 L0,214 Z")
    d.clip("tunnel_hill", [hill])
    d.add(hill, "#6DB75C")
    d.add(path("M50,0 C64,12 72,30 64,48 L62,52 L62,214 L54,214 L54,0 Z"), "#5A9A4E", sil=False, clip="tunnel_hill")
    for x, y in ((14, 40), (30, 66), (22, 150), (36, 178), (10, 100), (44, 92), (40, 160)):        # brins d'herbe
        d.raw(line(f"M{x - 2},{y} L{x},{y - 3.2} L{x + 2},{y}", "#4F8C45", 1.0))
    # la bouche : arc de pierres ; dedans, la route s'enfonce dans le noir
    mouth = path("M63,56 A20,72 0 0 0 63,200 Z")
    d.add(path("M63,46 A27,82 0 0 0 63,210 Z"), "#B5ADA0")
    d.add(mouth, "#2B1E17", sil=False)
    d.clip("tunnel_mouth", [mouth])
    d.add(rect(52, 64, 12, 128), "#3E4048", sil=False, clip="tunnel_mouth")                 # la route, dans l'ombre
    d.add(rect(52, 64, 12, 2.4), "#7A7D86", sil=False, clip="tunnel_mouth")                 # ses bordures
    d.add(rect(52, 189.6, 12, 2.4), "#7A7D86", sil=False, clip="tunnel_mouth")
    d.add(rect(56, 127, 7, 2), "#8D9098", sil=False, clip="tunnel_mouth")                   # ligne du milieu
    d.add(path("M63,74 A12,54 0 0 0 63,182 Z"), "#1C130E", sil=False)                     # le fond, tout noir
    for k in range(1, 12):                                                                 # joints des pierres
        a = math.pi / 2 + k * math.pi / 12
        x0, y0 = 63 + 20 * math.cos(a), 128 + 72 * math.sin(a)
        x1, y1 = 63 + 27 * math.cos(a), 128 + 82 * math.sin(a)
        d.raw(line(f"M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}", "#7E766B", 0.9))
    d.add(rect(60, 42, 6, 172, 2), "#CFC8BB", sil=False, edge=True)                       # dessus du mur de tête
    for y in range(50, 212, 12):
        d.raw(line(f"M61,{y} L65,{y}", "#9A9286", 0.8))
    # la butte est boisée, comme la lisière : des touffes en haut et en bas, par-dessus son contour
    for cx, cy, k in ((30, 10, 1.1), (48, 16, 1.0), (60, 30, 0.85), (20, 206, 1.0), (40, 208, 1.1), (60, 210, 0.8)):
        _clump(d, cx, cy, k)
    return d


DECOR = {   # nom : (fonction, (largeur, hauteur) 1x, origine 1x) ; dessinés dans l'atlas sous decor/<nom>
    "thicket": (thicket, (48, 32), (24, 28)),
    "thicket_dark": (lambda: thicket(dark=True), (48, 32), (24, 28)),
    "tunnel": (tunnel, (72, 216), (56, 208)),
}

# encombrement à l'écran (demi-largeur, hauteur au-dessus du pied), en tuiles : rien d'important ne doit être caché
SIZE = {"thicket": (0.72, 0.85), "thicket_dark": (0.72, 0.85), "tree": (0.8, 1.75), "fir": (0.9, 2.3)}
TUNNEL_H = 6.6                # hauteur de la butte du tunnel au-dessus de son pied (tuiles)


def decor(g, mw, mh, keep, forest, tunnels):
    """Décors de la lisière, hors de la carte : liste de (nom, x, y en tuiles, miroir). g : grille des coins de
    pack_web (l'eau et la route continuent au-delà du bord : on les laisse libres) ; keep : points (x, y) à ne jamais
    cacher (objets, personnages, panneaux…) ; forest(x, y) : au bord de la forêt (sapins) ? tunnels : (x, y du pied,
    miroir) des tunnels de la route."""
    rnd = random.Random(29)
    j = lambda a: rnd.uniform(-a, a)
    out = [("tunnel", x, y, f) for x, y, f in tunnels]

    def corner(x, y):
        return g[min(max(int(round(y)), 0), mh)][min(max(int(round(x)), 0), mw)]

    def put(n, x, y):
        if any(corner(x + dx, y + dy) in ("water", "road") for dx in (-0.8, 0, 0.8) for dy in (-0.8, 0, 0.8)):
            return                                  # la rivière, le ruisseau et la route passent
        if any(abs(x - tx) < 1.5 and ty - TUNNEL_H < y < ty + 0.8 for tx, ty, _ in tunnels):
            return                                  # la butte du tunnel
        hw, h = SIZE[n]
        if any(abs(kx - x) < hw + 0.3 and y - h - 0.3 < ky < y + 0.2 for kx, ky in keep):
            return
        out.append((n, round(x, 2), round(y, 2), False))

    def row(y, x0, x1, step, kind):                 # le long du bord nord ou sud (y : nombre, ou selon le décor)
        x = x0
        while x < x1:
            n = kind(x)
            put(n, x + j(0.15), (y(n) if callable(y) else y) + j(0.05))
            x += step + j(0.12)

    def column(x, y0, y1, step, kind):              # le long du bord ouest ou est
        y = y0
        while y < y1:
            n = kind(y)
            put(n, x + j(0.06), y + j(0.15))
            y += step + j(0.1)

    tall = lambda x, y: "fir" if forest(x, y) else "tree"
    low = lambda x, y: "thicket_dark" if forest(x, y) else "thicket"
    # nord : les arbres juste sur le bord, les fourrés devant (Tecky passe toujours devant eux)
    row(0.04, -0.7, mw + 0.8, 1.7, lambda x: "tree")
    row(0.16, -1.0, mw + 1.0, 1.05, lambda x: "thicket")
    # sud : les fourrés, puis les arbres ou les sapins (plus hauts, un peu plus loin), dont on voit le haut
    row(mh + 0.72, -1.0, mw + 1.0, 1.05, lambda x: low(x, mh))
    row(lambda n: mh + (2.05 if n == "fir" else 1.75), -0.6, mw + 0.8, 1.6, lambda x: tall(x, mh))
    # ouest et est : les arbres au fond, les fourrés devant (la rivière et le tunnel restent libres)
    for side, sgn in ((0, -1), (mw, 1)):
        column(side + sgn * 0.98, 0.9, mh - 0.4, 1.45, lambda y: tall(side, y))
        column(side + sgn * 0.5, 0.5, mh - 0.3, 0.74, lambda y: low(side, y))
    return out

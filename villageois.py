"""
Les villageois (sans quête) : ils animent la place et la rue du village et saluent Tecky quand il passe.
Vus de face, comme les personnages de npcs.py (dont on réutilise les outils : bras, visage, poses P()) : cellule 48 x 64,
pieds en (24, 60).

- baker : Bernard, le boulanger, devant sa boutique : toque, veste blanche croisée, foulard rouge, tablier, une baguette
  sous le bras, moustache.
- vendor : Josette, la marchande de fruits, à côté de son étal : fichu rouge à pois, chemisier jaune, tablier vert,
  une pomme dans les mains.
- florist : Lili, la fleuriste, à côté de son étal : queue de cheval et fleur dans les cheveux, tablier rose, un petit
  bouquet.
- kid : Lucas, un petit garçon, près de la fontaine : casquette, marinière, short, un ballon rouge au bout d'une ficelle
  (plus petit : tout est réduit autour des pieds, KID).

Animations (ANIMS[kind][nom] = (poses, fps, boucle)) : idle, wave (il salue Tecky) ; le petit garçon : hop (il
sautille de joie, à la place de wave).
"""
from spritelib import Drawing, circle, ellipse, rect, path, poly, leg, line, OUTLINE
from npcs import P, G, HK, W, H, _shadow, _arms, _ik, _head_frame, _eyes, _brows, _blush, _mouth, _IDLE, _WAVE

KINDS = ("baker", "vendor", "florist", "kid")
KID = 0.78                       # le petit garçon : réduit autour de ses pieds
PAL = {
    "baker": dict(skin="#F5C8A6", skin_dk="#E2A986", nose="#EA9C82", blush="#F28A8A", hair="#6B4A30", hair_dk="#4E3420",
                  jacket="#FFFDF7", jacket_dk="#D9D2C4", apron="#F3EFE6", scarf="#D7332B", toque="#FFFFFF",
                  toque_dk="#DCD6CB", pants="#5C6A86", pants_dk="#3F4A63", shoe="#3A3A44", bread="#E3A954",
                  bread_dk="#B97A30", eye="#2A1E1A", mouth="#B8505A", tongue="#E9858B"),
    "vendor": dict(skin="#EDBB94", skin_dk="#D79D74", nose="#DD8F74", blush="#F08A7E", hair="#7A4E2E", hair_dk="#57351D",
                   blouse="#F6D360", blouse_dk="#D9B23E", apron="#4E9A47", apron_dk="#3B7A35", scarf="#D7332B",
                   dot="#FFFFFF", skirt="#7A5238", skirt_dk="#5C3C27", shoe="#4A3A30", apple="#E0413A",
                   eye="#2A1E1A", mouth="#B8505A", tongue="#E9858B"),
    "florist": dict(skin="#F9D9C6", skin_dk="#E9B9A0", nose="#EFA690", blush="#F2879E", hair="#8A5530", hair_dk="#64391C",
                    top="#FFFDF7", top_dk="#E1D9CB", apron="#F28CB8", apron_dk="#D86A9A", jeans="#5B7DB8",
                    jeans_dk="#456399", shoe="#F3F0E8", flower="#F7D154", petal="#FFFFFF", leaf="#4E9A47",
                    eye="#2A1E1A", mouth="#B8505A", tongue="#E9858B"),
    "kid": dict(skin="#F5C8A6", skin_dk="#E2A986", nose="#EA9C82", blush="#F28A8A", hair="#A8743E", hair_dk="#7E5428",
                shirt="#FFFFFF", stripe="#3E66B0", shorts="#E08A3A", shorts_dk="#B86A22", cap="#D7332B",
                cap_dk="#A82520", shoe="#3A3A44", balloon="#E0413A", eye="#2A1E1A", mouth="#B8505A",
                tongue="#E9858B"),
}


def _face(d, c, p, X, V, hy, hair_back=None):
    """Oreilles, visage, yeux, joues, bouche, nez (commun à tous)."""
    k = HK
    for x in (14.5, 33.5):
        d.add(circle(X(x), V(1.4), 2.0 * k), c["skin"])
        d.add(circle(X(x), V(1.4), 0.9 * k), c["skin_dk"], sil=False)
    d.add(ellipse(24, hy, 9.7 * k, 9.1 * k), c["skin"])


def _features(d, c, p, X, V, brow, mouth_y=5.6, nose=True):
    k = HK
    _eyes(d, c, p, X, V)
    _brows(d, p, X, V, brow, 1.2)
    _blush(d, c, X, V)
    _mouth(d, c, p, X, V, mouth_y)
    if nose:
        d.add(ellipse(24, V(2.7), 1.5 * k, 1.2 * k), c["nose"], sil=False, edge=True)
        d.add(circle(X(23.5), V(2.3), 0.4 * k), "#FFFFFF", sil=False, opacity=0.7)


def _hands_joined(Y):
    """Bras au repos, mains jointes devant le ventre (pour tenir une pomme, un bouquet)."""
    def rest(s, sx):
        (ex, ey), tgt = _ik(sx, Y(31.4), 24 + s * 1.3, Y(40.6), 6.2, 6.0, s, 0.2)
        return (ex, ey), tgt, True
    return rest


# ================================================================== BERNARD, LE BOULANGER
def _baker(p):
    c = dict(PAL["baker"], sleeve=PAL["baker"]["jacket"], cuff=PAL["baker"]["jacket_dk"])
    d = Drawing(W, H)
    L = p["lift"]
    Y = lambda v: v + p["bob"] - L
    T = lambda v: v - L
    _shadow(d, L, 10.8)
    for x, s in ((20.4, -1), (27.6, 1)):
        d.add(ellipse(x + s * 0.6, T(G - 1.7), 3.6, 1.9), c["shoe"])
    for x in (20.4, 27.6):
        d.add(leg(x, Y(44), x, T(57.0), 5.2), c["pants"])
        for y in (47.5, 50.5, 53.5):                                   # pantalon pied-de-poule
            for dx in (-1.2, 1.2):
                d.add(rect(x + dx - 0.5, T(y + (dx > 0) * 1.5) - 0.5, 1.0, 1.0), c["pants_dk"], sil=False)
    # veste blanche croisée, bedaine de boulanger, boutons, tablier
    d.add(rect(14.0, Y(28.6), 20.0, 17.4, 4.8), c["jacket"])
    d.add(ellipse(24, Y(39.4), 10.8 + p["breath"], 7.2), c["jacket"])
    for x in (21.2, 26.8):
        for y in (32.4, 35.8):
            d.add(circle(x, Y(y), 0.7), c["jacket_dk"], sil=False, edge=True)
    d.add(path(f"M15.6,{Y(39.4):.2f} L32.4,{Y(39.4):.2f} L33.4,{Y(50.6):.2f} Q24,{Y(52.0):.2f} 14.6,{Y(50.6):.2f} Z"),
          c["apron"], sil=False, edge=True)
    d.raw(line(f"M15.4,{Y(39.6):.2f} L32.6,{Y(39.6):.2f}", c["jacket_dk"], 0.8))
    d.add(poly([(19.6, Y(28.6)), (28.4, Y(28.6)), (24, Y(32.6))]), c["scarf"], sil=False, edge=True)   # foulard

    def rest(s, sx):
        return (sx + s * 2.2, Y(31.2) + 5.8), (sx + s * 2.8, Y(31.2) + 11.6), False
    hy, X, V = _head_frame(Y, p)
    _arms(d, c, p, 15.0, 33.0, Y(31.2), rest)
    # la baguette, coincée sous le bras droit (à droite de l'image)
    bx, by = 36.2, Y(40.4)
    d.add(ellipse(bx - 1.2, by - 7.4, 1.9, 9.6, f"rotate(24 {bx - 1.2:.2f} {by - 7.4:.2f})"), c["bread"], sil=False, edge=True)
    for t in (-4.0, 0.0, 4.0):
        d.raw(line(f"M{bx - 1.2 + t * 0.42 - 0.7:.2f},{by - 7.4 - t:.2f} L{bx - 1.2 + t * 0.42 + 0.9:.2f},{by - 7.4 - t - 1.2:.2f}",
                   c["bread_dk"], 0.6))
    # tête : visage, moustache, cheveux courts, toque
    k = HK
    _face(d, c, p, X, V, hy)
    for s in (-1, 1):
        d.add(path(f"M{X(24 + s * 8.6):.2f},{V(-4.0):.2f} Q{X(24 + s * 10.4):.2f},{V(-2.0):.2f} {X(24 + s * 9.8):.2f},{V(1.2):.2f} "
                   f"Q{X(24 + s * 8.8):.2f},{V(-0.6):.2f} {X(24 + s * 8.0):.2f},{V(-1.4):.2f} Z"), c["hair"])
    d.add(rect(X(14.6), V(-9.6), 18.8 * k, 4.4 * k, 1.2), c["toque"])                                  # bandeau
    for cx, r in ((17.6, 4.6), (24, 5.6), (30.4, 4.6)):                                                 # le haut, bouffant
        d.add(circle(X(cx), V(-13.2), r * k), c["toque"])
    d.raw(line(f"M{X(20.8):.2f},{V(-10.0):.2f} L{X(20.6):.2f},{V(-15.0):.2f} M{X(27.2):.2f},{V(-10.0):.2f} "
               f"L{X(27.4):.2f},{V(-15.0):.2f}", c["toque_dk"], 0.7))
    _features(d, c, p, X, V, c["hair_dk"], mouth_y=6.6)
    for s in (-1, 1):                                                                                   # moustache
        d.add(path(f"M24,{V(4.0):.2f} Q{X(24 + s * 2.6):.2f},{V(3.0):.2f} {X(24 + s * 4.6):.2f},{V(4.6):.2f} "
                   f"Q{X(24 + s * 2.6):.2f},{V(5.6):.2f} 24,{V(4.8):.2f} Z"), c["hair"], sil=False, edge=True)
    return d


# ================================================================== JOSETTE, LA MARCHANDE DE FRUITS
def _vendor(p):
    c = dict(PAL["vendor"], sleeve=PAL["vendor"]["blouse"], cuff=PAL["vendor"]["blouse_dk"])
    d = Drawing(W, H)
    L = p["lift"]
    Y = lambda v: v + p["bob"] - L
    T = lambda v: v - L
    _shadow(d, L, 10.6)
    for x, s in ((21.0, -1), (27.0, 1)):
        d.add(ellipse(x + s * 0.5, T(G - 1.5), 3.2, 1.7), c["shoe"])
    d.add(path(f"M16.6,{Y(40):.2f} L31.4,{Y(40):.2f} L33.6,{T(57.0):.2f} Q24,{T(58.4):.2f} 14.4,{T(57.0):.2f} Z"), c["skirt"])
    d.raw(line(f"M20.6,{Y(46):.2f} L19.6,{T(57):.2f} M27.4,{Y(46):.2f} L28.4,{T(57):.2f}", c["skirt_dk"], 0.7))
    d.add(rect(14.4, Y(28.6), 19.2, 12.0, 4.6), c["blouse"])
    d.add(ellipse(24, Y(38.6), 10.2 + p["breath"], 6.8), c["blouse"])
    d.add(path(f"M17.4,{Y(33.4):.2f} L30.6,{Y(33.4):.2f} L32.4,{Y(51.0):.2f} Q24,{Y(52.4):.2f} 15.6,{Y(51.0):.2f} Z"),
          c["apron"], sil=False, edge=True)                                                             # tablier vert
    d.add(rect(19.6, Y(42.6), 8.8, 4.4, 1), c["apron_dk"], sil=False, edge=True)                       # poche
    hy, X, V = _head_frame(Y, p)
    _arms(d, c, p, 15.2, 32.8, Y(31.4), _hands_joined(Y))
    if p["wave"] <= 0:                                                                                  # une pomme
        d.add(circle(24, Y(39.4), 2.6), c["apple"], sil=False, edge=True)
        d.raw(line(f"M24,{Y(36.9):.2f} L24.6,{Y(35.6):.2f}", "#6B4A30", 0.7))
        d.add(circle(23.1, Y(38.6), 0.6), "#FFFFFF", sil=False, opacity=0.7)
    k = HK
    _face(d, c, p, X, V, hy)
    # fichu rouge à pois, noué sur le haut de la tête
    d.add(path(f"M{X(14.2):.2f},{V(1.0):.2f} Q{X(13.0):.2f},{V(-11.0):.2f} 24,{V(-11.2):.2f} Q{X(35.0):.2f},{V(-11.0):.2f} "
               f"{X(33.8):.2f},{V(1.0):.2f} Q{X(31.6):.2f},{V(-4.0):.2f} 24,{V(-4.6):.2f} Q{X(16.4):.2f},{V(-4.0):.2f} "
               f"{X(14.2):.2f},{V(1.0):.2f} Z"), c["scarf"])
    for x, y in ((18.4, -6.6), (23.4, -8.6), (28.6, -7.0), (20.8, -9.6), (26.4, -10.0), (31.2, -4.4), (16.4, -3.2)):
        d.add(circle(X(x), V(y), 0.6 * k), c["dot"], sil=False)
    for s in (-1, 1):                                                                                   # le nœud
        d.add(ellipse(X(24 + s * 2.8), V(-12.0), 2.6 * k, 1.5 * k, f"rotate({s * 30} {X(24 + s * 2.8):.2f} {V(-12.0):.2f})"), c["scarf"])
    d.add(circle(24, V(-11.6), 1.2 * k), c["scarf"])
    for s in (-1, 1):                                                                                   # mèches
        d.add(ellipse(X(24 + s * 6.4), V(-3.4), 2.6 * k, 1.4 * k, f"rotate({s * 20} {X(24 + s * 6.4):.2f} {V(-3.4):.2f})"),
              c["hair"], sil=False)
    _features(d, c, p, X, V, c["hair_dk"])
    return d


# ================================================================== LILI, LA FLEURISTE
def _florist(p):
    c = dict(PAL["florist"], sleeve=PAL["florist"]["top"], cuff=PAL["florist"]["top_dk"])
    d = Drawing(W, H)
    L = p["lift"]
    Y = lambda v: v + p["bob"] - L
    T = lambda v: v - L
    _shadow(d, L, 10.0)
    for x, s in ((21.2, -1), (26.8, 1)):
        d.add(ellipse(x + s * 0.5, T(G - 1.5), 3.0, 1.6), c["shoe"])
        d.add(leg(x, Y(44), x, T(57.2), 4.6), c["jeans"])
    d.raw(line(f"M24,{Y(45):.2f} L24,{Y(47.5):.2f}", c["jeans_dk"], 0.6))
    d.add(rect(15.0, Y(28.6), 18.0, 16.6, 4.4), c["top"])
    d.add(path(f"M17.2,{Y(32.0):.2f} L30.8,{Y(32.0):.2f} L31.8,{Y(49.4):.2f} Q24,{Y(50.6):.2f} 16.2,{Y(49.4):.2f} Z"),
          c["apron"], sil=False, edge=True)                                                             # tablier rose
    d.add(circle(24, Y(42.8), 1.6), c["flower"], sil=False, edge=True)                                 # fleur brodée
    hy, X, V = _head_frame(Y, p)
    _arms(d, c, p, 15.6, 32.4, Y(31.4), _hands_joined(Y))
    if p["wave"] <= 0:                                                                                  # un petit bouquet
        for dx, col in ((-2.2, "#F28CB8"), (0, c["flower"]), (2.2, "#B48ED8")):
            d.raw(line(f"M{24 + dx * 0.4:.2f},{Y(41.2):.2f} L{24 + dx:.2f},{Y(36.4):.2f}", c["leaf"], 0.9))
            d.add(circle(24 + dx, Y(35.6), 1.7), col, sil=False, edge=True)
            d.add(circle(24 + dx, Y(35.6), 0.6), c["petal"], sil=False)
    k = HK
    # queue de cheval (derrière la tête)
    d.add(ellipse(X(33.6), V(-1.0), 2.6 * k, 6.0 * k, f"rotate(-16 {X(33.6):.2f} {V(-1.0):.2f})"), c["hair"])
    _face(d, c, p, X, V, hy)
    hair = path(f"M{X(14.6):.2f},{V(1.0):.2f} Q{X(13.0):.2f},{V(-10.4):.2f} 24,{V(-10.6):.2f} Q{X(35.0):.2f},{V(-10.4):.2f} "
                f"{X(33.4):.2f},{V(1.0):.2f} Q{X(32.0):.2f},{V(-3.0):.2f} {X(28.6):.2f},{V(-4.2):.2f} Q{X(25.0):.2f},{V(-5.6):.2f} "
                f"{X(21.6):.2f},{V(-4.8):.2f} Q{X(17.0):.2f},{V(-3.6):.2f} {X(14.6):.2f},{V(1.0):.2f} Z")
    d.add(hair, c["hair"])
    d.raw(line(f"M{X(21.6):.2f},{V(-4.8):.2f} Q{X(24):.2f},{V(-8.6):.2f} {X(29.6):.2f},{V(-9.0):.2f}", c["hair_dk"], 0.6))
    fx, fy = X(17.8), V(-7.4)                                                                           # fleur dans les cheveux
    for i in range(5):
        a = i * 72
        d.add(ellipse(fx, fy - 1.6 * k, 1.0 * k, 1.5 * k, f"rotate({a} {fx:.2f} {fy:.2f})"), c["petal"], sil=False, edge=True)
    d.add(circle(fx, fy, 0.9 * k), c["flower"], sil=False, edge=True)
    _features(d, c, p, X, V, c["hair_dk"])
    return d


# ================================================================== LUCAS ET SON BALLON
def _kid(p):
    c = dict(PAL["kid"], sleeve=PAL["kid"]["shirt"], cuff=PAL["kid"]["stripe"])
    d = Drawing(W, H)
    L = p["lift"]
    Y = lambda v: v + p["bob"] - L
    T = lambda v: v - L
    # le ballon, au bout de sa ficelle tenue par la main gauche (à droite de l'image) ; il flotte un peu
    sway = p.get("look", 0) * 1.5 + L * 0.4
    hx, hy_ = 33.0, Y(41.6)
    bx, by = 37.0 + sway, Y(4.0) - L * 0.6
    d.raw(line(f"M{hx:.2f},{hy_:.2f} Q{36.0 + sway * 0.5:.2f},{Y(24):.2f} {bx:.2f},{by + 7.6:.2f}", OUTLINE, 0.5))
    d.add(ellipse(bx, by, 5.6, 6.8), c["balloon"])
    d.add(poly([(bx - 1.2, by + 7.6), (bx + 1.2, by + 7.6), (bx, by + 6.2)]), c["balloon"])
    d.add(ellipse(bx - 2.0, by - 2.6, 1.4, 2.2, f"rotate(-20 {bx - 2.0:.2f} {by - 2.6:.2f})"), "#FFFFFF", sil=False, opacity=0.6)
    # baskets, jambes, short orange
    for x, s in ((20.8, -1), (27.2, 1)):
        d.add(ellipse(x + s * 0.5, T(G - 1.6), 3.2, 1.8), c["shoe"])
        d.add(leg(x, T(52.0), x, T(G - 2.4), 3.0), c["skin"])
    d.add(rect(15.6, Y(42.4), 16.8, 8.4, 2.4), c["shorts"])
    d.raw(line(f"M24,{Y(46):.2f} L24,{Y(50.6):.2f}", c["shorts_dk"], 0.7))
    # marinière
    torso = rect(15.2, Y(28.6), 17.6, 15.0, 4.2)
    d.add(torso, c["shirt"])
    d.clip("kidtorso", [torso])
    for y in (31.4, 34.6, 37.8, 41.0):
        d.add(rect(14, Y(y), 20, 1.5), c["stripe"], sil=False, clip="kidtorso")
    hy, X, V = _head_frame(Y, p)

    def rest(s, sx):
        if s == 1:                                                                                      # la main qui tient la ficelle
            return (sx + 2.4, Y(31.2) + 5.6), (hx, hy_), False
        return (sx - 2.2, Y(31.2) + 5.8), (sx - 2.8, Y(31.2) + 11.6), False
    _arms(d, c, p, 15.6, 32.4, Y(31.2), rest)
    k = HK
    _face(d, c, p, X, V, hy)
    d.add(path(f"M{X(14.6):.2f},{V(0.0):.2f} Q{X(14.0):.2f},{V(-6.0):.2f} {X(18.0):.2f},{V(-5.6):.2f} L{X(30.0):.2f},{V(-5.6):.2f} "
               f"Q{X(34.0):.2f},{V(-6.0):.2f} {X(33.4):.2f},{V(0.0):.2f} Q{X(32.0):.2f},{V(-3.4):.2f} 24,{V(-3.6):.2f} "
               f"Q{X(16.0):.2f},{V(-3.4):.2f} {X(14.6):.2f},{V(0.0):.2f} Z"), c["hair"])
    d.add(path(f"M{X(14.4):.2f},{V(-5.0):.2f} Q{X(14.4):.2f},{V(-14.0):.2f} 24,{V(-14.2):.2f} Q{X(33.6):.2f},{V(-14.0):.2f} "
               f"{X(33.6):.2f},{V(-5.0):.2f} Z"), c["cap"])                                              # casquette
    d.add(path(f"M{X(12.4):.2f},{V(-5.6):.2f} L{X(35.6):.2f},{V(-5.6):.2f} Q{X(35.6):.2f},{V(-3.6):.2f} 24,{V(-3.4):.2f} "
               f"Q{X(12.4):.2f},{V(-3.6):.2f} {X(12.4):.2f},{V(-5.6):.2f} Z"), c["cap_dk"], edge=True)
    d.add(circle(24, V(-14.0), 1.0 * k), c["cap_dk"], sil=False, edge=True)
    _features(d, c, p, X, V, c["hair_dk"], nose=False)
    d.add(ellipse(24, V(2.7), 1.1 * k, 0.9 * k), c["nose"], sil=False, edge=True)
    for x, y in ((18.6, 3.6), (19.8, 4.4), (29.4, 3.6), (28.2, 4.4)):                                  # taches de rousseur
        d.add(circle(X(x), V(y), 0.35), "#C9875A", sil=False)
    return d


_DRAW = {"baker": _baker, "vendor": _vendor, "florist": _florist, "kid": _kid}
_HOP = [P(happy=True, lift=0.6), P(happy=True, lift=3.2, look=-0.6), P(happy=True, lift=4.2, look=0.4),
        P(happy=True, lift=1.6, look=0.6)]
ANIMS = {
    "baker": {"idle": (_IDLE, 4, True), "wave": (_WAVE, 8, True)},
    "vendor": {"idle": (_IDLE, 5, True), "wave": (_WAVE, 8, True)},
    "florist": {"idle": (_IDLE, 5, True), "wave": (_WAVE, 8, True)},
    "kid": {"idle": ([P(look=-0.6), P(bob=0.3, look=-0.2), P(bob=0.4, look=0.4), P(bob=0.3, blink=1, look=0.6)], 4, True),
            "hop": (_HOP, 8, True)},
}


def front(kind, p):
    return _DRAW[kind](p)


def frames(kind, anim):
    """SVG des images d'une animation (le petit garçon : réduit autour de ses pieds)."""
    tr = f"translate(24 {G}) scale({KID}) translate(-24 {-G})" if kind == "kid" else ""
    return [front(kind, p).svg(transform=tr) for p in ANIMS[kind][anim][0]]

"""
Le fermier Gaston (ferme des Tilleuls) — PNJ vu de face uniquement (il regarde vers le bas de l'écran).
Style chibi comme Alice (grosse tête), mais adulte jovial et un peu rond : chapeau de paille à ruban vert,
moustache grise, gros nez rond, joues roses, chemise à carreaux rouges aux manches retroussées, salopette
en jean à bretelles, bottes en caoutchouc vertes.

Cellule 48 x 64 (W, H), pieds posés sur y = 60 (G) : origine conseillée du sprite (24, 60).
Hauteur réelle : du haut du chapeau (y ≈ 4.5 contour compris, 5.4 sans) au bas des bottes (y ≈ 61 contour compris,
60.2 sans), soit environ 56.5 unités (55 sans le contour) ; Alice en fait environ 42.
En largeur : x ≈ 8.2..39.8 au repos ; la main qui salue va jusqu'à x ≈ 1.6. Rien ne sort de la cellule.

Portrait de dialogue : tête centrée horizontalement sur x = 24, centre de la tête (24, 20.3).
Recadrage conseillé (même principe que `_crop_face(svg, 24, 16.5, 12.5, scale)` pour Alice) : FACE = (24, 18.5, 15.5),
c'est-à-dire centre (24, 18.5) et demi-côté 15.5 (ruban du chapeau, visage, moustache et menton). Attention, le cadre
fait 48 x 64 : rendre le SVG en 48 x 64 avant de recadrer (le `_crop_face` de hud.py rend en 48 x 48).
`portrait_states()` donne les trois poses du portrait : normal, clignement, joyeux.

Animations (ANIMS, toutes en boucle, 4 images) : idle (5 i/s, respiration + un clignement), talk (8 i/s, bouche
qui s'ouvre et se ferme + hochement), wave (8 i/s, il agite la main droite levée en souriant, pour remercier ;
c'est sa main droite, donc à gauche de l'image).
"""
import math

from spritelib import Drawing, circle, ellipse, rect, path, poly, leg, line, OUTLINE

W, H = 48, 64
G = 60.0                      # ligne des pieds
FACE = (24, 18.5, 15.5)       # portrait : centre du recadrage (cx, cy) et demi-côté conseillé
HK = 1.08                     # agrandissement de la tête (style chibi), autour du menton

PAL = dict(skin="#F7CFB2", skin_dk="#E7AE8E", nose="#EDA088", blush="#F28A8A",
           hair="#D5D1CA", hair_dk="#A7A198",
           straw="#EFC76B", straw_dk="#C99A42", band="#5E8C4A",
           shirt="#D94A3D", shirt_dk="#8E2620", shirt_lt="#EE7A6C",
           denim="#4F80C2", denim_dk="#3A6198", denim_lt="#7FA8DD", brass="#F2C14E",
           boot="#5E9A4A", boot_dk="#467636", boot_lt="#86BE6C",
           eye="#2A1E1A", mouth="#B8505A", tongue="#E9858B")


def F(**kw):
    """Pose du fermier.
    bob : décalage vertical du buste (respiration) ; breath : ventre un peu plus large ;
    nod : la tête seule descend (hochement) ; blink : yeux fermés si > 0.5 ;
    mouth : 0 bouche fermée -> 1 grande ouverte (il parle) ; happy : yeux plissés et grand sourire ;
    wave : 0 bras le long du corps -> 1 bras levé (sa main droite, à gauche de l'image) ;
    wave_a : angle (°) de l'avant-bras levé depuis la verticale (négatif = vers l'extérieur, positif = vers la tête)."""
    base = dict(bob=0.0, breath=0.0, nod=0.0, blink=0.0, mouth=0.0, happy=False, wave=0.0, wave_a=0.0)
    base.update(kw)
    return base


def _seg(x0, y0, x1, y1, w):
    """Segment épais (bras) : quadrilatère perpendiculaire à l'axe, quelle que soit la direction."""
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1
    ox, oy = -dy / n * w / 2, dx / n * w / 2
    return poly([(x0 + ox, y0 + oy), (x1 + ox, y1 + oy), (x1 - ox, y1 - oy), (x0 - ox, y0 - oy)])


def _plaid(d, cid, shapes, x0, y0, x1, y1):
    """Carreaux de la chemise : bandes sombres translucides croisées, découpées à la forme du tissu."""
    c = PAL
    d.clip(cid, shapes)
    s = []
    x = x0
    while x <= x1:
        s.append(f"M{x:.2f},{y0:.2f} L{x:.2f},{y1:.2f}")
        x += 4
    y = y0 + 1.5
    while y <= y1:
        s.append(f"M{x0:.2f},{y:.2f} L{x1:.2f},{y:.2f}")
        y += 4
    d.raw(f'<g clip-path="url(#{cid})" opacity="0.45">' + line(" ".join(s), c["shirt_dk"], 1.3) + "</g>")


def _arm(d, sx, sy, ex, ey, hx, hy, cid, palm=False, ang=0.0):
    """Bras : manche à carreaux (épaule -> coude), revers retroussé, avant-bras nu, main."""
    c = PAL
    d.add(_seg(ex, ey, hx, hy, 3.2), c["skin"])                      # avant-bras
    if palm:   # main ouverte qui salue (paume vers l'avant, pouce vers l'intérieur)
        tr = f"rotate({ang:.1f} {hx:.2f} {hy:.2f})"
        d.add(ellipse(hx + 1.9, hy + 0.6, 1.0, 1.6, tr), c["skin"])     # pouce
        d.add(ellipse(hx, hy - 0.6, 2.4, 2.8, tr), c["skin"])
        d.raw(f'<g transform="{tr}">' + line(f"M{hx - 0.9:.2f},{hy - 2.6:.2f} L{hx - 0.9:.2f},{hy - 1.2:.2f} "
                                              f"M{hx + 0.6:.2f},{hy - 2.7:.2f} L{hx + 0.6:.2f},{hy - 1.3:.2f}",
                                              c["skin_dk"], 0.6) + "</g>")
    else:
        d.add(circle(hx, hy, 2.2), c["skin"])
    sleeve = _seg(sx, sy, ex, ey, 4.6)
    puff = circle(sx, sy, 2.5)
    d.add(sleeve, c["shirt"])
    d.add(puff, c["shirt"])
    _plaid(d, cid, [sleeve, puff], min(sx, ex) - 4, min(sy, ey) - 4, max(sx, ex) + 4, max(sy, ey) + 4)
    rot = math.degrees(math.atan2(ey - sy, ex - sx)) - 90
    d.add(rect(ex - 2.55, ey - 0.95, 5.1, 1.9, 0.9, f"rotate({rot:.1f} {ex:.2f} {ey:.2f})"),
          c["shirt_lt"], edge=True)                                    # revers de la manche retroussée


def front(p):
    c = PAL
    d = Drawing(W, H)
    b = p["bob"]
    Y = lambda v: v + b
    d.under.append(f'<ellipse cx="24" cy="{G + 0.2}" rx="11" ry="2.4" fill="#000" opacity="0.2"/>')

    # bottes en caoutchouc (posées au sol, ne bougent pas) et jambes de la salopette
    for x in (20.2, 27.8):
        d.add(leg(x, Y(45), x, 54, 5.4), c["denim"])
    for x, s in ((20.2, -1), (27.8, 1)):
        d.add(ellipse(x + s * 0.5, G - 1.7, 3.7, 1.9), c["boot"])                 # pied
        d.add(rect(x - 3, 51.6, 6, 7.4, 1.4), c["boot"])                          # tige
        d.add(rect(x - 3.3, 51.2, 6.6, 1.9, 0.9), c["boot_dk"], sil=False, edge=True)   # rebord
        d.add(ellipse(x - 1.2, 55.2, 0.7, 1.7), c["boot_lt"], sil=False, opacity=0.8)   # reflet

    # buste : épaules + ventre rond, chemise à carreaux
    shoulders = rect(14.2, Y(28.6), 19.6, 10, 4.5)
    belly = ellipse(24, Y(39.4), 10.4 + p["breath"], 9.2)
    d.add(shoulders, c["shirt"])
    d.add(belly, c["shirt"])
    _plaid(d, "torso", [shoulders, belly], 12, Y(27), 36, Y(49))

    # salopette : bas du ventre en jean, bavette, bretelles, boutons
    d.clip("lower", [rect(0, Y(42.6), 48, 20)])
    d.add(ellipse(24, Y(39.4), 10.4 + p["breath"], 9.2), c["denim"], sil=False, clip="lower")
    d.add(path(f"M18.6,{Y(33.6)} L29.4,{Y(33.6)} L29.8,{Y(43.4)} L18.2,{Y(43.4)} Z"), c["denim"], sil=False)
    d.raw(line(f"M{24 - 9.9 - p['breath']:.2f},{Y(42.6)} L18.4,{Y(42.6)} M29.6,{Y(42.6)} "
               f"L{24 + 9.9 + p['breath']:.2f},{Y(42.6)}", c["denim_dk"], 0.9))
    d.add(rect(21.4, Y(36.2), 5.2, 3.6, 0.8), c["denim_lt"], sil=False, edge=True)   # poche de bavette
    d.raw(line(f"M18.6,{Y(33.6)} L29.4,{Y(33.6)} M18.25,{Y(42.6)} L18.6,{Y(33.6)} M29.4,{Y(33.6)} L29.75,{Y(42.6)}",
               OUTLINE, 0.8))
    for x0, x1 in ((19.6, 17.6), (28.4, 30.4)):
        d.add(_seg(x0, Y(34.4), x1, Y(28.4), 2.4), c["denim"], sil=False, edge=True)
        d.add(circle(x0, Y(34.6), 0.95), c["brass"], sil=False, edge=True)
    d.raw(line(f"M24,{Y(44.2)} L24,{Y(48.4)}", c["denim_dk"], 0.8))            # couture entre les jambes

    # bras : celui de gauche de l'image (sa main droite) peut saluer
    sxL, sxR, sy = 15.2, 32.8, Y(31.4)
    w = p["wave"]
    if w > 0:   # le coude monte, l'avant-bras pivote vers l'extérieur jusqu'à la verticale (+ wave_a)
        ex, ey = sxL - 2.2 - 4.4 * w, sy + 5.8 - 8.6 * w
        phi = (1 - w) * -174 + w * p["wave_a"]     # angle depuis la verticale, sens horaire
        L = 5.8 + 1.4 * w
        hx, hy = ex + math.sin(math.radians(phi)) * L, ey - math.cos(math.radians(phi)) * L
        _arm(d, sxL, sy, ex, ey, hx, hy, "armL", palm=w > 0.5, ang=phi)
    else:
        _arm(d, sxL, sy, sxL - 2.2, sy + 5.8, sxL - 2.8, sy + 11.6, "armL")
    _arm(d, sxR, sy, sxR + 2.2, sy + 5.8, sxR + 2.8, sy + 11.6, "armR")

    # tête (grosse tête de chibi ; HK agrandit tout le visage, menton fixe)
    k = HK
    hy = Y(21) - 9.1 * (k - 1) + p["nod"]
    X = lambda x: 24 + (x - 24) * k
    V = lambda dy: hy + dy * k
    for x in (14.5, 33.5):
        d.add(circle(X(x), V(1.4), 2.0 * k), c["skin"])
        d.add(circle(X(x), V(1.4), 0.9 * k), c["skin_dk"], sil=False)
    d.add(ellipse(24, hy, 9.7 * k, 9.1 * k), c["skin"])
    for s in (-1, 1):   # cheveux gris sur les tempes
        d.add(path(f"M{X(24 + s * 7.6):.2f},{V(-6.6):.2f} Q{X(24 + s * 11.2):.2f},{V(-5.2):.2f} {X(24 + s * 10.4):.2f},{V(0.2):.2f} "
                   f"Q{X(24 + s * 9.6):.2f},{V(-0.6):.2f} {X(24 + s * 9.0):.2f},{V(-0.2):.2f} "
                   f"Q{X(24 + s * 8.6):.2f},{V(-2.6):.2f} {X(24 + s * 7.2):.2f},{V(-3.4):.2f} Z"), c["hair"])

    # chapeau de paille : calotte, ruban, large bord
    crown = path(f"M{X(16.6):.2f},{V(-6.6):.2f} Q{X(16.2):.2f},{V(-13.8):.2f} 24,{V(-13.8):.2f} "
                 f"Q{X(31.8):.2f},{V(-13.8):.2f} {X(31.4):.2f},{V(-6.6):.2f} Z")
    d.add(crown, c["straw"])
    d.clip("crown", [crown])
    d.add(rect(14, V(-11.9), 20, 2.5 * k), c["band"], sil=False, clip="crown")
    d.raw(line(f"M14,{V(-11.9):.2f} L34,{V(-11.9):.2f}", OUTLINE, 0.6).replace("/>", ' clip-path="url(#crown)"/>'))
    d.raw(line(f"M{X(21.8):.2f},{V(-13.0):.2f} Q24,{V(-12.3):.2f} {X(26.2):.2f},{V(-13.0):.2f}", c["straw_dk"], 0.7))   # creux de la calotte
    brim = ellipse(24, V(-6.8), 13.8 * k, 3.3 * k)
    d.add(brim, c["straw"], edge=True)
    d.raw(line(f"M{X(16.2):.2f},{V(-4.8):.2f} Q24,{V(-3.2):.2f} {X(31.8):.2f},{V(-4.8):.2f}", c["straw_dk"], 0.8))
    d.raw(line(f"M{X(13.2):.2f},{V(-6.4):.2f} L{X(14.6):.2f},{V(-5.3):.2f} M{X(33.4):.2f},{V(-5.3):.2f} L{X(34.8):.2f},{V(-6.4):.2f} "
               f"M{X(18.2):.2f},{V(-8.9):.2f} L{X(19):.2f},{V(-7.4):.2f} M{X(29.8):.2f},{V(-8.9):.2f} L{X(29):.2f},{V(-7.4):.2f}",
               c["straw_dk"], 0.7))   # brins de paille

    # visage
    if p["happy"]:
        d.raw(line(f"M{X(18.9):.2f},{V(1.3):.2f} Q{X(20.3):.2f},{V(-0.4):.2f} {X(21.7):.2f},{V(1.3):.2f} "
                   f"M{X(26.3):.2f},{V(1.3):.2f} Q{X(27.7):.2f},{V(-0.4):.2f} {X(29.1):.2f},{V(1.3):.2f}", c["eye"], 1.0))
    elif p["blink"] > 0.5:
        d.raw(line(f"M{X(19.1):.2f},{V(0.7):.2f} Q{X(20.3):.2f},{V(1.5):.2f} {X(21.5):.2f},{V(0.7):.2f} "
                   f"M{X(26.5):.2f},{V(0.7):.2f} Q{X(27.7):.2f},{V(1.5):.2f} {X(28.9):.2f},{V(0.7):.2f}", c["eye"], 0.9))
    else:
        for x in (20.3, 27.7):
            d.add(ellipse(X(x), V(0.6), 1.25 * k, 1.55 * k), c["eye"], sil=False)
            d.add(circle(X(x + 0.4), V(0.0), 0.45 * k), "#FFFFFF", sil=False)
    d.raw(line(f"M{X(18.7):.2f},{V(-2.2):.2f} Q{X(20.3):.2f},{V(-3.1):.2f} {X(21.9):.2f},{V(-2.3):.2f} "
               f"M{X(26.1):.2f},{V(-2.3):.2f} Q{X(27.7):.2f},{V(-3.1):.2f} {X(29.3):.2f},{V(-2.2):.2f}",
               c["hair_dk"], 1.2))                                           # sourcils gris
    for x in (17.8, 30.2):
        d.add(ellipse(X(x), V(3.2), 1.9 * k, 1.15 * k), c["blush"], sil=False, opacity=0.6)
    # bouche (sous la moustache)
    m = p["mouth"]
    if p["happy"]:
        d.add(path(f"M{X(20.8):.2f},{V(5.6):.2f} Q24,{V(10.6):.2f} {X(27.2):.2f},{V(5.6):.2f} Z"), c["mouth"], sil=False, edge=True)
        d.add(ellipse(24, V(7.9), 1.6 * k, 0.8 * k), c["tongue"], sil=False)
    elif m > 0.05:
        d.add(ellipse(24, V(6.5 + m * 0.6), (1.3 + m * 0.6) * k, (0.6 + m * 1.5) * k), c["mouth"], sil=False, edge=True)
        if m > 0.5:
            d.add(ellipse(24, V(7.3 + m * 0.9), 1.1 * k, 0.5 * k), c["tongue"], sil=False)
    else:
        d.raw(line(f"M{X(22.2):.2f},{V(6.9):.2f} Q24,{V(8.1):.2f} {X(25.8):.2f},{V(6.9):.2f}", c["eye"], 0.8))
    # moustache grise en deux mèches, puis le gros nez rond
    d.add(path(f"M24,{V(3.9):.2f} Q{X(21.4):.2f},{V(3.0):.2f} {X(19.2):.2f},{V(4.6):.2f} Q{X(18.6):.2f},{V(6.7):.2f} "
               f"{X(20.9):.2f},{V(6.5):.2f} Q{X(22.8):.2f},{V(6.3):.2f} 24,{V(5.4):.2f} Q{X(25.2):.2f},{V(6.3):.2f} "
               f"{X(27.1):.2f},{V(6.5):.2f} Q{X(29.4):.2f},{V(6.7):.2f} {X(28.8):.2f},{V(4.6):.2f} "
               f"Q{X(26.6):.2f},{V(3.0):.2f} 24,{V(3.9):.2f} Z"), c["hair"], sil=False, edge=True)
    d.raw(line(f"M{X(20.6):.2f},{V(5.0):.2f} Q{X(21.8):.2f},{V(4.5):.2f} {X(22.9):.2f},{V(4.8):.2f} "
               f"M{X(25.1):.2f},{V(4.8):.2f} Q{X(26.2):.2f},{V(4.5):.2f} {X(27.4):.2f},{V(5.0):.2f}", c["hair_dk"], 0.5))
    d.add(ellipse(24, V(2.7), 1.9 * k, 1.5 * k), c["nose"], sil=False, edge=True)
    d.add(circle(X(23.4), V(2.2), 0.5 * k), "#FFFFFF", sil=False, opacity=0.7)
    return d


ANIMS = {   # nom : (poses, fps, boucle)
    "idle": ([F(), F(bob=0.25, breath=0.15), F(bob=0.4, breath=0.3), F(bob=0.25, breath=0.15, blink=1)], 5, True),
    "talk": ([F(mouth=0.2), F(mouth=0.9, nod=0.5), F(mouth=0.35, nod=0.2), F(mouth=0.75, nod=0.6, bob=0.2)], 8, True),
    "wave": ([F(wave=1, wave_a=-28, happy=True), F(wave=1, wave_a=-12, happy=True, bob=0.2),
              F(wave=1, wave_a=4, happy=True), F(wave=1, wave_a=-12, happy=True, bob=0.2)], 8, True),
}


def portrait_states():
    """Trois poses pour le portrait de dialogue : normal, clignement, joyeux (grand sourire)."""
    return [F(), F(blink=1), F(happy=True)]


def frames(anim):
    """SVG des images d'une animation (vue de face)."""
    return [front(p).svg() for p in ANIMS[anim][0]]

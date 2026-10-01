"""
Les habitants du village — PNJ vus de face uniquement (ils regardent vers le bas de l'écran), même style et même
format que le fermier Gaston (farmer.py) : grosse tête de chibi (HK), aplats, contour brun via `Drawing`.

- "postman" : le facteur. Casquette bleu marine à visière (galon jaune, insigne doré), veste bleue à bande jaune
  (poitrine et avant-bras), pantalon bleu foncé, chaussures marron, grosse sacoche de cuir en bandoulière (sur sa
  hanche gauche, donc à droite de l'image) d'où dépasse une enveloppe, moustache brune aux pointes relevées.
- "neighbor" : la voisine, une gentille mamie. Cheveux gris-blanc en chignon (chouchou lilas), petites lunettes
  rondes, boucles d'oreilles en perle, joues roses, gilet lilas ouvert sur un chemisier blanc à col claudine,
  jupe longue bleu ardoise, chaussons roses à pompon. Au repos, elle garde les mains jointes devant elle.
  Elle a perdu son chat (critters "cat_white") : animation `worry`.

Cellule 48 x 64 (W, H), pieds posés sur y = 60 (G) : origine conseillée du sprite (24, 60), comme Gaston.
Hauteurs (contour compris) : le facteur va du haut de la casquette (y ≈ 3.9) au bas des chaussures (y ≈ 61) ; la
mamie, plus petite, du haut du chignon (y ≈ 6.2) au bas des chaussons (y ≈ 61). Gaston : y ≈ 4.4 .. 61.
Têtes de même taille que celle de Gaston. En largeur : x ≈ 9..39 au repos ; la main qui salue va jusqu'à x ≈ 2.8,
la main qui parle jusqu'à x ≈ 45, les bras levés de cheer de x ≈ 1.6 à 46.2 (et le saut monte le haut à y ≈ 1.2).
Rien ne sort de la cellule (l'ombre reste au sol pendant le saut et rétrécit).

Portrait de dialogue : `FACES[kind] = (cx, cy, demi-côté)`, même principe que `farmer.FACE` ; rendre le SVG en
48 x 64 avant de recadrer, comme `hud.farmer_portrait` :
    cx, cy, half = npcs.FACES[kind]
    [_portrait(scale, _crop_face(npcs.front(kind, p).svg(), cx, cy, half, scale, npcs.W, npcs.H), bg=npcs.PORTRAIT_BG[kind])
     for p in npcs.portrait_states(kind)]
`portrait_states(kind)` donne quatre poses : normal, clignement, joyeux, inquiet.

Animations (ANIMS[kind][nom] = (poses, fps, boucle), toutes en boucle, 4 images) :
  idle (5 i/s, respiration + un clignement), talk (8 i/s, bouche qui parle, hochement, la main gauche — à droite
  de l'image — qui accompagne la parole), wave (8 i/s, salue de la main droite levée, à gauche de l'image, en
  souriant), cheer (8 i/s, joie : bras levés et petit saut) ; pour la voisine seulement, worry (5 i/s : mains sur
  les joues, sourcils relevés, elle regarde à gauche puis à droite, une goutte d'inquiétude).

`letter_frames()` : la lettre perdue que Tecky ramasse (objet 32 x 32 comme ceux d'items.py, origine (16, 16)).
"""
import math

from spritelib import Drawing, circle, ellipse, rect, path, poly, leg, line, OUTLINE

W, H = 48, 64
G = 60.0                      # ligne des pieds
HK = 1.08                     # agrandissement de la tête (style chibi), autour du menton — comme Gaston
KINDS = ("postman", "neighbor")
FACES = {                     # portrait : centre du recadrage (cx, cy) et demi-côté conseillé
    "postman": (24, 18.5, 15.5),      # casquette, visage, moustache et menton (comme Gaston)
    "neighbor": (24, 21.5, 15.5),     # chignon, lunettes, menton (elle est plus petite : tout est 3 unités plus bas)
}
PORTRAIT_BG = {"postman": "#CFE0F5", "neighbor": "#E9DDF6"}   # fond conseillé du médaillon (Gaston : "#CFE8B0")

PAL = {
    "postman": dict(skin="#F5C8A6", skin_dk="#E2A986", nose="#EA9C82", blush="#F28A8A",
                    hair="#7A4E2E", hair_dk="#57351D",
                    cap="#2C3E6E", cap_dk="#1E2B50", cap_lt="#46609A", visor="#1A2340", visor_lt="#4A5C8C",
                    jacket="#3F72BD", jacket_dk="#2B5290", jacket_lt="#6F9BDA", band="#F6C83E", band_dk="#D9A520",
                    shirt="#D6E8FA", tie="#22335E", pen="#D7332B",
                    pants="#2E3F69", pants_dk="#223052",
                    shoe="#6B4430", shoe_lt="#9A6A4E",
                    leather="#A8683A", leather_dk="#7E4A25", leather_lt="#C7864F", brass="#F2C14E",
                    paper="#FFFAF0", paper_dk="#D8C8A6", paper2="#DCEBFA",
                    eye="#2A1E1A", mouth="#B8505A", tongue="#E9858B", sweat="#9ED8F5"),
    "neighbor": dict(skin="#F9D9C6", skin_dk="#E9B9A0", nose="#EFA690", blush="#F2879E",
                     hair="#E9E6E1", hair_dk="#B3ADA5", hair_lt="#FFFFFF", scrunchie="#B48ED8",
                     cardigan="#B79AD9", cardigan_dk="#8F70B8", cardigan_lt="#D3C1EC",
                     blouse="#FFFCF5", blouse_dk="#E1D9CB", button="#F6EFFF",
                     skirt="#62729C", skirt_dk="#4A5880", skirt_lt="#7D8DB5",
                     slipper="#EE8FAE", slipper_dk="#D06C8E", pompom="#FFF4F7",
                     pearl="#FFFDF8", lens="#E3F4FB",
                     eye="#2A1E1A", mouth="#B8505A", tongue="#E9858B", sweat="#9ED8F5"),
}


def P(**kw):
    """Pose d'un PNJ.
    bob : décalage vertical du buste (respiration) ; breath : ventre un peu plus large ; lift : tout le corps
    décolle du sol (saut ; l'ombre reste au sol et rétrécit) ; nod : la tête seule descend (hochement) ;
    blink : yeux fermés si > 0.5 ; look : regard de côté (-1 gauche de l'image .. 1 droite) ;
    mouth : 0 bouche fermée -> 1 grande ouverte (parle) ; happy : yeux plissés et grand sourire ;
    worry : 0..1 sourcils relevés au milieu, petite bouche inquiète ; sweat : goutte d'inquiétude sur la tempe ;
    wave : 1 = bras droit (à gauche de l'image) levé qui salue, wave_a : angle (°) de l'avant-bras depuis la
    verticale (négatif = vers l'extérieur) ; gesture : 0..1 main gauche (à droite de l'image) ouverte qui
    accompagne la parole ; cheer : 0..1 les deux bras levés ; cheeks : les deux mains sur les joues."""
    base = dict(bob=0.0, breath=0.0, lift=0.0, nod=0.0, blink=0.0, look=0.0, mouth=0.0, happy=False,
                worry=0.0, sweat=False, wave=0.0, wave_a=0.0, gesture=0.0, cheer=0.0, cheeks=False)
    base.update(kw)
    return base


# ================================================================== outils
def _seg(x0, y0, x1, y1, w):
    """Segment épais (bras) : quadrilatère perpendiculaire à l'axe, quelle que soit la direction."""
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1
    ox, oy = -dy / n * w / 2, dx / n * w / 2
    return poly([(x0 + ox, y0 + oy), (x1 + ox, y1 + oy), (x1 - ox, y1 - oy), (x0 - ox, y0 - oy)])


def _unit(dx, dy):
    n = math.hypot(dx, dy) or 1e-6
    return dx / n, dy / n


def _ik(sx, sy, hx, hy, l1, l2, bx, by):
    """Coude d'un bras à deux segments (épaule (sx, sy) -> main (hx, hy)), plié du côté de la direction (bx, by).
    Main trop loin : le bras se tend et la main est ramenée à portée. Renvoie (coude, main)."""
    dx, dy = hx - sx, hy - sy
    dist = math.hypot(dx, dy) or 1e-6
    reach = l1 + l2 - 0.05
    if dist > reach:
        hx, hy = sx + dx / dist * reach, sy + dy / dist * reach
        dist = reach
    a = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    ux, uy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
    px, py = -uy, ux
    if px * bx + py * by < 0:
        px, py = -px, -py
    return (sx + ux * a + px * h, sy + uy * a + py * h), (hx, hy)


def _fill(xml, color):
    return xml.replace('fill="%F%"', f'fill="{color}"')


def _sticker(d, items, w=1.3):
    """Formes posées PAR-DESSUS ce qui précède (bras devant le corps), avec leur propre contour (union des formes).
    items : liste de (forme, couleur)."""
    for s, _ in items:
        d.raw(s.replace('fill="%F%"', f'fill="{OUTLINE}" stroke="{OUTLINE}" stroke-width="{w:.2f}" '
                                      f'stroke-linejoin="round"'))
    for s, col in items:
        d.raw(_fill(s, col))


def _shadow(d, lift, rx=11.0):
    k = max(0.6, 1 - lift / 10)
    d.under.append(f'<ellipse cx="24" cy="{G + 0.2}" rx="{rx * k:.2f}" ry="{2.4 * k:.2f}" fill="#000" opacity="0.2"/>')


# ------------------------------------------------------------------ bras
def _palm(d, c, hx, hy, ux, uy, s, sticker=None):
    """Main ouverte (paume vers l'avant), doigts dans le prolongement de l'avant-bras, pouce vers l'intérieur."""
    r = math.degrees(math.atan2(ux, -uy))
    tr = f"translate({hx:.2f} {hy:.2f}) rotate({r:.1f})"
    shapes = [(ellipse(-s * 1.9, 0.6, 1.0, 1.6, tr), c["skin"]), (ellipse(0, -0.6, 2.4, 2.8, tr), c["skin"])]
    if sticker is not None:
        sticker.extend(shapes)
    else:
        for sh, col in shapes:
            d.add(sh, col)
    return f'<g transform="{tr}">' + line("M-0.9,-2.6 L-0.9,-1.2 M0.6,-2.7 L0.6,-1.3", c["skin_dk"], 0.6) + "</g>"


def _arm(d, c, s, sx, sy, ex, ey, hx, hy, hand="fist", front=False, band=None):
    """Bras à manche longue : épaule (sx, sy) -> coude (ex, ey) -> centre de la main (hx, hy).
    hand : 'fist' (main ronde) ou 'palm' (main ouverte) ; front : avant-bras et main devant le corps (contour
    propre, sinon la manche se confond avec le buste) ; band : couleur d'une bande sur l'avant-bras (facteur)."""
    ux, uy = _unit(hx - ex, hy - ey)
    wx, wy = hx - ux * 1.9, hy - uy * 1.9                     # poignet
    rot = math.degrees(math.atan2(uy, ux)) - 90
    upper = [(_seg(sx, sy, ex, ey, 4.6), c["sleeve"]), (circle(sx, sy, 2.5), c["sleeve"])]   # manche, épaule
    fore = [(circle(ex, ey, 2.1), c["sleeve"]), (_seg(ex, ey, wx, wy, 4.0), c["sleeve"])]
    details = []
    for sh, col in upper:
        d.add(sh, col)
    if front:   # tout le bras repasse par-dessus, avec son contour
        st = []
        if hand == "palm":
            details.append(_palm(d, c, hx, hy, ux, uy, s, st))
        else:
            st.append((circle(hx, hy, 2.15), c["skin"]))
        _sticker(d, st + [(_seg(sx, sy + 1.2, ex, ey, 4.6), c["sleeve"])] + fore)
    else:
        if hand == "palm":
            details.append(_palm(d, c, hx, hy, ux, uy, s))
        else:
            d.add(circle(hx, hy, 2.15), c["skin"])
        for sh, col in fore:
            d.add(sh, col)
    if band:   # bande jaune autour de l'avant-bras
        mx, my = (ex + wx) / 2, (ey + wy) / 2
        d.add(rect(mx - 2.0, my - 0.6, 4.0, 1.2, 0, f"rotate({rot:.1f} {mx:.2f} {my:.2f})"), band, sil=False)
    d.add(rect(wx - 2.4, wy - 0.85, 4.8, 1.7, 0.8, f"rotate({rot:.1f} {wx:.2f} {wy:.2f})"), c["cuff"],
          sil=False, edge=True)                                # poignet de la manche
    for x in details:
        d.raw(x)


def _arms(d, c, p, sxL, sxR, sy, rest, head=None, band=None):
    """Pose les deux bras selon la pose p. rest(s, sx) -> (coude ou None, main, devant ?) pour un bras au repos ;
    head : (X, V) du visage pour les mains sur les joues."""
    todo = []
    for s, sx in ((-1, sxL), (1, sxR)):
        hand, front, elbow = "fist", False, None
        if p["cheer"] > 0:                       # bras levés en Y, mains ouvertes
            a = math.radians(38 + (1 - p["cheer"]) * 40)   # en Y, bien à l'écart de la grosse tête
            tgt = (sx + s * 11.8 * math.sin(a), sy - 11.8 * math.cos(a))
            elbow, tgt = _ik(sx, sy, *tgt, 6.2, 6.0, s, 1.0)
            hand = "palm"
        elif p["cheeks"] and head:               # mains sur les joues (inquiète)
            X, V = head
            tgt = (X(24 + s * 8.0), V(4.0))
            elbow, tgt = _ik(sx, sy, *tgt, 6.2, 6.0, s, 0.3)
            front = True
        elif s == -1 and p["wave"] > 0:           # main droite levée qui salue (comme Gaston)
            elbow = (sx - 5.6, sy - 1.4)
            phi = math.radians(p["wave_a"])
            tgt = (elbow[0] + math.sin(phi) * 6.2, elbow[1] - math.cos(phi) * 6.2)
            hand = "palm"
        elif s == 1 and p["gesture"] > 0:         # main gauche ouverte qui accompagne la parole
            g = p["gesture"]
            elbow = (sx + 1.6, sy + 6.0)
            a = math.radians(84 - 22 * g)        # angle de l'avant-bras depuis la verticale, vers l'extérieur
            tgt = (elbow[0] + math.sin(a) * 6.2, elbow[1] - math.cos(a) * 6.2)
            hand = "palm"
        else:
            elbow, tgt, front = rest(s, sx)
        todo.append((front, s, sx, elbow, tgt, hand))
    for front, s, sx, elbow, tgt, hand in sorted(todo, key=lambda t: t[0]):   # les bras devant le corps en dernier
        _arm(d, c, s, sx, sy, elbow[0], elbow[1], tgt[0], tgt[1], hand, front, band)


# ------------------------------------------------------------------ visage
def _eyes(d, c, p, X, V, rx=1.25, ry=1.55):
    if p["happy"]:
        d.raw(line(f"M{X(18.9):.2f},{V(1.3):.2f} Q{X(20.3):.2f},{V(-0.4):.2f} {X(21.7):.2f},{V(1.3):.2f} "
                   f"M{X(26.3):.2f},{V(1.3):.2f} Q{X(27.7):.2f},{V(-0.4):.2f} {X(29.1):.2f},{V(1.3):.2f}", c["eye"], 1.0))
    elif p["blink"] > 0.5:
        d.raw(line(f"M{X(19.1):.2f},{V(0.7):.2f} Q{X(20.3):.2f},{V(1.5):.2f} {X(21.5):.2f},{V(0.7):.2f} "
                   f"M{X(26.5):.2f},{V(0.7):.2f} Q{X(27.7):.2f},{V(1.5):.2f} {X(28.9):.2f},{V(0.7):.2f}", c["eye"], 0.9))
    else:
        lk = p["look"] * 0.55
        for x in (20.3, 27.7):
            d.add(ellipse(X(x + lk), V(0.6), rx * HK, ry * HK), c["eye"], sil=False)
            d.add(circle(X(x + lk + 0.4), V(0.0), 0.45 * HK), "#FFFFFF", sil=False)


def _brows(d, p, X, V, col, w=1.2):
    """Sourcils ; worry relève leur bout intérieur (air inquiet)."""
    q = p["worry"]
    d.raw(line(f"M{X(18.7):.2f},{V(-2.2 + 0.3 * q):.2f} Q{X(20.3):.2f},{V(-3.1 - 0.3 * q):.2f} {X(21.9):.2f},{V(-2.3 - 1.3 * q):.2f} "
               f"M{X(26.1):.2f},{V(-2.3 - 1.3 * q):.2f} Q{X(27.7):.2f},{V(-3.1 - 0.3 * q):.2f} {X(29.3):.2f},{V(-2.2 + 0.3 * q):.2f}",
               col, w))


def _blush(d, c, X, V, y=3.2):
    for x in (17.8, 30.2):
        d.add(ellipse(X(x), V(y), 1.9 * HK, 1.15 * HK), c["blush"], sil=False, opacity=0.6)


def _mouth(d, c, p, X, V, y, size=1.0):
    """Bouche dont le haut est vers V(y) : grand sourire (happy), parle (mouth), inquiète (worry) ou sourire."""
    m = p["mouth"]
    if p["happy"]:
        d.add(path(f"M{X(24 - 3.2 * size):.2f},{V(y - 0.9):.2f} Q24,{V(y + 4.1 * size):.2f} {X(24 + 3.2 * size):.2f},{V(y - 0.9):.2f} Z"),
              c["mouth"], sil=False, edge=True)
        d.add(ellipse(24, V(y + 1.4 * size), 1.6 * size * HK, 0.8 * HK), c["tongue"], sil=False)
    elif m > 0.05:
        d.add(ellipse(24, V(y + m * 0.6), (1.3 + m * 0.6) * HK, (0.6 + m * 1.5) * HK), c["mouth"], sil=False, edge=True)
        if m > 0.5:
            d.add(ellipse(24, V(y + 0.8 + m * 0.9), 1.1 * HK, 0.5 * HK), c["tongue"], sil=False)
    elif p["worry"] > 0.3:     # petite bouche ondulée
        d.raw(line(f"M{X(22.0):.2f},{V(y + 0.9):.2f} Q{X(23.0):.2f},{V(y - 0.1):.2f} 24,{V(y + 0.5):.2f} "
                   f"Q{X(25.0):.2f},{V(y + 1.1):.2f} {X(26.0):.2f},{V(y + 0.2):.2f}", c["eye"], 0.85))
    else:
        d.raw(line(f"M{X(22.2):.2f},{V(y + 0.4):.2f} Q24,{V(y + 1.6):.2f} {X(25.8):.2f},{V(y + 0.4):.2f}", c["eye"], 0.8))


def _sweat(d, c, X, V):
    """Goutte d'inquiétude sur la tempe (à droite de l'image)."""
    x, y = X(32.4), V(-4.2)
    d.add(path(f"M{x:.2f},{y - 2.0:.2f} Q{x + 1.6:.2f},{y + 0.4:.2f} {x:.2f},{y + 1.2:.2f} "
               f"Q{x - 1.6:.2f},{y + 0.4:.2f} {x:.2f},{y - 2.0:.2f} Z"), c["sweat"], sil=False, edge=True)
    d.add(ellipse(x - 0.4, y + 0.1, 0.35, 0.6), "#FFFFFF", sil=False, opacity=0.9)


def _head_frame(Y, p):
    """Centre de la tête et fonctions de placement (HK agrandit le visage autour du menton, comme Gaston)."""
    hy = Y(21) - 9.1 * (HK - 1) + p["nod"]
    return hy, (lambda x: 24 + (x - 24) * HK), (lambda dy: hy + dy * HK)


# ================================================================== LE FACTEUR
def _postman(p):
    c = dict(PAL["postman"], sleeve=PAL["postman"]["jacket"], cuff=PAL["postman"]["jacket_dk"])
    d = Drawing(W, H)
    L = p["lift"]
    Y = lambda v: v + p["bob"] - L          # buste (respire, saute)
    T = lambda v: v - L                     # jambes et pieds (sautent seulement)
    _shadow(d, L, 10.6)

    # chaussures puis jambes du pantalon (le bas du pantalon recouvre le haut des chaussures)
    for x, s in ((20.4, -1), (27.6, 1)):
        d.add(ellipse(x + s * 0.6, T(G - 1.7), 3.6, 1.9), c["shoe"])
        d.add(ellipse(x + s * 0.6 - 1.1, T(G - 2.5), 1.1, 0.55), c["shoe_lt"], sil=False, opacity=0.9)
    for x in (20.4, 27.6):
        d.add(leg(x, Y(44), x, T(57.0), 5.2), c["pants"])
    d.raw(line(f"M20.4,{Y(47.4):.2f} L20.4,{T(56.2):.2f} M27.6,{Y(47.4):.2f} L27.6,{T(56.2):.2f}", c["pants_dk"], 0.7))

    # veste bleue : buste + ventre, bande jaune, ceinture élastique, fermeture
    jacket = rect(14.2, Y(28.6), 19.6, 17.4, 4.8)
    belly = ellipse(24, Y(39.6), 10.0 + p["breath"], 6.6)
    d.add(jacket, c["jacket"])
    d.add(belly, c["jacket"])
    d.clip("jacket", [jacket, belly])
    d.add(rect(8, Y(36.4), 32, 2.0), c["band"], sil=False, clip="jacket")
    d.raw(f'<g clip-path="url(#jacket)">' + line(f"M8,{Y(36.4):.2f} L40,{Y(36.4):.2f} M8,{Y(38.4):.2f} L40,{Y(38.4):.2f}",
                                                 c["band_dk"], 0.5) + "</g>")
    d.add(rect(8, Y(43.8), 32, 3.0), c["jacket_dk"], sil=False, clip="jacket")
    d.raw(line(f"M24,{Y(33.4):.2f} L24,{Y(45.6):.2f}", c["jacket_dk"], 0.8))
    # col de chemise et cravate
    d.add(poly([(20.2, Y(28.9)), (27.8, Y(28.9)), (24, Y(33.8))]), c["shirt"], sil=False, edge=True)
    d.add(poly([(23.1, Y(30.2)), (24.9, Y(30.2)), (25.1, Y(32.6)), (24, Y(33.6)), (22.9, Y(32.6))]), c["tie"],
          sil=False, edge=True)
    # poche de poitrine (à droite de l'image) et son stylo rouge
    d.add(rect(28.9, Y(31.0), 1.5, 3.4, 0.7), c["pen"], sil=False, edge=True)
    d.add(rect(27.4, Y(33.4), 4.8, 1.5, 0.6), c["jacket_dk"], sil=False, edge=True)

    # bandoulière (de son épaule droite à la sacoche), enveloppes qui dépassent, sacoche
    d.add(_seg(18.0, Y(29.2), 26.6, Y(42.0), 2.3), c["leather_dk"], sil=False, edge=True)
    d.add(rect(29.3, Y(38.6), 4.6, 3.4, 0.4, f"rotate(9 31.6 {Y(40.3):.2f})"), c["paper2"], sil=False, edge=True)
    etr = f"rotate(-13 27.8 {Y(40.0):.2f})"
    d.add(rect(24.9, Y(37.7), 5.8, 4.4, 0.4, etr), c["paper"], sil=False, edge=True)
    d.raw(f'<g transform="{etr}">' + line(f"M25.3,{Y(38.1):.2f} L27.8,{Y(40.0):.2f} L30.3,{Y(38.1):.2f}", c["paper_dk"], 0.6)
          + "</g>")
    d.add(rect(24.6, Y(40.8), 10.4, 7.6, 1.6), c["leather"], edge=True)
    d.add(rect(24.3, Y(40.5), 11.0, 4.6, 1.6), c["leather_lt"], edge=True)                     # rabat
    d.raw(line(f"M25.5,{Y(43.9):.2f} L34.1,{Y(43.9):.2f}", c["leather"], 0.5).replace("/>", ' stroke-dasharray="0.9 0.7"/>'))
    d.add(rect(28.6, Y(44.2), 2.6, 2.0, 0.5), c["brass"], sil=False, edge=True)                 # boucle
    d.add(rect(29.4, Y(44.8), 1.0, 0.8, 0.2), c["leather_dk"], sil=False)

    # bras
    def rest(s, sx):
        return (sx + s * 2.2, Y(31.2) + 5.8), (sx + s * 2.8, Y(31.2) + 11.6), False

    hy, X, V = _head_frame(Y, p)
    _arms(d, c, p, 15.0, 33.0, Y(31.2), rest, band=c["band"])

    # tête : oreilles, visage, cheveux bruns sur les tempes
    k = HK
    for x in (14.5, 33.5):
        d.add(circle(X(x), V(1.4), 2.0 * k), c["skin"])
        d.add(circle(X(x), V(1.4), 0.9 * k), c["skin_dk"], sil=False)
    d.add(ellipse(24, hy, 9.7 * k, 9.1 * k), c["skin"])
    for s in (-1, 1):
        d.add(path(f"M{X(24 + s * 7.8):.2f},{V(-6.6):.2f} Q{X(24 + s * 11.0):.2f},{V(-5.0):.2f} {X(24 + s * 10.2):.2f},{V(0.6):.2f} "
                   f"Q{X(24 + s * 9.5):.2f},{V(-0.2):.2f} {X(24 + s * 8.9):.2f},{V(0.2):.2f} "
                   f"Q{X(24 + s * 8.5):.2f},{V(-2.6):.2f} {X(24 + s * 7.0):.2f},{V(-3.6):.2f} Z"), c["hair"])

    # casquette : calotte (plus large en haut), bandeau à galon jaune, insigne doré, visière
    top = ellipse(24, V(-11.6), 10.4 * k, 2.7 * k)
    crown = poly([(X(13.8), V(-11.6)), (X(34.2), V(-11.6)), (X(32.6), V(-6.4)), (X(15.4), V(-6.4))])
    d.add(crown, c["cap"])
    d.add(top, c["cap"])
    d.add(ellipse(24, V(-12.2), 7.4 * k, 1.5 * k), c["cap_lt"], sil=False, opacity=0.8)
    d.add(rect(X(15.0), V(-9.6), 18.0 * k, 3.2 * k), c["cap_dk"], sil=False, edge=True)
    d.raw(line(f"M{X(15.4):.2f},{V(-9.0):.2f} L{X(32.6):.2f},{V(-9.0):.2f}", c["band"], 0.7))
    d.add(ellipse(24, V(-9.6), 1.9 * k, 2.1 * k), c["brass"], sil=False, edge=True)
    d.add(path(f"M{X(22.9):.2f},{V(-10.2):.2f} L24,{V(-9.2):.2f} L{X(25.1):.2f},{V(-10.2):.2f}"), c["brass"], sil=False)
    d.raw(line(f"M{X(22.9):.2f},{V(-10.3):.2f} L24,{V(-9.3):.2f} L{X(25.1):.2f},{V(-10.3):.2f}", c["leather_dk"], 0.45))
    visor = path(f"M{X(14.6):.2f},{V(-6.6):.2f} L{X(33.4):.2f},{V(-6.6):.2f} Q{X(33.0):.2f},{V(-3.6):.2f} 24,{V(-3.3):.2f} "
                 f"Q{X(15.0):.2f},{V(-3.6):.2f} {X(14.6):.2f},{V(-6.6):.2f} Z")
    d.add(visor, c["visor"], edge=True)
    d.raw(line(f"M{X(18.0):.2f},{V(-5.4):.2f} Q24,{V(-4.4):.2f} {X(30.0):.2f},{V(-5.4):.2f}", c["visor_lt"], 0.7))

    # visage
    _eyes(d, c, p, X, V)
    _brows(d, p, X, V, c["hair_dk"], 1.3)
    _blush(d, c, X, V)
    _mouth(d, c, p, X, V, 6.5)
    # moustache brune en deux mèches aux pointes relevées, puis le nez
    d.add(path(f"M24,{V(4.0):.2f} Q{X(21.8):.2f},{V(3.1):.2f} {X(19.8):.2f},{V(4.3):.2f} Q{X(18.9):.2f},{V(4.6):.2f} "
               f"{X(18.3):.2f},{V(3.5):.2f} Q{X(17.7):.2f},{V(5.6):.2f} {X(19.6):.2f},{V(6.2):.2f} "
               f"Q{X(22.4):.2f},{V(6.9):.2f} 24,{V(5.5):.2f} Q{X(25.6):.2f},{V(6.9):.2f} {X(28.4):.2f},{V(6.2):.2f} "
               f"Q{X(30.3):.2f},{V(5.6):.2f} {X(29.7):.2f},{V(3.5):.2f} Q{X(29.1):.2f},{V(4.6):.2f} {X(28.2):.2f},{V(4.3):.2f} "
               f"Q{X(26.2):.2f},{V(3.1):.2f} 24,{V(4.0):.2f} Z"), c["hair"], sil=False, edge=True)
    d.raw(line(f"M{X(20.4):.2f},{V(5.2):.2f} Q{X(21.7):.2f},{V(4.6):.2f} {X(22.9):.2f},{V(4.9):.2f} "
               f"M{X(25.1):.2f},{V(4.9):.2f} Q{X(26.3):.2f},{V(4.6):.2f} {X(27.6):.2f},{V(5.2):.2f}", c["hair_dk"], 0.5))
    d.add(ellipse(24, V(2.7), 1.6 * k, 1.3 * k), c["nose"], sil=False, edge=True)
    d.add(circle(X(23.5), V(2.3), 0.42 * k), "#FFFFFF", sil=False, opacity=0.7)
    if p["sweat"]:
        _sweat(d, c, X, V)
    return d


# ================================================================== LA VOISINE
DY = 3.0      # la mamie est plus petite : tout le haut du corps est 3 unités plus bas que chez Gaston


def _neighbor(p):
    c = dict(PAL["neighbor"], sleeve=PAL["neighbor"]["cardigan"], cuff=PAL["neighbor"]["cardigan_lt"])
    d = Drawing(W, H)
    L = p["lift"]
    Y = lambda v: v + DY + p["bob"] - L
    T = lambda v: v - L
    _shadow(d, L, 10.4)

    # chevilles et chaussons roses à pompon
    for x, s in ((21.0, -1), (27.0, 1)):
        d.add(leg(x, T(55.5), x, T(G - 2.2), 2.6), c["skin"])
        d.add(ellipse(x + s * 0.5, T(G - 1.5), 3.4, 1.8), c["slipper"])
        d.add(ellipse(x + s * 0.5, T(G - 2.4), 2.2, 0.7), c["slipper_dk"], sil=False, opacity=0.7)
        d.raw(f'<circle cx="{x + s * 0.2:.2f}" cy="{T(G - 2.6):.2f}" r="1.4" fill="{c["pompom"]}" '
              f'stroke="{OUTLINE}" stroke-width="0.5"/>')                                      # pompon

    # jupe longue évasée, plis
    skirt = path(f"M17.0,{Y(37.0):.2f} L31.0,{Y(37.0):.2f} L34.8,{T(56.6):.2f} Q24,{T(58.2):.2f} 13.2,{T(56.6):.2f} Z")
    d.add(skirt, c["skirt"])
    d.raw(line(f"M20.8,{Y(43.0):.2f} L19.2,{T(56.6):.2f} M27.2,{Y(43.0):.2f} L28.8,{T(56.6):.2f} "
               f"M24,{Y(45.0):.2f} L24,{T(57.2):.2f}", c["skirt_dk"], 0.8))
    d.clip("skirt", [skirt])
    d.raw(f'<g clip-path="url(#skirt)">' + line(f"M12,{T(55.6):.2f} Q24,{T(57.2):.2f} 36,{T(55.6):.2f}", c["skirt_lt"], 0.9)
          + "</g>")

    # gilet lilas (épaules + ventre rond), ouvert en V sur le chemisier, boutonné en bas
    shoulders = rect(14.6, Y(28.8), 18.8, 9.6, 4.6)
    belly = ellipse(24, Y(37.6), 9.9 + p["breath"], 7.2)
    d.add(shoulders, c["cardigan"])
    d.add(belly, c["cardigan"])
    d.clip("cardigan", [shoulders, belly])
    d.add(poly([(19.8, Y(28.9)), (28.2, Y(28.9)), (24, Y(36.2))]), c["blouse"], sil=False, edge=True)
    for s in (-1, 1):   # col claudine
        d.add(ellipse(24 + s * 2.3, Y(30.9), 2.6, 1.5, f"rotate({s * 18} {24 + s * 2.3} {Y(30.9):.2f})"), c["blouse"],
              sil=False, edge=True)
    d.add(circle(24, Y(33.0), 0.55), c["blouse_dk"], sil=False)
    d.raw(line(f"M24,{Y(36.2):.2f} L24,{Y(44.6):.2f}", c["cardigan_dk"], 0.8))
    for y in (38.0, 41.0):
        d.add(circle(24.9, Y(y), 0.75), c["button"], sil=False, edge=True)

    # bras : au repos, mains jointes devant elle
    hy, X, V = _head_frame(Y, p)

    def rest(s, sx):
        (ex, ey), tgt = _ik(sx, Y(31.4), 24 + s * 1.3, Y(40.9), 6.2, 6.0, s, 0.2)
        return (ex, ey), tgt, True

    _arms(d, c, p, 15.4, 32.6, Y(31.4), rest, head=(X, V))

    # tête : chignon, oreilles (perles), visage, cheveux gris-blanc
    k = HK
    d.add(circle(24, V(-11.0), 3.9 * k), c["hair"])                                           # chignon
    d.raw(line(f"M{X(21.6):.2f},{V(-12.2):.2f} Q24,{V(-14.0):.2f} {X(26.6):.2f},{V(-12.0):.2f} "
               f"M{X(22.2):.2f},{V(-10.2):.2f} Q24,{V(-11.6):.2f} {X(25.6):.2f},{V(-10.4):.2f}", c["hair_dk"], 0.6))
    for x in (14.5, 33.5):
        d.add(circle(X(x), V(1.6), 2.0 * k), c["skin"])
        d.add(circle(X(x), V(1.6), 0.9 * k), c["skin_dk"], sil=False)
    d.add(ellipse(24, hy, 9.7 * k, 9.1 * k), c["skin"])
    for x in (14.4, 33.6):
        d.add(circle(X(x), V(3.9), 0.85), c["pearl"], sil=False, edge=True)
    hair = path(f"M{X(14.6):.2f},{V(1.2):.2f} Q{X(13.0):.2f},{V(-9.6):.2f} 24,{V(-10.2):.2f} "
                f"Q{X(35.0):.2f},{V(-9.6):.2f} {X(33.4):.2f},{V(1.2):.2f} "
                f"Q{X(32.6):.2f},{V(-2.4):.2f} {X(31.2):.2f},{V(-3.2):.2f} Q{X(29.2):.2f},{V(-3.4):.2f} {X(27.8):.2f},{V(-4.6):.2f} "
                f"Q{X(25.8):.2f},{V(-6.0):.2f} 24,{V(-6.4):.2f} Q{X(22.2):.2f},{V(-6.0):.2f} {X(20.2):.2f},{V(-4.6):.2f} "
                f"Q{X(18.8):.2f},{V(-3.4):.2f} {X(16.8):.2f},{V(-3.2):.2f} Q{X(15.4):.2f},{V(-2.4):.2f} {X(14.6):.2f},{V(1.2):.2f} Z")
    d.add(hair, c["hair"])
    d.raw(line(f"M24,{V(-6.4):.2f} Q{X(19.4):.2f},{V(-9.4):.2f} {X(15.6):.2f},{V(-4.4):.2f} "
               f"M24,{V(-6.4):.2f} Q{X(28.6):.2f},{V(-9.4):.2f} {X(32.4):.2f},{V(-4.4):.2f} "
               f"M24,{V(-6.4):.2f} L24,{V(-9.6):.2f}", c["hair_dk"], 0.6))
    d.add(ellipse(X(19.2), V(-7.6), 2.4 * k, 1.0 * k, f"rotate(-24 {X(19.2):.2f} {V(-7.6):.2f})"), c["hair_lt"],
          sil=False, opacity=0.8)
    d.add(ellipse(24, V(-10.3), 3.5 * k, 1.15 * k), c["scrunchie"], sil=False, edge=True)        # chouchou du chignon
    d.raw(line(f"M{X(22.2):.2f},{V(-10.9):.2f} L{X(22.0):.2f},{V(-9.7):.2f} M{X(25.8):.2f},{V(-10.9):.2f} "
               f"L{X(26.0):.2f},{V(-9.7):.2f}", c["cardigan_dk"], 0.5))

    # visage : yeux, petites lunettes rondes, sourcils, joues, bouche, petit nez
    _eyes(d, c, p, X, V, 1.1, 1.4)
    _blush(d, c, X, V, 3.6)
    _mouth(d, c, p, X, V, 5.6, 0.85)
    d.add(ellipse(24, V(2.9), 1.15 * k, 0.95 * k), c["nose"], sil=False, edge=True)
    for x in (20.3, 27.7):
        d.raw(f'<circle cx="{X(x):.2f}" cy="{V(0.6):.2f}" r="{2.55 * k:.2f}" fill="{c["lens"]}" fill-opacity="0.18" '
              f'stroke="{OUTLINE}" stroke-width="0.7"/>')
        d.raw(line(f"M{X(x - 1.6):.2f},{V(-0.4):.2f} Q{X(x - 1.2):.2f},{V(-1.3):.2f} {X(x - 0.3):.2f},{V(-1.6):.2f}",
                   "#FFFFFF", 0.5))
    d.raw(line(f"M{X(22.85):.2f},{V(0.3):.2f} Q24,{V(-0.5):.2f} {X(25.15):.2f},{V(0.3):.2f} "
               f"M{X(17.75):.2f},{V(0.2):.2f} L{X(14.9):.2f},{V(-0.2):.2f} M{X(30.25):.2f},{V(0.2):.2f} L{X(33.1):.2f},{V(-0.2):.2f}",
               OUTLINE, 0.7))
    _brows(d, p, X, V, c["hair_dk"], 1.1)
    if p["sweat"]:
        _sweat(d, c, X, V)
    if p["cheeks"]:   # les mains, posées sur les joues, passent devant le visage
        for s in (-1, 1):
            hx, hy_ = X(24 + s * 8.0), V(4.0)
            _sticker(d, [(ellipse(hx, hy_, 2.2, 2.6, f"rotate({-s * 12} {hx:.2f} {hy_:.2f})"), c["skin"])], 1.0)
            d.raw(line(f"M{hx - s * 0.9:.2f},{hy_ - 1.8:.2f} L{hx - s * 0.9:.2f},{hy_ - 0.6:.2f} "
                       f"M{hx + s * 0.5:.2f},{hy_ - 2.0:.2f} L{hx + s * 0.5:.2f},{hy_ - 0.8:.2f}", c["skin_dk"], 0.55))
    return d


# ================================================================== animations
_DRAW = {"postman": _postman, "neighbor": _neighbor}

_WAVE = [P(wave=1, wave_a=-28, happy=True), P(wave=1, wave_a=-12, happy=True, bob=0.2),
         P(wave=1, wave_a=4, happy=True), P(wave=1, wave_a=-12, happy=True, bob=0.2)]
_IDLE = [P(), P(bob=0.25, breath=0.15), P(bob=0.4, breath=0.3), P(bob=0.25, breath=0.15, blink=1)]
_TALK = [P(mouth=0.2, gesture=0.4), P(mouth=0.9, nod=0.5, gesture=1.0), P(mouth=0.35, nod=0.2, gesture=0.75),
         P(mouth=0.75, nod=0.6, bob=0.2, gesture=1.0)]

ANIMS = {   # PNJ : {nom : (poses, fps, boucle)}
    "postman": {
        "idle": (_IDLE, 5, True),
        "talk": (_TALK, 8, True),
        "wave": (_WAVE, 8, True),
        "cheer": ([P(cheer=0.6, happy=True, bob=0.4), P(cheer=1, happy=True, lift=1.8),
                   P(cheer=1, happy=True, lift=2.6), P(cheer=0.85, happy=True, lift=1.0)], 8, True),
    },
    "neighbor": {
        "idle": (_IDLE, 5, True),
        "talk": (_TALK, 8, True),
        "wave": (_WAVE, 8, True),
        "cheer": ([P(cheer=0.6, happy=True, bob=0.4), P(cheer=1, happy=True, lift=1.4),
                   P(cheer=1, happy=True, lift=2.0), P(cheer=0.85, happy=True, lift=0.8)], 8, True),
        "worry": ([P(worry=1, cheeks=True, look=-1, sweat=True), P(worry=1, cheeks=True, look=-1, bob=0.25, sweat=True),
                   P(worry=1, cheeks=True, look=1, sweat=True), P(worry=1, cheeks=True, look=1, bob=0.25, blink=1, sweat=True)],
                  5, True),
    },
}


def front(kind, p):
    """Dessin (Drawing) d'un PNJ vu de face dans la pose p (voir P)."""
    return _DRAW[kind](p)


def portrait_states(kind):
    """Quatre poses pour le portrait de dialogue : normal, clignement, joyeux (grand sourire), inquiet."""
    return [P(), P(blink=1), P(happy=True), P(worry=1, sweat=kind == "neighbor")]


def frames(kind, anim):
    """SVG des images d'une animation (vue de face)."""
    return [front(kind, p).svg() for p in ANIMS[kind][anim][0]]


# ================================================================== la lettre perdue
LW = LH = 32      # comme les objets d'items.py : origine conseillée (16, 16)


def _letter(d, flap=0.0):
    """Enveloppe crème vue de dos (rabat en V), petit timbre rouge oblitéré ; flap : le rabat se soulève un peu."""
    d.add(rect(5.4, 10.4, 21.2, 14.2, 1.6), "#FFF8EA")
    d.raw(line("M6.6,23.6 L13.8,17.9 M25.4,23.6 L18.2,17.9", "#D9C8A6", 0.8))                 # plis du dos
    tip = 19.4 - flap * 1.6
    d.add(poly([(5.9, 10.9), (26.1, 10.9), (16, tip)]), "#F2E4C6", sil=False, edge=True)      # rabat
    d.add(circle(16, tip - 1.6, 1.3), "#E9D5AE", sil=False, opacity=0.8)                      # pointe collée
    # timbre (bord blanc dentelé) dans le coin
    d.add(rect(20.2, 12.0, 5.0, 5.8, 0.3), "#FFFFFF", sil=False, edge=True)
    for k in range(4):
        d.add(circle(20.2 + 0.4 + k * 1.4, 12.0, 0.32), "#F2E4C6", sil=False)
        d.add(circle(20.2 + 0.4 + k * 1.4, 17.8, 0.32), "#F2E4C6", sil=False)
    d.add(rect(20.9, 12.7, 3.6, 4.4, 0.3), "#D7332B", sil=False)
    d.add(path("M22.7,16.0 C21.4,15.1 21.2,14.5 21.2,14.1 C21.2,13.6 21.6,13.3 22.0,13.3 C22.3,13.3 22.6,13.5 22.7,13.8 "
               "C22.8,13.5 23.1,13.3 23.4,13.3 C23.8,13.3 24.2,13.6 24.2,14.1 C24.2,14.5 24.0,15.1 22.7,16.0 Z"),
          "#FFE3E3", sil=False)                                                                 # petit cœur
    d.raw(line("M15.4,13.0 q0.9,-0.8 1.8,0 t1.8,0 t1.8,0 M15.4,14.8 q0.9,-0.8 1.8,0 t1.8,0 t1.8,0", "#8E96A3", 0.55))


def letter_frames():
    """4 SVG 32 x 32 : la lettre perdue qui frémit au vent (petite rotation, le rabat se soulève, léger rebond)
    au-dessus de son ombre, avec l'éclat de brillance des objets. Origine conseillée (16, 16), comme item/*."""
    out = []
    for i in range(4):
        t = i / 4 * 2 * math.pi
        a = 5 * math.sin(t)
        bob = -1.2 + 0.9 * math.cos(t)
        k = 1 - 0.18 * (-bob / 2.1)
        d = Drawing(LW, LH)
        d.under.append(f'<ellipse cx="16" cy="29.5" rx="{9 * k:.2f}" ry="{1.8 * k:.2f}" fill="#000" opacity="0.2"/>')
        _letter(d, flap=[0.0, 0.6, 1.0, 0.4][i])
        if i == 2:
            d.raw(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in _star(27.5, 6.5, 3.0, 1.05))}" '
                  f'fill="#FFFFFF" stroke="{OUTLINE}" stroke-width="0.5"/>')
        out.append(d.svg(f"translate(0 {bob:.2f}) rotate({a:.1f} 16 17.5)"))
    return out


def _star(cx, cy, r1, r2, n=4):
    pts = []
    for i in range(n * 2):
        a = i * math.pi / n - math.pi / 2
        r = r1 if i % 2 == 0 else r2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ================================================================== planche de contrôle
if __name__ == "__main__":
    import os

    import numpy as np
    from PIL import Image, ImageDraw

    import critters
    import farmer
    import hud
    import items
    from spritelib import render_svg, PAD

    OUT = "/tmp/claude-1000/-home-cgerardin-Sources-314-SOFTWARE-tecky-quest/6b721a3c-761f-447f-a079-6967b45600df/scratchpad"
    os.makedirs(OUT, exist_ok=True)
    BG = (222, 238, 206, 255)
    S = 4

    def touches_edge(im):
        a = np.array(im.getchannel("A"))
        return any((e > 0).sum() for e in (a[0], a[-1], a[:, 0], a[:, -1]))

    def sheet(rows, fn, gap=10, label_w=150):
        """rows : liste de (étiquette, [images])."""
        w = label_w + max(sum(im.width + gap for im in ims) for _, ims in rows)
        h = sum(max(im.height for im in ims) + gap for _, ims in rows) + gap
        out = Image.new("RGBA", (w, h), BG)
        dr = ImageDraw.Draw(out)
        f = hud.font(22)
        y = gap
        for lab, ims in rows:
            dr.text((8, y + 8), lab, font=f, fill=(58, 30, 18, 255))
            x = label_w
            for im in ims:
                out.alpha_composite(im, (x, y))
                x += im.width + gap
            y += max(im.height for im in ims) + gap
        out.save(fn)
        return fn

    # contrôle : rien ne touche le bord (rendu avec la marge PAD, à l'échelle du jeu et de la planche),
    # et rien ne sort de la cellule 48 x 64 (rendu sans marge)
    bad = []
    for kind in KINDS:
        for a in ANIMS[kind]:
            for i, sv in enumerate(frames(kind, a)):
                for sc in (2, S):
                    if touches_edge(render_svg(sv, W, H, sc, PAD)):
                        bad.append(f"{kind}/{a}/{i} (x{sc}, marge)")
                if touches_edge(render_svg(sv, W, H, 2)):
                    bad.append(f"{kind}/{a}/{i} (sort de la cellule 48x64)")
    for i, sv in enumerate(letter_frames()):
        if touches_edge(render_svg(sv, LW, LH, 2, PAD)) or touches_edge(render_svg(sv, LW, LH, 2)):
            bad.append(f"letter/{i}")
    for k in critters.KINDS:
        for a in critters.anims(k):
            for i, sv in enumerate(critters.frames(k, a)):
                if touches_edge(render_svg(sv, 32, 32, 2, PAD)):
                    bad.append(f"{k}/{a}/{i}")
    print("bords touchés :", bad or "aucun")

    def npc_portrait(kind, scale):
        cx, cy, half = FACES[kind]
        return [hud._portrait(scale, hud._crop_face(front(kind, p).svg(), cx, cy, half, scale, W, H), bg=PORTRAIT_BG[kind])
                for p in portrait_states(kind)]

    rows = []
    gaston = [render_svg(sv, farmer.W, farmer.H, S, PAD) for sv in farmer.frames("idle")][:1]
    for kind in KINDS:
        for a, (_, fps, _) in ANIMS[kind].items():
            rows.append((f"{kind}\n{a} ({fps} i/s)", [render_svg(sv, W, H, S, PAD) for sv in frames(kind, a)] + gaston))
    rows.append(("Gaston\nwave", [render_svg(sv, farmer.W, farmer.H, S, PAD) for sv in farmer.frames("wave")]))
    rows.append(("portraits", npc_portrait("postman", S) + npc_portrait("neighbor", S) + hud.farmer_portrait(S)[:1]))
    rows.append(("lettre\n(x4)", [render_svg(sv, LW, LH, S, PAD) for sv in letter_frames()]
                 + [render_svg(sv, 32, 32, S, PAD) for sv in items.item_frames("shoe")[:1]]))
    print(sheet(rows, os.path.join(OUT, "npcs_preview.png")))

    crow = []
    for k in ("cat_white", "cat"):
        for a, (_, fps, _) in critters.anims(k).items():
            crow.append((f"{k}\n{a}", [render_svg(sv, 32, 32, 6, PAD) for sv in critters.frames(k, a)]))
    print(sheet(crow, os.path.join(OUT, "cat_white_preview.png"), label_w=170))

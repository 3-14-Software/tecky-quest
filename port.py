"""
Le port (zone industrielle agrandie) : ce qui sert aux quêtes de ses habitants.

- Les gros ballons de Léon (quête : les pousser dans le filet) : ballons de plage, une image par couleur, vus de
  dessus (le jeu les fait tourner quand ils roulent). Cadre 32 x 32, origine conseillée au centre (16, 16).
- Les trois jouets d'Iris, le vieux Jack Russell, ami de Tecky (quête du verger : les lui rapporter un par un dans la gueule) :
  poulet en caoutchouc (la tête à gauche), anneau, corde à nœuds. Cadre 32 x 32, origine au centre.
"""
import math

from spritelib import Drawing, circle, ellipse, rect, path, poly, line, OUTLINE

BALL_COLORS = ["#E24B4B", "#F2C14E", "#4A90D9", "#5DBB63", "#A070D0"]   # rouge, jaune, bleu, vert, violet


def beach_ball(d, cx, cy, r, color):
    """Ballon de plage : six quartiers, couleur et blanc en alternance, pastille au centre, reflet."""
    d.add(circle(cx, cy, r), color)
    for k in range(1, 6, 2):
        a0, a1 = math.radians(k * 60 - 90), math.radians((k + 1) * 60 - 90)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        d.add(path(f"M{cx},{cy} L{x0:.2f},{y0:.2f} A{r},{r} 0 0 1 {x1:.2f},{y1:.2f} Z"), "#FFFFFF", sil=False)
    d.add(circle(cx, cy, r * 0.22), color, sil=False, edge=True)


def balloon_frames():
    """Les cinq ballons de Léon (une image par couleur, dans l'ordre de BALL_COLORS)."""
    out = []
    for col in BALL_COLORS:
        d = Drawing(32, 32)
        beach_ball(d, 16, 16, 13, col)
        out.append(d.svg())
    return out


def balloon_relief():
    """Le relief d'un ballon : un croissant d'ombre en bas à droite, un reflet en haut à gauche. Une image à part,
    que le jeu pose sur le ballon sans la faire tourner avec lui (game.js : drawBall()) : la lumière ne roule pas."""
    d = Drawing(32, 32)
    d.raw('<path fill-rule="evenodd" d="M3,16 a13,13 0 1,0 26,0 a13,13 0 1,0 -26,0 Z '
          'M0.6,13.4 a12.8,12.8 0 1,0 25.6,0 a12.8,12.8 0 1,0 -25.6,0 Z" fill="#1F2A44" opacity="0.3"/>')
    d.add(ellipse(10.4, 9.8, 3.8, 2.3, "rotate(-35 10.4 9.8)"), "#FFFFFF", sil=False, opacity=0.8)
    d.add(circle(7.4, 14.4, 0.9), "#FFFFFF", sil=False, opacity=0.6)
    return [d.svg()]


TOYS = ["chicken", "ring", "rope"]


def _dans(d, cid, forme, couleur, opacity=None):
    """Une forme bornée à une silhouette (relief : un croissant d'ombre, une plage claire)."""
    op = f' opacity="{opacity}"' if opacity is not None else ""
    d.raw(f'<g clip-path="url(#{cid})"{op}>' + forme.replace('fill="%F%"', f'fill="{couleur}"') + "</g>")


def _arc(cx, cy, r, a0, a1):
    """Un arc de cercle de l'angle a0 à l'angle a1 (degrés, dans le sens des aiguilles d'une montre à l'écran)."""
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    return f"M{x0:.2f},{y0:.2f} A{r},{r} 0 {1 if (a1 - a0) % 360 > 180 else 0} 1 {x1:.2f},{y1:.2f}"


def _trait(d, chemin, couleur, w, opacity=None, bout="round"):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    d.raw(f'<path d="{chemin}" fill="none" stroke="{couleur}" stroke-width="{w}" stroke-linecap="{bout}" '
          f'stroke-linejoin="round"{op}/>')


def poulet(d, dx=0.0, dy=0.0):
    """Le poulet en caoutchouc, le pouic-pouic d'Iris : couché, la tête à gauche, les pattes en l'air (aussi l'icône
    du badge d'Iris). C'était un canard jaune, trop proche du canard pouic-pouic des trésors : Christophe a choisi
    le poulet sur reference/v2/jouets_iris_options.png."""
    peau, ombre, clair = "#F8E7A6", "#E2C672", "#FFF6CF"
    X, Y = lambda x: x + dx, lambda y: y + dy
    for a, b in (((23.6, 19.4), (28.2, 15.6)), ((23.2, 22.2), (28.6, 21.6))):                         # les pattes
        ch = f"M{X(a[0])},{Y(a[1])} L{X(b[0])},{Y(b[1])}"
        _trait(d, ch, OUTLINE, 3.4)
        _trait(d, ch + f" m-1.4,-1.5 l1.4,1.5 l-0.6,1.9", OUTLINE, 3.0)
        _trait(d, ch, "#F28C28", 1.6)
        _trait(d, f"M{X(b[0]) - 1.4},{Y(b[1]) - 1.5} l1.4,1.5 l-0.6,1.9", "#F28C28", 1.2)
    for x, y in ((6, 9.6), (8, 8.8), (10, 9.8)):                                                    # la crête
        d.add(circle(X(x), Y(y), 1.6), "#E24B4B")
    d.add(ellipse(X(5.4), Y(17), 1.1, 1.7), "#E24B4B")                                               # le barbillon
    d.add(path(f"M{X(5)},{Y(12.2)} L{X(1.4)},{Y(13.8)} L{X(5)},{Y(15.2)} Z"), "#F28C28")
    corps = path(f"M{X(4.6)},{Y(13.4)} Q{X(4.6)},{Y(9.8)} {X(8)},{Y(9.8)} Q{X(11.4)},{Y(9.8)} {X(11.6)},{Y(13)} "
                 f"Q{X(13.4)},{Y(14.4)} {X(15.6)},{Y(14.2)} Q{X(25.6)},{Y(13)} {X(26)},{Y(20.4)} "
                 f"Q{X(25.6)},{Y(26.6)} {X(17.6)},{Y(26.2)} Q{X(11.6)},{Y(25.8)} {X(9.4)},{Y(19.6)} "
                 f"Q{X(8.6)},{Y(17.2)} {X(7.4)},{Y(16.8)} Q{X(4.6)},{Y(16.6)} {X(4.6)},{Y(13.4)} Z")
    d.clip("jouet_poulet", [corps])
    d.add(corps, peau)
    _dans(d, "jouet_poulet", ellipse(X(19), Y(27), 10, 4), ombre)
    _dans(d, "jouet_poulet", ellipse(X(18), Y(16), 4.4, 1.3, f"rotate(-6 {X(18)} {Y(16)})"), clair)
    _trait(d, f"M{X(15.4)},{Y(19.4)} Q{X(19)},{Y(23.4)} {X(22.4)},{Y(19.8)}", ombre, 1.2)            # l'aile
    d.add(circle(X(7.6), Y(12.6), 1.05), OUTLINE, sil=False)
    d.add(circle(X(7.9), Y(12.2), 0.34), "#FFFFFF", sil=False)


def anneau(d):
    """L'anneau à mâcher : rouge, trois bandes bleues qui en font le tour ; le relief d'un boudin (le dehors en bas à
    droite et le dedans en haut à gauche restent à l'ombre : l'anneau clair est décalé vers la lumière)."""
    ring = path("M5,16 a11,11 0 1,0 22,0 a11,11 0 1,0 -22,0 Z M10.6,16 a5.4,5.4 0 1,0 10.8,0 a5.4,5.4 0 1,0 -10.8,0 Z")
    d.add(ring.replace("<path ", '<path fill-rule="evenodd" '), "#B93A34")
    for a in (20, 140, 260):
        _trait(d, _arc(16, 16, 8.2, a - 11, a + 11), "#2F68A8", 5.6, bout="butt")
    _trait(d, _arc(15.3, 15.3, 8.1, 0, 359.9) + " Z", "#E24B4B", 4.2)
    for a in (20, 140, 260):
        _trait(d, _arc(15.3, 15.3, 8.1, a - 11, a + 11), "#4A90D9", 4.2, bout="butt")
    _trait(d, _arc(15.3, 15.3, 8.9, 200, 258), "#FFFFFF", 1.0, 0.6)


CORDE = ((5.6, 20.6), (11.5, 9.4), (19.6, 27.2), (26.4, 15.2))      # la corde : une courbe en S (Bézier), pas une tige


def corde(d, demi=2.7):
    """La corde à nœuds : une grosse corde torsadée posée en S, un brin écru, un brin bleu, un nœud et un bout
    effiloché de chaque côté. (La première était une tige lisse entre deux boules : Christophe y voyait un piercing ;
    la deuxième, droite, il l'a voulue « plus organique ».) Tout est placé le long de la courbe : p(s, v) = le point
    à la distance s du départ, écarté de v sur le côté (v > 0 : vers le bas)."""
    ecru, ombre, bleu = "#F1E4C3", "#CDB888", "#4A90D9"
    n = 80
    pts, tan = [], []
    for i in range(n + 1):
        t = i / n
        k = ((1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3)
        pts.append(tuple(sum(k[j] * CORDE[j][c] for j in range(4)) for c in (0, 1)))
        q = (3 * (1 - t) ** 2, 6 * t * (1 - t), 3 * t * t)
        g = tuple(sum(q[j] * (CORDE[j + 1][c] - CORDE[j][c]) for j in range(3)) for c in (0, 1))
        h = math.hypot(*g)
        tan.append((g[0] / h, g[1] / h))
    cumul = [0.0]
    for i in range(n):
        cumul.append(cumul[-1] + math.dist(pts[i], pts[i + 1]))
    L = cumul[-1]

    def p(s, v):
        s2 = min(max(s, 0.0), L)
        i = min(n - 1, max(j for j in range(n + 1) if cumul[j] <= s2))
        f = (s2 - cumul[i]) / (cumul[i + 1] - cumul[i])
        x, y = pts[i][0] + f * (pts[i + 1][0] - pts[i][0]), pts[i][1] + f * (pts[i + 1][1] - pts[i][1])
        tx, ty = tan[i][0] + f * (tan[i + 1][0] - tan[i][0]), tan[i][1] + f * (tan[i + 1][1] - tan[i][1])
        e = s - s2                                        # au-delà d'un bout : tout droit, dans l'axe
        return x + e * tx - v * ty, y + e * ty + v * tx

    def ruban(s0, s1, v0, v1, biais=0.0, pas=0.5):
        m = max(2, int((s1 - s0) / pas) + 1)
        ss = [s0 + (s1 - s0) * i / (m - 1) for i in range(m)]
        return poly([p(x, v0) for x in ss] + [p(x + biais, v1) for x in reversed(ss)])

    for bout, k in ((0.0, -1), (L, 1)):       # les bouts effilochés, sous les nœuds
        d.add(poly([p(bout + k * u, k * v) for u, v in ((0.6, -2.0), (4.0, -2.7), (3.5, -1.2), (4.6, -0.2), (3.6, 0.7),
                                                        (4.2, 2.3), (0.6, 2.0))]), ecru)
        for v0, v1 in ((-0.8, -1.3), (0.6, 0.9)):
            a, b = p(bout + k * 2, k * v0), p(bout + k * 3.6, k * v1)
            _trait(d, f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", ombre, 0.6)
    tresse = ruban(0, L, -demi, demi)
    d.clip("jouet_corde", [tresse])
    d.add(tresse, ecru)
    s0 = 1.6
    while s0 < L - 2.2:                       # le brin bleu, en biais, tout le long de la courbe
        _dans(d, "jouet_corde", ruban(s0, s0 + 1.5, -demi - 0.3, demi + 0.3, -1.7), bleu)
        s0 += 3.3
    _dans(d, "jouet_corde", ruban(0, L, 1.0, demi + 1), "#3A2A1A", 0.22)        # le dessous, à l'ombre
    _dans(d, "jouet_corde", ruban(1.5, L - 1.5, -1.9, -1.3), "#FFFFFF", 0.5)
    for i, (bout, k) in enumerate(((0.0, -1), (L, 1))):                         # les nœuds : plus gros que la corde
        x, y = p(bout, 0)
        tx, ty = tan[0] if k < 0 else tan[-1]
        noeud = ellipse(x, y, 2.9, demi + 1.6, f"rotate({math.degrees(math.atan2(ty, tx)):.1f} {x:.2f} {y:.2f})")
        d.clip(f"jouet_noeud{i}", [noeud])
        d.add(noeud, ecru)
        _dans(d, f"jouet_noeud{i}", rect(x - 6, y + 1.5, 12, 6), ombre)             # le dessous (de l'écran), à l'ombre
        a, m, b = p(bout - 0.7, -demi - 1.3), p(bout + 1.0, 0), p(bout - 0.7, demi + 1.3)
        _trait(d, f"M{a[0]:.2f},{a[1]:.2f} Q{m[0]:.2f},{m[1]:.2f} {b[0]:.2f},{b[1]:.2f}", bleu, 1.3)


def toy_frames():
    """Les trois jouets d'Iris (dans l'ordre de TOYS)."""
    out = []
    for dessin in (poulet, anneau, corde):
        d = Drawing(32, 32)
        dessin(d)
        out.append(d.svg())
    return out

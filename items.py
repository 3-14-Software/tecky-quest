"""
Objets (32x32) et effets.
Objets : bobbent en l'air avec une ombre au sol et un éclat de brillance.
Effets : aboiement (48x48, orienté vers la droite), morsure, impact, soin, ramassage, terre, vaguelette, scintillement,
cœur (32x32) ; feuilles qui tombent (16x16, une image par couleur) ; météo : flaque (48x48, une image par forme),
éclaboussure de pluie (32x32), gouttelette, flocon (une image par variante) et « z » du sommeil (16x16).
"""
import math

from spritelib import Drawing, circle, ellipse, rect, poly, path, line, OUTLINE

IW = IH = 32


def star_pts(cx, cy, r1, r2, n=4, rot=0):
    pts = []
    for i in range(n * 2):
        a = math.radians(rot) + i * math.pi / n - math.pi / 2
        r = r1 if i % 2 == 0 else r2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ------------------------------------------------------------------ dessins
def bone(d):
    tr = "rotate(-25 16 16)"
    for x, y in ((9, 13.4), (9, 18.6), (23, 13.4), (23, 18.6)):
        d.add(circle(x, y, 3, tr), "#F3E7CF")
    d.add(rect(8.5, 13.5, 15, 5, 2, tr), "#F3E7CF")
    d.add(rect(10, 16.6, 12, 1.6, 0.8, tr), "#D9C8A2", sil=False)


def sausage(d):
    cx, cy, R, t = 16, 28.5, 11, 3.6
    a0, a1 = math.radians(222), math.radians(318)
    arc = lambda r: [(cx + r * math.cos(a0 + (a1 - a0) * i / 16), cy + r * math.sin(a0 + (a1 - a0) * i / 16)) for i in range(17)]
    outer, inner = arc(R + t), arc(R - t)
    d.add(poly(outer + list(reversed(inner))), "#C4513A")
    for a in (a0, a1):
        d.add(circle(cx + R * math.cos(a), cy + R * math.sin(a), t), "#C4513A")
    hl = arc(R + 1.2)
    d.raw(line("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in hl[3:14]), "#E88467", 1.4))
    for a, s in ((a0, -1), (a1, 1)):
        x, y = cx + (R) * math.cos(a) + s * 2.6, cy + R * math.sin(a) + 1.4
        d.add(ellipse(x, y, 1.3, 1), "#8A3322")


def medal(d):
    d.add(poly([(9, 2), (14, 2), (18, 13), (14, 14)]), "#D7332B")
    d.add(poly([(23, 2), (18, 2), (14, 13), (18, 14)]), "#2E6FD1")
    d.add(circle(16, 20, 7.5), "#F2C14E")
    d.add(circle(16, 20, 5.3), "#E0A92E", sil=False)
    for x, y in ((13.3, 17.6), (15.2, 16.4), (16.8, 16.4), (18.7, 17.6)):
        d.add(circle(x, y, 0.95), "#9C6A12", sil=False)
    d.add(ellipse(16, 21.2, 2.7, 2.1), "#9C6A12", sil=False)
    d.add(ellipse(13.5, 16.5, 1.6, 0.9, "rotate(-35 13.5 16.5)"), "#FFF1B8", sil=False, opacity=0.8)


def duck(d, squash=0.0):
    tr = f"translate(16 26) scale({1 + squash * 0.15:.3f} {1 - squash * 0.2:.3f}) translate(-16 -26)"
    d.add(ellipse(17.5, 20, 8.5, 5.8, tr), "#FFD34D")
    d.add(circle(12, 12.8, 4.8, tr), "#FFD34D")
    d.add(ellipse(7, 14, 2.8, 1.3 + squash * 0.8, tr), "#F28C28")
    d.add(ellipse(20, 19.4, 4.2, 2.6, f"{tr} rotate(-10 20 19.4)"), "#F0B429", sil=False)
    d.add(circle(11.2, 11.8, 0.95, tr), OUTLINE, sil=False)
    d.add(circle(11.5, 11.5, 0.3, tr), "#FFFFFF", sil=False)
    d.add(ellipse(15, 22.5, 3, 1.2, tr), "#FFE58F", sil=False)


def ball(d, spin=0.0):
    d.add(circle(16, 17, 7.5), "#CFE84A")
    d.raw(f'<g transform="rotate({spin:.1f} 16 17)">' +
          line("M10.2,12.8 Q15,17 10.2,21.2", "#FFFFFF", 1.3) +
          line("M21.8,12.8 Q17,17 21.8,21.2", "#FFFFFF", 1.3) + "</g>")
    d.add(ellipse(13.2, 13.6, 2, 1.2, "rotate(-35 13.2 13.6)"), "#EDF7A6", sil=False, opacity=0.8)


# --- indices semés par Alice (couleurs de sa tenue : rose de la jupe, jaune du t-shirt)
def hairclip(d):
    """Barrette : nœud rose sur une pince."""
    tr = "rotate(-12 16 18)"
    d.add(rect(6.5, 19.2, 19, 2.6, 1.3, tr), "#C9CED6")
    d.add(path("M16,18 Q9.5,8.5 5.6,12.6 Q3.6,18 5.6,23.4 Q9.5,27.5 16,18 Z", tr), "#F4A7C3")
    d.add(path("M16,18 Q22.5,8.5 26.4,12.6 Q28.4,18 26.4,23.4 Q22.5,27.5 16,18 Z", tr), "#F4A7C3")
    for s in (-1, 1):
        d.add(path(f"M{16 + s * 3},18 Q{16 + s * 7},12.5 {16 + s * 9.2},14.6 Q{16 + s * 10},18 {16 + s * 9.2},21.4 "
                   f"Q{16 + s * 7},23.5 {16 + s * 3},18 Z", tr), "#F9C6D9", sil=False)
    d.add(circle(16, 18, 3, tr), "#DE85A8")
    d.add(circle(15.2, 17.2, 0.9, tr), "#FBE36A", sil=False)


def shoe(d):
    """Petite chaussure rose à bride (Alice finit pieds nus…)."""
    d.add(path("M6,24 Q5,16.5 10.5,15.8 L14.5,15.8 Q16.5,19.5 21,18.8 Q27.5,18 28,22.4 Q28.2,25 26,25 L8,25 Q6,25 6,24 Z"),
          "#F4A7C3")
    d.add(rect(5.4, 24.2, 23.4, 2.6, 1.3), "#DE85A8")
    d.add(ellipse(12.4, 17.2, 3.4, 1.4), "#B8505A", sil=False)
    d.raw(line("M10.6,18.4 Q15.6,13.4 20,18.2", "#C9658E", 1.8))
    d.add(circle(20, 18.2, 1.2), "#FBE36A", sil=False, edge=True)
    d.add(ellipse(23.5, 20.4, 2.2, 0.9, "rotate(-15 23.5 20.4)"), "#F9C6D9", sil=False)


def plush(d):
    """Doudou lapin."""
    fur, ink = "#F3E7CF", "#E28CA6"
    for s in (-1, 1):
        d.add(ellipse(16 + s * 4, 7.6, 2.6, 6.4, f"rotate({s * 12} {16 + s * 4} 12)"), fur)
        d.add(ellipse(16 + s * 4, 8.2, 1.2, 4.4, f"rotate({s * 12} {16 + s * 4} 12)"), "#F4A7C3", sil=False)
    d.add(ellipse(16, 23.4, 7.4, 6.4), fur)
    for s in (-1, 1):
        d.add(ellipse(16 + s * 6.4, 22, 2, 3.3, f"rotate({-s * 20} {16 + s * 6.4} 22)"), fur)
        d.add(ellipse(16 + s * 4.6, 28.4, 2.9, 1.8), fur)
    d.add(circle(16, 15.4, 6), fur)
    d.add(ellipse(16, 24.6, 4, 3.6), "#FFF7E6", sil=False)
    d.add(path("M12.4,20.4 L16,21.8 L19.6,20.4 L19.6,23 L16,21.8 L12.4,23 Z"), "#F4A7C3", sil=False, edge=True)
    for s in (-1, 1):
        d.add(circle(16 + s * 2.5, 14.6, 0.95), OUTLINE, sil=False)
        d.add(circle(16 + s * 4, 17, 1.1), "#F4A1A1", sil=False, opacity=0.7)
    d.add(ellipse(16, 16.8, 1.1, 0.75), ink, sil=False)


def goldbone(d):
    """Os doré : le trésor enterré sous les traces de pattes."""
    tr = "rotate(-25 16 16)"
    for x, y in ((8.6, 13.2), (8.6, 18.8), (23.4, 13.2), (23.4, 18.8)):
        d.add(circle(x, y, 3.3, tr), "#F2C14E")
    d.add(rect(8.2, 13.2, 15.6, 5.6, 2, tr), "#F2C14E")
    d.add(rect(10, 16.9, 12, 1.6, 0.8, tr), "#D99A26", sil=False)
    d.add(rect(11, 13.9, 8, 1.4, 0.7, tr), "#FFF1B8", sil=False)
    d.add(circle(8.2, 12.4, 1.1, tr), "#FFF7D6", sil=False)


ITEMS = {   # nom : (fonction de dessin, rôle)
    "bone": (bone, "soin +1"),
    "sausage": (sausage, "soin +3"),
    "medal": (medal, "score +100"),
    "squeaky": (duck, "score +50"),
    "ball": (ball, "score +20"),
    "hairclip": (hairclip, "indice : barrette d'Alice"),
    "shoe": (shoe, "indice : chaussure d'Alice"),
    "plush": (plush, "indice : doudou d'Alice"),
    "goldbone": (goldbone, "os doré : trésor enterré, à collectionner"),
}
CLUES = ("hairclip", "shoe", "plush")   # dans l'ordre du jeu


def item_frames(name, n=6):
    fn = ITEMS[name][0]
    out = []
    for i in range(n):
        t = i / n * 2 * math.pi
        bob = -2.2 * (0.5 + 0.5 * math.sin(t))
        k = 1 - 0.25 * (0.5 + 0.5 * math.sin(t))
        d = Drawing(IW, IH)
        d.under.append(f'<ellipse cx="16" cy="29.5" rx="{8 * k:.2f}" ry="{1.8 * k:.2f}" fill="#000" opacity="0.2"/>')
        if name == "squeaky":
            fn(d, squash=[0, 0, 0, 1, 0.4, 0][i])
            if i in (3, 4):
                d.raw(line("M3,6 L5,8 M6,3 L7,6 M1.5,10 L4.5,10.5", OUTLINE, 1.0))
        elif name == "ball":
            fn(d, spin=i * 60)
        else:
            fn(d)
        if i in (2, 3):
            s = 3.2 if i == 2 else 2.2
            d.raw(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in star_pts(26, 6, s, s * 0.35))}" '
                  f'fill="#FFFFFF" stroke="{OUTLINE}" stroke-width="0.5"/>')
        out.append(d.svg(f"translate(0 {bob:.2f})"))
    return out


# ------------------------------------------------------------------ effets
def fx_bark():
    """48x48, onde sonore vers la droite (tourner via image_angle pour les autres directions)."""
    out = []
    for i in range(4):
        d = Drawing(48, 48)
        for j, r0 in enumerate((6, 12)):
            r = r0 + i * 5
            if r > 30:
                continue
            a = math.radians(40)
            x0, y0 = 6 + r * math.cos(-a), 24 + r * math.sin(-a)
            x1, y1 = 6 + r * math.cos(a), 24 + r * math.sin(a)
            dd = f"M{x0:.1f},{y0:.1f} A{r},{r} 0 0 1 {x1:.1f},{y1:.1f}"
            op = max(0.25, 1 - i * 0.22 - j * 0.1)
            d.raw(f'<g opacity="{op:.2f}">' + line(dd, OUTLINE, 3.6) + line(dd, "#FFFFFF", 1.8) + "</g>")
        out.append(d.svg())
    return out


def fx_bite():
    """Mâchoires qui se referment, éclat jaune à l'impact."""
    def jaw(y_edge, direction, shift):
        pts = [(5, y_edge - direction * 4), (27, y_edge - direction * 4), (27, y_edge)]
        for k in range(5, -1, -1):
            x = 5 + shift + k * 4
            pts.append((min(27, x + 2), y_edge + direction * 2.8))
            pts.append((max(5, x), y_edge))
        pts.append((5, y_edge))
        return pts

    out = []
    for i, gap in enumerate((10, 5, 1, 1)):
        d = Drawing(32, 32)
        d.add(poly(jaw(16 - gap / 2 - 1.4, 1, 0)), "#FFFFFF")
        d.add(poly(jaw(16 + gap / 2 + 1.4, -1, 2)), "#FFFFFF")
        if i == 3:
            for a in range(0, 360, 45):
                r = math.radians(a)
                d.raw(line(f"M{16 + 11 * math.cos(r):.1f},{16 + 11 * math.sin(r):.1f} "
                           f"L{16 + 15 * math.cos(r):.1f},{16 + 15 * math.sin(r):.1f}", "#F2C14E", 1.4))
        out.append(d.svg())
    return out


def fx_hit():
    out = []
    for i in range(4):
        d = Drawing(32, 32)
        R = 4 + i * 3.2
        s = 3.2 - i * 0.5
        for k in range(5):
            a = math.radians(k * 72 + i * 20 - 90)
            x, y = 16 + R * math.cos(a), 16 + R * math.sin(a)
            d.add(poly(star_pts(x, y, s, s * 0.45, n=5, rot=i * 25)), "#FFE066")
        out.append(d.svg())
    return out


def fx_heal():
    """Petites croix vertes qui montent."""
    out = []
    for i in range(5):
        d = Drawing(32, 32)
        for k, (x0, ph) in enumerate(((10, 0), (20, 1.5), (15, 3))):
            t = (i + ph) % 5
            y = 26 - t * 4.5
            s = 2.6 if k != 2 else 2
            op = 1 - t / 6
            cross = (f"M{x0 - s / 3:.2f},{y - s:.2f} h{s * 2 / 3:.2f} v{s * 2 / 3:.2f} h{s * 2 / 3:.2f} "
                     f"v{s * 2 / 3:.2f} h{-s * 2 / 3:.2f} v{s * 2 / 3:.2f} h{-s * 2 / 3:.2f} v{-s * 2 / 3:.2f} "
                     f"h{-s * 2 / 3:.2f} v{-s * 2 / 3:.2f} h{s * 2 / 3:.2f}Z")
            d.raw(f'<path d="{cross}" fill="#6DD36F" stroke="{OUTLINE}" stroke-width="0.9" '
                  f'stroke-linejoin="round" opacity="{op:.2f}"/>')
        out.append(d.svg())
    return out


def fx_pickup():
    out = []
    for i in range(5):
        d = Drawing(32, 32)
        R = 3 + i * 3
        s = max(0.8, 3.4 - i * 0.6)
        for k in range(6):
            a = math.radians(k * 60 + 30)
            d.add(poly(star_pts(16 + R * math.cos(a), 16 + R * math.sin(a), s, s * 0.35)), "#FFFFFF")
        if i < 2:
            d.add(circle(16, 16, 3 - i * 1.2), "#FFF1B8")
        out.append(d.svg())
    return out


def fx_dirt():
    """Mottes de terre projetées vers le haut (32x32, 5 images)."""
    out = []
    clods = [(-7, 2.2, 1.6), (-3, 3.0, 1.2), (2, 2.6, 1.8), (6, 2.0, 1.3), (-1, 3.4, 1.0)]
    for f in range(5):
        t = (f + 1) / 5
        d = Drawing(32, 32)
        for k, (vx, vy, r) in enumerate(clods):
            x = 16 + vx * t * 1.6
            y = 28 - vy * 9 * t + 11 * t * t
            rr = r * (1 - 0.35 * t)
            d.add(ellipse(x, y, rr * 1.2, rr), "#9C6B3F" if k % 2 else "#B98F58")
        if f < 2:
            d.add(ellipse(16, 28.5, 7 - f * 2, 1.8), "#8A6A3E", sil=False, opacity=0.8)
        out.append(d.svg())
    return out


def fx_ripple():
    """Vaguelette sur l'eau (32x32, 8 images) : un petit arc fin qui naît, s'étire en remontant un peu, avec un
    reflet au plus fort, puis s'efface. Le jeu en sème peu, à des endroits qui changent à chaque cycle."""
    out = []
    for i in range(8):
        u = (i + 0.5) / 8
        a = math.sin(math.pi * u)
        w, y = 2.2 + 2.4 * a, 17 - 1.2 * u
        d = Drawing(32, 32)
        d.raw(f'<g opacity="{0.15 + 0.55 * a:.2f}">'
              + line(f"M{16 - w:.2f},{y + 0.8:.2f} Q16,{y - 1.6:.2f} {16 + w:.2f},{y + 0.8:.2f}", "#D2F0FB", 1.0) + "</g>")
        if 0.35 < u < 0.65:
            d.add(circle(16, y - 0.6, 0.55), "#FFFFFF", sil=False, opacity=round(0.8 * a, 2))
        out.append(d.svg())
    return out


def fx_glint():
    """Scintillement sur l'eau (32x32, 8 images) : mini-étoile blanche à 4 branches qui grandit en tournant un peu,
    avec un halo bleuté, puis s'éteint. Le jeu en sème en plus des vaguelettes."""
    out = []
    for i, k in enumerate((0.15, 0.4, 0.75, 1.0, 0.85, 0.6, 0.35, 0.12)):
        d = Drawing(32, 32)
        d.add(circle(16, 16, 2.2 * k), "#E6F7FD", sil=False, opacity=round(0.3 * k, 2))
        pts = star_pts(16, 16, 4.4 * k, 0.7 * k, n=4, rot=i * 5)
        d.raw(f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in pts)}" fill="#FFFFFF" '
              f'opacity="{0.35 + 0.65 * k:.2f}"/>')
        out.append(d.svg())
    return out


def fx_heart():
    """Petit cœur (32x32, 6 images) qui gonfle, monte et s'efface : un chien qui veut jouer (mode balade)."""
    out = []
    heart = ("M16,23.5 C9,18.6 7,15.2 7,12.6 C7,9.9 9.1,8 11.6,8 C13.6,8 15.1,9.2 16,10.9 "
             "C16.9,9.2 18.4,8 20.4,8 C22.9,8 25,9.9 25,12.6 C25,15.2 23,18.6 16,23.5 Z")
    for s, dy, op in ((0.55, 4, 1), (0.92, 2, 1), (1.1, 0, 1), (1.0, -3, 1), (0.98, -6, 0.7), (0.95, -9, 0.35)):
        d = Drawing(32, 32)
        d.add(path(heart), "#F2607E")
        d.add(ellipse(11.8, 11.6, 2.2, 1.5, "rotate(-30 11.8 11.6)"), "#FFFFFF", sil=False, opacity=0.8)
        svg = d.svg(f"translate(16 {16 + dy}) scale({s}) translate(-16 -16)")
        out.append(svg.replace("<g transform=", f'<g opacity="{op}" transform=', 1))
    return out


def fx_footprint():
    """Empreinte de pied nu d'Alice (16x16, orteils vers le haut ; le jeu la tourne dans le sens de la piste).
    2 images : pied gauche, pied droit. Piste d'odeur que Tecky fait apparaître en flairant."""
    out = []
    for flip in (1, -1):
        d = Drawing(16, 16)
        tr = f"translate(8 0) scale({flip} 1) translate(-8 0)"
        d.add(path("M6.2,14.6 C4.4,14.4 4.2,11.6 4.8,9.4 C5.4,7.2 6.4,6 8.2,6 C10,6 10.8,7.6 10.4,9.8 "
                   "C10,12 9.2,13.4 8.6,14 C8,14.6 7.2,14.7 6.2,14.6 Z", tr), "#FFE9A8")
        for x, y, r in ((4.6, 4.6, 1.15), (6.4, 3.4, 1.05), (8.1, 3.1, 0.95), (9.6, 3.6, 0.85), (10.8, 4.6, 0.75)):
            d.add(circle(x, y, r, tr), "#FFE9A8")
        out.append(d.svg())
    return out


LEAF_COLORS = ("#6DB656", "#A7C94A", "#F2C14E", "#E58A3A")    # vert, vert tendre, jaune, orange


def fx_leaf():
    """Feuille qui tombe d'un arbre (16x16) : une image par couleur. Le jeu la fait tourner et basculer en tombant."""
    out = []
    for c in LEAF_COLORS:
        d = Drawing(16, 16)
        d.add(path("M3,11.5 C3.5,6 8,3 13,3.2 C13,8.6 9.4,12.6 3,11.5 Z"), c)
        d.raw(line("M4,10.6 Q8,8 12,4.2", OUTLINE, 0.7))
        out.append(d.svg())
    return out


# ------------------------------------------------------------------ météo (et sommeil)
PUDDLE_EDGE = "#5B6573"     # contour doux brun-bleu : la flaque est posée au sol, pas le brun des personnages
DROP_EDGE = "#2F6F9A"       # contour des gouttes (bleu des berges, tiles.py)
SNOW_EDGE = "#B5D8EE"       # contour bleu très clair des flocons (en brun, la neige ferait des taches sombres)

PUDDLES = (   # (cx, cy, rx, ry, harmoniques (n, amplitude, phase)) de la flaque, puis ses petites flaques voisines
    ((24, 24, 19.2, 7.4, ((2, 0.10, 0.6), (3, 0.08, 2.1), (5, 0.04, 0.4))), ((9.6, 32.2, 2.6, 1.3, ()),)),
    ((24, 24, 18.4, 8.0, ((2, 0.10, 0.2), (3, 0.07, 1.0), (4, 0.06, 2.6))), ()),
    ((23.4, 24.6, 18.4, 7.0, ((2, 0.08, 0.0), (3, 0.11, 5.2), (4, 0.05, 0.8))), ((38.6, 15.4, 2.8, 1.4, ()),
                                                                              (42.4, 19.0, 1.5, 0.8, ()))),
)


def _blob(cx, cy, rx, ry, waves, n=20, k=1.0, dx=0.0, dy=0.0):
    """Forme ronde irrégulière au contour lissé : ellipse dont le rayon ondule selon quelques harmoniques.
    k la réduit, dx/dy la décalent (aplats intérieurs)."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = k * (1 + sum(a * math.sin(h * t + ph) for h, a, ph in waves))
        pts.append((cx + dx + rx * r * math.cos(t), cy + dy + ry * r * math.sin(t)))
    mid = [((x0 + x1) / 2, (y0 + y1) / 2) for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])]
    return path(f"M{mid[-1][0]:.2f},{mid[-1][1]:.2f} " + " ".join(
        f"Q{x:.2f},{y:.2f} {mx:.2f},{my:.2f}" for (x, y), (mx, my) in zip(pts, mid)) + " Z")


def fx_puddle():
    """Flaque d'eau vue de dessus, posée au sol (48x48, environ 40 de large, centrée) : une image par forme
    (3 variantes, le jeu choisit). Aplats : eau bleu-gris, bord plus sombre côté haut (la berge), reflets clairs ;
    contour doux brun-bleu."""
    out = []
    for k, (main, sats) in enumerate(PUDDLES):
        d = Drawing(48, 48)
        for j, (cx, cy, rx, ry, waves) in enumerate((main,) + sats):
            cid = f"puddle{k}_{j}"
            shape = _blob(cx, cy, rx, ry, waves)
            d.clip(cid, [shape])
            d.add(shape, "#7398B3")
            d.add(_blob(cx, cy, rx, ry, waves, k=0.97, dx=0.5, dy=min(1.3, ry * 0.22)), "#93BCD5", sil=False, clip=cid)
        cx, cy, rx, ry, _ = main
        d.add(ellipse(cx + rx * 0.22, cy + ry * 0.32, rx * 0.42, ry * 0.32), "#AED3E6", sil=False, clip=f"puddle{k}_0")
        x0, y0 = cx - rx * 0.55, cy - ry * 0.02
        d.raw(line(f"M{x0:.2f},{y0:.2f} Q{x0 + rx * 0.18:.2f},{y0 - ry * 0.34:.2f} {x0 + rx * 0.48:.2f},{y0 - ry * 0.32:.2f}",
                   "#E4F4FB", 1.3))
        d.raw(line(f"M{cx + rx * 0.05:.2f},{cy + ry * 0.46:.2f} L{cx + rx * 0.36:.2f},{cy + ry * 0.40:.2f}", "#E4F4FB", 1.0))
        d.add(circle(x0 + rx * 0.6, y0 - ry * 0.3, 0.7), "#FFFFFF", sil=False)
        out.append(d.svg(outline=PUDDLE_EDGE, outline_w=1.1))
    return out


def fx_splash():
    """Impact d'une goutte de pluie (32x32, 4 images, ~16 i/s), point d'impact au centre du cadre : un anneau
    aplati qui s'élargit et s'efface, trois gouttelettes qui sautent puis retombent."""
    out = []
    jumps = ((-6.4, 7.0, 1.05), (0.8, 9.0, 1.2), (6.0, 6.2, 0.95))   # (dérive x, hauteur, rayon)
    for i in range(4):
        t = (i + 0.8) / 4.4
        rx = 2.2 + 9.4 * t ** 0.8
        op = 1 - 0.75 * t * t
        ring = f'<ellipse cx="16" cy="16" rx="{rx:.2f}" ry="{rx * 0.38:.2f}" fill="none" stroke="%C%" stroke-width="%W%"/>'
        d = Drawing(32, 32)
        d.raw(f'<g opacity="{op:.2f}">' + ring.replace("%C%", "#3F7EA8").replace("%W%", "2.0")
              + ring.replace("%C%", "#E6F7FD").replace("%W%", "0.9") + "</g>")
        for vx, h, r in jumps:
            d.raw(f'<circle cx="{16 + vx * t:.2f}" cy="{16 - 4 * h * t * (1 - t) - 0.6:.2f}" r="{r * (1 - 0.35 * t):.2f}" '
                  f'fill="#CDEBF8" stroke="#3F7EA8" stroke-width="0.6" opacity="{min(1, op + 0.25):.2f}"/>')
        out.append(d.svg())
    return out


def fx_drop():
    """Gouttelette d'eau bleue (16x16, centrée, pointe vers le haut) : Tecky s'ébroue."""
    d = Drawing(16, 16)
    d.add(path("M8,2.9 C9.5,5.2 11.2,7.2 11.2,9.6 C11.2,11.7 9.8,13.1 8,13.1 C6.2,13.1 4.8,11.7 4.8,9.6 "
               "C4.8,7.2 6.5,5.2 8,2.9 Z"), "#7CC4EA")
    d.add(path("M8,13.1 C9.8,13.1 11.2,11.7 11.2,9.6 C10.6,11 9.6,11.9 8,12 C6.4,11.9 5.4,11 4.8,9.6 "
               "C4.8,11.7 6.2,13.1 8,13.1 Z"), "#4FA3D3", sil=False)
    d.add(ellipse(6.6, 9.2, 0.9, 1.5, "rotate(20 6.6 9.2)"), "#FFFFFF", sil=False, opacity=0.85)
    return [d.svg(outline=DROP_EDGE, outline_w=1.2)]


def fx_snowflake():
    """Flocon de neige (16x16, centré), 3 variantes (le jeu choisit) : rond doux, petit flocon à 6 branches,
    grand flocon ramifié. Blanc, contour bleu très clair."""
    d = Drawing(16, 16)
    d.add(circle(8, 8, 2.3), "#FFFFFF")
    d.add(circle(7.3, 7.3, 0.7), "#EAF5FC", sil=False)
    out = [d.svg(outline=SNOW_EDGE, outline_w=1.0)]
    for L, side in ((3.4, 0), (5.6, 1.9)):        # longueur des branches, longueur des rameaux
        dd = ""
        for k in range(6):
            a = math.radians(k * 60 - 90)
            c, s = math.cos(a), math.sin(a)
            dd += f"M8,8 L{8 + L * c:.2f},{8 + L * s:.2f} "
            m = L * 0.58
            for sg in ((-1, 1) if side else ()):
                b = a + sg * math.radians(48)
                dd += f"M{8 + m * c:.2f},{8 + m * s:.2f} L{8 + m * c + side * math.cos(b):.2f},{8 + m * s + side * math.sin(b):.2f} "
        w = 1.0 if side else 1.1
        d = Drawing(16, 16)
        d.raw(line(dd, SNOW_EDGE, w + 1.0) + line(dd, "#FFFFFF", w))
        d.add(circle(8, 8, 1.0 if side else 0.9), "#FFFFFF", sil=False)
        out.append(d.svg())
    return out


def fx_zzz():
    """Lettre « z » arrondie (16x16, centrée), blanc crème au contour brun : Tecky dort."""
    d = Drawing(16, 16)
    dd = "M5,5 L11,5 L5,11 L11,11"
    d.raw('<g transform="rotate(-8 8 8)">' + line(dd, OUTLINE, 4.0) + line(dd, "#FFF7E6", 2.0) + "</g>")
    return [d.svg()]


def fx_steam():
    """Bouffée de vapeur de Titine, le petit train (32x32, 6 images) : trois boules blanches qui gonflent et
    s'éclaircissent (le jeu la fait monter)."""
    out = []
    for f in range(6):
        t = (f + 1) / 6
        d = Drawing(32, 32)
        for k, (x, y, r) in enumerate(((16, 20, 5.5), (11, 15, 4.2), (21, 14, 4.6))):
            d.add(circle(x + (x - 16) * t * 0.5, y - t * 4, r * (0.55 + 0.6 * t)), "#FFFFFF", sil=False,
                  opacity=round(0.95 - 0.75 * t, 2))
        out.append(d.svg())
    return out


EFFECTS = {   # nom : (fonction, taille, fps)
    "bark": (fx_bark, 48, 12),
    "bite": (fx_bite, 32, 14),
    "hit": (fx_hit, 32, 14),
    "heal": (fx_heal, 32, 10),
    "pickup": (fx_pickup, 32, 14),
    "dirt": (fx_dirt, 32, 14),
    "ripple": (fx_ripple, 32, 3),
    "glint": (fx_glint, 32, 7),
    "heart": (fx_heart, 32, 10),
    "leaf": (fx_leaf, 16, 0),        # pas une animation : image = couleur
    "footprint": (fx_footprint, 16, 0),   # pied gauche, pied droit
    "puddle": (fx_puddle, 48, 0),         # flaque : image = forme (3)
    "splash": (fx_splash, 32, 16),        # goutte de pluie qui tombe au sol
    "drop": (fx_drop, 16, 0),             # gouttelette (Tecky s'ébroue)
    "snowflake": (fx_snowflake, 16, 0),   # flocon : image = variante (3)
    "zzz": (fx_zzz, 16, 0),               # « z » du sommeil
    "steam": (fx_steam, 32, 10),          # vapeur du petit train
}

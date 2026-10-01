"""
Objets (32x32) et effets.
Objets : bobbent en l'air avec une ombre au sol et un éclat de brillance.
Effets : aboiement (48x48, orienté vers la droite), morsure, impact, soin, ramassage (32x32).
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


ITEMS = {   # nom : (fonction de dessin, rôle)
    "bone": (bone, "soin +1"),
    "sausage": (sausage, "soin +3"),
    "medal": (medal, "score +100"),
    "squeaky": (duck, "score +50"),
    "ball": (ball, "score +20"),
    "hairclip": (hairclip, "indice : barrette d'Alice"),
    "shoe": (shoe, "indice : chaussure d'Alice"),
    "plush": (plush, "indice : doudou d'Alice"),
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


EFFECTS = {   # nom : (fonction, taille, fps)
    "bark": (fx_bark, 48, 12),
    "bite": (fx_bite, 32, 14),
    "hit": (fx_hit, 32, 14),
    "heal": (fx_heal, 32, 10),
    "pickup": (fx_pickup, 32, 14),
    "dirt": (fx_dirt, 32, 14),
}

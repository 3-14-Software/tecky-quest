"""
Tecky — le teckel au harnais rouge.
Vue de dessus 3/4, cellule 48x48 (unités = pixels en 1x), pieds à y=44.

Vues dessinées : side (profil, tourné vers la droite), down (vers la caméra),
up (de dos). La vue gauche est le miroir de la vue droite.
"""
import math

from spritelib import (Drawing, circle, ellipse, rect, poly, path, leg, line, OUTLINE)

W = H = 48
GROUND = 44

PAL = dict(
    fur="#C4642E", dark="#8F4320", light="#E3955C",
    nose="#221715", white="#FFFFFF", pupil="#2A1810",
    mouth="#5B1A16", tongue="#E8707A",
    harness="#D7332B", ring="#F2C14E",
)
HARNESS = True


def P(**kw):
    base = dict(phase=None, bob=0.0, tail=None, mouth=0.0, head_dx=0.0, head_dy=0.0,
                head_rot=0.0, lunge=0.0, blink=0.0, xeyes=False, ear=0.0,
                # poses de repos (REST_ANIMS) ; ces valeurs par défaut ne changent rien aux ANIMS
                pose="stand",     # "stand" (debout), "sit" (assis), "lie" (couché)
                lid=0.0,          # paupières mi-closes (0 = ouvert, 1 = presque fermé)
                lid_tilt=0.0,     # inclinaison de la paupière (degrés ; < 0 : tombe vers l'arrière, air béat)
                squint=False,     # yeux plissés « > < »
                fluff=0.0,        # poils ébouriffés : hauteur des pics sur le contour
                fluff_ph=0.0,     # phase des pics (ils changent d'une image à l'autre)
                twist=0.0,        # torsion du corps (-1..1) : roulis en profil, décalage en face
                ear_tilt=0.0,     # face : les deux oreilles penchent du même côté (degrés)
                breath=0.0,       # couché : respiration (0..1), le flanc monte
                paw=None,         # assis de profil : (x, y) de la patte arrière qui gratte
                scratch_ph=0)     # traits de vitesse autour de cette patte (0 ou 1)
    base.update(kw)
    return base


def _legs_offsets(p):
    if p["phase"] is None:
        return (0, 0), (0, 0)
    a = p["phase"]
    b = a + math.pi
    return ((2.2 * math.cos(a), max(0, math.sin(a)) * 1.8),
            (2.2 * math.cos(b), max(0, math.sin(b)) * 1.8))


def _eye(d, x, y, p, tr, r=1.8, look=0.4, sq=1):
    """Œil : ouvert, fermé (blink), en croix (xeyes), plissé (squint, pointe vers sq), mi-clos (lid)."""
    c = PAL
    if p["xeyes"]:
        s = 1.4
        d.raw(f'<g transform="{tr}">' + line(f"M{x-s},{y-s} L{x+s},{y+s} M{x-s},{y+s} L{x+s},{y-s}", OUTLINE, 1.0) + "</g>")
    elif p.get("squint"):
        d.raw(f'<g transform="{tr}">' + line(f"M{x - sq * 1.3:.2f},{y - 1.3:.2f} L{x + sq * 1.2:.2f},{y:.2f} "
                                             f"L{x - sq * 1.3:.2f},{y + 1.3:.2f}", OUTLINE, 1.0) + "</g>")
    elif p["blink"] > 0.5:
        d.raw(f'<g transform="{tr}">' + line(f"M{x-1.7},{y} Q{x},{y+1.1} {x+1.7},{y}", OUTLINE, 0.9) + "</g>")
    else:
        lid = p.get("lid", 0.0)
        d.add(circle(x, y, r, tr), c["white"], sil=False)
        d.add(circle(x + look, y + 0.25 + lid * 0.5, r * 0.64, tr), c["pupil"], sil=False)
        if lid > 0:
            # paupière : segment de disque couleur pelage qui descend sur le haut de l'œil
            yl = y - r + 2 * r * lid
            w = math.sqrt(max(0.0, r * r - (yl - y) ** 2)) + 0.15
            big = 1 if lid > 0.5 else 0
            ltr = f"{tr} rotate({p.get('lid_tilt', 0.0):.1f} {x:.2f} {y:.2f})"
            d.add(path(f"M{x - w:.2f},{yl:.2f} A{r + 0.15:.2f},{r + 0.15:.2f} 0 {big} 1 {x + w:.2f},{yl:.2f} Z", ltr),
                  c["fur"], sil=False)
            d.raw(f'<g transform="{ltr}">' + line(f"M{x - w:.2f},{yl:.2f} Q{x:.2f},{yl + 0.7:.2f} {x + w:.2f},{yl:.2f}",
                                                  OUTLINE, 0.9) + "</g>")
        else:
            d.add(circle(x + look + 0.35, y - 0.35, r * 0.24, tr), c["white"], sil=False)


def _fluff(cx, cy, rx, ry, k, ph, a0, a1, n):
    """Poils ébouriffés : n pics de hauteur ~k (unités) sur l'arc a0..a1 (degrés) d'une ellipse.
    À ajouter en silhouette AVANT la forme qu'il hérisse : seuls les pics dépassent."""
    pts = [(cx, cy)]
    for i in range(2 * n + 1):
        t = math.radians(a0 + (a1 - a0) * i / (2 * n))
        s = k * (0.75 + 0.35 * math.sin(ph + i * 2.3)) if i % 2 else -0.6
        pts.append((cx + (rx + s) * math.cos(t), cy + (ry + s) * math.sin(t)))
    return pts


def _rot(pts, a, cx, cy):
    """Tourne des points de a degrés autour de (cx, cy) (sens de rotate() en SVG)."""
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def _oval(cx, cy, rx, ry, a):
    """Ellipse inclinée de a degrés, sans attribut transform (utilisable telle quelle dans un clipPath)."""
    (x1, y1), (x2, y2) = _rot([(cx - rx, cy), (cx + rx, cy)], a, cx, cy)
    return path(f"M{x1:.2f},{y1:.2f} A{rx:.2f},{ry:.2f} {a:.1f} 1 1 {x2:.2f},{y2:.2f} "
                f"A{rx:.2f},{ry:.2f} {a:.1f} 1 1 {x1:.2f},{y1:.2f} Z")


def _limb(x1, y1, x2, y2, w1, w2):
    """Patte en biais : quadrilatère de (x1, y1) (largeur w1) à (x2, y2) (largeur w2)."""
    L = math.hypot(x2 - x1, y2 - y1) or 1
    nx, ny = -(y2 - y1) / L, (x2 - x1) / L
    return poly([(x1 + nx * w1 / 2, y1 + ny * w1 / 2), (x2 + nx * w2 / 2, y2 + ny * w2 / 2),
                 (x2 - nx * w2 / 2, y2 - ny * w2 / 2), (x1 - nx * w1 / 2, y1 - ny * w1 / 2)])


# ====================================================================== PROFIL
def side(p):
    c = PAL
    d = Drawing(W, H)
    b = p["bob"]
    Y = lambda v: v + b
    ld = p["lunge"] * 0.5
    (dxA, lA), (dxB, lB) = _legs_offsets(p)
    d.under.append(f'<ellipse cx="22" cy="{GROUND+0.2}" rx="14" ry="2" fill="#000" opacity="0.2"/>')

    # pattes (A = avant-proche + arrière-loin, B = l'inverse), toutes sous le corps
    for hx, fx, lift, col in ((17, 17 + dxA, lA, c["dark"]), (27, 27 + dxB, lB, c["dark"]),
                              (14, 14 + dxB, lB, c["fur"]), (30, 30 + dxA, lA, c["fur"])):
        fy = GROUND - 0.6 - lift
        d.add(leg(hx, Y(35), fx, fy, 3.4), col)
        d.add(ellipse(fx + 0.9, fy, 2.2, 1.3), col)

    # queue
    ta = -35 if p["tail"] is None else p["tail"]
    d.add(ellipse(10.6, Y(24.2), 1.9, 6.5, f"rotate({ta} 10.6 {Y(30.7)})"), c["fur"])

    if p["fluff"]:      # poils ébouriffés (ébrouement) : pics sur le dos, la croupe et le poitrail
        d.add(poly(_fluff(22, Y(32), 13.5, 6, p["fluff"], p["fluff_ph"], 150, 390, 11)), c["fur"])
        d.add(poly(_fluff(31 + ld, Y(27), 5, 6, p["fluff"] * 0.8, p["fluff_ph"] + 2, -60, 80, 4)), c["fur"])

    tw = p["twist"] * 1.6   # roulis : le dos (bretelle, ombre) descend ou remonte sur le flanc
    body = ellipse(22, Y(32), 13.5, 6)
    neck = ellipse(31 + ld, Y(27), 5, 6)
    d.clip("bodyclip", [body, neck])
    d.add(body, c["fur"])
    d.add(neck, c["fur"])
    d.add(ellipse(20, Y(28.5 + tw), 12, 3.2), c["dark"], sil=False, clip="bodyclip", opacity=0.45)
    d.add(ellipse(24, Y(35.6 + tw), 9, 2.2), c["light"], sil=False, clip="bodyclip")

    if HARNESS:
        # bretelle dorsale qui suit la courbe du dos
        top = lambda x: Y(32) - 6 * math.sqrt(max(0, 1 - ((x - 22) / 13.5) ** 2)) + tw
        xs = [15 + i * 0.7 for i in range(21)]
        pts = [(x, top(x) - 0.3) for x in xs] + [(x, top(x) + 2.1) for x in reversed(xs)]
        d.add(poly(pts), c["harness"], sil=False, clip="bodyclip")
        d.add(rect(27.2 + ld * 0.6, Y(19), 3.4, 22), c["harness"], sil=False, clip="bodyclip")
        d.add(circle(21, top(21) + 1.1, 1.35), c["ring"], sil=False, edge=True)

    # tête
    htr = f"translate({ld + p['head_dx']:.2f} {p['head_dy']:.2f}) rotate({p['head_rot']:.1f} 32 {Y(25)})"
    _side_head(d, p, Y, htr)
    return d


def _side_head(d, p, Y, htr):
    """Tête de profil (museau vers la droite) et oreille, posées par la transformation htr."""
    c = PAL
    if p["fluff"]:
        d.add(poly(_fluff(35, Y(21), 6.5, 6.5, p["fluff"] * 0.8, p["fluff_ph"] + 4, 175, 330, 6), htr), c["fur"])
    m = p["mouth"]
    d.add(circle(35, Y(21), 6.5, htr), c["fur"])
    d.add(ellipse(34.5, Y(17.6), 4, 2, htr), c["dark"], sil=False, opacity=0.35)
    if m > 0.05:
        d.add(ellipse(40.5, Y(24.6 + m * 0.9), 3.6, 0.4 + m * 1.6, htr), c["mouth"])
    d.add(ellipse(39.8, Y(25.4 + m * 2.0), 4, 1.5, f"{htr} rotate({m * 12:.1f} 36 {Y(25)})"), c["light"])
    if m > 0.4:
        d.add(ellipse(41, Y(25.3 + m * 1.2), 1.8, 0.9, htr), c["tongue"], sil=False)
    d.add(ellipse(40.5, Y(22.8 - m * 0.4), 5, 2.8, htr), c["light"])
    d.add(ellipse(45.2, Y(22 - m * 0.4), 1.9, 1.5, htr), c["nose"])
    if m <= 0.05:
        d.raw(f'<g transform="{htr}">' + line(f"M40,{Y(25)} Q42,{Y(25.9)} 44,{Y(24.8)}", OUTLINE, 0.8) + "</g>")
    _eye(d, 37.6, Y(19.3), p, htr)
    d.add(ellipse(32.2, Y(23.5), 3, 6, f"{htr} rotate({12 + p['ear']:.1f} 32.2 {Y(18)})"), c["dark"])


# ====================================================================== FACE (vers la caméra)
def down(p):
    c = PAL
    d = Drawing(W, H)
    b = p["bob"]
    Y = lambda v: v + b
    (_, lA), (_, lB) = _legs_offsets(p)
    d.under.append(f'<ellipse cx="24" cy="{GROUND}" rx="9.5" ry="2.2" fill="#000" opacity="0.2"/>')

    bx = p["twist"] * 2.2       # torsion : l'arrière-train part d'un côté, la tête de l'autre
    ta = 25 if p["tail"] is None else p["tail"]
    d.add(ellipse(24 + bx, Y(12.5), 1.7, 4, f"rotate({ta} {24 + bx} {Y(16)})"), c["dark"])
    d.add(ellipse(16.9 + bx, Y(30.5) - lB, 2.3, 2), c["dark"])
    d.add(ellipse(31.1 + bx, Y(30.5) - lA, 2.3, 2), c["dark"])

    if p["fluff"]:      # poils ébouriffés sur les flancs
        d.add(poly(_fluff(24 + bx, Y(24), 7.5, 10, p["fluff"], p["fluff_ph"], -80, 80, 5)), c["fur"])
        d.add(poly(_fluff(24 + bx, Y(24), 7.5, 10, p["fluff"], p["fluff_ph"] + 3, 100, 260, 5)), c["fur"])
    body = ellipse(24 + bx, Y(24), 7.5, 10)
    d.clip("bodyclip", [body])
    d.add(body, c["fur"])
    d.add(ellipse(24 + bx, Y(21), 5, 8), c["dark"], sil=False, clip="bodyclip", opacity=0.4)
    if HARNESS:
        d.add(rect(15 + bx, Y(22.6), 18, 3), c["harness"], sil=False, clip="bodyclip")
        d.add(circle(24 + bx, Y(24.1), 1.35), c["ring"], sil=False, edge=True)

    for hx, lift in ((20.3, lA), (27.7, lB)):
        fy = GROUND - 0.7 - lift
        d.add(leg(hx, Y(35), hx, fy, 3.4), c["fur"])
        d.add(ellipse(hx, fy, 2.3, 1.4), c["fur"])

    chest = ellipse(24, Y(33.5), 6.5, 5)
    d.clip("chestclip", [chest])
    d.add(chest, c["fur"])
    d.add(ellipse(24, Y(35), 4, 3), c["light"], sil=False, clip="chestclip")
    if HARNESS:
        d.add(rect(16, Y(35.2), 16, 2.4), c["harness"], sil=False, clip="chestclip")

    htr = f"translate({p['head_dx']:.2f} {p['head_dy']:.2f})"
    _down_head(d, p, Y, htr)
    return d


def _down_head(d, p, Y, htr):
    """Tête de face et oreilles, posées par la transformation htr."""
    c = PAL
    m = p["mouth"]
    if p["fluff"]:
        d.add(poly(_fluff(24, Y(27.5), 7, 7, p["fluff"] * 0.8, p["fluff_ph"] + 4, 200, 340, 5), htr), c["fur"])
    d.add(circle(24, Y(27.5), 7, htr), c["fur"])
    d.add(ellipse(24, Y(23.2), 4.2, 2, htr), c["dark"], sil=False, opacity=0.35)
    d.add(ellipse(24, Y(32), 4.4, 3.3, htr), c["light"])
    if m > 0.05:
        # au-delà de 1 (bâillement), la gueule s'élargit aussi
        d.add(ellipse(24, Y(34.2 + m * 0.8), 2.5 + max(0, m - 1) * 1.6, 0.3 + m * 1.8, htr), c["mouth"])
        if m > 0.4:
            d.add(ellipse(24, Y(35 + m * 1.2), 1.4 + max(0, m - 1) * 1.2, 0.9 * m, htr), c["tongue"], sil=False)
    else:
        d.raw(f'<g transform="{htr}">' + line(f"M21.8,{Y(33.4)} Q24,{Y(34.8)} 26.2,{Y(33.4)}", OUTLINE, 0.8) + "</g>")
    d.add(ellipse(24, Y(30.6), 2.2, 1.6, htr), c["nose"])
    d.add(ellipse(23.3, Y(30.1), 0.6, 0.35, htr), c["white"], sil=False, opacity=0.8)
    _eye(d, 20.9, Y(26.6), p, htr, look=0)
    _eye(d, 27.1, Y(26.6), p, htr, look=0, sq=-1)
    e, t = p["ear"], p["ear_tilt"]
    d.add(ellipse(16.9, Y(30), 2.8, 6, f"{htr} rotate({12 + e + t:.1f} 16.9 {Y(25)})"), c["dark"])
    d.add(ellipse(31.1, Y(30), 2.8, 6, f"{htr} rotate({-12 - e + t:.1f} 31.1 {Y(25)})"), c["dark"])


# ====================================================================== DOS
def up(p):
    c = PAL
    d = Drawing(W, H)
    b = p["bob"]
    Y = lambda v: v + b
    (_, lA), (_, lB) = _legs_offsets(p)
    d.under.append(f'<ellipse cx="24" cy="{GROUND}" rx="9.5" ry="2.2" fill="#000" opacity="0.2"/>')

    d.add(ellipse(17, Y(21) - lA, 2.2, 1.8), c["dark"])
    d.add(ellipse(31, Y(21) - lB, 2.2, 1.8), c["dark"])
    for hx, lift in ((19.8, lA), (28.2, lB)):
        fy = GROUND - 0.7 - lift
        d.add(leg(hx, Y(33), hx, fy, 3.6), c["fur"])
        d.add(ellipse(hx, fy, 2.4, 1.4), c["fur"])

    body = ellipse(24, Y(26), 7.5, 10.5)
    d.clip("bodyclip", [body])
    d.add(body, c["fur"])
    d.add(ellipse(24, Y(24), 4.8, 9), c["dark"], sil=False, clip="bodyclip", opacity=0.4)
    if HARNESS:
        d.add(rect(15, Y(19.3), 18, 3), c["harness"], sil=False, clip="bodyclip")
        d.add(rect(22.9, Y(19.3), 2.2, 9), c["harness"], sil=False, clip="bodyclip")
        d.add(circle(24, Y(26.5), 1.35), c["ring"], sil=False, edge=True)

    ta = 25 if p["tail"] is None else p["tail"]
    d.add(ellipse(24, Y(31), 1.8, 4.8, f"rotate({ta} 24 {Y(35.5)})"), c["dark"], sil=False, edge=True)

    htr = f"translate({p['head_dx']:.2f} {p['head_dy']:.2f})"
    d.add(circle(24, Y(14), 6.6, htr), c["fur"])
    d.add(ellipse(24, Y(12.8), 4.8, 4, htr), c["dark"], sil=False, opacity=0.35)
    e = p["ear"]
    d.add(ellipse(17.6, Y(16.5), 2.7, 5.5, f"{htr} rotate({10 + e:.1f} 17.6 {Y(12)})"), c["dark"])
    d.add(ellipse(30.4, Y(16.5), 2.7, 5.5, f"{htr} rotate({-10 - e:.1f} 30.4 {Y(12)})"), c["dark"])
    return d


VIEWS = {"right": side, "down": down, "up": up}


# ====================================================================== ANIMATIONS
# chaque animation : fonction(view) -> liste de (params, transform_global)
def a_idle(view):
    wag = {"right": [-35, -22, -35, -48], "down": [10, 25, 40, 25], "up": [10, 25, 40, 25]}[view]
    bob = [0, 0.3, 0.5, 0.3]
    return [(P(bob=bob[i], tail=wag[i], blink=1 if i == 3 else 0), "") for i in range(4)]


def a_walk(view):
    out = []
    for i in range(6):
        ph = i / 6 * 2 * math.pi
        wag = 10 * math.sin(ph * 2)
        base = -35 if view == "right" else 25
        out.append((P(phase=ph, bob=-0.7 * abs(math.sin(ph)), tail=base + wag, ear=6 * math.sin(ph)), ""))
    return out


def a_bark(view):
    ms = [0.2, 0.7, 1.0, 0.4]
    rot = [0, -6, -10, -3]
    out = []
    for i in range(4):
        if view == "right":
            out.append((P(mouth=ms[i], head_rot=rot[i], ear=-rot[i], tail=-50), ""))
        elif view == "down":
            out.append((P(mouth=ms[i], head_dy=rot[i] / 6, ear=-rot[i] * 0.8, tail=40), ""))
        else:
            out.append((P(head_dy=rot[i] / 5, ear=-rot[i] * 0.8, tail=40), ""))
    return out


def a_bite(view):
    lunge = [-1.5, 2.5, 4.5, 3.5, 0.5]
    ms = [0.3, 1.0, 1.0, 0.0, 0.0]
    out = []
    for i in range(5):
        L, m = lunge[i], ms[i]
        if view == "right":
            out.append((P(lunge=L, mouth=m, ear=-L * 2, tail=-45), f"translate({L * 0.6:.2f} 0)"))
        elif view == "down":
            out.append((P(mouth=m, head_dy=L * 0.5, ear=-L * 2), f"translate(0 {L * 0.35:.2f})"))
        else:
            out.append((P(head_dy=-L * 0.6, ear=-L * 2), f"translate(0 {-L * 0.3:.2f})"))
    return out


def a_hurt(view):
    dx, dy = {"right": (-1.5, 0), "down": (0, -2), "up": (0, 2)}[view]
    return [(P(blink=1, ear=-12), f"translate({dx} {dy})"), (P(blink=1, ear=-6), f"translate({dx / 2} {dy / 2})")]


def a_ko(view):
    # profil uniquement : titube, bascule, sur le dos
    return [
        (P(blink=1, ear=-10), "rotate(-8 22 44)"),
        (P(xeyes=True, ear=20, tail=-62), "translate(3 0) rotate(-22 22 44) translate(0 -1)"),
        (P(xeyes=True, ear=30, tail=-64, mouth=0.5), "translate(0 58) scale(1 -1)"),
        (P(xeyes=True, ear=30, tail=-68, mouth=0.5, bob=0.4), "translate(0 58) scale(1 -1)"),
    ]


def a_dig(view):
    """Gratter le sol : tête basse, pattes avant qui moulinent, queue qui frétille."""
    out = []
    for i in range(6):
        ph = i / 3 * 2 * math.pi            # deux cycles de pattes sur 6 images
        wag = 14 * math.sin(i / 6 * 4 * math.pi)
        if view == "right":
            out.append((P(phase=ph, bob=0.9, head_rot=24, head_dy=1.2, head_dx=0.5, ear=-8, tail=-58 + wag), ""))
        elif view == "down":
            out.append((P(phase=ph, bob=0.6, head_dy=2.2, ear=6, tail=25 + wag), ""))
        else:
            out.append((P(phase=ph, bob=0.6, head_dy=1.2, ear=-4, tail=25 + wag), ""))
    return out


ANIMS = {   # nom : (fonction, fps, directions)
    "idle": (a_idle, 6, ("down", "up", "right")),
    "walk": (a_walk, 12, ("down", "up", "right")),
    "bark": (a_bark, 10, ("down", "up", "right")),
    "bite": (a_bite, 14, ("down", "up", "right")),
    "hurt": (a_hurt, 10, ("down", "up", "right")),
    "dig":  (a_dig, 14, ("down", "up", "right")),
    "ko":   (a_ko, 6, ("right",)),
}


# cadrage : le profil est réduit et recentré pour tenir dans 48 px (museau + fente)
BASE = {"right": "translate(0.9 5.3) scale(0.88)", "down": "", "up": ""}


def frames(anim, view):
    """Liste de SVG (chaînes) pour une animation et une vue ('right', 'down', 'up')."""
    fn = ANIMS[anim][0]
    return [VIEWS[view](p).svg(f"{BASE[view]} {tr}".strip()) for p, tr in fn(view)]


# ====================================================================== POSES DE REPOS
# Jouées quand le joueur ne touche à rien. Même cadre 48x48, mêmes pieds (y = 44) et même
# cadrage (BASE) que les animations ci-dessus : passer de idle à une pose ne fait rien sauter.
# Volontairement hors de ANIMS (enemies.py et build.py parcourent ANIMS pour les chiens).
SIT_A = -38      # inclinaison du corps assis, de profil (degrés)


def _band(cx, cy, rx, ry, a0, a1, w0, w1, n=14):
    """Bande courbe le long d'un arc d'ellipse (degrés a0 -> a1), largeur w0 -> w1 (bretelle du harnais)."""
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        w = (w0 + (w1 - w0) * t) / 2
        outer.append((cx + (rx + w) * math.cos(a), cy + (ry + w) * math.sin(a)))
        inner.append((cx + (rx - w) * math.cos(a), cy + (ry - w) * math.sin(a)))
    return outer + inner[::-1]


def side_sit(p):
    """Assis de profil (vers la droite) : derrière et cuisse au sol, dos redressé, pattes avant tendues.
    Avec p["paw"] = (x, y), la patte arrière se lève et gratte derrière l'oreille."""
    c = PAL
    d = Drawing(W, H)
    b = p["bob"]
    Y = lambda v: v + b
    d.under.append(f'<ellipse cx="21" cy="{GROUND+0.2}" rx="12.5" ry="2" fill="#000" opacity="0.2"/>')

    # queue posée au sol derrière le derrière : elle balaie autour de sa base
    ta = -80 if p["tail"] is None else p["tail"]
    d.add(ellipse(11.6, GROUND - 2.2 - 6.2, 1.9, 6.2, f"rotate({ta:.1f} 11.6 {GROUND - 2.2})"), c["fur"])

    # pattes avant tendues, de la poitrine au sol (loin : foncée)
    for hx, col in ((27.2, c["dark"]), (30.2, c["fur"])):
        fy = GROUND - 0.6
        d.add(leg(hx, Y(31), hx + 0.3, fy, 3.6), col)
        d.add(ellipse(hx + 1.2, fy, 2.3, 1.3), col)
    if p["paw"] is not None:        # la patte arrière d'en face reste au sol
        d.add(ellipse(22.8, GROUND - 0.7, 2.5, 1.3), c["dark"])

    # corps incliné et poitrail ; ombre du dos et ventre clair dans le repère du corps
    cx, cy, rx, ry = 20.4, Y(34), 11, 6.3
    body = _oval(cx, cy, rx, ry, SIT_A)
    neck = _oval(28.6, Y(27), 5.2, 6.8, -12)
    d.clip("bodyclip", [body, neck])
    d.add(body, c["fur"])
    d.add(neck, c["fur"])
    (sx, sy), (vx, vy) = _rot([(cx - 2, cy - 3.5), (cx + 2, cy + 3.6)], SIT_A, cx, cy)
    d.add(_oval(sx, sy, 12, 3.2, SIT_A), c["dark"], sil=False, clip="bodyclip", opacity=0.45)
    d.add(_oval(vx, vy, 9, 2.2, SIT_A), c["light"], sil=False, clip="bodyclip")
    d.add(_oval(32, Y(30), 2.4, 5.2, -12), c["light"], sil=False, clip="bodyclip")

    if HARNESS:
        top = lambda x: cy - ry * math.sqrt(max(0, 1 - ((x - cx) / rx) ** 2))
        xs = [cx - 6.5 + i * 0.6 for i in range(21)]
        pts = [(x, top(x) - 0.3) for x in xs] + [(x, top(x) + 2.1) for x in reversed(xs)]
        d.add(poly(_rot(pts, SIT_A, cx, cy)), c["harness"], sil=False, clip="bodyclip")
        girth = [(cx + 5.6, cy - 16), (cx + 9, cy - 16), (cx + 9, cy + 9), (cx + 5.6, cy + 9)]
        d.add(poly(_rot(girth, SIT_A, cx, cy)), c["harness"], sil=False, clip="bodyclip")
        (gx, gy), = _rot([(cx - 1.5, top(cx - 1.5) + 1.1)], SIT_A, cx, cy)
        d.add(circle(gx, gy, 1.35), c["ring"], sil=False, edge=True)

    # patte arrière proche : cuisse posée au sol, pied devant… ou levée pour se gratter
    foot = None
    if p["paw"] is None:
        d.add(ellipse(21.8, GROUND - 0.7, 2.8, 1.4), c["fur"])
        thigh = _oval(16, Y(38), 6.3, 5.3, -15)
        d.add(thigh, c["fur"])
        d.add(thigh, c["fur"], sil=False, edge=True)
    else:
        px, py = p["paw"]
        kx, ky = 20.6, Y(33.6)                       # genou
        shin = _limb(kx, ky, px, py, 3.8, 3.0)
        foot = ellipse(px, py, 2.6, 1.7, f"rotate({math.degrees(math.atan2(py - ky, px - kx)):.1f} {px:.2f} {py:.2f})")
        thigh = _oval(16.2, Y(37.2), 6.3, 5.4, -50)
        for part in (shin, thigh):
            d.add(part, c["fur"])
            d.add(part, c["fur"], sil=False, edge=True)

    htr = f"translate({-2.6 + p['head_dx']:.2f} {-3.4 + p['head_dy']:.2f}) rotate({p['head_rot']:.1f} 32 {Y(25)})"
    _side_head(d, p, Y, htr)
    if foot:        # le pied gratte par-dessus le bas de l'oreille ; petits traits de vitesse
        d.add(foot, c["fur"])
        d.add(foot, c["fur"], sil=False, edge=True)
        s = p["scratch_ph"]
        for k in (0, 1):
            r = 3.6 + 1.4 * k
            a0, a1 = math.radians(150 + 30 * s), math.radians(215 + 30 * s)
            d.raw(line(f"M{px + r * math.cos(a0):.2f},{py + r * math.sin(a0):.2f} "
                       f"A{r},{r} 0 0 1 {px + r * math.cos(a1):.2f},{py + r * math.sin(a1):.2f}", OUTLINE, 0.7))
    return d


def down_sit(p):
    """Assis, vers la caméra : tête haute, cuisses posées de chaque côté, pattes avant tendues."""
    c = PAL
    d = Drawing(W, H)
    b = p["bob"]
    Y = lambda v: v + b
    d.under.append(f'<ellipse cx="24" cy="{GROUND}" rx="11" ry="2.3" fill="#000" opacity="0.2"/>')

    # queue posée au sol derrière : elle dépasse à droite et balaie
    ta = 72 if p["tail"] is None else p["tail"]
    d.add(ellipse(27, GROUND - 4 - 6.4, 1.8, 6.4, f"rotate({ta:.1f} 27 {GROUND - 4})"), c["dark"])
    # cuisses au sol de part et d'autre, pattes arrière qui dépassent à peine
    for s in (-1, 1):
        d.add(ellipse(24 + s * 9, GROUND - 1.1, 2.2, 1.3), c["fur"])
        d.add(ellipse(24 + s * 6.6, Y(38.8), 3.9, 4.4), c["fur"])

    body = ellipse(24, Y(30), 7.8, 9.5)
    d.clip("bodyclip", [body])
    d.add(body, c["fur"])
    d.add(ellipse(24, Y(27), 5.2, 8), c["dark"], sil=False, clip="bodyclip", opacity=0.4)

    for hx in (20.6, 27.4):
        fy = GROUND - 0.7
        d.add(leg(hx, Y(34), hx, fy, 3.4), c["fur"])
        d.add(ellipse(hx, fy, 2.3, 1.4), c["fur"])

    chest = ellipse(24, Y(32.4), 6.4, 5.4)
    d.clip("chestclip", [chest])
    d.add(chest, c["fur"])
    d.add(ellipse(24, Y(34), 3.8, 3.2), c["light"], sil=False, clip="chestclip")
    if HARNESS:
        d.add(rect(16, Y(32.6), 16, 2.6), c["harness"], sil=False, clip="chestclip")
        d.add(circle(24, Y(33.9), 1.35), c["ring"], sil=False, edge=True)

    htr = f"translate({p['head_dx']:.2f} {-5.4 + p['head_dy']:.2f})"
    _down_head(d, p, Y, htr)
    return d


def side_lie(p):
    """Couché de profil (vers la droite), la tête posée sur les pattes avant ; le flanc respire."""
    c = PAL
    d = Drawing(W, H)
    br = p["breath"]
    d.under.append(f'<ellipse cx="23" cy="{GROUND+0.2}" rx="16" ry="2.1" fill="#000" opacity="0.2"/>')

    # queue posée au sol, derrière
    ta = -96 if p["tail"] is None else p["tail"]
    d.add(ellipse(9.6, GROUND - 2.2 - 6.5, 1.9, 6.5, f"rotate({ta:.1f} 9.6 {GROUND - 2.2})"), c["fur"])
    # patte avant d'en face, allongée devant (foncée)
    d.add(_limb(29, 40.6, 38.4, 41.6, 3.2, 2.8), c["dark"])
    d.add(ellipse(39.6, 41.8, 2.3, 1.3), c["dark"])

    # corps couché : le ventre reste au sol, le dos monte et descend avec la respiration
    cx, cy, rx, ry = 21.5, 38.4 - br * 0.5, 13.8, 5.4 + br * 0.5
    body = ellipse(cx, cy, rx, ry)
    neck = ellipse(30.6, 37.6 - br * 0.3, 5.2, 5.4)
    d.clip("bodyclip", [body, neck])
    d.add(body, c["fur"])
    d.add(neck, c["fur"])
    d.add(ellipse(cx - 2, cy - 3.2, 12.3, 3.2), c["dark"], sil=False, clip="bodyclip", opacity=0.45)
    if HARNESS:
        top = lambda x: cy - ry * math.sqrt(max(0, 1 - ((x - cx) / rx) ** 2))
        xs = [cx - 7 + i * 0.7 for i in range(21)]
        pts = [(x, top(x) - 0.3) for x in xs] + [(x, top(x) + 2.1) for x in reversed(xs)]
        d.add(poly(pts), c["harness"], sil=False, clip="bodyclip")
        d.add(rect(cx + 5.4, cy - 12, 3.4, 22), c["harness"], sil=False, clip="bodyclip")
        d.add(circle(cx - 1, top(cx - 1) + 1.1, 1.35), c["ring"], sil=False, edge=True)

    # cuisse arrière proche, pied replié devant elle
    d.add(ellipse(18.6, GROUND - 0.8, 2.6, 1.3), c["fur"])
    thigh = ellipse(12.8, 39.4 - br * 0.3, 5.6, 4.4)
    d.add(thigh, c["fur"])
    d.add(thigh, c["fur"], sil=False, edge=True)
    # patte avant proche, allongée devant
    d.add(_limb(29.5, 41.2, 39.4, 42.4, 3.4, 3.0), c["fur"])
    d.add(ellipse(40.8, 42.6, 2.5, 1.4), c["fur"])

    htr = f"translate({0.4 + p['head_dx']:.2f} {14.4 + p['head_dy']:.2f}) rotate({6 + p['head_rot']:.1f} 32 25)"
    _side_head(d, p, lambda v: v, htr)
    return d


def down_lie(p):
    """Couché en rond, vers la caméra : le dos (et le harnais) derrière, la cuisse à droite (la queue
    est cachée dessous), la tête posée à gauche ; le dos respire."""
    c = PAL
    d = Drawing(W, H)
    br = p["breath"]
    d.under.append(f'<ellipse cx="24" cy="{GROUND - 0.6}" rx="14.5" ry="2.8" fill="#000" opacity="0.2"/>')

    # corps en boule : le bas reste au sol, le haut (le dos) monte et descend
    cx, cy, rx, ry = 25, 35.4 - br * 0.4, 12.6 + br * 0.3, 6.9 + br * 0.4
    body = ellipse(cx, cy, rx, ry)
    d.clip("bodyclip", [body])
    d.add(body, c["fur"])
    d.add(ellipse(cx + 1, cy - 4.2, 10.5, 4), c["dark"], sil=False, clip="bodyclip", opacity=0.4)
    if HARNESS:     # bretelle le long de l'échine, sangle autour du poitrail (côté tête), anneau
        d.add(poly(_band(cx, cy, rx - 2.3, ry - 2.3, 200, 335, 2.4, 2.4)), c["harness"], sil=False, clip="bodyclip")
        a = math.radians(285)
        d.add(circle(cx + (rx - 2.3) * math.cos(a), cy + (ry - 2.3) * math.sin(a), 1.35), c["ring"], sil=False, edge=True)

    # cuisse arrière à droite, pied rentré
    d.add(ellipse(35, GROUND - 1.6, 2.4, 1.3), c["fur"])
    thigh = ellipse(32.4, 35.8 - br * 0.3, 5.4, 4.6)
    d.add(thigh, c["fur"])
    d.add(thigh, c["fur"], sil=False, edge=True)
    # pattes avant repliées sous le menton
    for hx in (14.2, 21.2):
        d.add(ellipse(hx, GROUND - 1.5, 2.4, 1.5), c["fur"])

    htr = f"translate({-6.4 + p['head_dx']:.2f} {8.2 + p['head_dy']:.2f}) rotate({-8 + p['head_rot']:.1f} 24 35.5)"
    _down_head(d, p, lambda v: v, htr)
    return d


POSES = {"stand": VIEWS,
         "sit": {"right": side_sit, "down": down_sit},
         "lie": {"right": side_lie, "down": down_lie}}


def a_sit(view):
    """Assis : la queue balaie doucement le sol, petite respiration, un clignement sur 8 images."""
    out = []
    for i in range(8):
        a = i / 8 * 2 * math.pi
        ta = -80 + 9 * math.sin(a) if view == "right" else 70 + 22 * math.sin(a)
        out.append((P(pose="sit", tail=ta, bob=0.15 * (1 - math.cos(a)), blink=1 if i == 5 else 0), ""))
    return out


def a_yawn(view):
    """Assis, il bâille : yeux fermés, tête levée, gueule grande ouverte, puis il referme."""
    ms = [0.0, 0.35, 0.9, 1.5, 1.65, 1.3, 0.5, 0.0]
    up = [0.0, 0.3, 0.7, 1.0, 1.0, 0.8, 0.3, 0.0]
    out = []
    for i in range(8):
        k = up[i]
        q = dict(pose="sit", mouth=ms[i], blink=1 if 0 < i < 7 else 0, squint=2 <= i <= 5,
                 tail=-80 if view == "right" else 70)
        if view == "right":
            q.update(head_rot=-16 * k, head_dx=-0.6 * k, ear=14 * k)
        else:
            q.update(head_dy=-1.6 * k, ear=-8 * k)
        out.append((P(**q), ""))
    return out


def a_scratch(view):
    """Assis de profil, il se gratte derrière l'oreille : la patte arrière mouline, yeux mi-clos de plaisir."""
    out = []
    for i in range(4):
        a = i / 4 * 2 * math.pi
        paw = (24.2 + 1.4 * math.cos(a), 25.2 + 1.4 * math.sin(a))
        out.append((P(pose="sit", paw=paw, scratch_ph=i % 2, head_rot=16, head_dx=-1.4, head_dy=2.6, lid=0.55, lid_tilt=-34,
                      mouth=0.5, ear=-6 + 7 * math.sin(a), tail=-78 + 8 * math.sin(2 * a),
                      bob=0.25 * math.sin(a)), ""))
    return out


def a_sleep(view):
    """Endormi : yeux fermés, respiration lente (le flanc monte et descend). Le jeu ajoute les « Z »."""
    return [(P(pose="lie", blink=1, breath=br, ear=-2 if view == "down" else 6), "") for br in (0, 0.5, 1, 0.5)]


def a_shake(view):
    """Il s'ébroue : le corps se tord d'un côté puis de l'autre (deux bonnes secousses), oreilles au vent, poils
    hérissés, puis se calme."""
    ks = [0.6, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -0.8, 0.5, -0.2]
    fl = [1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.9, 1.8, 1.5, 1.1, 0.8]
    out = []
    for i, k in enumerate(ks):
        q = dict(fluff=fl[i], fluff_ph=i * 1.9, twist=k, squint=i < len(ks) - 1, mouth=0.5 if i % 2 else 0.25)
        if view == "right":
            q.update(head_rot=-10 * k, ear=(40 if k > 0 else 100) * abs(k), tail=-40 - 28 * k, bob=-0.4 * abs(k))
            tr = f"translate({0.7 * k:.2f} 0)"
        else:
            q.update(head_dx=-1.8 * k, ear=20, ear_tilt=-60 * k, tail=25 + 45 * k)
            tr = ""
        out.append((P(**q), tr))
    return out


REST_ANIMS = {   # nom : (fonction, fps, vues, boucle)
    "sit":     (a_sit, 6, ("down", "right"), True),
    "yawn":    (a_yawn, 8, ("down", "right"), False),
    "scratch": (a_scratch, 14, ("right",), True),
    "sleep":   (a_sleep, 3, ("down", "right"), True),
    "shake":   (a_shake, 16, ("down", "right"), False),
}


def rest_frames(anim, view):
    """Liste de SVG d'une pose de repos ('right' ou 'down' ; la gauche est le miroir de la droite)."""
    fn = REST_ANIMS[anim][0]
    return [POSES[p["pose"]][view](p).svg(f"{BASE[view]} {tr}".strip()) for p, tr in fn(view)]

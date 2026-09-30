"""
Tecky — le teckel au harnais rouge.
Vue de dessus 3/4, cellule 48x48 (unités = pixels en 1x), pieds à y=44.

Vues dessinées : side (profil, tourné vers la droite), down (vers la caméra),
up (de dos). La vue gauche est le miroir de la vue droite.
"""
import math

from spritelib import (Drawing, circle, ellipse, rect, poly, leg, line, OUTLINE)

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
                head_rot=0.0, lunge=0.0, blink=0.0, xeyes=False, ear=0.0)
    base.update(kw)
    return base


def _legs_offsets(p):
    if p["phase"] is None:
        return (0, 0), (0, 0)
    a = p["phase"]
    b = a + math.pi
    return ((2.2 * math.cos(a), max(0, math.sin(a)) * 1.8),
            (2.2 * math.cos(b), max(0, math.sin(b)) * 1.8))


def _eye(d, x, y, p, tr, r=1.8, look=0.4):
    c = PAL
    if p["xeyes"]:
        s = 1.4
        d.raw(f'<g transform="{tr}">' + line(f"M{x-s},{y-s} L{x+s},{y+s} M{x-s},{y+s} L{x+s},{y-s}", OUTLINE, 1.0) + "</g>")
    elif p["blink"] > 0.5:
        d.raw(f'<g transform="{tr}">' + line(f"M{x-1.7},{y} Q{x},{y+1.1} {x+1.7},{y}", OUTLINE, 0.9) + "</g>")
    else:
        d.add(circle(x, y, r, tr), c["white"], sil=False)
        d.add(circle(x + look, y + 0.25, r * 0.64, tr), c["pupil"], sil=False)
        d.add(circle(x + look + 0.35, y - 0.35, r * 0.24, tr), c["white"], sil=False)


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

    body = ellipse(22, Y(32), 13.5, 6)
    neck = ellipse(31 + ld, Y(27), 5, 6)
    d.clip("bodyclip", [body, neck])
    d.add(body, c["fur"])
    d.add(neck, c["fur"])
    d.add(ellipse(20, Y(28.5), 12, 3.2), c["dark"], sil=False, clip="bodyclip", opacity=0.45)
    d.add(ellipse(24, Y(35.6), 9, 2.2), c["light"], sil=False, clip="bodyclip")

    if HARNESS:
        # bretelle dorsale qui suit la courbe du dos
        top = lambda x: Y(32) - 6 * math.sqrt(max(0, 1 - ((x - 22) / 13.5) ** 2))
        xs = [15 + i * 0.7 for i in range(21)]
        pts = [(x, top(x) - 0.3) for x in xs] + [(x, top(x) + 2.1) for x in reversed(xs)]
        d.add(poly(pts), c["harness"], sil=False, clip="bodyclip")
        d.add(rect(27.2 + ld * 0.6, Y(19), 3.4, 22), c["harness"], sil=False, clip="bodyclip")
        d.add(circle(21, top(21) + 1.1, 1.35), c["ring"], sil=False, edge=True)

    # tête
    htr = f"translate({ld + p['head_dx']:.2f} {p['head_dy']:.2f}) rotate({p['head_rot']:.1f} 32 {Y(25)})"
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
    return d


# ====================================================================== FACE (vers la caméra)
def down(p):
    c = PAL
    d = Drawing(W, H)
    b = p["bob"]
    Y = lambda v: v + b
    (_, lA), (_, lB) = _legs_offsets(p)
    d.under.append(f'<ellipse cx="24" cy="{GROUND}" rx="9.5" ry="2.2" fill="#000" opacity="0.2"/>')

    ta = 25 if p["tail"] is None else p["tail"]
    d.add(ellipse(24, Y(12.5), 1.7, 4, f"rotate({ta} 24 {Y(16)})"), c["dark"])
    d.add(ellipse(16.9, Y(30.5) - lB, 2.3, 2), c["dark"])
    d.add(ellipse(31.1, Y(30.5) - lA, 2.3, 2), c["dark"])

    body = ellipse(24, Y(24), 7.5, 10)
    d.clip("bodyclip", [body])
    d.add(body, c["fur"])
    d.add(ellipse(24, Y(21), 5, 8), c["dark"], sil=False, clip="bodyclip", opacity=0.4)
    if HARNESS:
        d.add(rect(15, Y(22.6), 18, 3), c["harness"], sil=False, clip="bodyclip")
        d.add(circle(24, Y(24.1), 1.35), c["ring"], sil=False, edge=True)

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
    m = p["mouth"]
    d.add(circle(24, Y(27.5), 7, htr), c["fur"])
    d.add(ellipse(24, Y(23.2), 4.2, 2, htr), c["dark"], sil=False, opacity=0.35)
    d.add(ellipse(24, Y(32), 4.4, 3.3, htr), c["light"])
    if m > 0.05:
        d.add(ellipse(24, Y(34.2 + m * 0.8), 2.5, 0.3 + m * 1.8, htr), c["mouth"])
        if m > 0.4:
            d.add(ellipse(24, Y(35 + m * 1.2), 1.4, 0.9 * m, htr), c["tongue"], sil=False)
    else:
        d.raw(f'<g transform="{htr}">' + line(f"M21.8,{Y(33.4)} Q24,{Y(34.8)} 26.2,{Y(33.4)}", OUTLINE, 0.8) + "</g>")
    d.add(ellipse(24, Y(30.6), 2.2, 1.6, htr), c["nose"])
    d.add(ellipse(23.3, Y(30.1), 0.6, 0.35, htr), c["white"], sil=False, opacity=0.8)
    _eye(d, 20.9, Y(26.6), p, htr, look=0)
    _eye(d, 27.1, Y(26.6), p, htr, look=0)
    e = p["ear"]
    d.add(ellipse(16.9, Y(30), 2.8, 6, f"{htr} rotate({12 + e:.1f} 16.9 {Y(25)})"), c["dark"])
    d.add(ellipse(31.1, Y(30), 2.8, 6, f"{htr} rotate({-12 - e:.1f} 31.1 {Y(25)})"), c["dark"])
    return d


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

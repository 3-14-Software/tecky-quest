"""
Chiens ennemis — même squelette que Tecky, mais paramétré (gabarit,
oreilles, museau, queue, couleurs) pour obtenir des silhouettes distinctes.
Les animations sont celles de tecky.py (mêmes noms, mêmes FPS).
"""
import math

import tecky
from spritelib import Drawing, circle, ellipse, rect, poly, leg, line, OUTLINE

W = H = 48
G = 43.4          # ligne des pieds

DOGS = {
    # petit roquet nerveux : rapide, fragile
    "roquet": dict(fur="#F1ECE2", dark="#B9AFA0", light="#FFFFFF", legcol=None, patch="#D59A5B",
                   body_rx=9.5, body_ry=5.2, leg=10, leg_w=2.8, head_r=5.6, snout=(3.6, 2.2),
                   snout_f=(3.2, 2.4), ear="pointy", tail="long", top_w=6, collar="spike"),
    # bouledogue : lent, costaud
    "bouledogue": dict(fur="#8C8F99", dark="#5E616B", light="#E4E1DA", legcol=None, patch=None,
                       body_rx=11, body_ry=7.4, leg=8.5, leg_w=4.4, head_r=7.2, snout=(3.2, 3.4),
                       snout_f=(4.8, 3.2), ear="rose", tail="stub", top_w=9.5, collar="spike"),
    # grand molosse noir et feu : le plus dangereux
    "molosse": dict(fur="#2E2A2B", dark="#1C1819", light="#C77B3B", legcol="#C77B3B", patch=None,
                    body_rx=12.5, body_ry=6.2, leg=13, leg_w=3.4, head_r=6.2, snout=(5.2, 2.7),
                    snout_f=(3.8, 3.4), ear="pointy", tail="bushy", top_w=7.5, collar="spike"),
}

EYE_ANGRY = True


def _brow(d, x0, y0, x1, y1, tr):
    d.raw(f'<g transform="{tr}">' + line(f"M{x0:.2f},{y0:.2f} L{x1:.2f},{y1:.2f}", OUTLINE, 1.2) + "</g>")


def _collar_studs(d, pts, tr=""):
    for x, y in pts:
        d.add(circle(x, y, 0.75, tr), "#D4D8E0", sil=False)


# ================================================================== PROFIL
def side(S, p):
    d = Drawing(W, H)
    b = p["bob"]
    Y = lambda v: v + b
    ld = p["lunge"] * 0.5
    (dxA, lA), (dxB, lB) = tecky._legs_offsets(p)
    rx, ry = S["body_rx"], S["body_ry"]
    cx = 22
    cy = G - S["leg"] - ry + 3
    hip = cy + ry - 3
    fx, bx = cx + rx, cx - rx
    legc = S["legcol"] or S["fur"]
    d.under.append(f'<ellipse cx="{cx}" cy="{G + 0.8}" rx="{rx + 1}" ry="2" fill="#000" opacity="0.2"/>')

    for hx, dx, lift, col in ((bx + 7.5, dxA, lA, S["dark"]), (fx - 8.5, dxB, lB, S["dark"]),
                              (bx + 4.5, dxB, lB, legc), (fx - 5.5, dxA, lA, legc)):
        fy = G - lift
        d.add(leg(hx, Y(hip), hx + dx, fy, S["leg_w"]), col)
        d.add(ellipse(hx + dx + 0.9, fy, S["leg_w"] * 0.65, 1.3), col)

    ta = -35 if p["tail"] is None else p["tail"]
    px, py = bx + 1, Y(cy - 3)
    if S["tail"] == "long":
        d.add(ellipse(px, py - 6, 1.7, 6, f"rotate({ta} {px} {py})"), S["fur"])
    elif S["tail"] == "stub":
        d.add(circle(bx + 0.8, Y(cy - 2.5), 2.4, f"rotate({(ta + 35) * 0.3:.1f} {bx + 2} {Y(cy)})"), S["fur"])
    else:
        d.add(ellipse(px, py - 7, 2.8, 7.5, f"rotate({ta - 100:.1f} {px} {py})"), S["fur"])

    body = ellipse(cx, Y(cy), rx, ry)
    neck = ellipse(fx - 4.5 + ld, Y(cy - 5), 5, 6)
    d.clip("bodyclip", [body, neck])
    d.add(body, S["fur"])
    d.add(neck, S["fur"])
    d.add(ellipse(cx - 2, Y(cy - ry * 0.55), rx * 0.9, ry * 0.55), S["dark"], sil=False, clip="bodyclip", opacity=0.45)
    d.add(ellipse(cx + 2, Y(cy + ry * 0.6), rx * 0.66, ry * 0.37), S["light"], sil=False, clip="bodyclip")
    if S["patch"]:
        d.add(ellipse(cx - 3, Y(cy - 1), 3.5, 2.8), S["patch"], sil=False, clip="bodyclip")
    # collier à clous
    ctr = f"rotate(28 {fx - 4.2 + ld:.2f} {Y(cy - 5):.2f})"
    d.add(rect(fx - 6 + ld, Y(cy - 13), 3.2, 16, 0, ctr), "#2B2B33", sil=False, clip="bodyclip")
    _collar_studs(d, [(fx - 4.4 + ld, Y(cy - 8.5 + k * 3.2)) for k in range(3)], ctr)

    hx, hy, hr = fx - 0.5, cy - 11, S["head_r"]
    sr, sry = S["snout"]
    htr = f"translate({ld + p['head_dx']:.2f} {p['head_dy']:.2f}) rotate({p['head_rot']:.1f} {fx - 3.5:.2f} {Y(cy - 7):.2f})"
    m = p["mouth"]
    ear = p["ear"]
    if S["ear"] == "pointy":
        d.add(poly([(hx - 4.8, Y(hy - 2)), (hx - 0.3, Y(hy - 4.5)), (hx - 3.8, Y(hy - 12))],
                   f"{htr} rotate({-ear * 0.6:.1f} {hx - 2.5:.2f} {Y(hy - 3):.2f})"), S["dark"])
    d.add(circle(hx, Y(hy), hr, htr), S["fur"])
    if S["patch"]:
        d.add(circle(hx - 1, Y(hy - 1), hr * 0.7, htr), S["patch"], sil=False, opacity=0.9)
    mcx = hx + hr * 0.35 + sr * 0.65
    if m > 0.05:
        d.add(ellipse(mcx, Y(hy + sry + 0.8 + m * 0.9), sr * 0.72, 0.4 + m * 1.6, htr), tecky.PAL["mouth"])
    d.add(ellipse(mcx - 0.7, Y(hy + sry + 1.6 + m * 2), sr * 0.8, 1.5,
                  f"{htr} rotate({m * 12:.1f} {hx + 1:.2f} {Y(hy + 4):.2f})"), S["light"])
    if m > 0.4:
        d.add(ellipse(mcx + 0.5, Y(hy + sry + 1.5 + m * 1.2), 1.6, 0.9, htr), tecky.PAL["tongue"], sil=False)
    d.add(ellipse(mcx, Y(hy + 1.8 - m * 0.4), sr, sry, htr), S["light"])
    d.add(ellipse(mcx + sr * 0.9, Y(hy + 1.8 - sry * 0.4 - m * 0.4), 1.8, 1.4, htr), "#1A1414")
    if m <= 0.05:
        # babines retroussées : petit croc
        d.add(poly([(mcx + 0.3, Y(hy + sry + 1.3)), (mcx + 1.5, Y(hy + sry + 1.3)), (mcx + 0.9, Y(hy + sry + 2.8))], htr),
              "#FFFFFF", sil=False, edge=True)
    tecky._eye(d, hx + 2.6, Y(hy - 1.7), p, htr, r=1.6)
    if EYE_ANGRY and not p["xeyes"] and p["blink"] < 0.5:
        _brow(d, hx + 0.9, Y(hy - 4.4), hx + 4.4, Y(hy - 3.0), htr)
    if S["ear"] == "droop":
        d.add(ellipse(hx - 2.8, Y(hy + 2.5), 3, 6, f"{htr} rotate({12 + ear:.1f} {hx - 2.8:.2f} {Y(hy - 3):.2f})"), S["dark"])
    elif S["ear"] == "rose":
        d.add(poly([(hx - 5, Y(hy - 3)), (hx - 1, Y(hy - 5.8)), (hx - 6.5, Y(hy - 7.5 - ear * 0.05))], htr), S["dark"])
    return d


# ================================================================== FACE
def down(S, p):
    d = Drawing(W, H)
    shift = S["leg"] - 8.4
    b = p["bob"] - shift
    Y = lambda v: v + b
    (_, lA), (_, lB) = tecky._legs_offsets(p)
    tw, hr = S["top_w"], S["head_r"] + 0.5
    legc = S["legcol"] or S["fur"]
    d.under.append(f'<ellipse cx="24" cy="{G + 0.6}" rx="{tw + 2}" ry="2.2" fill="#000" opacity="0.2"/>')

    # (queue cachée derrière le corps en vue de face)
    d.add(ellipse(24 - tw - 0.4, Y(30.5) - lB, 2.3, 2), S["dark"])
    d.add(ellipse(24 + tw + 0.4, Y(30.5) - lA, 2.3, 2), S["dark"])

    body = ellipse(24, Y(24), tw, S["body_rx"] * 0.74)
    d.clip("bodyclip", [body])
    d.add(body, S["fur"])
    d.add(ellipse(24, Y(21), tw * 0.66, S["body_rx"] * 0.6), S["dark"], sil=False, clip="bodyclip", opacity=0.4)
    if S["patch"]:
        d.add(ellipse(22, Y(19), 3, 2.5), S["patch"], sil=False, clip="bodyclip")

    sx = 3.7 * tw / 7.5 + 0.5
    for hx, lift in ((24 - sx, lA), (24 + sx, lB)):
        fy = G - lift
        d.add(leg(hx, Y(35), hx, fy, S["leg_w"]), legc)
        d.add(ellipse(hx, fy, S["leg_w"] * 0.68, 1.4), legc)

    chest = ellipse(24, Y(33.5), tw * 0.87, 5)
    d.clip("chestclip", [chest])
    d.add(chest, S["fur"])
    d.add(ellipse(24, Y(35), tw * 0.55, 3), S["light"], sil=False, clip="chestclip")
    d.add(rect(12, Y(31.2), 24, 2.6), "#2B2B33", sil=False, clip="chestclip")
    _collar_studs(d, [(24 + k * 2.6, Y(32.5)) for k in (-2, -1, 0, 1, 2)])

    htr = f"translate({p['head_dx']:.2f} {p['head_dy']:.2f})"
    m = p["mouth"]
    ear = p["ear"]
    ex = hr * 0.45
    if S["ear"] == "pointy":
        for s in (-1, 1):
            d.add(poly([(24 + s * (hr - 1.5), Y(27.5 - hr * 0.35)), (24 + s * 1.8, Y(27.5 - hr * 0.8)),
                        (24 + s * (hr - 0.5), Y(27.5 - hr - 5.5))],
                       f"{htr} rotate({s * ear * 0.6:.1f} 24 {Y(27.5 - hr * 0.5):.2f})"), S["dark"])
    d.add(circle(24, Y(27.5), hr, htr), S["fur"])
    if S["patch"]:
        d.add(circle(21.8, Y(26.5), hr * 0.5, htr), S["patch"], sil=False, opacity=0.9)
    fr, fry = S["snout_f"]
    d.add(ellipse(24, Y(27.5 + hr * 0.62), fr, fry, htr), S["light"])
    if m > 0.05:
        d.add(ellipse(24, Y(27.5 + hr * 0.62 + fry * 0.7 + m * 0.8), fr * 0.55, 0.3 + m * 1.8, htr), tecky.PAL["mouth"])
        if m > 0.4:
            d.add(ellipse(24, Y(27.5 + hr * 0.62 + fry * 0.7 + 0.8 + m * 1.2), 1.3, 0.9 * m, htr), tecky.PAL["tongue"], sil=False)
    else:
        yy = Y(27.5 + hr * 0.62 + fry * 0.45)
        d.raw(f'<g transform="{htr}">' + line(f"M{24 - fr * 0.5:.2f},{yy + 0.6:.2f} Q24,{yy - 0.6:.2f} {24 + fr * 0.5:.2f},{yy + 0.6:.2f}", OUTLINE, 0.8) + "</g>")
        for s in (-1, 1):
            d.add(poly([(24 + s * 1.2, yy + 0.3), (24 + s * 2.2, yy + 0.5), (24 + s * 1.7, yy + 1.8)], htr),
                  "#FFFFFF", sil=False, edge=True)
    d.add(ellipse(24, Y(27.5 + hr * 0.62 - fry * 0.45), 2.1, 1.5, htr), "#1A1414")
    for s in (-1, 1):
        tecky._eye(d, 24 + s * ex * 1.45 if False else 24 + s * 3.1, Y(26.4), p, htr, r=1.6, look=0)
        if EYE_ANGRY and not p["xeyes"] and p["blink"] < 0.5:
            _brow(d, 24 + s * 5, Y(23.6), 24 + s * 1.6, Y(24.9), htr)
    if S["ear"] == "droop":
        for s in (-1, 1):
            d.add(ellipse(24 + s * 7.1, Y(30), 2.8, 6, f"{htr} rotate({-s * (12 + ear):.1f} {24 + s * 7.1} {Y(25)})"), S["dark"])
    elif S["ear"] == "rose":
        for s in (-1, 1):
            d.add(poly([(24 + s * (hr - 2.5), Y(27.5 - hr * 0.7)), (24 + s * (hr - 6), Y(27.5 - hr * 0.95)),
                        (24 + s * (hr + 1.5), Y(27.5 - hr * 0.35))], htr), S["dark"])
    return d


# ================================================================== DOS
def up(S, p):
    d = Drawing(W, H)
    shift = S["leg"] - 8.4
    b = p["bob"] - shift
    Y = lambda v: v + b
    (_, lA), (_, lB) = tecky._legs_offsets(p)
    tw, hr = S["top_w"], S["head_r"] + 0.1
    legc = S["legcol"] or S["fur"]
    blen = S["body_rx"] * 0.78
    d.under.append(f'<ellipse cx="24" cy="{G + 0.6}" rx="{tw + 2}" ry="2.2" fill="#000" opacity="0.2"/>')

    d.add(ellipse(24 - tw + 0.5, Y(21) - lA, 2.2, 1.8), S["dark"])
    d.add(ellipse(24 + tw - 0.5, Y(21) - lB, 2.2, 1.8), S["dark"])
    sx = 4.2 * tw / 7.5
    for hx, lift in ((24 - sx, lA), (24 + sx, lB)):
        fy = G - lift
        d.add(leg(hx, Y(33), hx, fy, S["leg_w"] + 0.2), legc)
        d.add(ellipse(hx, fy, S["leg_w"] * 0.7, 1.4), legc)

    body = ellipse(24, Y(26), tw, blen)
    d.clip("bodyclip", [body])
    d.add(body, S["fur"])
    d.add(ellipse(24, Y(24), tw * 0.64, blen * 0.86), S["dark"], sil=False, clip="bodyclip", opacity=0.4)
    if S["patch"]:
        d.add(ellipse(25.5, Y(27), 3, 3.5), S["patch"], sil=False, clip="bodyclip")

    ta = 25 if p["tail"] is None else p["tail"]
    if S["tail"] == "long":
        d.add(ellipse(24, Y(31), 1.6, 4.6, f"rotate({ta} 24 {Y(35.5)})"), S["dark"], sil=False, edge=True)
    elif S["tail"] == "stub":
        d.add(circle(24, Y(26 + blen - 2.5), 2, ""), S["fur"], sil=False, edge=True)
    else:
        d.add(ellipse(24, Y(32), 2.7, 5.5, f"rotate({ta * 0.6:.1f} 24 {Y(26 + blen - 2)})"), S["dark"], sil=False, edge=True)

    htr = f"translate({p['head_dx']:.2f} {p['head_dy']:.2f})"
    ear = p["ear"]
    hy = 26 - blen - hr * 0.35
    d.add(rect(12, Y(hy + hr - 1.2), 24, 2.6), "#2B2B33", sil=False, clip="bodyclip")
    if S["ear"] == "pointy":
        for s in (-1, 1):
            d.add(poly([(24 + s * (hr - 1.5), Y(hy - hr * 0.3)), (24 + s * 1.8, Y(hy - hr * 0.8)),
                        (24 + s * (hr - 0.5), Y(hy - hr - 5.5))],
                       f"{htr} rotate({s * ear * 0.6:.1f} 24 {Y(hy - hr * 0.5):.2f})"), S["dark"])
    d.add(circle(24, Y(hy), hr, htr), S["fur"])
    d.add(ellipse(24, Y(hy - 1.2), hr * 0.72, hr * 0.6, htr), S["dark"], sil=False, opacity=0.35)
    if S["ear"] == "droop":
        for s in (-1, 1):
            d.add(ellipse(24 + s * 6.4, Y(hy + 2.5), 2.7, 5.5, f"{htr} rotate({-s * (10 + ear):.1f} {24 + s * 6.4} {Y(hy - 2)})"), S["dark"])
    elif S["ear"] == "rose":
        for s in (-1, 1):
            d.add(poly([(24 + s * (hr - 2.5), Y(hy - hr * 0.7)), (24 + s * (hr - 6), Y(hy - hr * 0.95)),
                        (24 + s * (hr + 1.5), Y(hy - hr * 0.35))], htr), S["dark"])
    return d


BASE = {"right": "translate(0.9 5.3) scale(0.88)", "down": "", "up": ""}
# les grands chiens sont réduits un peu en face / de dos pour que les oreilles tiennent
BASE_TALL = {"right": "translate(0.9 5.3) scale(0.88)",
             "down": "translate(2.4 4.4) scale(0.9)", "up": "translate(3.6 6.6) scale(0.85)"}


def frames(dog, anim, view):
    S = DOGS[dog]
    fn = tecky.ANIMS[anim][0]
    views = {"right": side, "down": down, "up": up}
    base = BASE_TALL if S["leg"] > 10 else BASE
    # KO sur le dos : ligne de retournement calculée pour que la tête reste dans le cadre
    cy = G - S["leg"] - S["body_ry"] + 3
    top = cy - 11 - (12 if S["ear"] == "pointy" else S["head_r"])
    flip = f"translate(0 {45 + top:.1f}) scale(1 -1)"
    out = []
    for p, tr in fn(view):
        tr = tr.replace("translate(0 58) scale(1 -1)", flip)
        out.append(views[view](S, p).svg(f"{base[view]} {tr}".strip()))
    return out

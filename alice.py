"""
Alice — style chibi (grosse tête), cellule 48x48, pieds à y=44.
Cheveux carré blond cendré avec frange, t-shirt jaune, jupe rose.
Animations : idle, walk (4 directions), happy (saut de joie des retrouvailles).
"""
import math

from spritelib import Drawing, circle, ellipse, rect, path, poly, leg, line, OUTLINE

W = H = 48
G = 43.6

PAL = dict(skin="#F9DCC8", skin_dk="#E9BFA5", hair="#B89A6E", hair_hl="#D8C08F", hair_dk="#977B52",
           shirt="#FBE36A", shirt_dk="#E9C94A", skirt="#F4A7C3", skirt_dk="#DE85A8",
           eye="#2A1E1A", blush="#F4A1A1", mouth="#B8505A")


def A(**kw):
    base = dict(phase=None, bob=0.0, lift=0.0, arms=0.0, blink=0.0, happy=False, sway=0.0)
    base.update(kw)
    return base


def _walk(p):
    if p["phase"] is None:
        return 0, 0, 0
    a = p["phase"]
    return math.sin(a), max(0, math.sin(a)) * 1.6, max(0, -math.sin(a)) * 1.6


def _front_back(p, back):
    c = PAL
    d = Drawing(W, H)
    b = p["bob"] - p["lift"]
    Y = lambda v: v + b
    sw, lA, lB = _walk(p)
    k = max(0.5, 1 - p["lift"] / 12)
    d.under.append(f'<ellipse cx="24" cy="{G + 0.3}" rx="{7 * k:.2f}" ry="{1.8 * k:.2f}" fill="#000" opacity="0.2"/>')

    # jambes
    for x, lift in ((21.3, lA), (26.7, lB)):
        fy = G - lift - p["lift"]
        d.add(leg(x, Y(35), x, fy, 2.8), c["skin"])
        d.add(ellipse(x, fy, 2.1, 1.2), c["skin_dk"])

    # bras : arms=0 le long du corps, arms=1 levés
    ar = p["arms"]
    for s, ph in ((-1, sw), (1, -sw)):
        sx, sy = 24 + s * 6.2, Y(24.3)
        swing = ph * 1.2 if not back else -ph * 1.2
        hx = sx + s * (1.2 + ar * 2.5)
        hy = sy + 7.5 - ar * 15 + swing
        d.add(leg(sx, sy, hx, hy, 2.6), c["skin"])
        d.add(circle(hx, hy, 1.6), c["skin"])

    # jupe
    d.add(path(f"M18.8,{Y(30)} L29.2,{Y(30)} L32.4,{Y(37.2)} Q24,{Y(39.2)} 15.6,{Y(37.2)} Z"), c["skirt"])
    d.raw(line(f"M21.5,{Y(31.5)} L20.3,{Y(37.6)} M26.5,{Y(31.5)} L27.7,{Y(37.6)}", c["skirt_dk"], 0.9))
    # t-shirt + manches
    d.add(ellipse(17.8, Y(24.6), 2.8, 2.4), c["shirt"])
    d.add(ellipse(30.2, Y(24.6), 2.8, 2.4), c["shirt"])
    d.add(rect(18.2, Y(21.8), 11.6, 9.4, 3), c["shirt"])
    d.add(rect(18.2, Y(29.2), 11.6, 2, 1), c["shirt_dk"], sil=False)

    hy = Y(14)
    if back:
        d.add(circle(24, hy, 9.2), c["hair"])
        d.add(rect(14.6, hy - 1, 18.8, 10.5, 3.5), c["hair"])
        d.raw(line(f"M24,{hy - 8} L24,{hy + 9}", c["hair_dk"], 0.8))
        d.add(ellipse(20, hy - 5, 3.2, 1.6, "rotate(-25 20 %.2f)" % (hy - 5)), c["hair_hl"], sil=False, opacity=0.8)
        return d

    # face
    d.add(rect(14.6, hy - 1, 18.8, 10.5, 3.5), c["hair"])               # cheveux derrière
    d.add(circle(24, hy + 0.5, 8.6), c["skin"])
    d.add(path(f"M14.8,{hy + 3} Q14.4,{hy - 9.8} 24,{hy - 9.6} Q33.6,{hy - 9.8} 33.2,{hy + 3} "
               f"L31.6,{hy + 3} L31,{hy - 2.4} L29,{hy - 1.4} L27.6,{hy - 2.6} L25.6,{hy - 1.5} L24,{hy - 2.7} "
               f"L22.4,{hy - 1.5} L20.4,{hy - 2.6} L19,{hy - 1.4} L17,{hy - 2.4} L16.4,{hy + 3} Z"), c["hair"])
    d.add(ellipse(20.5, hy - 6.3, 3.2, 1.4, f"rotate(-20 20.5 {hy - 6.3:.2f})"), c["hair_hl"], sil=False, opacity=0.8)
    if p["happy"]:
        d.raw(line(f"M19.2,{hy + 2.4} Q20.6,{hy + 0.8} 22,{hy + 2.4} M26,{hy + 2.4} Q27.4,{hy + 0.8} 28.8,{hy + 2.4}", c["eye"], 1.0))
        d.add(path(f"M22.3,{hy + 5.2} Q24,{hy + 8} 25.7,{hy + 5.2} Z"), c["mouth"], sil=False)
    elif p["blink"] > 0.5:
        d.raw(line(f"M19.4,{hy + 2.2} Q20.6,{hy + 3} 21.8,{hy + 2.2} M26.2,{hy + 2.2} Q27.4,{hy + 3} 28.6,{hy + 2.2}", c["eye"], 0.9))
        d.raw(line(f"M22.6,{hy + 5.4} Q24,{hy + 6.5} 25.4,{hy + 5.4}", c["eye"], 0.8))
    else:
        for x in (20.6, 27.4):
            d.add(ellipse(x, hy + 2.2, 1.3, 1.6), c["eye"], sil=False)
            d.add(circle(x + 0.4, hy + 1.6, 0.45), "#FFFFFF", sil=False)
        d.raw(line(f"M22.6,{hy + 5.4} Q24,{hy + 6.5} 25.4,{hy + 5.4}", c["eye"], 0.8))
    for x in (18.6, 29.4):
        d.add(ellipse(x, hy + 4.4, 1.7, 1.1), c["blush"], sil=False, opacity=0.6)
    return d


def front(p):
    return _front_back(p, back=False)


def back(p):
    return _front_back(p, back=True)


def side(p):
    c = PAL
    d = Drawing(W, H)
    b = p["bob"] - p["lift"]
    Y = lambda v: v + b
    sw = math.sin(p["phase"]) if p["phase"] is not None else 0
    k = max(0.5, 1 - p["lift"] / 12)
    d.under.append(f'<ellipse cx="24" cy="{G + 0.3}" rx="{6 * k:.2f}" ry="{1.8 * k:.2f}" fill="#000" opacity="0.2"/>')
    ar = p["arms"]

    def arm(s, col):
        sx, sy = 24.2, Y(24.3)
        hx = sx - s * 3.2 * (1 - ar) + ar * 2.5
        hy = sy + 7.2 - ar * 15
        d.add(leg(sx, sy, hx, hy, 2.6), col)
        d.add(circle(hx, hy, 1.6), col)

    # jambe et bras arrière
    lift_b = max(0, -sw) * 1.4
    d.add(leg(24, Y(35), 24 - sw * 2.6, G - lift_b - p["lift"], 2.8), c["skin_dk"])
    d.add(ellipse(24 - sw * 2.6 + 0.8, G - lift_b - p["lift"], 2.1, 1.2), c["skin_dk"])
    arm(-sw, c["skin_dk"])
    lift_f = max(0, sw) * 1.4
    d.add(leg(24, Y(35), 24 + sw * 2.6, G - lift_f - p["lift"], 2.8), c["skin"])
    d.add(ellipse(24 + sw * 2.6 + 0.8, G - lift_f - p["lift"], 2.1, 1.2), c["skin_dk"])

    d.add(path(f"M20.5,{Y(30)} L28,{Y(30)} L30.4,{Y(37.2)} Q24,{Y(39)} 17.8,{Y(37.2)} Z"), c["skirt"])
    d.raw(line(f"M23,{Y(31.5)} L22.3,{Y(37.6)}", c["skirt_dk"], 0.9))
    d.add(rect(20.2, Y(21.8), 8, 9.4, 3), c["shirt"])
    d.add(rect(20.2, Y(29.2), 8, 2, 1), c["shirt_dk"], sil=False)

    hy = Y(14)
    d.add(circle(24.6, hy + 0.5, 8.6), c["skin"])
    d.add(path(f"M16,{hy + 3} L15.6,{hy + 9} Q20,{hy + 10.2} 24.4,{hy + 9} L24,{hy + 1} "
               f"Q25,{hy - 1.5} 27,{hy - 2.2} L28.4,{hy - 1.2} L29.8,{hy - 2.4} L31.3,{hy - 1.4} L32.4,{hy - 2.6} "
               f"L33.2,{hy - 0.6} Q34.2,{hy - 9.6} 24.6,{hy - 9.8} Q15.6,{hy - 9.6} 16,{hy + 3} Z"), c["hair"])
    d.add(ellipse(22, hy - 6.3, 3.4, 1.4, f"rotate(-15 22 {hy - 6.3:.2f})"), c["hair_hl"], sil=False, opacity=0.8)
    if p["happy"]:
        d.raw(line(f"M28.4,{hy + 2.4} Q29.8,{hy + 0.8} 31.2,{hy + 2.4}", c["eye"], 1.0))
        d.add(path(f"M30,{hy + 5.2} Q31.5,{hy + 7.8} 32.6,{hy + 5.2} Z"), c["mouth"], sil=False)
    elif p["blink"] > 0.5:
        d.raw(line(f"M28.6,{hy + 2.2} Q29.8,{hy + 3} 31,{hy + 2.2}", c["eye"], 0.9))
    else:
        d.add(ellipse(30, hy + 2.2, 1.2, 1.6), c["eye"], sil=False)
        d.add(circle(30.4, hy + 1.6, 0.45), "#FFFFFF", sil=False)
    if not p["happy"]:
        d.raw(line(f"M30.6,{hy + 5.6} Q31.6,{hy + 6.3} 32.4,{hy + 5.4}", c["eye"], 0.8))
    d.add(ellipse(30.6, hy + 4.2, 1.5, 1), c["blush"], sil=False, opacity=0.6)
    arm(sw, c["skin"])
    d.add(ellipse(24.3, Y(24.4), 2.3, 2.6), c["shirt"], sil=False, edge=True)   # manche
    return d


VIEWS = {"down": front, "up": back, "right": side}


def a_idle(view):
    return [A(bob=[0, 0.25, 0.4, 0.25][i], blink=1 if i == 3 else 0) for i in range(4)]


def a_walk(view):
    return [A(phase=i / 6 * 2 * math.pi, bob=-0.6 * abs(math.sin(i / 6 * 2 * math.pi))) for i in range(6)]


def a_happy(view):
    lift = [0, 2.5, 3.8, 1.5]
    arms = [0.3, 1, 1, 0.6]
    return [A(lift=lift[i], arms=arms[i], happy=True, bob=0.6 if i == 0 else 0) for i in range(4)]


ANIMS = {"idle": (a_idle, 6), "walk": (a_walk, 10), "happy": (a_happy, 8)}


def frames(anim, view):
    fn = ANIMS[anim][0]
    return [VIEWS[view](p).svg() for p in fn(view)]

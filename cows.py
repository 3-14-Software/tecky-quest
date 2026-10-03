"""
Les vaches du grand pré de la campagne : de profil, tournées vers la droite (la vue gauche est le miroir, faite par
le jeu), la tête tournée vers nous (plus mignonne, et lisible de loin). Cellule 64 x 48, pieds à y = 44 : origine
conseillée (32, 44).

Espèces (KINDS) : cow_bw (pie noire, la vache qu'on dessine aux enfants), cow_brown (pie rouge, façon montbéliarde),
calf (le veau : plus petit, sans cornes ni pis). Toutes ont une clochette jaune au cou.
Animations (anims(kind)[nom] = (poses, fps, boucle)) : idle (elle chasse les mouches avec la queue, bouge une oreille,
cligne), graze (tête dans l'herbe, elle rumine), walk (les pattes pivotent autour de la hanche, cachée dans le
ventre : jamais le haut d'une patte hors du corps ; diagonales ensemble), moo (tête levée, bouche ronde : « Meuh ! »).
"""
import re

from spritelib import Drawing, circle, ellipse, rect, path, line, OUTLINE

W, H = 64, 48
G = 44
KINDS = ("cow_bw", "cow_brown", "calf")
C = dict(white="#FFFDF7", white_dk="#E6DED0", muzzle="#F6B9B3", muzzle_dk="#D98C86", hoof="#5A4636", horn="#F3E5C2",
         bell="#F2C14E", strap="#B9452F", eye="#2A1E1A", udder="#F6B9B3", tuft="#4A3A30", blush="#F29A9A")
SPOTS = {"cow_bw": "#2E2A2A", "cow_brown": "#A8582C", "calf": "#C98A4B"}
# hanches (x, y) des quatre pattes, bien à l'intérieur du ventre ; (fond : plus sombres, un peu plus haut)
LEGS = ((16.5, 30.0, True), (38.0, 30.0, True), (20.5, 31.0, False), (42.0, 31.0, False))
LEG_LEN, LEG_W = 13.0, 5.0


def _shadow(d, cx, cy, rx, ry):
    d.under.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="#000" opacity="0.2"/>')


def cow(kind, p):
    """Une vache dans la pose p : head (0 tête droite -> 1 dans l'herbe ; négatif : levée), chew (mâchoire), swing
    (-1..1 : angle des pattes), bob (balancement du corps), tail (angle de la queue, °), ear (oreille relevée),
    blink, moo (bouche ouverte)."""
    calf = kind == "calf"
    k = 0.74 if calf else 1.0
    X = lambda x: 32 + (x - 32) * k                 # tout se réduit autour des pieds pour le veau
    Y = lambda y: G - (G - y) * k
    R = lambda r: r * k
    spot = SPOTS[kind]
    d = Drawing(W, H)
    _shadow(d, X(30), G + 0.2, R(20), R(2.8))
    b = p.get("bob", 0)
    sw = p.get("swing", 0)
    # queue, derrière tout : elle chasse les mouches
    ta = p.get("tail", 0)
    rot = f' transform="rotate({ta:.1f} {X(12.4):.2f} {Y(21 + b):.2f})"'
    d.raw(line(f"M{X(12.4):.2f},{Y(21 + b):.2f} Q{X(6.5):.2f},{Y(24 + b):.2f} {X(7.2):.2f},{Y(33 + b):.2f}", OUTLINE, 1.5 * k)
          .replace("/>", rot + "/>"))
    d.add(ellipse(X(7.2), Y(34.2 + b), R(1.9), R(2.6), rot[12:-1]), C["tuft"])
    # pattes : rectangles arrondis qui pivotent autour de la hanche (diagonales ensemble), sabots au bout
    for i, (hx, hy, back) in enumerate(LEGS):
        a = sw * 20 * (1 if i in (0, 3) else -1)
        tr = f"rotate({a:.1f} {X(hx):.2f} {Y(hy + b * 0.6):.2f})"
        col = C["white_dk"] if back else C["white"]
        top = Y(hy + b * 0.6)
        d.add(rect(X(hx) - R(LEG_W) / 2, top, R(LEG_W), R(LEG_LEN + (G - 1 - (hy + LEG_LEN)) - b * 0.6), R(2.0), tr), col)
        d.add(rect(X(hx) - R(LEG_W + 0.4) / 2, Y(G - 2.9) + (top - Y(hy)) * 0, R(LEG_W + 0.4), R(2.9), R(1.1), tr), C["hoof"])
    # le corps : rond, avec ses taches (gardées dans le corps) et le pis
    body = ellipse(X(28.5), Y(25 + b), R(17.0), R(10.6))
    d.add(body, C["white"])
    d.clip("cowbody" + kind, [body])
    # (coordonnées calculées ici, pas de transformation : elle s'appliquerait aussi à la découpe)
    pt = lambda m: f"{X(float(m.group(1))):.2f},{Y(float(m.group(2)) + b):.2f}"
    for sp in ("M15,18 Q19,13 25,15 Q28,19 24,23 Q19,26 16,23 Z", "M30,22 Q35,19 39,22 Q41,28 36,30 Q31,30 30,26 Z",
               "M10,26 Q13,24 15,28 Q14,33 11,33 Z", "M28,14 Q32,13 34,15 Q32,17 29,17 Z"):
        d.add(path(re.sub(r"(-?[\d.]+),(-?[\d.]+)", pt, sp)), spot, sil=False, clip="cowbody" + kind)
    if not calf:
        d.add(ellipse(X(22.5), Y(35.0 + b), R(3.4), R(2.1)), C["udder"], sil=False, edge=True)
    # la tête, tournée vers nous : droite, baissée dans l'herbe, ou levée pour meugler
    h = p.get("head", 0)
    hx, hy = 47.5 + h * 3.0, 17.5 + b + h * 14.0
    d.add(path(f"M{X(40):.2f},{Y(19 + b):.2f} L{X(hx - 3):.2f},{Y(hy - 2):.2f} L{X(hx - 2):.2f},{Y(hy + 7):.2f} "
               f"L{X(40):.2f},{Y(31 + b):.2f} Z"), C["white"])                                          # le cou
    ear = p.get("ear", 0)
    for s in (-1, 1):                                                                                   # oreilles
        ea = s * (14 + (ear * 22 if s > 0 else 0))
        ex = hx + s * 7.6
        d.add(ellipse(X(ex), Y(hy - 2.6), R(3.6), R(1.8), f"rotate({ea:.1f} {X(hx + s * 4.5):.2f} {Y(hy - 2.6):.2f})"),
              C["white"])
        d.add(ellipse(X(ex), Y(hy - 2.6), R(2.2), R(0.9), f"rotate({ea:.1f} {X(hx + s * 4.5):.2f} {Y(hy - 2.6):.2f})"),
              C["muzzle"], sil=False)
    if not calf:                                                                                        # cornes
        for s in (-1, 1):
            d.add(path(f"M{X(hx + s * 2.6):.2f},{Y(hy - 6.0):.2f} Q{X(hx + s * 3.4):.2f},{Y(hy - 9.4):.2f} "
                       f"{X(hx + s * 5.6):.2f},{Y(hy - 9.6):.2f} Q{X(hx + s * 4.8):.2f},{Y(hy - 7.6):.2f} "
                       f"{X(hx + s * 4.8):.2f},{Y(hy - 5.6):.2f} Z"), C["horn"])
    d.add(ellipse(X(hx), Y(hy), R(6.6), R(6.8)), C["white"])
    d.add(path(f"M{X(hx - 6.2):.2f},{Y(hy - 2.4):.2f} Q{X(hx - 5.2):.2f},{Y(hy - 7.0):.2f} {X(hx - 0.6):.2f},{Y(hy - 6.6):.2f} "
               f"Q{X(hx - 0.4):.2f},{Y(hy - 2.0):.2f} {X(hx - 3.2):.2f},{Y(hy + 0.4):.2f} Z"), spot, sil=False)   # tache
    m = p.get("moo", 0)
    chew = p.get("chew", 0)
    d.add(ellipse(X(hx), Y(hy + 4.4 + m * 0.4), R(5.6 + chew * 0.3), R(3.6 + m * 0.6)), C["muzzle"])   # museau
    for s in (-1, 1):
        d.add(ellipse(X(hx + s * 2.2), Y(hy + 3.8), R(0.75), R(1.0)), C["muzzle_dk"], sil=False)       # naseaux
    if m > 0:
        d.add(ellipse(X(hx), Y(hy + 6.2 + m * 0.4), R(1.4 + m * 0.4), R(0.6 + m * 1.0)), "#8E3B3B", sil=False, edge=True)
    else:
        d.raw(line(f"M{X(hx - 1.6):.2f},{Y(hy + 6.2 + chew * 0.4):.2f} Q{X(hx):.2f},{Y(hy + 7.0 + chew * 0.4):.2f} "
                   f"{X(hx + 1.6):.2f},{Y(hy + 6.2 + chew * 0.4):.2f}", C["muzzle_dk"], 0.7 * k))
    for s in (-1, 1):                                                                                   # yeux
        ex, ey = X(hx + s * 2.7), Y(hy - 1.2)
        if p.get("blink"):
            d.raw(line(f"M{ex - R(1.2):.2f},{ey:.2f} Q{ex:.2f},{ey + R(0.9):.2f} {ex + R(1.2):.2f},{ey:.2f}", C["eye"], 0.8 * k))
        else:
            d.add(ellipse(ex, ey, R(1.25), R(1.6)), C["eye"], sil=False)
            d.add(circle(ex + R(0.4), ey - R(0.6), R(0.45)), "#FFFFFF", sil=False)
        d.add(ellipse(X(hx + s * 4.6), Y(hy + 1.6), R(1.2), R(0.7)), C["blush"], sil=False, opacity=0.6)
    # collier et clochette, sous la tête
    d.raw(line(f"M{X(hx - 4.4):.2f},{Y(hy + 6.6):.2f} Q{X(hx):.2f},{Y(hy + 9.2):.2f} {X(hx + 4.4):.2f},{Y(hy + 6.6):.2f}",
               C["strap"], 1.5 * k))
    d.add(path(f"M{X(hx - 1.6):.2f},{Y(hy + 8.6):.2f} L{X(hx + 1.6):.2f},{Y(hy + 8.6):.2f} L{X(hx + 2.2):.2f},{Y(hy + 11.8):.2f} "
               f"L{X(hx - 2.2):.2f},{Y(hy + 11.8):.2f} Z"), C["bell"], sil=False, edge=True)
    return d


def anims(kind):
    """{animation : (poses, fps, boucle)}."""
    return {
        "idle": ([dict(), dict(tail=-14, bob=0.2), dict(tail=-22, ear=1, bob=0.3), dict(tail=-10, blink=1, bob=0.2),
                  dict(tail=6), dict()], 4, True),
        "graze": ([dict(head=1, chew=0), dict(head=1, chew=1, tail=-10), dict(head=1, chew=0, tail=-18),
                   dict(head=1, chew=1, tail=-8)], 4, True),
        "walk": ([dict(swing=1, bob=-0.3), dict(swing=0.4), dict(swing=-1, bob=-0.3), dict(swing=-0.4)], 6, True),
        "moo": ([dict(head=-0.3, moo=0.6, ear=1), dict(head=-0.4, moo=1, ear=1), dict(head=-0.4, moo=1, ear=1, tail=-14),
                 dict(head=-0.3, moo=0.6, ear=1)], 5, False),
    }


def frames(kind, anim):
    """SVG des images d'une animation."""
    return [cow(kind, p).svg() for p in anims(kind)[anim][0]]

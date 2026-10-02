"""
Les vaches du grand pré de la campagne : de profil, tournées vers la droite (la vue gauche est le miroir, faite par
le jeu). Cellule 64 x 48, pieds à y = 44 : origine conseillée (32, 44).

Espèces (KINDS) : cow_bw (pie noire, la vache qu'on dessine aux enfants), cow_brown (pie rouge, façon montbéliarde),
calf (le veau : plus petit, sans cornes ni pis). Toutes ont une clochette jaune au cou.
Animations (anims(kind)[nom] = (poses, fps, boucle)) : idle (elle chasse les mouches avec la queue, bouge une oreille,
cligne), graze (tête dans l'herbe, elle rumine), walk (quatre pattes, le corps balance), moo (tête levée, bouche
ouverte : « Meuh ! »).
"""
from spritelib import Drawing, circle, ellipse, rect, path, line, OUTLINE

W, H = 64, 48
G = 44
KINDS = ("cow_bw", "cow_brown", "calf")
C = dict(white="#FFFDF7", white_dk="#E4DCCF", muzzle="#F4B6B0", muzzle_dk="#D98C86", hoof="#4A3A30", horn="#F3E5C2",
         bell="#F2C14E", strap="#B9452F", eye="#2A1E1A", udder="#F4B6B0", tuft="#4A3A30")
SPOTS = {"cow_bw": "#2E2A2A", "cow_brown": "#A8582C", "calf": "#C98A4B"}


def _shadow(d, cx, cy, rx, ry):
    d.under.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="#000" opacity="0.2"/>')


def cow(kind, p):
    """Une vache dans la pose p : head (0 tête droite -> 1 dans l'herbe), chew (mâchoire), step (-1..1 pas),
    bob (balancement du corps), tail (angle de la queue, °), ear (oreille relevée), blink, moo (bouche ouverte)."""
    calf = kind == "calf"
    k = 0.72 if calf else 1.0
    X = lambda x: 32 + (x - 32) * k                 # tout se réduit autour des pieds pour le veau
    Y = lambda y: G - (G - y) * k
    R = lambda r: r * k
    spot = SPOTS[kind]
    d = Drawing(W, H)
    _shadow(d, X(31), G + 0.2, R(21), R(2.8))
    b = p.get("bob", 0)
    st = p.get("step", 0)
    # queue (derrière tout), qui chasse les mouches
    ta = p.get("tail", 0)
    rot = f' transform="rotate({ta:.1f} {X(11.5):.2f} {Y(20 + b):.2f})"'
    d.raw(line(f"M{X(11.5):.2f},{Y(20 + b):.2f} Q{X(5):.2f},{Y(24 + b):.2f} {X(5.6):.2f},{Y(34 + b):.2f}", OUTLINE, 1.4 * k)
          .replace("/>", rot + "/>"))
    d.add(ellipse(X(5.6), Y(35.2 + b), R(1.8), R(2.6), rot[12:-1]), C["tuft"])
    # pattes : celles du fond plus sombres, celles de devant claires ; elles avancent tour à tour
    for x, s, back in ((17, 1, True), (41, -1, True), (21, -1, False), (45, 1, False)):
        dx = st * s * 2.2
        col = C["white_dk"] if back else C["white"]
        d.add(rect(X(x - 2.2 + dx), Y(31 + b * 0.5), R(4.4), R(12.4 - b * 0.5), R(1.6)), col)
        d.add(rect(X(x - 2.3 + dx), Y(41.4), R(4.6), R(2.8), R(1)), C["hoof"])
    # le corps, ses taches, le pis
    d.add(ellipse(X(29), Y(25 + b), R(18.5), R(10)), C["white"])
    if not calf:
        d.add(ellipse(X(23), Y(34.2 + b), R(3.4), R(2.2)), C["udder"], sil=False, edge=True)
    for cx, cy, rx, ry, a in ((22, 21, 6.5, 5, -15), (35, 26, 5.5, 4.2, 20), (15.5, 27, 3, 4, 0), (31, 17.4, 3.2, 2, 0)):
        d.add(ellipse(X(cx), Y(cy + b), R(rx), R(ry), f"rotate({a} {X(cx):.2f} {Y(cy + b):.2f})"), spot, sil=False)
    # la tête : droite, ou baissée dans l'herbe
    h = p.get("head", 0)
    hx, hy = 51 + h * 2.5, 18 + b + h * 15
    d.add(path(f"M{X(42):.2f},{Y(19 + b):.2f} L{X(hx - 2):.2f},{Y(hy - 3):.2f} L{X(hx - 1):.2f},{Y(hy + 6):.2f} "
               f"L{X(42):.2f},{Y(31 + b):.2f} Z"), C["white"])                                       # le cou
    ear = p.get("ear", 0)
    d.add(ellipse(X(hx - 4.6), Y(hy - 3.6 - ear * 1.2), R(3.6), R(1.6), f"rotate({-20 - ear * 25:.1f} {X(hx - 2.5):.2f} {Y(hy - 3):.2f})"),
          spot if kind == "cow_bw" else C["white"])                                                 # oreille
    if not calf:
        d.add(path(f"M{X(hx - 1.6):.2f},{Y(hy - 5.6):.2f} Q{X(hx - 1):.2f},{Y(hy - 9.2):.2f} {X(hx + 1.2):.2f},{Y(hy - 9.4):.2f} "
                   f"Q{X(hx + 0.6):.2f},{Y(hy - 7):.2f} {X(hx + 0.8):.2f},{Y(hy - 5.4):.2f} Z"), C["horn"])  # corne
    d.add(ellipse(X(hx + 1), Y(hy), R(5.6), R(6.2)), C["white"])
    d.add(ellipse(X(hx - 0.4), Y(hy - 2.4), R(3.4), R(3)), spot, sil=False)                         # tache sur l'œil
    m = p.get("moo", 0)
    chew = p.get("chew", 0)
    d.add(ellipse(X(hx + 4.4), Y(hy + 4 + m * 0.6), R(4.4), R(3.4 + m * 0.6 + chew * 0.3)), C["muzzle"])  # museau
    d.add(ellipse(X(hx + 6.6), Y(hy + 3.2), R(0.7), R(0.9)), C["muzzle_dk"], sil=False)              # naseau
    if m > 0:
        d.add(ellipse(X(hx + 4.6), Y(hy + 6.4 + m), R(1.8), R(0.6 + m * 1.2)), "#8E3B3B", sil=False, edge=True)
    else:
        d.raw(line(f"M{X(hx + 2.4):.2f},{Y(hy + 6.2 + chew * 0.5):.2f} Q{X(hx + 4.2):.2f},{Y(hy + 7 + chew * 0.5):.2f} "
                   f"{X(hx + 6.4):.2f},{Y(hy + 6 + chew * 0.5):.2f}", C["muzzle_dk"], 0.7 * k))
    if p.get("blink"):
        d.raw(line(f"M{X(hx + 0.6):.2f},{Y(hy - 1.2):.2f} Q{X(hx + 1.6):.2f},{Y(hy - 0.4):.2f} {X(hx + 2.6):.2f},{Y(hy - 1.2):.2f}",
                   C["eye"], 0.8 * k))
    else:
        d.add(ellipse(X(hx + 1.6), Y(hy - 1.4), R(1.1), R(1.35)), C["eye"], sil=False)
        d.add(circle(X(hx + 1.9), Y(hy - 1.9), R(0.4)), "#FFFFFF", sil=False)
    # collier et clochette
    d.raw(line(f"M{X(hx - 4.4):.2f},{Y(hy + 3.4):.2f} Q{X(hx - 3):.2f},{Y(hy + 7.6):.2f} {X(hx - 0.6):.2f},{Y(hy + 8.4):.2f}",
               C["strap"], 1.6 * k))
    d.add(path(f"M{X(hx - 3.4):.2f},{Y(hy + 8):.2f} L{X(hx - 0.8):.2f},{Y(hy + 8):.2f} L{X(hx - 0.2):.2f},{Y(hy + 11.4):.2f} "
               f"L{X(hx - 4):.2f},{Y(hy + 11.4):.2f} Z"), C["bell"], sil=False, edge=True)
    return d


def anims(kind):
    """{animation : (poses, fps, boucle)}."""
    return {
        "idle": ([dict(), dict(tail=-14, bob=0.2), dict(tail=-22, ear=1, bob=0.3), dict(tail=-10, blink=1, bob=0.2),
                  dict(tail=6), dict()], 4, True),
        "graze": ([dict(head=1, chew=0), dict(head=1, chew=1, tail=-10), dict(head=1, chew=0, tail=-18),
                   dict(head=1, chew=1, tail=-8)], 4, True),
        "walk": ([dict(step=1, bob=-0.4), dict(step=0), dict(step=-1, bob=-0.4), dict(step=0)], 6, True),
        "moo": ([dict(head=-0.3, moo=0.6, ear=1), dict(head=-0.4, moo=1, ear=1), dict(head=-0.4, moo=1, ear=1, tail=-14),
                 dict(head=-0.3, moo=0.6, ear=1)], 5, False),
    }


def frames(kind, anim):
    """SVG des images d'une animation."""
    return [cow(kind, p).svg() for p in anims(kind)[anim][0]]

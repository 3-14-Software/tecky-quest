"""
Poules de la ferme (32x32, de profil tournées vers la droite ; la vue gauche est le miroir).
Animations : idle (petits mouvements de tête), peck (picorer), walk (marcher en hochant la tête),
flap (s'enfuir en battant des ailes, avec de petits sauts).
"""
from spritelib import Drawing, circle, ellipse, poly, path, line, OUTLINE

W = H = 32
COLORS = {   # nom : (corps, aile, queue)
    "hen": ("#D9772B", "#B9601E", "#A3502A"),          # poule rousse
    "hen_white": ("#FFF7E6", "#E6DCC8", "#F3E7CF"),    # poule blanche
}


def _shadow(d, cx, cy, rx, ry):
    d.under.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" opacity="0.2"/>')


def pose(kind, peck=0.0, wing=None, step=0.0, hop=0.0, head=0.0):
    """peck : 0 tête haute -> 1 bec au sol ; wing : None = aile repliée, sinon angle (°) de l'aile ouverte ;
    step : -1..1 pas des pattes ; hop : hauteur du saut ; head : avancée de la tête (hochement en marchant)."""
    body, wing_c, tail = COLORS[kind]
    d = Drawing(W, H)
    _shadow(d, 15.5, 28, 9 - hop * 0.6, 1.8)
    up = f"translate(0 {-hop:.2f})"
    # pattes (au sol, sauf en plein saut)
    lift = min(hop, 2.5)
    for x0, s in ((13, 1), (17, -1)):
        dx = step * s * 1.6
        d.raw(f'<g transform="translate(0 {-lift:.2f})">' + line(
            f"M{x0},23 L{x0 + dx:.2f},27.6 M{x0 + dx - 1.8:.2f},28 L{x0 + dx + 1.6:.2f},28", "#E8A33A", 1.3) + "</g>")
    # le corps bascule un peu vers l'avant quand elle picore
    tilt = f"{up} rotate({peck * 14:.1f} 16 22)"
    d.add(path("M10,19 Q3,15 4.5,7 Q8,10 9,9 Q10,13 13,15 Z", tilt), tail)
    d.add(ellipse(15.5, 19, 8.5, 6.2, tilt), body)
    # cou + tête : pivotent autour de la base du cou pour aller picorer
    neck = f"{tilt} translate({head:.2f} 0) rotate({peck * 62:.1f} 19 17.5)"
    d.add(path("M17.5,17 Q18,10 21.5,8.5 L24.5,12 Q23,17 23.5,19 Z", neck), body)
    d.add(circle(22, 9.5, 4.3, neck), body)
    for cx, cy, r in ((19.6, 5.6, 1.8), (22, 4.8, 2.0), (24.3, 5.8, 1.6)):
        d.add(circle(cx, cy, r, neck), "#E2332B")
    d.add(ellipse(25.3, 13.4, 1.4, 2.0, neck), "#E2332B")
    d.add(poly([(25.6, 8.6), (29.6, 10.2), (25.6, 11.8)], neck), "#F2C14E")
    # aile : repliée sur le flanc, ou grande ouverte qui bat
    if wing is None:
        d.add(path("M10.5,17.5 Q15,14.8 20,17.2 Q18.5,22.5 13,22 Q10,20.5 10.5,17.5 Z", tilt), wing_c, sil=False, edge=True)
        d.raw(f'<g transform="{tilt}">' + line("M13,19.4 Q15.5,18.6 18,19.4", "#9E4E1C", 0.7) + "</g>")
    else:
        wtr = f"{tilt} rotate({wing:.1f} 16 17.5)"
        d.add(path("M16,18 Q11,8 3.5,7.5 Q5.5,10.5 4.5,12 Q7.5,12.6 7,14.6 Q10,15 10,17.4 Q13,18.6 16,19.5 Z", wtr), wing_c)
        d.raw(f'<g transform="{wtr}">' + line("M14,17 Q10,12 6,10 M13,18 Q10.5,15.5 8,14.4", "#9E4E1C", 0.7) + "</g>")
    # œil + joue
    d.add(circle(22.6, 9, 1.05, neck), OUTLINE, sil=False)
    d.add(circle(22.9, 8.6, 0.38, neck), "#FFFFFF", sil=False)
    d.add(circle(24, 11.4, 1.1, neck), "#F28CB8", sil=False, opacity=0.7)
    return d


ANIMS = {   # nom : (poses, fps, boucle)
    "idle": ([dict(), dict(head=0.5), dict(), dict(head=-0.4)], 4, True),
    "peck": ([dict(), dict(peck=0.55), dict(peck=1.0), dict(peck=0.8), dict(peck=1.0), dict(peck=0.5), dict()], 10, False),
    "walk": ([dict(step=1, head=1.0), dict(step=0, head=0.2, hop=0.4), dict(step=-1, head=1.0), dict(step=0, head=0.2, hop=0.4)],
             10, True),
    "flap": ([dict(wing=32, hop=2.0, step=0.6), dict(wing=-6, hop=3.4), dict(wing=-46, hop=2.4, step=-0.6), dict(wing=-6, hop=1.0)],
             14, True),
}


def frames(kind, anim):
    """SVG des images d'une animation (vue de droite)."""
    return [pose(kind, **p).svg() for p in ANIMS[anim][0]]

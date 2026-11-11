"""
Poules de la ferme (32x32, de profil tournées vers la droite ; la vue gauche est le miroir).
Animations : idle (petits mouvements de tête), peck (picorer), walk (marcher en hochant la tête),
flap (s'enfuir en battant des ailes, avec de petits sauts).

Depuis la v2 (PLAN_V2.md, lot 3), dans la famille du Tecky de tecky2.py : une poule dodue, la tête petite, la crête
et les barbillons nets, l'aile repliée fondue dans le flanc (un pli, pas un ovale cerné), les plumes de la queue en
éventail. Elle est dessinée grande puis réduite de SCALE autour de ses pieds (16, 28), le contour compensé, comme
les bêtes de critters.py : sa taille se juge à côté de Tecky (34 x 22 unités), qu'elle dépassait avant (27 x 27) ;
elle fait maintenant environ 18 x 18.
"""
from spritelib import Drawing, circle, ellipse, path, line, OUTLINE, OUTLINE_W

W = H = 32
G = 28            # ligne des pieds
SCALE = 0.66      # réduction autour de (16, G)
COLORS = {   # nom : (corps, aile, queue)
    "hen": ("#D9772B", "#BE621F", "#A3502A"),          # poule rousse
    "hen_white": ("#FFF7E6", "#ECE2CD", "#E9DCC2"),    # poule blanche
}
PLI = {"hen": "#8F4518", "hen_white": "#BFB199"}       # les plis des plumes (aile, queue)
CRETE, BEC, BEC_DK, PATTE, JOUE = "#E2332B", "#F6BE3F", "#D9962A", "#EDA63A", "#F28CB8"

CORPS = ("M6.6,17.4 C6.4,13.6 9.8,11.8 14.2,12.2 C18.6,12.4 23.2,14.6 23.5,19.0 C23.7,22.9 19.8,25.5 14.8,25.5 "
         "C10.0,25.5 6.8,22.6 6.6,17.4 Z")
QUEUE = ("M9.4,16.2 C6.6,14.4 4.4,11.0 4.2,6.6 C6.0,7.0 7.2,8.0 7.9,9.4 C8.2,7.6 9.2,6.0 10.8,5.2 "
         "C11.0,8.4 12.0,11.6 14.0,13.8 Z")
QUEUE_PLI = "M7.9,9.4 C8.2,11.6 9.2,13.4 10.8,14.8"
COU = "M16.8,14.6 C17.2,10.6 18.8,8.0 21.2,7.2 L24.8,10.6 C23.7,12.6 23.2,14.8 23.1,17.4 L19,19 Z"
TETE = (22.2, 9.0, 3.7)
CRETE_F = ("M19.3,7.4 C18.0,5.6 19.2,3.7 21.0,4.3 C21.1,2.3 23.6,2.1 24.0,4.0 C25.8,3.3 27.0,5.3 25.6,6.9 Z")
BEC_F = "M25.3,7.9 C26.8,8.2 28.2,8.9 29.2,9.8 C28.0,10.5 26.6,11.0 25.3,11.2 Z"
AILE = ("M9.8,17.3 C12.4,14.9 17.2,15.0 19.9,17.3 C19.5,20.9 16.4,22.8 12.8,22.2 C10.5,21.6 9.3,19.6 9.8,17.3 Z")
AILE_PLI = "M19.9,17.3 C19.5,20.9 16.4,22.8 12.8,22.2 C10.5,21.6 9.3,19.6 9.8,17.3"
AILE_PLUMES = "M12.4,19.6 C13.6,20.3 15.0,20.4 16.4,19.9 M11.2,17.9 C12.4,18.4 13.6,18.5 14.8,18.2"
# aile ouverte (elle bat), autour de son attache (16, 17.5) : trois grandes plumes arrondies au bout
AILE_OUVERTE = ("M16.4,19.4 C13.6,18.8 11.2,17.8 9.6,16.4 C9.9,15.2 9.4,14.2 7.4,14.0 C7.9,12.8 7.2,11.8 5.2,11.4 "
                "C5.6,10.0 4.9,8.6 3.2,7.6 C8.6,7.0 13.4,10.6 16.6,17.4 Z")
AILE_OUVERTE_PLIS = "M14.2,16.8 C11.4,13.6 8.6,11.4 5.6,10.2 M13.6,17.9 C11.6,16.2 9.6,15.0 7.6,14.4"


def _shadow(d, cx, cy, rx, ry):
    d.under.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" opacity="0.2"/>')


def _g(tr, xml):
    return f'<g transform="{tr}">{xml}</g>'


def pose(kind, peck=0.0, wing=None, step=0.0, hop=0.0, head=0.0):
    """peck : 0 tête haute -> 1 bec au sol ; wing : None = aile repliée, sinon angle (°) de l'aile ouverte ;
    step : -1..1 pas des pattes ; hop : hauteur du saut ; head : avancée de la tête (hochement en marchant).
    Dessin à l'échelle de conception : la réduction SCALE est appliquée par frames()."""
    body, wing_c, tail = COLORS[kind]
    pli = PLI[kind]
    d = Drawing(W, H)
    _shadow(d, 15.2, G, 8.6 - hop * 0.6, 1.8)
    up = f"translate(0 {-hop:.2f})"
    # pattes fines (au sol, sauf en plein saut) : un trait jaune sur un trait brun un peu plus large
    lift = min(hop, 2.5)
    for x0, s in ((12.2, 1), (17.0, -1)):
        dx = step * s * 1.3
        trait = (f"M{x0:.2f},23.6 L{x0 + dx:.2f},{G - 0.5:.2f} M{x0 + dx - 1.5:.2f},{G - 0.1:.2f} L{x0 + dx + 2.2:.2f},{G - 0.1:.2f}")
        d.raw(_g(f"translate(0 {-lift:.2f})", line(trait, OUTLINE, 2.3) + line(trait, PATTE, 1.2)))
    # le corps bascule vers l'avant quand elle picore
    tilt = f"{up} rotate({peck * 16:.1f} 15 22)"
    d.add(path(QUEUE, tilt), tail)
    d.raw(_g(tilt, line(QUEUE_PLI, pli, 0.7)))
    d.add(path(CORPS, tilt), body)
    # cou + tête : pivotent autour de la base du cou pour aller picorer
    neck = f"{tilt} translate({head:.2f} 0) rotate({peck * 64:.1f} 19 16.5)"
    hx, hy, hr = TETE
    d.add(path(CRETE_F, neck), CRETE)
    d.add(path(COU, neck), body)
    d.add(circle(hx, hy, hr, neck), body)
    d.add(ellipse(25.0, 12.9, 1.25, 1.9, neck), CRETE)                       # barbillon
    d.add(path(BEC_F, neck), BEC)
    d.raw(_g(neck, line("M25.5,9.7 L28.4,9.8", BEC_DK, 0.6)))
    # aile : repliée, fondue dans le flanc (un pli le long du bas, deux petites plumes) ; ou ouverte, qui bat
    if wing is None:
        d.add(path(AILE, tilt), wing_c, sil=False)
        d.raw(_g(tilt, line(AILE_PLI, pli, 0.9) + line(AILE_PLUMES, pli, 0.6)))
    else:
        wtr = f"{tilt} rotate({wing:.1f} 16 17.5)"
        d.add(path(AILE_OUVERTE, wtr), wing_c)
        d.raw(_g(wtr, line(AILE_OUVERTE_PLIS, pli, 0.7)))
    # œil vif, joue
    d.add(circle(23.3, 8.7, 1.3, neck), OUTLINE, sil=False)
    d.add(circle(23.75, 8.25, 0.48, neck), "#FFFFFF", sil=False)
    d.add(circle(23.6, 11.3, 1.05, neck), JOUE, sil=False, opacity=0.7)
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
    """SVG des images d'une animation (vue de droite), réduites de SCALE autour des pieds."""
    tr = f"translate(16 {G}) scale({SCALE}) translate(-16 -{G})"
    out = []
    for p in ANIMS[anim][0]:
        d = pose(kind, **p)
        d.under = [_g(tr, u) for u in d.under]
        out.append(d.svg(tr, outline_w=OUTLINE_W / SCALE))
    return out

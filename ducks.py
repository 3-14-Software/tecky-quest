"""
Canards de la rivière (cellule 32x32, de profil tournés vers la droite ; la vue gauche est le miroir, fait par le jeu).

- "duck" : colvert mâle (tête vert bouteille, fin collier blanc, poitrine brun-roux, corps gris clair,
  croupion noir avec sa petite boucle, bec jaune, pattes orange en vol).
- "duck_f" : cane (brune mouchetée, sourcil et calotte foncés, bec orange-brun, petit miroir bleu sur l'aile).
- "duckling" : caneton (duvet jaune, environ 57 % de la longueur d'un adulte, bec orange).

Sur l'eau, la ligne de flottaison est à y = 24 (G) : origine conseillée (16, 24), point que le jeu pose sur l'eau.
Tout ce qui est sous la ligne est coupé (on ne voit pas les pattes) ; un liseré d'écume clair cache la coupe,
une ombre bleutée et des ronds dans l'eau (qui s'élargissent en « swim ») sont dessinés autour.

Animations (`anims(kind)` -> {nom : (poses, fps, boucle)}, `frames(kind, anim)` -> SVG) :
- swim (tous) : flotte en se balançant, ronds dans l'eau ; 4 images, 6 i/s, en boucle.
- quack (tous) : cancan, cou tendu et bec qui s'ouvre deux fois ; 4 images, 8 i/s, une fois.
- dive (adultes) : bascule tête sous l'eau, croupion et queue en l'air qui frétillent (pattes qui pagaient),
  puis remonte ; 8 images, 8 i/s, une fois.
- fly (adultes) : en vol, sans eau ni ombre, cou tendu, pattes orange repliées sous la queue, ailes qui battent ;
  centre du corps vers (16, 18) ; 4 images, 12 i/s, en boucle. Le jeu dessine l'ombre au sol et remonte le sprite.

Même principe que critters.py / hens.py : silhouette d'abord (contour brun), aplats ensuite.
"""
import math

from spritelib import Drawing, circle, ellipse, poly, path, leg, line, OUTLINE, OUTLINE_W

W = H = 32
G = 24            # ligne de flottaison
ORIGIN = (16, G)  # point posé sur l'eau par le jeu (aussi pour « fly », que le jeu remonte)
FOAM = "#D2F0FB"  # écume (même bleu très clair que les vaguelettes fx/ripple)
DEEP = "#2F6F9A"  # partie immergée devinée sous l'eau (contour des berges dans tiles.py)

KINDS = {   # couleurs par espèce
    "duck": dict(drake=True, body="#DCD7CD", wing="#AFA392", tip="#7F7467", head="#2E8A55", sheen="#5BBB84",
                 neck="#2E8A55", chest="#A9552F", rump="#2B2A30", tail="#F1EEE6", collar="#FFFFFF",
                 bill="#F2CB45", bill_dk="#C99A2A", spec="#4C5FD2", mottle=None),
    "duck_f": dict(drake=False, body="#C08D5B", wing="#9A6C42", tip="#6E4A2B", head="#CDA474", sheen="#E2C49A",
                   neck="#CDA474", chest="#C8975F", rump="#9A6C42", tail="#A87A4C", collar=None,
                   crown="#6E4A2B", bill="#E69A3E", bill_dk="#7A4A2A", spec="#4C6FD8", mottle="#7A5233"),
    "duckling": dict(down="#F8D84E", shade="#E8B62E", light="#FFF1A6", bill="#F39A3A", blush="#F28CB8"),
}
ADULTS = ("duck", "duck_f")
DUCKLING_SCALE = 0.92   # caneton : environ 56 % de la longueur d'un adulte (bec à queue)


# ================================================================== outils
class _Duck(Drawing):
    """Dessin d'un canard : l'oiseau est un groupe (transformé : roulis, plongeon) coupé à la ligne d'eau ;
    `under` (ombre, ronds) et `over` (écume, éclaboussures) restent fixes, sous et sur l'oiseau."""

    def __init__(self, water=True):
        super().__init__(W, H)
        self.water = water
        self.over = []
        self.tr = ""
        self.ow = OUTLINE_W   # épaisseur du contour (compensée si le groupe est réduit : caneton)

    def svg(self, transform=None, outline=OUTLINE, outline_w=None):
        tr = self.tr if transform is None else transform
        s = super().svg(tr, outline, self.ow if outline_w is None else outline_w)
        if self.water:
            s = s.replace("<defs>", f'<defs><clipPath id="above"><rect x="-8" y="-8" width="{W + 16}" '
                                    f'height="{G + 8}"/></clipPath>', 1)
            i = s.rindex(f'<g transform="{tr}">')
            s = s[:i] + '<g clip-path="url(#above)">' + s[i:-len("</svg>")] + "</g></svg>"
        return s[:-len("</svg>")] + "".join(self.over) + "</svg>"


def _rot(x, y, cx, cy, a):
    """Rotation du point (x, y) de a degrés autour de (cx, cy) (même sens que SVG)."""
    r = math.radians(a)
    c, s = math.cos(r), math.sin(r)
    return cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c


def _lerp(a, b, t):
    return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t


def _local(hx, hy, ang):
    """Repère local (u vers l'avant, v vers le bas) tourné de ang degrés, centré en (hx, hy)."""
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return lambda u, v: (hx + u * c - v * s, hy + u * s + v * c)


def _smooth(pts):
    """Chemin fermé lissé passant par le milieu des côtés (les sommets servent de points de contrôle)."""
    n = len(pts)
    mids = [_lerp(pts[i], pts[(i + 1) % n], 0.5) for i in range(n)]
    d = f"M{mids[-1][0]:.2f},{mids[-1][1]:.2f} "
    for i in range(n):
        d += f"Q{pts[i][0]:.2f},{pts[i][1]:.2f} {mids[i][0]:.2f},{mids[i][1]:.2f} "
    return path(d + "Z")


def _sticker(d, shapes, fill, w=OUTLINE_W):
    """Formes posées PAR-DESSUS ce qui précède, avec leur propre contour (aile proche en vol)."""
    for s in shapes:
        d.raw(s.replace('fill="%F%"', f'fill="{OUTLINE}" stroke="{OUTLINE}" stroke-width="{w:.2f}" '
                                      f'stroke-linejoin="round"'))
    for s in shapes:
        d.raw(s.replace('fill="%F%"', f'fill="{fill}"'))


def _eye(d, x, y, r=1.2):
    """Œil rond tout noir avec reflet (comme les poules)."""
    d.add(circle(x, y, r), OUTLINE, sil=False)
    d.add(circle(x + r * 0.32, y - r * 0.36, r * 0.38), "#FFFFFF", sil=False)


def _chord(outlines, tr_pt):
    """Étendue en x de la coupe des contours (listes de points, repère de l'oiseau) par la ligne d'eau."""
    xs = []
    for pts in outlines:
        q = [tr_pt(x, y) for x, y in pts]
        for (x0, y0), (x1, y1) in zip(q, q[1:] + q[:1]):
            if (y0 - G) * (y1 - G) < 0:
                xs.append(x0 + (x1 - x0) * (G - y0) / (y1 - y0))
    return (min(xs), max(xs)) if xs else None


def _ellipse_pts(cx, cy, rx, ry, n=48):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


# ================================================================== eau autour de l'oiseau
def _water(d, span, ring=None, splash=0.0, wake=0.0):
    """Ombre immergée et ronds (sous l'oiseau), écume sur la ligne de flottaison et éclaboussures (dessus).
    span : (x0, x1) de la coupe ; ring : phase 0..1 des ronds qui s'élargissent ; splash : 0..1 ; wake : phase
    des petites vagues aux deux bouts de l'écume."""
    x0, x1 = max(span[0], 4.5), min(span[1], 27.5)   # les vaguelettes et gouttes restent dans le cadre
    cx, hw = (x0 + x1) / 2, (x1 - x0) / 2
    d.under.append(f'<ellipse cx="{cx:.2f}" cy="{G + 1.1:.2f}" rx="{hw + 0.6:.2f}" ry="1.7" fill="{DEEP}" '
                   f'opacity="0.35"/>')
    if ring is not None:                              # deux ronds décalés d'une demi-phase : boucle continue
        for j in (0.0, 0.5):
            u = (ring + j) % 1.0
            rx, ry = min(hw + 2.2 + 4.2 * u, cx - 1.5, 30.5 - cx), 1.5 + 0.9 * u
            d.under.append(f'<ellipse cx="{cx:.2f}" cy="{G + 0.3:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="none" '
                           f'stroke="{FOAM}" stroke-width="0.8" opacity="{0.75 * (1 - u):.2f}"/>')
    # écume : un fuseau clair qui cache la coupe, et deux petites vagues qui ondulent aux bouts
    d.over.append(f'<ellipse cx="{cx:.2f}" cy="{G:.2f}" rx="{hw + 0.9:.2f}" ry="0.8" fill="{FOAM}" '
                  f'opacity="0.95"/>')
    w = 0.35 * math.sin(2 * math.pi * wake)
    for side, x in ((-1, x0 - 0.5), (1, x1 + 0.5)):
        d.over.append(line(f"M{x:.2f},{G + 0.2:.2f} q{side * 1.0:.2f},{-0.9 - w:.2f} {side * 2.1:.2f},{0.2:.2f}",
                           FOAM, 0.8))
    d.over.append(f'<ellipse cx="{cx - hw * 0.35:.2f}" cy="{G - 0.15:.2f}" rx="{hw * 0.28:.2f}" ry="0.3" '
                  f'fill="#FFFFFF" opacity="0.9"/>')
    if splash > 0:                                    # gouttes qui jaillissent des deux côtés
        for k, (dx, h, r) in enumerate(((-1.0, 4.2, 0.75), (-0.6, 6.0, 0.6), (-0.2, 3.4, 0.55),
                                         (0.35, 5.2, 0.7), (0.8, 3.0, 0.6), (1.1, 4.6, 0.5))):
            x = min(max(cx + dx * (hw + 1.2 + 1.6 * splash), 2.0), 30.0)
            y = G - 0.6 - h * splash
            d.over.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r * (0.6 + 0.6 * splash):.2f}" fill="#FFFFFF" '
                          f'stroke="{FOAM}" stroke-width="0.4" opacity="{0.6 + 0.35 * splash:.2f}"/>')


# ================================================================== ADULTES
BODY = (15.0, 21.4, 8.6, 5.0)      # corps sur l'eau : centre et rayons (le bas est sous la ligne)
NECK_BASE = (20.6, 19.4)
HEAD = (21.6, 12.4)
HEAD_R = 4.1


def _bill(d, C, L, r, open_=0.0):
    """Bec de canard plat, de profil (repère local L de la tête, rayon r) ; open_ : 0 fermé -> 1 grand ouvert."""
    hinge = L(r * 0.55, 1.5)
    up = -9 * open_
    lo = 30 * open_
    U = lambda u, v: _rot(*L(u, v), *hinge, up)
    D = lambda u, v: _rot(*L(u, v), *hinge, lo)
    if open_ > 0.05:                                  # intérieur du bec
        d.add(poly([hinge, U(r + 3.4, 1.4), D(r + 3.0, 1.7)]), "#7A2A2A")
        d.add(poly([D(r * 0.9, 1.9), D(r + 2.4, 1.8), U(r + 1.6, 1.6)]), "#E8707A", sil=False)
    lower = [D(r * 0.45, 1.3), D(r + 3.1, 1.5), D(r + 3.5, 2.0), D(r + 2.7, 2.6), D(r * 0.7, 2.7)]
    upper = [U(r * 0.35, -1.6), U(r + 1.6, -0.9), U(r + 3.4, -0.3), U(r + 4.3, 0.6), U(r + 3.8, 1.7),
             U(r + 1.2, 1.6), U(r * 0.4, 1.8)]
    d.add(_smooth(lower), C["bill"])
    d.add(_smooth(upper), C["bill"])
    if open_ <= 0.05:
        d.raw(line(f"M{U(r * 0.75, 1.55)[0]:.2f},{U(r * 0.75, 1.55)[1]:.2f} "
                   f"Q{U(r + 2.0, 1.75)[0]:.2f},{U(r + 2.0, 1.75)[1]:.2f} {U(r + 3.4, 1.45)[0]:.2f},"
                   f"{U(r + 3.4, 1.45)[1]:.2f}", OUTLINE, 0.6))
    if not C["drake"]:                                # cane : selle foncée sur le dessus du bec
        d.add(_smooth([U(r * 0.55, -1.2), U(r + 1.6, -0.6), U(r + 2.8, -0.15), U(r + 2.2, 0.5),
                       U(r + 0.4, 0.4)]), C["bill_dk"], sil=False)
    else:                                             # colvert : onglet foncé au bout du bec
        d.add(_smooth([U(r + 3.5, 0.0), U(r + 4.2, 0.6), U(r + 3.8, 1.4), U(r + 3.3, 0.8)]), C["bill_dk"],
              sil=False)
    d.add(circle(*U(r + 1.0, -0.2), 0.32), OUTLINE, sil=False)        # narine


def _head(d, C, hx, hy, r=HEAD_R, ang=0.0, open_=0.0):
    """Tête de profil vers la droite (centre (hx, hy)), bec tourné de ang degrés."""
    L = _local(hx, hy, ang)
    head = circle(hx, hy, r)
    d.add(head, C["head"])
    if C["drake"]:                                    # reflet de la tête verte
        d.add(ellipse(hx - 1.1, hy - 1.7, 1.9, 1.1, f"rotate(-20 {hx - 1.1:.2f} {hy - 1.7:.2f})"), C["sheen"],
              sil=False, opacity=0.85)
    else:                                             # cane : calotte et sourcil foncés, joue claire
        d.clip("fhead", [head])
        d.add(ellipse(hx - 1.2, hy - r + 0.2, r * 0.95, 1.9), C["crown"], sil=False, clip="fhead")
        d.add(ellipse(hx + 0.4, hy + 1.8, 2.8, 1.6), C["sheen"], sil=False, clip="fhead")
        d.raw(line(f"M{hx - r + 0.6:.2f},{hy + 0.4:.2f} Q{hx:.2f},{hy - 0.4:.2f} {hx + r - 0.4:.2f},{hy - 0.5:.2f}",
                   C["crown"], 0.9))
    _bill(d, C, L, r, open_)
    _eye(d, *L(1.3, -0.6), 1.2)
    return head


def _neck(d, C, base, head, wb=3.0, wh=2.2):
    """Cou entre la base (sur le corps) et le centre de la tête ; colvert : collier blanc et bas brun-roux."""
    dx, dy = head[0] - base[0], head[1] - base[1]
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln
    Lb, Rb = (base[0] - nx * wb, base[1] - ny * wb), (base[0] + nx * wb, base[1] + ny * wb)
    Lh, Rh = (head[0] - nx * wh, head[1] - ny * wh), (head[0] + nx * wh, head[1] + ny * wh)
    d.add(poly([Lb, Rb, Rh, Lh]), C["neck"])
    if C["collar"]:
        t0, t1 = 0.40, 0.52                           # de la base vers la tête
        d.add(poly([Lb, Rb, _lerp(Rb, Rh, t0), _lerp(Lb, Lh, t0)]), C["chest"], sil=False)
        d.add(poly([_lerp(Lb, Lh, t0), _lerp(Rb, Rh, t0), _lerp(Rb, Rh, t1), _lerp(Lb, Lh, t1)]), C["collar"],
              sil=False)
    return [Lb, Rb, Rh, Lh]


def _tail(d, C, wag=0.0, fly=False):
    """Queue pointue relevée à l'arrière (colvert : plumes blanches + croupion noir et sa boucle)."""
    tr = f"rotate({wag:.1f} 8.0 19.6)"
    if fly:
        shape = _smooth([(8.6, 16.8), (4.2, 16.2), (1.8, 17.6), (4.4, 19.6), (8.6, 20.6)])
    else:
        shape = _smooth([(9.0, 17.0), (5.0, 15.6), (2.6, 13.6), (3.6, 17.2), (5.8, 20.2), (8.8, 21.6)])
    d.add(shape.replace("/>", f' transform="{tr}"/>'), C["tail"])
    if C["drake"]:
        if fly:
            return
        d.raw(f'<g transform="{tr}">' + line("M8.2,17.4 Q7.4,14.2 9.4,13.6 Q11.0,13.6 10.6,15.0 Q10.2,15.8 9.4,15.4",
                                              C["rump"], 1.25) + "</g>")
    else:
        d.raw(f'<g transform="{tr}">' + line("M7.6,17.6 L4.6,15.8 M7.4,19.4 L4.4,18.0", C["tip"], 0.7) + "</g>")


def _body_marks(d, C, cid, cx, cy, rx, ry):
    """Détails du corps, découpés à sa forme : croupion, poitrine, mouchetures de la cane."""
    if C["drake"]:
        d.add(ellipse(cx - rx + 1.9, cy - 0.6, 3.2, ry + 1), C["rump"], sil=False, clip=cid)
        d.add(ellipse(cx + rx - 1.4, cy - 1.0, 4.4, ry + 1.6), C["chest"], sil=False, clip=cid)
    else:
        d.add(ellipse(cx + rx - 1.2, cy - 1.0, 4.0, ry + 1.4), C["chest"], sil=False, clip=cid)
        for mx, my in ((cx - 4.6, cy - 1.0), (cx - 1.6, cy + 0.4), (cx + 1.6, cy - 0.2), (cx + 4.4, cy + 0.9),
                       (cx - 3.4, cy + 1.8), (cx + 0.2, cy + 2.2), (cx + 3.0, cy + 2.6), (cx + 5.6, cy - 1.8),
                       (cx - 6.0, cy + 1.0)):
            d.raw(f'<g clip-path="url(#{cid})">' + line(f"M{mx - 0.8:.2f},{my - 0.5:.2f} L{mx:.2f},{my + 0.3:.2f} "
                                                       f"L{mx + 0.8:.2f},{my - 0.5:.2f}", C["mottle"], 0.75)
                  + "</g>")


def _folded_wing(d, C):
    """Aile repliée sur le haut du flanc : pointe foncée vers l'arrière, petit miroir bleu bordé de blanc."""
    wing = _smooth([(20.2, 17.8), (15.2, 15.8), (9.0, 17.2), (7.4, 18.4), (11.8, 20.0), (17.0, 20.0)])
    d.clip("dwing", [wing])
    d.add(wing, C["wing"], sil=False, edge=True)
    d.add(_smooth([(11.6, 16.4), (7.0, 17.0), (6.6, 19.4), (10.4, 19.8), (12.0, 18.6)]), C["tip"], sil=False,
          clip="dwing")
    d.add(poly([(12.0, 18.8), (15.0, 19.0), (14.8, 19.9), (12.0, 19.7)]), C["spec"], sil=False)
    d.raw(line("M11.8,18.6 L15.2,18.8 M11.8,19.9 L15.0,20.1", "#FFFFFF", 0.45))
    if C["mottle"]:
        d.raw(line("M16.2,17.4 l0.7,0.6 l0.7,-0.6 M18.4,18.2 l0.6,0.5 l0.6,-0.5", C["tip"], 0.6))


def _paddles(d, tr, paddle, near):
    """Pattes palmées orange qui pagaient en l'air (tête sous l'eau), à gauche du croupion dressé.
    Coordonnées de l'écran : tr annule la transformation de l'oiseau (elles restent dans sa silhouette)."""
    k = 1 if near else 0
    s = math.sin(paddle + k * math.pi)
    hx, hy = 12.4, 19.0 + 2.6 * k                     # hanche (le pied proche est plus bas)
    ang = 200 - 28 * s                                # direction de la patte (vers la gauche, plus ou moins relevée)
    L = _local(hx, hy, ang)
    ax, ay = L(2.4 + 0.5 * s, 0)
    col = "#F28C28" if near else "#D9711C"
    d.add(leg(hx, hy, ax, ay, 1.1).replace("/>", f' transform="{tr}"/>'), col)
    F = _local(ax, ay, ang - 25 + 20 * s)
    d.add(_smooth([F(-0.4, 0), F(2.2, -1.9), F(2.0, -0.7), F(2.9, 0.1), F(2.0, 0.9), F(2.4, 2.0)]).replace(
        "/>", f' transform="{tr}"/>'), col)


def _adult(C, tilt=0.0, bob=0.0, rock=0.0, stretch=0.0, nod=0.0, dip=0.0, tuck=0.0, open_=0.0, wag=0.0, ring=None,
           splash=0.0, wake=0.0, paddle=None):
    """Adulte sur l'eau. tilt : bascule en avant (plongeon, en degrés) ; bob : enfoncement (+ = plus bas) ;
    rock : roulis (degrés) ; stretch : cou tendu (cancan) ; nod : tête baissée ; dip : tête qui plonge
    (degrés, autour de la base du cou) ; tuck : cou rentré (0..1) ; open_ : bec ouvert ;
    wag : frétillement de la queue (degrés) ; paddle : phase des pattes qui pagaient en l'air (tête sous l'eau)."""
    d = _Duck(water=True)
    pivot = (15.0, 22.6)
    a = tilt + rock
    d.tr = f"translate(0 {bob:.2f}) rotate({a:.1f} {pivot[0]} {pivot[1]})"
    tp = lambda x, y: (lambda p: (p[0], p[1] + bob))(_rot(x, y, *pivot, a))
    cx, cy, rx, ry = BODY
    k = 1 - 0.45 * tuck
    hx, hy = HEAD[0] + 1.0 * stretch, HEAD[1] - 0.5 * stretch + 1.0 * nod
    hx, hy = _rot(NECK_BASE[0] + (hx - NECK_BASE[0]) * k, NECK_BASE[1] + (hy - NECK_BASE[1]) * k, *NECK_BASE, dip)
    inv = f"rotate({-a:.1f} {pivot[0]} {pivot[1]}) translate(0 {-bob:.2f})"
    if paddle is not None:
        _paddles(d, inv, paddle, near=False)
    _tail(d, C, wag)
    body = ellipse(cx, cy, rx, ry)
    d.clip("dbody", [body])
    d.add(body, C["body"])
    _body_marks(d, C, "dbody", cx, cy, rx, ry)
    _folded_wing(d, C)
    neck = _neck(d, C, NECK_BASE, (hx, hy))
    d.add(circle(21.4, 20.2, 3.2), C["chest"])                     # poitrail bombé
    if C["mottle"]:
        d.raw(line("M20.4,19.0 l0.6,0.5 l0.6,-0.5 M21.6,21.0 l0.6,0.5 l0.6,-0.5", C["mottle"], 0.7))
    if paddle is not None:
        _paddles(d, inv, paddle, near=True)
    _head(d, C, hx, hy, ang=-4 * stretch + 10 * nod + dip, open_=open_)
    span = _chord([_ellipse_pts(cx, cy, rx, ry), neck, _ellipse_pts(21.4, 20.2, 3.2, 3.2),
                   _ellipse_pts(hx, hy, HEAD_R, HEAD_R)], tp)
    _water(d, span, ring, splash, wake)
    return d


def _flap_wing(theta, span, root, far=False, chord=1.0):
    """Aile en vol, de profil : theta = direction de l'aile (degrés, -90 = vers le haut, 90 = vers le bas),
    span = envergure apparente (courte quand l'aile vient vers nous), chord : largeur relative.
    Renvoie la forme et un repère local Wp(u, v) : u de l'attache (0) à la pointe (1), v vers le bord de fuite."""
    t = math.radians(theta)
    e1 = (math.cos(t) * span, math.sin(t) * span)
    e2 = (math.sin(t) * chord, -math.cos(t) * chord)  # perpendiculaire, côté arrière (bord de fuite)
    if e2[0] > 0:
        e2 = (-e2[0], -e2[1])
    ox, oy = root
    if far:
        ox, oy = ox + 1.4, oy - 0.9
    Wp = lambda u, v: (ox + e1[0] * u + e2[0] * v, oy + e1[1] * u + e2[1] * v)
    # bord d'attaque bombé, pointe, puis trois plumes arrondies au bord de fuite
    pts = [(-0.05, -1.6), (0.4, -2.8), (0.85, -2.0), (1.05, 0.4), (0.94, 2.6), (0.8, 1.2), (0.7, 4.1),
           (0.55, 2.5), (0.4, 5.2), (0.24, 3.5), (0.06, 5.4), (-0.08, 3.2)]
    return _smooth([Wp(u, v) for u, v in pts]), Wp


def _flying(C, theta=-100.0, span=11.0, chord=1.0, bob=0.0):
    """Adulte en vol (pas d'eau) : corps centré vers (14, 18), oiseau entier (queue à bec) centré sur x = 16 ;
    cou tendu, pattes repliées, ailes qui battent (theta, span, chord : voir _flap_wing)."""
    d = _Duck(water=False)
    d.tr = f"translate(0 {bob:.2f})"
    cx, cy, rx, ry = 14.0, 18.4, 8.0, 3.9
    root = (16.4, 16.8)
    # aile lointaine (derrière le corps, plus foncée)
    far, _ = _flap_wing(theta, span, root, far=True, chord=chord)
    d.add(far, C["tip"])
    # pattes orange repliées sous la queue
    for dx in (0.0, 1.4):
        d.add(path(f"M{9.4 + dx:.2f},{20.8:.2f} L{6.2 + dx:.2f},{21.8:.2f} L{5.8 + dx:.2f},{23.2:.2f} "
                   f"L{7.4 + dx:.2f},{23.0:.2f} L{10.2 + dx:.2f},{21.8:.2f} Z"), "#F28C28")
    _tail(d, C, fly=True)
    body = ellipse(cx, cy, rx, ry)
    d.clip("fbody", [body])
    d.add(body, C["body"])
    if C["drake"]:
        d.add(ellipse(cx - rx + 1.4, cy, 2.8, ry + 1), C["rump"], sil=False, clip="fbody")
        d.add(ellipse(cx + rx - 1.2, cy + 0.4, 4.0, ry + 1.2), C["chest"], sil=False, clip="fbody")
    else:
        _body_marks(d, C, "fbody", cx, cy - 0.6, rx, ry)
    d.add(ellipse(cx, cy + 2.6, rx - 1.6, 1.2), "#FFFFFF", sil=False, clip="fbody", opacity=0.25)
    hx, hy = 22.6, 14.6
    _neck(d, C, (19.6, 16.8), (hx, hy), wb=2.6, wh=2.0)
    _head(d, C, hx, hy, r=3.7, ang=6)
    # aile proche, par-dessus, avec son propre contour ; pointe foncée et miroir bleu près de l'attache
    near, Wp = _flap_wing(theta, span, root, chord=chord)
    _sticker(d, [near], C["wing"])
    d.clip("fwing", [near])
    tip = _smooth([Wp(u, v) for u, v in ((0.62, -3.6), (1.4, -1.0), (1.2, 3.0), (0.62, 4.6))])
    d.raw('<g clip-path="url(#fwing)">' + tip.replace('fill="%F%"', f'fill="{C["tip"]}"') + "</g>")
    spec = poly([Wp(0.04, 2.6), Wp(0.4, 2.6), Wp(0.4, 6.0), Wp(0.04, 6.0)])
    d.raw('<g clip-path="url(#fwing)">' + spec.replace('fill="%F%"', f'fill="{C["spec"]}"') + "</g>")
    a, b = Wp(0.04, 2.3), Wp(0.42, 2.3)
    d.raw(f'<g clip-path="url(#fwing)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", "#FFFFFF", 0.5)
          + "</g>")
    return d


# ================================================================== CANETON
def _duckling(C, bob=0.0, rock=0.0, stretch=0.0, open_=0.0, wag=0.0, ring=None, wake=0.0):
    """Caneton sur l'eau : gros duvet rond, grosse tête, petit bec. Dessiné à l'échelle des adultes puis réduit
    de DUCKLING_SCALE autour de (16, G), contour compensé (même épaisseur que les autres sprites)."""
    d = _Duck(water=True)
    pivot = (15.0, 23.0)
    k = DUCKLING_SCALE
    d.tr = (f"translate(0 {bob:.2f}) rotate({rock:.1f} {pivot[0]} {pivot[1]}) "
            f"translate(16 {G}) scale({k}) translate(-16 -{G})")
    d.ow = OUTLINE_W / k
    tp = lambda x, y: (lambda p: (p[0], p[1] + bob))(_rot(16 + (x - 16) * k, G + (y - G) * k, *pivot, rock))
    cx, cy, rx, ry = 14.6, 22.2, 5.0, 3.5
    # petite queue en pointe (duvet)
    d.add(_smooth([(10.6, 20.2), (8.6, 18.8), (8.0, 19.8), (9.6, 21.6)]).replace(
        "/>", f' transform="rotate({wag:.1f} 10.2 20.8)"/>'), C["down"])
    body = ellipse(cx, cy, rx, ry)
    d.clip("kbody", [body])
    d.add(body, C["down"])
    d.add(ellipse(cx + 2.4, cy + 0.8, 3.0, 2.8), C["light"], sil=False, clip="kbody")
    # tête ronde posée sur le devant du corps
    hx, hy = 18.4 + 0.7 * stretch, 17.2 - 0.4 * stretch
    d.add(circle(hx, hy, 3.4), C["down"])
    # petite houppe sur le crâne
    d.raw(line(f"M{hx - 0.9:.2f},{hy - 3.2:.2f} q-0.2,-1.3 0.9,-1.7 M{hx - 0.2:.2f},{hy - 3.3:.2f} q0.5,-1.0 1.4,-0.9",
               OUTLINE, 0.65))
    # bec court
    L = _local(hx, hy, -3 * stretch)
    hinge = L(2.2, 0.9)
    U = lambda u, v: _rot(*L(u, v), *hinge, -8 * open_)
    D = lambda u, v: _rot(*L(u, v), *hinge, 32 * open_)
    if open_ > 0.05:
        d.add(poly([hinge, U(5.2, 0.9), D(4.8, 1.1)]), "#7A2A2A")
    d.add(_smooth([D(2.4, 0.8), D(4.8, 0.9), D(5.0, 1.4), D(3.0, 1.9)]), C["bill"])
    d.add(_smooth([U(2.2, -0.9), U(4.4, -0.3), U(5.9, 0.5), U(4.6, 1.2), U(2.4, 1.2)]), C["bill"])
    # aileron (duvet un peu plus foncé)
    d.add(_smooth([(16.6, 20.4), (13.8, 19.8), (11.2, 20.6), (12.6, 22.4), (15.8, 22.4)]), C["shade"], sil=False)
    d.raw(line("M16.2,20.5 Q13.6,19.5 11.6,20.7", OUTLINE, 0.7))
    # œil, joue rose
    _eye(d, *L(1.2, -0.5), 1.05)
    d.add(ellipse(*L(1.0, 1.6), 0.95, 0.6), C["blush"], sil=False, opacity=0.7)
    span = _chord([_ellipse_pts(cx, cy, rx, ry)], tp)
    _water(d, span, ring, 0.0, wake)
    return d


# ================================================================== animations
_SWIM = [dict(bob=0.4 * math.sin(k * math.pi / 2), rock=-1.6 * math.cos(k * math.pi / 2),
              wag=6 * math.sin(k * math.pi / 2 + 0.8), ring=k / 4, wake=k / 4) for k in range(4)]
_QUACK = [dict(stretch=0.7, open_=0.9, ring=0.0), dict(stretch=0.4, open_=0.1, ring=0.1),
          dict(stretch=1.0, open_=1.0, ring=0.2, wag=6), dict(stretch=0.2, open_=0.0, ring=0.3)]

ANIMS = {   # espèce : {nom : (poses, fps, boucle)} ; chaque pose = dict(mode=..., paramètres)
    "adult": {
        "swim": ([dict(mode="swim", **p) for p in _SWIM], 6, True),
        "quack": ([dict(mode="swim", **p) for p in _QUACK], 8, False),
        "dive": ([dict(mode="swim", nod=0.8, stretch=0.3, ring=0.0),
                  dict(mode="swim", tilt=40, dip=70, tuck=1.0, bob=0.4, splash=0.5, ring=0.1),
                  dict(mode="swim", tilt=70, dip=30, tuck=1.0, bob=0.6, splash=0.9, ring=0.25, wag=-8),
                  dict(mode="swim", tilt=86, dip=30, tuck=1.0, bob=0.4, wag=14, ring=0.4, paddle=0.0),
                  dict(mode="swim", tilt=88, dip=30, tuck=1.0, bob=0.6, wag=-14, ring=0.55, paddle=math.pi / 2),
                  dict(mode="swim", tilt=86, dip=30, tuck=1.0, bob=0.4, wag=12, ring=0.7, paddle=math.pi),
                  dict(mode="swim", tilt=40, dip=70, tuck=1.0, bob=0.4, splash=0.7, ring=0.85),
                  dict(mode="swim", bob=-0.3, rock=-3, splash=0.3, ring=0.95, wag=8)], 8, False),
        "fly": ([dict(mode="fly", theta=-104, span=11.5, bob=0.6),
                 dict(mode="fly", theta=-172, span=9.5, chord=0.6),
                 dict(mode="fly", theta=112, span=10.5, bob=-0.6),
                 dict(mode="fly", theta=-172, span=9.5, chord=0.6)],
                12, True),
    },
    "duckling": {
        "swim": ([dict(mode="swim", **p) for p in _SWIM], 6, True),
        "quack": ([dict(mode="swim", **p) for p in _QUACK], 8, False),
    },
}

_DRAW = {
    "adult": {"swim": _adult, "fly": _flying},
    "duckling": {"swim": _duckling},
}


def _species(kind):
    return "adult" if kind in ADULTS else "duckling"


def anims(kind):
    """Animations d'un kind ("duck", "duck_f", "duckling") : {nom : (poses, fps, boucle)}."""
    return ANIMS[_species(kind)]


def pose(kind, mode, **kw):
    """Dessin d'une pose ; mode : 'swim' (sur l'eau : nage, cancan, plongeon) ou 'fly' (adultes)."""
    return _DRAW[_species(kind)][mode](KINDS[kind], **kw)


def frames(kind, anim):
    """SVG des images d'une animation (vue de droite)."""
    return [pose(kind, **p).svg() for p in anims(kind)[anim][0]]


# ================================================================== planche de contrôle
if __name__ == "__main__":
    import os
    import numpy as np
    from PIL import Image, ImageDraw
    from spritelib import render_svg, PAD

    OUT = ("/tmp/claude-1000/-home-cgerardin-Sources-314-SOFTWARE-tecky-quest/"
           "6b721a3c-761f-447f-a079-6967b45600df/scratchpad/ducks_preview.png")
    SC, GAP = 4, 6
    cell = (W + 2 * PAD) * SC
    rows = [(k, a) for k in KINDS for a in anims(k)]
    ncol = max(len(anims(k)[a][0]) for k, a in rows)
    small = 2                                         # rangée à la taille du jeu (S = 2)
    sheet = Image.new("RGBA", (ncol * (cell + GAP) + GAP, len(rows) * (cell + GAP) + GAP + (W + 2 * PAD) * small * 2),
                      (40, 40, 40, 255))
    bad = []
    for r, (kind, anim) in enumerate(rows):
        for c, sv in enumerate(frames(kind, anim)):
            im = render_svg(sv, W, H, SC, PAD)
            for name, pad in (("cadre", 0), ("marge", PAD)):
                a = np.array(render_svg(sv, W, H, SC, pad).getchannel("A"))
                if any((e > 40).sum() for e in (a[0], a[-1], a[:, 0], a[:, -1])):
                    bad.append(f"{kind}/{anim}/{c} ({name})")
            x, y = GAP + c * (cell + GAP), GAP + r * (cell + GAP)
            bg = Image.new("RGBA", im.size, (124, 195, 107, 255) if anim == "fly" else (93, 173, 226, 255))
            if anim == "fly":                         # ombre au sol, comme le jeu la dessinera
                ImageDraw.Draw(bg).ellipse([(PAD + 8) * SC, (PAD + 28) * SC, (PAD + 22) * SC, (PAD + 30) * SC],
                                           fill=(80, 130, 70, 255))
            ImageDraw.Draw(bg).line([(0, (PAD + G) * SC), (4 * SC, (PAD + G) * SC)], fill=(255, 80, 80, 255), width=2)
            bg.alpha_composite(im)
            sheet.alpha_composite(bg, (x, y))
    # rangée à la taille réelle (échelle 2) : un exemple par espèce et animation, sur l'eau
    y0 = GAP + len(rows) * (cell + GAP)
    x = GAP
    for kind, anim in rows:
        sv = frames(kind, anim)[0 if anim != "dive" else 4]
        im = render_svg(sv, W, H, small, PAD)
        bg = Image.new("RGBA", im.size, (124, 195, 107, 255) if anim == "fly" else (93, 173, 226, 255))
        bg.alpha_composite(im)
        sheet.alpha_composite(bg, (x, y0))
        x += im.width + 4
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet.save(OUT)
    print(OUT)
    print("touchent un bord :", ", ".join(bad) if bad else "aucun")

"""
Petits animaux que Tecky peut poursuivre (cellule 32x32, pieds à y=28 : origine conseillée (16, 28)).

- L'écureuil roux de la forêt ("squirrel") : assis qui grignote une noisette (idle), course bondissante (run)
  et escalade d'un tronc vu de DOS (climb, seule animation qui n'est pas de profil).
- Les chats du village ("cat" roux tigré, "cat_black" noir aux yeux jaune-vert) : assis (idle), marche (walk),
  galop (run), saut (jump : élan puis bond) et feulement dos rond (hiss).
- Le chat de la voisine ("cat_white") : blanc aux yeux bleus, oreilles, tache sur le dos et bout de queue gris,
  collier rose à grelot doré pour le reconnaître. Mêmes poses et animations que les autres chats.

Vues de profil tournées vers la droite ; la vue gauche est le miroir (fait par le jeu).
Même principe que hens.py : `ANIMS[espèce][anim] = (poses, fps, boucle)`, `frames(kind, anim)` -> SVG.
"""
import math

from spritelib import Drawing, circle, ellipse, rect, poly, path, leg, line, OUTLINE, OUTLINE_W

W = H = 32
G = 28            # ligne des pieds

KINDS = {   # couleurs par espèce / variante
    "squirrel": dict(fur="#C8642E", dark="#9E4A22", belly="#F6DDB8", nut="#D9A15E", cap="#8A5A2E"),
    "cat": dict(fur="#E8923A", dark="#C26A22", stripe="#C26A22", belly="#FFF1DC", eye="#9BCB45",
                ear="#F4A3A8", nose="#E57C8E", whisker="#FFF1DC"),
    "cat_black": dict(fur="#3B3540", dark="#27222B", stripe=None, belly="#5E5566", eye="#D9E64A",
                      ear="#8A6878", nose="#C48E9C", whisker="#B9B1BF"),
    # chat de la voisine : patch = taches grises (oreilles, dos, bout de queue), collar + bell = collier à grelot
    "cat_white": dict(fur="#FBF8F3", dark="#D9D3CB", stripe=None, belly="#FFFFFF", eye="#6DB8EA",
                      ear="#F4A3A8", nose="#EE97A8", whisker="#ABA49B",
                      patch="#9D9BA8", patch_dk="#7D7B88", collar="#F2729E", bell="#F2C14E"),
}
SPECIES = {"squirrel": "squirrel", "cat": "cat", "cat_black": "cat", "cat_white": "cat"}   # les chats partagent les poses
# l'écureuil est dessiné un peu grand puis réduit autour de l'origine (16, 28) : plus petit qu'une poule,
# le contour garde la même épaisseur que les autres sprites
SCALE = {"squirrel": 0.85, "cat": 1.0}


# ================================================================== outils
def _shadow(d, cx, cy, rx, ry=1.7):
    d.under.append(f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="#000" opacity="0.2"/>')


def _g(tr, xml):
    return f'<g transform="{tr}">{xml}</g>' if tr else xml


def _clipped(cid, tr, xml):
    """Détail découpé à une forme (le clip s'applique hors de la transformation, comme la forme elle-même)."""
    return f'<g clip-path="url(#{cid})">{_g(tr, xml)}</g>'


def _rot(x, y, cx, cy, a):
    """Rotation du point (x, y) de a degrés autour de (cx, cy) (même sens que SVG)."""
    r = math.radians(a)
    c, s = math.cos(r), math.sin(r)
    return cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c


def _spline(pts, n=4):
    """Courbe lisse passant par les points (Catmull-Rom), n points par segment."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(0.5 * (2 * p1[k] + (p2[k] - p0[k]) * t
                                    + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                                    + (3 * p1[k] - p0[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
    out.append(tuple(pts[-1]))
    return out


def _normals(pts):
    out = []
    n = len(pts)
    for i in range(n):
        (ax, ay), (bx, by) = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        tx, ty = bx - ax, by - ay
        ln = math.hypot(tx, ty) or 1.0
        out.append((-ty / ln, tx / ln))
    return out


def _wave(pts, amp, phase, k=1.0):
    """Ondulation : décale les points le long de la normale, de plus en plus vers le bout."""
    n = len(pts)
    out = []
    for i, ((x, y), (nx, ny)) in enumerate(zip(pts, _normals(pts))):
        t = i / (n - 1)
        o = amp * t * math.sin(2 * math.pi * k * t - phase)
        out.append((x + nx * o, y + ny * o))
    return out


def _interp(vals, t):
    """Interpolation linéaire dans une liste de valeurs régulièrement espacées (t de 0 à 1)."""
    f = t * (len(vals) - 1)
    i = min(int(f), len(vals) - 2)
    return vals[i] + (vals[i + 1] - vals[i]) * (f - i)


def _tube(pts, r0, r1):
    """Boudin le long d'une courbe (rayon r0 à la base -> r1 au bout), bouts arrondis : liste de formes."""
    n = len(pts)
    rs = [r0 + (r1 - r0) * i / (n - 1) for i in range(n)]
    nrm = _normals(pts)
    left = [(x + nx * r, y + ny * r) for (x, y), (nx, ny), r in zip(pts, nrm, rs)]
    right = [(x - nx * r, y - ny * r) for (x, y), (nx, ny), r in zip(pts, nrm, rs)]
    return [poly(left + right[::-1]), circle(*pts[0], r0), circle(*pts[-1], r1)]


def _sticker(d, shapes, fill, w=OUTLINE_W):
    """Groupe de formes posé PAR-DESSUS ce qui précède, avec son propre contour (union des formes)."""
    for s in shapes:
        d.raw(s.replace('fill="%F%"', f'fill="{OUTLINE}" stroke="{OUTLINE}" stroke-width="{w:.2f}" '
                                      f'stroke-linejoin="round"'))
    for s in shapes:
        d.raw(s.replace('fill="%F%"', f'fill="{fill}"'))


def _limb(d, hx, hy, fx, fy, w, col, paw=1.0):
    """Patte (de la hanche au pied) + petit pied arrondi tourné vers l'avant."""
    d.add(leg(hx, hy, fx, fy, w), col)
    d.add(ellipse(fx + 0.5 * paw, fy - 0.1, w * 0.62 * paw + 0.25, w * 0.42 + 0.2), col)


def _thigh(d, col, hx, hy, fx, fy, a=3.4, b=2.6):
    """Cuisse arrière : ovale orienté de la hanche vers le pied, contour fin sur le corps."""
    ang = math.degrees(math.atan2(fy - hy, fx - hx))
    c = math.cos(math.radians(ang))
    s = math.sin(math.radians(ang))
    d.add(ellipse(hx + c * 1.0, hy + s * 1.0, a, b, f"rotate({ang:.1f} {hx + c:.2f} {hy + s:.2f})"), col, edge=True)


def _tuft(bx0, by0, bx1, by1, tx, ty, lean=-0.6, tr=""):
    """Plumet de l'écureuil : flamme qui part des deux bords de l'oreille et dépasse de la pointe (tx, ty)."""
    return path(f"M{bx0:.2f},{by0:.2f} Q{tx + lean - 0.5:.2f},{ty + 0.6:.2f} {tx + lean:.2f},{ty - 1.6:.2f} "
                f"Q{tx + 0.5:.2f},{ty + 0.4:.2f} {bx1:.2f},{by1:.2f} Z", tr)


def _eye_dot(d, x, y, r=1.15, tr=""):
    """Œil rond tout noir avec reflet (écureuil, comme les poules)."""
    d.add(circle(x, y, r, tr), OUTLINE, sil=False)
    d.add(circle(x + r * 0.3, y - r * 0.35, r * 0.36, tr), "#FFFFFF", sil=False)


# ================================================================== ÉCUREUIL
def _sq_tail_shapes(pts, radii, step=1.7):
    """Panache : chapelet de cercles espacés d'environ `step` (le bord bosselé fait les poils)."""
    out = []
    acc, last = 0.0, None
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        if last is not None:
            acc += math.hypot(x - last[0], y - last[1])
        last = (x, y)
        if i in (0, n - 1) or acc >= step:
            acc = 0.0
            out.append(circle(x, y, _interp(radii, i / (n - 1))))
    return out


def _sq_tail(d, C, pts, radii, front=False, fold=(0.15, 0.8), side=1):
    """Queue en panache + petit trait foncé (pli des poils) ; front=True : posée par-dessus le corps."""
    shapes = _sq_tail_shapes(pts, radii)
    if front:
        _sticker(d, shapes, C["fur"], OUTLINE_W / SCALE["squirrel"])
    else:
        for s in shapes:
            d.add(s, C["fur"])
    n = len(pts)
    a, b = int(fold[0] * (n - 1)), int(fold[1] * (n - 1))
    nrm = _normals(pts)
    mid = [(x + nx * side * _interp(radii, i / (n - 1)) * 0.3, y + ny * side * _interp(radii, i / (n - 1)) * 0.3)
           for i, ((x, y), (nx, ny)) in enumerate(zip(pts, nrm)) if a <= i <= b]
    d.raw(line("M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in mid), C["dark"], 1.0))


def _sq_head(d, C, hx, hy, tr="", chew=0.0):
    """Tête de profil vers la droite, centre (hx, hy) : grosse tête ronde, museau court, oreille à plumet ;
    chew : joue gonflée (grignotage)."""
    # oreille lointaine : à peine visible derrière
    d.add(poly([(hx - 3.4, hy - 2.0), (hx - 1.6, hy - 3.4), (hx - 3.2, hy - 6.6)], tr), C["dark"])
    d.add(circle(hx, hy, 4.2, tr), C["fur"])
    d.add(ellipse(hx + 2.8, hy + 1.2, 3.1, 2.5, tr), C["fur"])                       # museau
    d.add(ellipse(hx + 2.2, hy + 2.6, 2.4 + chew * 0.35, 1.45 + chew * 0.3, tr), C["belly"], sil=False)
    # oreille proche, pointue, bout foncé + plumet
    tx, ty = hx - 1.5, hy - 8.0
    d.add(poly([(hx - 2.6, hy - 2.4), (hx + 0.7, hy - 3.4), (tx, ty)], tr), C["fur"])
    d.add(poly([(hx - 1.7, hy - 3.3), (hx - 0.3, hy - 3.7), (hx - 1.4, hy - 6.0)], tr), C["dark"], sil=False,
          opacity=0.55)
    d.add(_tuft(hx - 2.05, hy - 5.4, hx - 0.55, hy - 5.7, tx, ty, -0.7, tr), C["dark"])
    # œil (cerclé de clair), truffe
    d.add(circle(hx + 1.55, hy - 0.5, 1.7, tr), C["belly"], sil=False)
    _eye_dot(d, hx + 1.7, hy - 0.5, 1.2, tr)
    d.add(ellipse(hx + 5.7, hy + 0.6, 0.85, 0.7, tr), OUTLINE, sil=False)


def _nut(d, C, x, y):
    """Noisette : ronde, le haut plus foncé, un reflet."""
    nut = ellipse(x, y, 2.0, 2.1)
    d.clip("nut", [nut])
    d.add(nut, C["nut"], sil=False, edge=True)
    d.add(ellipse(x, y - 1.9, 2.6, 1.4), C["cap"], sil=False, clip="nut")
    d.add(circle(x + 0.8, y + 0.5, 0.5), "#FFFFFF", sil=False, opacity=0.6)


def _sq_sit(C, nib=0.0, wag=0.0, chew=0.0):
    """Assis sur les pattes arrière, grignote une noisette. nib : 0 noisette contre le ventre -> 1 à la bouche ;
    wag : frétillement de la queue (-1..1) ; chew : joue gonflée."""
    d = Drawing(W, H)
    _shadow(d, 14.6, G, 7.8)
    # queue : part sous la croupe, remonte le long du dos, le haut se recourbe vers l'arrière
    a = wag
    ctrl = [(12.6, 26.6), (6.6, 25.4), (4.6, 18.6), (6.0 + a * 0.3, 11.6), (8.0 + a * 0.8, 6.4),
            (6.6 + a * 1.4, 3.4), (3.6 + a * 1.6, 3.6 + a * 0.4)]
    _sq_tail(d, C, _spline(ctrl, 5), [2.4, 3.3, 3.9, 4.1, 3.9, 3.4, 2.7], fold=(0.2, 0.85), side=-1)
    # corps (penché vers l'avant), ventre crème
    btr = "rotate(12 17.0 20.8)"
    body = ellipse(17.0, 20.8, 4.4, 5.7, btr)
    d.clip("sqbody", [body])
    d.add(body, C["fur"])
    d.add(ellipse(19.5, 21.6, 2.3, 4.8, btr), C["belly"], sil=False, clip="sqbody")
    # grand pied à plat et cuisse
    d.add(ellipse(18.9, 27.35, 3.2, 1.1), C["fur"])
    d.add(ellipse(15.0, 24.5, 4.3, 3.1, "rotate(-28 15.0 24.5)"), C["fur"], edge=True)
    # tête : s'incline vers la noisette quand il grignote
    _sq_head(d, C, 19.6, 12.8, f"rotate({nib * 7:.1f} 17.6 16.5)", chew=chew)
    # pattes avant qui tiennent la noisette
    nx, ny = 23.0 + nib * 0.6, 19.2 - nib * 2.6
    d.add(ellipse(nx - 1.3, ny + 0.2, 1.0, 0.9), C["dark"], sil=False, edge=True)
    _nut(d, C, nx, ny)
    d.add(leg(19.2, 18.8, nx - 0.9, ny + 1.3, 1.8), C["fur"], sil=False, edge=True)
    d.add(ellipse(nx - 0.6, ny + 1.2, 1.25, 0.95), C["fur"], sil=False, edge=True)
    return d


def _sq_run(C, cx=15.5, cy=21.6, tilt=0.0, rx=6.4, ry=3.8, ff=(23, G), hf=(8, G, 0), wave=0.0, sh=7.5):
    """Course bondissante de profil. ff : pied avant (x, y) ; hf : pied arrière (x, y, angle) ;
    tilt : bascule du corps (négatif = nez en l'air)."""
    d = Drawing(W, H)
    _shadow(d, 15.5, G, sh)
    btr = f"rotate({tilt:.1f} {cx} {cy})"
    R = lambda x, y: _rot(x, y, cx, cy, tilt)
    # queue : flotte derrière, relevée, ondule
    bx, by = R(cx - rx + 1.4, cy - 1.0)
    ctrl = [(bx, by), (bx - 4.0, by - 1.2), (bx - 6.2, by - 5.4), (bx - 5.4, by - 9.6), (bx - 2.6, by - 11.6)]
    pts = _wave(_spline(ctrl, 4), 1.5, wave, 0.8)
    _sq_tail(d, C, pts, [2.0, 3.0, 3.5, 3.3, 2.6], fold=(0.2, 0.85), side=-1)
    # pattes lointaines (foncées)
    sx, sy = R(cx + rx - 2.4, cy + 1.6)
    hx, hy = R(cx - rx + 2.9, cy + 0.6)
    _limb(d, sx + 0.9, sy, ff[0] + 1.2, ff[1] - 0.3, 1.7, C["dark"], 0.9)
    d.add(ellipse(hf[0] + 1.2, hf[1] - 1.0, 2.5, 0.95, f"rotate({hf[2]:.1f} {hf[0] + 1.2:.2f} {hf[1] - 1.0:.2f})"),
          C["dark"])
    # corps + ventre
    body = ellipse(cx, cy, rx, ry, btr)
    d.clip("sqbody", [body])
    d.add(body, C["fur"])
    d.add(ellipse(cx + 1.2, cy + ry * 0.78, rx * 0.78, ry * 0.42, btr), C["belly"], sil=False, clip="sqbody")
    # patte arrière proche : pied allongé + cuisse
    d.add(ellipse(hf[0], hf[1] - 0.95, 2.7, 1.05, f"rotate({hf[2]:.1f} {hf[0]:.2f} {hf[1] - 0.95:.2f})"), C["fur"])
    d.add(leg(hx, hy, hf[0] - 1.2, hf[1] - 1.0, 2.0), C["fur"])
    _thigh(d, C["fur"], hx, hy, hf[0] - 1.2, hf[1] - 1.0, 3.2, 2.6)
    # patte avant proche
    _limb(d, sx, sy, ff[0], ff[1], 1.8, C["fur"], 0.9)
    # tête
    hx_, hy_ = R(cx + rx - 0.8, cy - 3.6)
    _sq_head(d, C, hx_, hy_, f"rotate({tilt * 0.4:.1f} {hx_:.2f} {hy_ + 3:.2f})")
    return d


def _sq_climb(C, phase=0.0, wave=0.0):
    """Vu de DOS, grimpe un tronc vertical : pattes écartées qui alternent (en diagonale), queue qui pend."""
    d = Drawing(W, H)
    s = math.sin(phase)
    bob = 0.5 * math.cos(2 * phase)
    Y = lambda v: v + bob
    # pattes : avant gauche + arrière droite ensemble, puis l'inverse ; griffes plantées dans l'écorce
    paws = []
    for side, k in ((-1, s), (1, -s)):
        fx, fy = 16 + side * 6.4, Y(8.4 - k * 1.7)
        d.add(leg(16 + side * 2.4, Y(12.6), fx, fy, 2.3), C["fur"])
        d.add(ellipse(fx, fy, 1.5, 1.35), C["fur"])
        gx, gy = 16 + side * 6.6, Y(22.6 + k * 1.5)
        d.add(leg(16 + side * 3.0, Y(18.8), gx, gy, 2.6), C["fur"])
        d.add(ellipse(gx, gy + 0.3, 1.45, 2.1, f"rotate({-side * 25} {gx:.2f} {gy + 0.3:.2f})"), C["fur"])
        paws += [(fx + side * 0.9, fy - 0.6, side), (gx + side * 0.9, gy + 0.6, side)]
    # dos en poire : épaules + hanches, raie plus foncée le long de l'échine
    upper = ellipse(16, Y(14.0), 4.3, 4.8)
    hips = ellipse(16, Y(18.4), 5.0, 3.7)
    d.clip("sqback", [upper, hips])
    d.add(upper, C["fur"])
    d.add(hips, C["fur"])
    d.add(ellipse(16, Y(13.6), 1.9, 4.4), C["dark"], sil=False, clip="sqback", opacity=0.35)
    for side in (-1, 1):                      # cuisses
        d.add(ellipse(16 + side * 3.5, Y(19.2), 2.3, 2.8, f"rotate({side * -20} {16 + side * 3.5} {Y(19.2):.2f})"),
              C["fur"], sil=False, edge=True)
    for x, y, side in paws:
        d.raw(line(f"M{x:.2f},{y - 0.5:.2f} l{side * 0.7:.2f},-0.3 M{x + side * 0.2:.2f},{y + 0.4:.2f} "
                   f"l{side * 0.7:.2f},0.2", OUTLINE, 0.55))
    # tête vue de dos : deux oreilles pointues à plumet
    hy = Y(8.2)
    for side in (-1, 1):
        ex = 16 + side * 2.3
        tx, ty = ex + side * 0.5, hy - 6.0
        d.add(poly([(ex - 1.6, hy - 1.8), (ex + 1.6, hy - 1.8), (tx, ty)]), C["fur"])
        d.add(_tuft(tx - 0.75, ty + 2.4, tx + 0.75, ty + 2.4, tx, ty, side * 0.5), C["dark"])
    d.add(circle(16, hy, 4.2), C["fur"])
    d.add(ellipse(16, hy - 0.9, 2.6, 2.2), C["dark"], sil=False, opacity=0.25)
    # queue : pend sous la croupe, par-dessus, et ondule
    ctrl = [(16, Y(19.8)), (16, Y(22.6)), (16, Y(25.6)), (16, Y(28.6)), (16, Y(30.4))]
    pts = _wave(_spline(ctrl, 4), 2.8, wave, 0.8)
    _sq_tail(d, C, pts, [1.8, 3.0, 3.7, 3.6, 2.7], front=True, fold=(0.3, 0.92))
    return d


# ================================================================== CHAT
def _spot(d, C, cid, shapes, spot):
    """Tache grise du chat blanc (C["patch"]), découpée aux formes `shapes` ; rien pour les autres chats."""
    if not C.get("patch"):
        return
    d.clip(cid, shapes)
    d.raw(f'<g clip-path="url(#{cid})">' + spot.replace('fill="%F%"', f'fill="{C["patch"]}"') + "</g>")


def _cat_tail(d, C, pts, r0, r1, puff=0.0):
    """Queue en boudin (rayures si chat tigré) ; puff > 0 : poils hérissés (feulement)."""
    n = len(pts)
    if puff:
        for i, (x, y) in enumerate(pts):
            r = r0 + (r1 - r0) * i / (n - 1) + puff * (0.7 + 0.5 * (i % 2))
            d.add(circle(x, y, r), C["fur"])
    else:
        for sh in _tube(pts, r0, r1):
            d.add(sh, C["fur"])
    if C["stripe"]:
        nrm = _normals(pts)
        for i in range(3, n - 2, 3):
            (x, y), (nx, ny) = pts[i], nrm[i]
            q = (r0 + (r1 - r0) * i / (n - 1) + puff * 0.8) * 0.85
            d.raw(line(f"M{x + nx * q:.2f},{y + ny * q:.2f} L{x - nx * q:.2f},{y - ny * q:.2f}", C["stripe"], 1.0))
        d.add(circle(*pts[-1], r1 * 0.8 + puff * 0.6), C["stripe"], sil=False)
    if C.get("patch"):   # bout de queue gris (chat blanc) : mêmes rayons que la queue, il en épouse le bord
        for i in range(n - max(3, n // 4), n):
            r = r0 + (r1 - r0) * i / (n - 1) + (puff * (0.7 + 0.5 * (i % 2)) if puff else 0.0)
            d.add(circle(*pts[i], r), C["patch"], sil=False)


def _cat_head(d, C, hx, hy, tr="", ears=0.0, eye="open", mouth=0.0):
    """Tête de profil vers la droite, centre (hx, hy). ears : 0 dressées -> 1 couchées en arrière ;
    eye : 'open', 'blink', 'angry' ; mouth : 0 fermée -> 1 grande ouverte (feulement)."""
    er = -ears * 62
    if C.get("collar"):   # cou et collier (chat de la voisine) : bande en travers du cou, sous la tête
        neck = ellipse(hx - 1.7, hy + 4.4, 3.1, 3.4, tr)
        d.add(neck, C["fur"])
        d.clip("catneck", [neck])
        d.raw(_clipped("catneck", tr, rect(hx - 5.8, hy + 4.35, 8.8, 2.3, 0.6, f"rotate(24 {hx - 1.4:.2f} {hy + 5.5:.2f})")
                       .replace('fill="%F%"', f'fill="{C["collar"]}" stroke="{OUTLINE}" stroke-width="0.7"')))
    # oreille lointaine (derrière)
    d.add(poly([(hx - 4.4, hy - 1.4), (hx - 1.4, hy - 4.2), (hx - 4.4, hy - 8.4)],
               f"{tr} rotate({er:.1f} {hx - 2.9:.2f} {hy - 2.8:.2f})"), C.get("patch_dk") or C["dark"])
    # crâne rond, joues un peu plus larges en bas
    skull = circle(hx, hy, 4.9, tr)
    d.add(skull, C["fur"])
    d.add(ellipse(hx + 1.0, hy + 1.6, 4.6, 3.4, tr), C["fur"])
    d.add(ellipse(hx + 2.9, hy + 2.2, 2.7, 1.9, tr), C["belly"], sil=False)       # museau clair
    _spot(d, C, "catcap", [skull], ellipse(hx - 1.4, hy - 4.0, 3.4, 2.2, f"{tr} rotate(-15 {hx - 1.4:.2f} {hy - 4.0:.2f})"))
    # oreille proche + intérieur rose
    etr = f"{tr} rotate({er:.1f} {hx - 0.8:.2f} {hy - 3.8:.2f})"
    d.add(poly([(hx - 2.8, hy - 3.2), (hx + 1.6, hy - 4.2), (hx - 1.4, hy - 9.0)], etr), C.get("patch") or C["fur"])
    d.add(poly([(hx - 1.7, hy - 4.0), (hx + 0.5, hy - 4.5), (hx - 1.3, hy - 7.4)], etr), C["ear"], sil=False)
    # rayures du front (chat tigré)
    if C["stripe"]:
        d.raw(_g(tr, line(f"M{hx - 1.8:.2f},{hy - 4.6:.2f} L{hx - 1.2:.2f},{hy - 2.7:.2f} "
                          f"M{hx + 0.3:.2f},{hy - 4.9:.2f} L{hx + 0.5:.2f},{hy - 3.0:.2f} "
                          f"M{hx - 4.0:.2f},{hy - 2.6:.2f} L{hx - 2.6:.2f},{hy - 1.5:.2f}", C["stripe"], 1.0)))
    # œil
    ex, ey = hx + 2.1, hy - 0.7
    if eye == "blink":
        d.raw(_g(tr, line(f"M{ex - 1.4:.2f},{ey + 0.1:.2f} Q{ex:.2f},{ey + 1.1:.2f} {ex + 1.4:.2f},{ey + 0.1:.2f}",
                          OUTLINE, 0.9)))
    else:
        d.add(ellipse(ex, ey, 1.35, 1.6, tr), C["eye"], sil=False, edge=True)
        d.add(ellipse(ex + 0.35, ey + 0.1, 0.5, 1.15, tr), OUTLINE, sil=False)
        d.add(circle(ex - 0.3, ey - 0.65, 0.42, tr), "#FFFFFF", sil=False)
        if eye == "angry":       # paupière basse et sourcil froncé
            d.add(poly([(ex - 1.9, ey - 2.6), (ex + 1.9, ey - 1.4), (ex + 1.9, ey - 0.5), (ex - 1.9, ey - 1.0)], tr),
                  C["fur"], sil=False)
            d.raw(_g(tr, line(f"M{ex - 1.6:.2f},{ey - 1.3:.2f} L{ex + 1.7:.2f},{ey - 0.2:.2f}", OUTLINE, 1.0)))
    # truffe, bouche, moustaches
    nx, ny = hx + 5.0, hy + 1.0
    if mouth > 0.05:
        d.add(ellipse(nx - 1.4, ny + 2.0 + mouth * 0.5, 1.5, 0.6 + mouth * 1.0, tr), "#7A2A2A")
        d.add(ellipse(nx - 1.7, ny + 2.4 + mouth * 1.1, 0.8, 0.4, tr), "#E8707A", sil=False)
        d.add(poly([(nx - 1.4, ny + 1.3), (nx - 0.6, ny + 1.3), (nx - 1.0, ny + 2.6)], tr), "#FFFFFF", sil=False)
    else:
        d.raw(_g(tr, line(f"M{nx - 0.3:.2f},{ny + 0.4:.2f} L{nx - 0.3:.2f},{ny + 1.1:.2f} "
                          f"Q{nx - 0.9:.2f},{ny + 1.8:.2f} {nx - 1.6:.2f},{ny + 1.3:.2f}", OUTLINE, 0.6)))
    d.add(path(f"M{nx - 0.9:.2f},{ny - 0.5:.2f} L{nx + 0.5:.2f},{ny - 0.5:.2f} L{nx - 0.1:.2f},{ny + 0.5:.2f} Z", tr),
          C["nose"], sil=False, edge=True)
    d.raw(_g(tr, line(f"M{nx - 1.2:.2f},{ny + 1.0:.2f} L{nx + 1.9:.2f},{ny + 0.4:.2f} "
                      f"M{nx - 1.2:.2f},{ny + 1.4:.2f} L{nx + 1.8:.2f},{ny + 1.9:.2f}", C["whisker"], 0.5)))
    if C.get("bell"):     # grelot doré sous la gorge
        bx, by = hx + 1.2, hy + 7.2
        d.add(circle(bx, by, 1.2, tr), C["bell"], sil=False, edge=True)
        d.raw(_g(tr, line(f"M{bx - 0.5:.2f},{by + 0.45:.2f} L{bx + 0.5:.2f},{by + 0.45:.2f}", OUTLINE, 0.45)))
        d.add(circle(bx - 0.4, by - 0.4, 0.35, tr), "#FFF7D6", sil=False)


def _cat_stripes(d, C, cid, tr, cx, top, ry, xs):
    """Rayures du dos (chat tigré), découpées à la forme du corps."""
    if not C["stripe"]:
        return
    for x in xs:
        d.raw(_clipped(cid, tr, line(f"M{x - 0.8:.2f},{top - 0.5:.2f} Q{x + 0.7:.2f},{top + ry * 0.6:.2f} "
                                     f"{x - 0.2:.2f},{top + ry * 1.1:.2f}", C["stripe"], 1.15)))


def _cat_sit(C, sweep=0.0, blink=False):
    """Assis de profil, queue posée au sol dont le bout balaie ; sweep : -1..1."""
    d = Drawing(W, H)
    _shadow(d, 14.6, G, 8.4)
    # queue : posée derrière, le bout se relève et balaie
    tip = (3.4 - sweep * 0.9, 23.6 - sweep * 2.6)
    pts = _spline([(10.5, 25.8), (6.6, 27.4), (3.8, 26.8), tip], 4)
    _cat_tail(d, C, pts, 1.5, 1.35)
    # patte avant lointaine (foncée)
    _limb(d, 19.8, 20.0, 20.6, G - 0.4, 2.2, C["dark"])
    # croupe ronde + poitrail
    rump = ellipse(13.4, 23.6, 5.3, 4.4)
    d.add(rump, C["fur"])
    btr = "rotate(14 17.4 19.6)"
    chest = ellipse(17.4, 19.6, 3.9, 5.4, btr)
    d.clip("catchest", [chest])
    d.add(chest, C["fur"])
    d.add(ellipse(20.0, 18.8, 1.9, 3.6, btr), C["belly"], sil=False, clip="catchest")
    _cat_stripes(d, C, "catchest", "rotate(-50 17.4 19.6)", 17.4, 14.6, 4.0, (15.6, 18.0))
    _spot(d, C, "catspot", [rump, chest], ellipse(13.6, 19.0, 3.4, 2.4, "rotate(-38 13.6 19.0)"))
    # cuisse et pied arrière
    d.add(ellipse(16.0, 27.3, 2.6, 1.05), C["fur"])
    d.add(ellipse(12.8, 24.2, 3.9, 3.3), C["fur"], edge=True)
    if C["stripe"]:
        d.raw(line("M10.4,22.0 Q11.6,23.2 11.2,24.8 M12.6,21.2 Q13.8,22.6 13.6,24.0", C["stripe"], 1.0))
    # patte avant proche
    _limb(d, 18.2, 20.6, 18.9, G - 0.3, 2.3, C["fur"])
    # tête
    _cat_head(d, C, 20.3, 12.0, eye="blink" if blink else "open")
    return d


def _cat_stand(C, cx=14.6, cy=20.8, rx=7.4, ry=4.0, tilt=0.0, hop=0.0, legs=None, head=(0.0, 0.0, 0.0),
               ears=0.0, tail=None, tail_wave=(0.0, 0.0), eye="open", shadow=None):
    """Chat debout de profil (marche, galop, saut).
    legs : 4 pieds (x, y) dans l'ordre avant-loin, arrière-loin, arrière-proche, avant-proche ;
    head : (dx, dy, rotation) de la tête ; tail : points de passage de la queue, relatifs à sa base."""
    d = Drawing(W, H)
    cy -= hop
    sh = shadow or (cx + 1.5, rx + 1.2)
    _shadow(d, sh[0], G, sh[1])
    btr = f"rotate({tilt:.1f} {cx:.2f} {cy:.2f})" if tilt else ""
    R = lambda x, y: _rot(x, y, cx, cy, tilt)
    # attaches des pattes (épaules / hanches) dans le repère du corps
    sx, sy = R(cx + rx - 2.5, cy + 1.2)
    hx, hy = R(cx - rx + 2.8, cy + 0.8)
    f1, h1, h2, f2 = legs
    # pattes lointaines (foncées)
    _limb(d, sx + 1.0, sy, f1[0], f1[1], 2.1, C["dark"])
    _limb(d, hx + 1.2, hy, h1[0], h1[1], 2.1, C["dark"])
    # queue
    bx, by = R(cx - rx + 0.9, cy - ry * 0.5)
    pts = _spline([(bx, by)] + [(bx + px, by + py) for px, py in tail], 4)
    if tail_wave[0]:
        pts = _wave(pts, tail_wave[0], tail_wave[1])
    _cat_tail(d, C, pts, 1.5, 1.35)
    # corps, ventre clair, rayures
    body = ellipse(cx, cy, rx, ry, btr)
    d.clip("catbody", [body])
    d.add(body, C["fur"])
    d.add(ellipse(cx + 1.5, cy + ry * 0.82, rx * 0.68, ry * 0.42, btr), C["belly"], sil=False, clip="catbody")
    _cat_stripes(d, C, "catbody", btr, cx, cy - ry, ry, (cx - 2.6, cx + 0.4, cx + 3.2))
    _spot(d, C, "catspot", [body], ellipse(cx - 0.6, cy - ry * 0.85, 3.4, 2.1, btr))
    # pattes proches : arrière (cuisse orientée vers le pied) puis avant
    _limb(d, hx, hy, h2[0], h2[1], 2.3, C["fur"])
    _thigh(d, C["fur"], hx, hy, h2[0], h2[1], 3.3, 2.7)
    _limb(d, sx, sy, f2[0], f2[1], 2.2, C["fur"])
    # tête
    hx_, hy_ = R(cx + rx + 0.2, cy - 5.0)
    hdx, hdy, hrot = head
    hx_, hy_ = hx_ + hdx, hy_ + hdy
    _cat_head(d, C, hx_, hy_, f"rotate({hrot:.1f} {hx_ - 2:.2f} {hy_ + 3:.2f})" if hrot else "", ears=ears, eye=eye)
    return d


def _cat_walk(C, phase=0.0):
    """Marche : pattes en diagonale (comme Tecky), queue dressée en point d'interrogation."""
    a, b = phase, phase + math.pi

    def foot(x, ph):
        return (x + 2.0 * math.cos(ph), G - max(0.0, math.sin(ph)) * 1.6)

    bob = 0.35 * abs(math.sin(phase))
    sway = math.sin(phase) * 0.7
    legs = [foot(20.8, b), foot(10.8, a), foot(9.2, b), foot(19.2, a)]
    return _cat_stand(C, hop=bob, legs=legs, head=(0, bob * 0.5, 0),
                      tail=[(-3.2, -1.4), (-4.6 + sway * 0.5, -5.6), (-4.0 + sway, -9.6), (-1.8 + sway, -11.4)])


def _cat_run(C, k=0):
    """Galop allongé en 4 temps : allongé, réception avant, rassemblé, poussée arrière."""
    K = [  # tilt, hop, rx, ry, pieds (avant-loin, arrière-loin, arrière-proche, avant-proche)
        (-2, 1.4, 8.4, 3.6, [(26.4, 25.8), (4.2, 26.4), (5.2, 25.6), (27.6, 26.6)]),
        (6, 0.4, 7.9, 3.7, [(22.4, G), (7.4, 24.4), (8.6, 23.8), (24.2, G - 0.4)]),
        (0, -0.2, 6.9, 4.1, [(16.0, G - 0.6), (14.6, G), (12.8, G - 0.2), (17.8, G)]),
        (-7, 1.2, 7.8, 3.7, [(21.2, 23.6), (8.6, G), (10.4, G - 0.3), (22.6, 22.6)]),
    ]
    tilt, hop, rx, ry, legs = K[k]
    return _cat_stand(C, cy=21.2, rx=rx, ry=ry, tilt=tilt, hop=hop, legs=legs, head=(0.2, 1.4, 5), ears=0.55,
                      tail=[(-3.4, -0.4), (-6.2, -1.8), (-8.4, -1.8)], tail_wave=(1.2, k * math.pi / 2),
                      shadow=(15.5, 9.0 - hop * 0.6))


def _cat_jump(C, k=0):
    """0 : élan (accroupi, prêt à bondir) ; 1 : bond étiré vers l'avant et le haut."""
    if k == 0:
        return _cat_stand(C, cx=14.2, cy=23.2, rx=7.6, ry=3.7, tilt=3, legs=[(20.6, G), (11.6, G), (9.8, G), (19.0, G)],
                          head=(-0.8, 3.0, 4), ears=0.15, tail=[(-3.4, 1.6), (-6.2, 2.4), (-8.6, 1.0)],
                          shadow=(15.0, 9.4))
    return _cat_stand(C, cx=15.6, cy=19.4, rx=8.8, ry=3.4, tilt=-24, hop=2.5,
                      legs=[(27.8, 10.6), (3.4, 26.6), (4.6, 25.6), (28.6, 12.2)], head=(0.8, 0.6, -4), ears=0.4,
                      tail=[(-3.6, 2.0), (-6.2, 4.2), (-8.4, 4.6)], shadow=(15.0, 6.5))


def _cat_hiss(C, k=0):
    """Dos rond en arche, poils hérissés, queue dressée et gonflée, bouche ouverte (« Pfff ! »)."""
    d = Drawing(W, H)
    up = 0.7 * k
    puff = 0.8 + 0.35 * k
    _shadow(d, 15.0, G, 8.6)
    # arche du dos (courbe extérieure) : de la croupe à l'épaule
    P0, P1, P2, P3 = (8.8, 22.4), (7.4, 8.4 - up), (20.6, 7.6 - up), (21.2, 19.6)

    def arch(t):
        u = 1 - t
        return tuple(u ** 3 * P0[i] + 3 * u * u * t * P1[i] + 3 * u * t * t * P2[i] + t ** 3 * P3[i] for i in (0, 1))

    # pattes lointaines, raides
    _limb(d, 11.4, 21.4, 11.2, G, 2.0, C["dark"])
    _limb(d, 20.2, 20.4, 21.4, G, 2.0, C["dark"])
    # queue dressée, gonflée, un peu en S
    pts = _spline([(9.4, 17.0), (7.4, 13.0), (8.0, 8.8 - up), (6.6, 4.8 - up)], 4)
    _cat_tail(d, C, pts, 1.6, 1.5, puff=puff)
    # poils hérissés le long de l'arche : dents de scie derrière le corps
    teeth = []
    N = 18
    for i in range(N + 1):
        t = 0.14 + 0.66 * i / N
        x, y = arch(t)
        (x0, y0), (x1, y1) = arch(t - 0.01), arch(t + 0.01)
        nx, ny = (y1 - y0), -(x1 - x0)
        ln = math.hypot(nx, ny) or 1
        o = (0.9 + 0.7 * puff) if i % 2 else -0.4
        teeth.append((x + nx / ln * o, y + ny / ln * o))
    d.add(poly(teeth + [arch(0.6), (15, 16), arch(0.3)]), C["fur"])
    # corps en arche : dos rond, ventre rentré
    body = path(f"M{P0[0]},{P0[1]} C{P1[0]},{P1[1]} {P2[0]},{P2[1]} {P3[0]},{P3[1]} "
                f"L20.4,22.4 Q15.2,{15.6 - up:.2f} 10.6,23.4 Z")
    d.clip("cathiss", [body])
    d.add(body, C["fur"])
    sx_, sy_ = arch(0.45)
    _spot(d, C, "catspot", [body], ellipse(sx_ - 0.4, sy_ + 0.6, 3.4, 2.3, f"rotate(8 {sx_:.2f} {sy_:.2f})"))
    if C["stripe"]:
        for t in (0.32, 0.5, 0.68):
            x, y = arch(t)
            d.raw(_clipped("cathiss", "", line(f"M{x:.2f},{y - 0.6:.2f} Q{x + 1.2:.2f},{y + 2:.2f} "
                                                f"{x + (t - 0.5) * 5:.2f},{y + 4.0:.2f}", C["stripe"], 1.15)))
    # pattes proches, raides (sur la pointe des pieds)
    _limb(d, 10.2, 21.4, 9.8, G, 2.2, C["fur"])
    _limb(d, 19.4, 20.6, 20.0, G, 2.2, C["fur"])
    # tête basse en avant, oreilles en arrière, crocs
    _cat_head(d, C, 24.2, 18.6 - up * 0.3, "rotate(-4 22.2 21.6)", ears=0.8, eye="angry", mouth=0.75 + 0.25 * k)
    return d


# ================================================================== animations
ANIMS = {   # espèce : {nom : (poses, fps, boucle)} ; chaque pose = dict(mode=..., paramètres)
    "squirrel": {
        "idle": ([dict(mode="sit", nib=0.0, wag=0.0), dict(mode="sit", nib=1.0, wag=0.7, chew=1.0),
                  dict(mode="sit", nib=0.7, wag=-0.5), dict(mode="sit", nib=1.0, wag=0.4, chew=1.0)], 6, True),
        "run": ([dict(mode="run", cx=15.4, cy=20.6, tilt=-3, rx=6.8, ry=3.6, ff=(24.6, 25.8), hf=(6.4, 24.6, -24),
                      wave=0.0, sh=6.5),
                 dict(mode="run", cx=16.0, cy=21.8, tilt=12, rx=6.4, ry=3.8, ff=(22.2, G), hf=(10.8, 25.6, 12),
                      wave=math.pi / 2, sh=7.5),
                 dict(mode="run", cx=15.6, cy=22.4, tilt=2, rx=5.4, ry=4.4, ff=(22.4, 26.2), hf=(17.6, G, 0),
                      wave=math.pi, sh=7.5),
                 dict(mode="run", cx=15.2, cy=21.0, tilt=-14, rx=6.6, ry=3.7, ff=(22.0, 23.4), hf=(9.6, G, 0),
                      wave=3 * math.pi / 2, sh=7.0)],
                14, True),
        "climb": ([dict(mode="climb", phase=k * math.pi / 2, wave=k * math.pi / 2) for k in range(4)], 12, True),
    },
    "cat": {
        "idle": ([dict(mode="sit", sweep=-1.0), dict(mode="sit", sweep=0.0), dict(mode="sit", sweep=1.0, blink=True),
                  dict(mode="sit", sweep=0.0)], 5, True),
        "walk": ([dict(mode="walk", phase=k * math.pi / 2) for k in range(4)], 10, True),
        "run": ([dict(mode="run", k=k) for k in range(4)], 14, True),
        "jump": ([dict(mode="jump", k=0), dict(mode="jump", k=1)], 8, False),
        "hiss": ([dict(mode="hiss", k=0), dict(mode="hiss", k=1)], 6, True),
    },
}

_DRAW = {
    "squirrel": {"sit": _sq_sit, "run": _sq_run, "climb": _sq_climb},
    "cat": {"sit": _cat_sit, "walk": _cat_walk, "run": _cat_run, "jump": _cat_jump, "hiss": _cat_hiss},
}


def anims(kind):
    """Animations d'un kind ("squirrel", "cat", "cat_black", "cat_white") : {nom : (poses, fps, boucle)}."""
    return ANIMS[SPECIES[kind]]


def pose(kind, mode, **kw):
    """Dessin (Drawing) d'une pose ; mode : 'sit', 'run', 'climb' (écureuil) ou 'sit', 'walk', 'run', 'jump',
    'hiss' (chats). Dessin à l'échelle de conception : la réduction SCALE est appliquée par frames()."""
    return _DRAW[SPECIES[kind]][mode](KINDS[kind], **kw)


def frames(kind, anim):
    """SVG des images d'une animation (vue de droite ; 'climb' : vue de dos)."""
    k = SCALE[SPECIES[kind]]
    tr = f"translate(16 {G}) scale({k}) translate(-16 -{G})" if k != 1 else ""
    out = []
    for p in anims(kind)[anim][0]:
        d = pose(kind, **p)
        if tr:
            d.under = [_g(tr, u) for u in d.under]
        out.append(d.svg(tr, outline_w=OUTLINE_W / k))
    return out
